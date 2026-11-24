#!/usr/bin/env python3
"""Unpack a zip of an artifact type's own files, as the artifact service packs them, into a new folder in the emulator's
work folder. Prints one JSON line saying where the files are.
A zip that is not in the form the service packs is refused with a plain message. Nothing in the zip is run.
"""

import argparse
import errno
import io
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import warnings
import zipfile
import zlib

# The tool's full name, as in SKILL.md's step 2, so that Claude does not take another server's emulator_type_files for it.
TOOL = "mcp__claude-artifacts__emulator_type_files"
# Fixed on purpose, as in bootstrap.py, which makes ROOT/run: no caller can have the files unpacked anywhere else.
ROOT = "/opt/frame-emulator"
# How claude-code-server (with the eight closing hex digits) and Claude Code (without) name a file saved from an answer of
# the MCP server named claude-artifacts. A file saved from another server's answer is refused.
SAVED_NAME_RE = re.compile(r"mcp-claude-artifacts-blob-[0-9]{1,20}-[A-Za-z0-9]{1,6}(-[0-9a-f]{8})?\.zip")
# The zip's first member: a JSON summary of the other members. No file of a type can have this name.
NOTE = "_emulator/type-files.json"
NOTE_KEYS = ["bytes", "contract", "files", "leftOut", "v"]  # in sorted order
CONTRACT_RE = re.compile(r"(0|[1-9][0-9]{0,3})\.(0|[1-9][0-9]{0,4})\.(0|[1-9][0-9]{0,5})")
MAX_ZIP_BYTES = 8 * 1024 * 1024
MAX_FILES = 64
MAX_FOLDERS = 64  # counting every folder above each file
MAX_TOTAL_BYTES = 16 * 1024 * 1024
MAX_NOTE_BYTES = 4096
MAX_NAME_BYTES = 512
MAX_PART_BYTES = 255  # the longest file or folder name that Linux takes
PLAIN_FILE = 0o100644 << 16  # a member's external attributes: a regular file, mode 0644, and nothing else
SIZES_FOLLOW, UTF8_NAME = 0x0008, 0x0800  # the only flag bits a member may carry in the zip's central directory
CARRY_ON = "say that you could not check how the artifact looks, and carry on"
AGAIN = "If this happens again, " + CARRY_ON
# What Claude is told, keyed by the short code (such as M2) of the check that refused. A line holds that code, and O1's
# line the name of an errno too. It never holds an argument, a member's name, a file's bytes or an exception's text:
# a stranger may have chosen those.
LINES = {code: line for codes, line in (
    ("A1", f"this script takes one argument: the path of the file that the {TOOL} tool saved [{{code}}]. " + AGAIN),
    ("W1", "the emulator's work folder is missing or unsafe [{code}]; do not create or change it yourself. If you have not "
           "run bootstrap.py (the skill's step 1) in this session, run it and try once more. Otherwise " + CARRY_ON),
    ("Z1 Z2", f"the argument is not a file that the {TOOL} tool saved; pass the path from that tool's answer [{{code}}]. "
              + AGAIN),
    ("Z3 Z4 Z5 M1 M2 M3 M4 M5 N1 M6", "the saved file is not the zip that the artifact service sends [{code}]. "
                                      f"Call {TOOL} once more. " + AGAIN),
    ("O1", "could not write the files ({detail}) [{code}]. " + CARRY_ON.capitalize()),
) for code in codes.split()}


class Stop(Exception):
    def __init__(self, code, detail=""):
        super().__init__(LINES[code].format(code=code, detail=detail))


class Arguments(argparse.ArgumentParser):
    def error(self, message):  # argparse's own words would repeat the arguments, and its exit status is 2
        raise Stop("A1")


def say(msg):
    print(msg, file=sys.stderr, flush=True)


def work_dir():
    """The emulator's work folder, by its real path. Stops unless it is a directory, not a link, that this user owns and
    nobody else can open, with no directory above it that another user could change (sticky ones such as /tmp excepted):
    so the folder that is checked here is the one that is written to later."""
    path = step = os.path.join(os.path.realpath(ROOT), "run")
    try:
        st = os.lstat(path)
        ok = stat.S_ISDIR(st.st_mode) and st.st_uid == os.geteuid() and not st.st_mode & 0o077
        while ok and step != os.path.dirname(step):
            step = os.path.dirname(step)
            st = os.lstat(step)
            ok = st.st_uid in (0, os.geteuid()) and (not st.st_mode & 0o022 or bool(st.st_mode & stat.S_ISVTX))
    except OSError:
        ok = False
    if not ok:
        raise Stop("W1")
    return path


def read_saved(path):
    """The bytes of the saved file at path, read once. Every later check and read is of this copy, so nothing that happens
    to the file afterwards matters."""
    if not SAVED_NAME_RE.fullmatch(os.path.basename(path)):
        raise Stop("Z1")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)  # O_NONBLOCK: opening a pipe must not wait
    except OSError:
        raise Stop("Z2")
    try:
        st, data = os.fstat(fd), b""
        if not stat.S_ISREG(st.st_mode) or not 0 < st.st_size <= MAX_ZIP_BYTES:
            raise Stop("Z3")
        while block := os.read(fd, st.st_size + 1 - len(data)):  # one byte past that size and no further
            data += block
    except OSError:
        raise Stop("Z2")
    finally:
        os.close(fd)
    if len(data) != st.st_size:  # its size changed while it was read
        raise Stop("Z3")
    return data


def good_name(name):
    """Whether name is a path that the artifact service stores a file under, by the service's own rule, that Linux can
    hold, and that has no part starting with a dot: the emulator silently skips a file with such a path."""
    raw = name.encode("utf-8")
    return (len(raw) <= MAX_NAME_BYTES and not any(ord(c) < 0x20 or c in "\x7f%;\\:" for c in name)
            and not name.endswith(".cmekshadow") and not name.startswith("_")
            # so no part is "", "." or "..": the path is relative, stays inside its folder and names a file
            and all(0 < len(part) <= MAX_PART_BYTES and not part.startswith(b".") for part in raw.split(b"/")))


def body(archive, member):
    """The member's bytes. Stops unless they are as many as the zip's central directory declares and match its checksum."""
    try:
        with archive.open(member) as f:
            # read(n), not read(): read() would unpack the whole stream before cutting it to the declared size
            data = f.read(member.file_size)
    except Exception:  # zipfile raises many kinds, and not the same ones in every version of Python
        raise Stop("M6")
    if len(data) != member.file_size or zlib.crc32(data) != member.CRC:  # zipfile checks no empty member's checksum
        raise Stop("M6")
    return data


def read_note(raw, files, total):
    """The contract named by the note, whose bytes are raw. Stops unless the note is one JSON object with exactly NOTE_KEYS,
    each once, and agrees with the central directory: files is how many members follow the note, total their declared bytes."""
    try:
        # An object becomes a tuple of its pairs, which keeps a key that is there twice. Nothing else in JSON becomes one.
        pairs = json.loads(raw.decode("utf-8"), object_pairs_hook=tuple)
        note = dict(pairs)
        ok = (type(pairs) is tuple and sorted(key for key, _ in pairs) == NOTE_KEYS
              and all(type(note[key]) is int for key in NOTE_KEYS if key != "contract")  # True is not an int here
              and note["v"] == 1 and note["files"] == files and note["bytes"] == total and note["leftOut"] >= 0
              and CONTRACT_RE.fullmatch(note["contract"]) is not None)
    except Exception:
        ok = False
    if not ok:
        raise Stop("N1")
    return note["contract"]


def check(data):
    """The contract and the files, as pairs of a name (in UTF-8) and its bytes, of the zip whose bytes are data.
    Writes nothing."""
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # as in body
        raise Stop("Z4")
    with archive:
        members = archive.infolist()
        if not members or members[0].header_offset != 0:  # zipfile accepts a zip with something else in front of it
            raise Stop("Z4")
        if archive.comment != b"":
            raise Stop("Z5")
        files = [m for m in members if m.filename != NOTE]
        total = sum(m.file_size for m in files)
        if len(members) > MAX_FILES + 1 or total > MAX_TOTAL_BYTES:
            raise Stop("M1")
        # zipfile cuts a name at a NUL byte, and from Python 3.12 on replaces it with the one in a Unicode path extra field
        # (0x7075): orig_filename is the name as it stands in the central directory
        if any(m.orig_filename != m.filename for m in members) or not all(good_name(m.filename) for m in files):
            raise Stop("M2")
        if any(m.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED) or m.flag_bits & ~(SIZES_FOLLOW | UTF8_NAME)
               for m in members):
            raise Stop("M3")
        if not all(m.filename.isascii() or m.flag_bits & UTF8_NAME for m in members):  # else zipfile read the name as cp437
            raise Stop("M3")
        if any(m.external_attr != PLAIN_FILE for m in members):
            raise Stop("M4")
        names = [m.filename.encode("utf-8") for m in files]
        folders = {name[:at] for name in names for at in range(len(name)) if name[at:at + 1] == b"/"}
        if len(folders) > MAX_FOLDERS:
            raise Stop("M1")
        if any(a >= b for a, b in zip(names, names[1:])):  # in order, so none is there twice
            raise Stop("M5")
        if folders.intersection(names):  # one member's name is a folder in another's
            raise Stop("M5")
        if (len(members) != len(files) + 1 or members[0].filename != NOTE or members[0].file_size > MAX_NOTE_BYTES
                or b"index.html" not in names):
            raise Stop("N1")
        contract = read_note(body(archive, members[0]), len(files), total)
        return contract, [(name, body(archive, m)) for name, m in zip(names, files)]


def write(work, unpacked):
    """Writes the files into a new folder in work and returns its path. If one cannot be written, that folder is removed."""
    out = None
    try:
        out = tempfile.mkdtemp(prefix="type-", dir=work)  # mode 0700: the emulator runs as this user
        for name, data in unpacked:
            dest = os.path.join(os.fsencode(out), name)  # in bytes, so the locale has no say in a file's name
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644), "wb") as f:
                f.write(data)
    except BaseException as e:
        if out is not None:
            shutil.rmtree(out, ignore_errors=True)
        if isinstance(e, OSError):
            raise Stop("O1", errno.errorcode.get(e.errno, "unknown cause"))
        raise
    return out


def main():
    ap = Arguments(formatter_class=argparse.RawDescriptionHelpFormatter,  # argparse can break the tool's name at its hyphen
                   description=f"Unpack the zip of an artifact type's files that the tool\n{TOOL}\nsaved. Takes the saved "
                   "file's path. Prints one JSON line:\ntypeFiles (the folder), contract, files (how many).")
    ap.add_argument("zip")
    warnings.simplefilter("ignore")  # a warning from zipfile can carry a member's name to the terminal
    os.umask(0o022)  # files come out 0644 and folders 0755: the emulator refuses a file that others may not read
    try:
        args = ap.parse_args()
        work = work_dir()
        contract, unpacked = check(read_saved(args.zip))
        out = write(work, unpacked)
    except Stop as e:
        say(f"artifact-emulator: stopped: {e}")
        return 1
    except Exception as e:
        say(f"artifact-emulator: stopped: unexpected error ({type(e).__name__}). {CARRY_ON.capitalize()}")
        return 1
    print(json.dumps({"typeFiles": out, "contract": contract, "files": len(unpacked)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
