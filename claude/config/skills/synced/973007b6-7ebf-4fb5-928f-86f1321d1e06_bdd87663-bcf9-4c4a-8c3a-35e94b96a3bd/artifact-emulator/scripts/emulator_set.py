"""The zip of the emulator's own files, as a tool of the artifact service saves it where there is no session token file:
learning that the service made it and still holds it, checking it, and unpacking it. bootstrap.py loads this. It prints
and runs nothing.

What is unpacked is run as this user, and other files can lie where the zip is looked for, so the order matters. Until
the service has said yes to the list's sha256, every byte of a zip is a stranger's. After that only the list is the service's.
"""

import hashlib
import io
import json
import os
import re
import shutil
import stat
import tempfile
import time
import warnings
import zipfile
import zlib

# The tool's full name, as in SKILL.md's step 1, so that Claude does not take another server's tool for it.
TOOL = "mcp__claude-artifacts__emulator_files"
# The zip's first member: the list of the others. No file of a set can have this name.
LIST = "_emulator/set.json"
KEPT_LIST = "set.json"  # the list's bytes, kept at the top of an unpacked set
MAX_ZIP_BYTES = 8 * 1024 * 1024
MAX_LIST_BYTES = 256 * 1024
MAX_FILES = 1024
MAX_TOTAL_BYTES = 24 * 1024 * 1024
MAX_PATH_BYTES = 240
# Names of ASCII letters, digits, ".", "_" and "-", none starting with a dot, joined by single slashes. Use fullmatch.
PATH_RE = re.compile(r"[A-Za-z0-9_-][A-Za-z0-9._-]*(/[A-Za-z0-9_-][A-Za-z0-9._-]*)*")
PROGRAM, VIEWER, RUNTIME = "program", "shell", "runtime"
HEX64_RE = re.compile(r"[0-9a-f]{64}")
PLAIN_FILE = 0o100644 << 16  # a member's external attributes: a regular file, mode 0644, and nothing else
SIZES_FOLLOW, UTF8_NAME = 0x0008, 0x0800  # the only flag bits a member may carry
PACKED_AT = (1980, 1, 1, 0, 0, 0)
END_RECORD, END_RECORD_BYTES = b"PK\x05\x06", 22
MAX_ZIPS_TRIED = 3
ASKS, ASK_PAUSE_S = 5, 2.0
OLD_SET_S = 24 * 3600  # an unpacked set that is not the one in use is removed once it is this old
CARRY_ON = "say that you could not check how the artifact looks, and carry on"
AGAIN = (f"Call {TOOL} with no arguments, then run this script once more. If the tool refuses, do as its description says. "
         "If it is not listed, or if this happens again, " + CARRY_ON)
# What Claude is told, keyed by the short code of the check that refused. A line holds that code and nothing else that
# varies: never a member's name, a file's bytes or an exception's text, which a stranger may have chosen.
LINES = {code: line for codes, line in (
    ("F1", "the emulator's files are not in this session yet [{code}]. " + AGAIN),
    ("F2", "the artifact service did not confirm the emulator's files that are saved here, or could not be reached [{code}]. "
           + AGAIN),
    ("Z1 Z2 L1 L2 L3 M1 M2 M3 M4 M5", "the saved file is not the zip that the artifact service sends [{code}]. " + AGAIN),
    ("O1", "could not write the emulator's files [{code}]. " + CARRY_ON.capitalize()),
) for code in codes.split()}


class Refused(Exception):
    """Why no set could be had, in words for Claude."""

    def __init__(self, code):
        super().__init__(LINES[code].format(code=code))
        self.code = code


def body(archive, member, size):
    """The member's bytes. Refuses unless they are size bytes and match the zip's checksum for them."""
    if member.file_size != size:
        raise Refused("M5")
    try:
        with archive.open(member) as f:
            # read(n), not read(): it stops unpacking at n bytes, whatever the stream goes on to hold
            data = f.read(size)
    except Exception:  # zipfile raises many kinds, and not the same ones in every version of Python
        raise Refused("M5")
    if len(data) != size or zlib.crc32(data) != member.CRC:  # zipfile checks no empty member's checksum
        raise Refused("M5")
    return data


def open_zip(data):
    try:
        return zipfile.ZipFile(io.BytesIO(data))
    except Exception:  # as in body
        raise Refused("Z1")


def list_of(data):
    """The bytes of the list in the zip whose bytes are data, unpacked and not parsed. They are the list from here on:
    a planted zip can hold a second member of the list's name, and zipfile returns the last when asked by name."""
    with open_zip(data) as archive:
        members = archive.infolist()  # in the order of the central directory
        if not members or members[0].header_offset != 0:  # zipfile accepts a zip with something else in front of it
            raise Refused("Z1")
        first = members[0]
        if (first.orig_filename != LIST or first.filename != LIST or first.compress_type != zipfile.ZIP_DEFLATED
                or first.file_size > MAX_LIST_BYTES):
            raise Refused("L1")
        return body(archive, first, first.file_size)


def set_id(raw_list):
    return hashlib.sha256(raw_list).hexdigest()


def exactly(pairs, keys):
    """The object whose pairs these are, as a dict. Raises unless it is an object with exactly these keys, each once."""
    if type(pairs) is not tuple or sorted(key for key, _ in pairs) != sorted(keys):
        raise ValueError
    return dict(pairs)


def read_list(raw_list):
    """(entry, files) from the list's bytes, files being (path, bytes, sha256) in the list's order. Refuses a list that
    is not in the form the artifact service writes."""
    try:
        # An object becomes a tuple of its pairs, which keeps a key that is there twice. Nothing else in JSON becomes one.
        top = exactly(json.loads(raw_list.decode("utf-8"), object_pairs_hook=tuple), ("v", "entry", "files"))
        listed = [exactly(pairs, ("path", "bytes", "sha256")) for pairs in top["files"]]
        files = [(f["path"], f["bytes"], f["sha256"]) for f in listed]
        paths = [path.encode("ascii") for path, _, _ in files]
        folders = {path[:at] for path in paths for at in range(len(path)) if path[at:at + 1] == b"/"}
        ok = (type(top["v"]) is int and top["v"] == 1 and type(top["files"]) is list and 0 < len(files) <= MAX_FILES
              and all(PATH_RE.fullmatch(path) and len(path) <= MAX_PATH_BYTES and type(size) is int and size >= 0
                      and HEX64_RE.fullmatch(digest) for path, size, digest in files)
              and all(path.split("/")[0] in (PROGRAM, VIEWER, RUNTIME) and "/" in path for path, _, _ in files)
              and sum(size for _, size, _ in files) <= MAX_TOTAL_BYTES
              and all(a < b for a, b in zip(paths, paths[1:]))  # in order, so none is there twice
              and not folders.intersection(paths)  # no file's path is a folder in another's
              and all(path.count("/") == 1 for path, _, _ in files if path.startswith(PROGRAM + "/"))
              and type(top["entry"]) is str and top["entry"].startswith(PROGRAM + "/")
              and top["entry"] in (path for path, _, _ in files))
    except Exception:
        ok = False
    if not ok:
        raise Refused("L2")
    return top["entry"], files


def check(data, raw_list):
    """(entry, files) of the zip whose bytes are data, files being (path, bytes of the file). raw_list is what list_of gave
    for data, and the artifact service has said yes to it. Every path comes from it and none from the zip. Writes nothing."""
    entry, listed = read_list(raw_list)
    with open_zip(data) as archive:
        members = archive.infolist()
        if archive.comment != b"" or data[-END_RECORD_BYTES:][:len(END_RECORD)] != END_RECORD:  # nothing after the archive
            raise Refused("Z2")
        # zipfile cuts a name at a NUL byte, and from Python 3.12 on replaces it with the one in a Unicode path extra field
        # (0x7075): orig_filename is the name as it stands in the central directory
        if any(m.orig_filename != m.filename for m in members):
            raise Refused("M1")
        # The list, then each listed file, in order: so no name is there twice, none is missing and none is unlisted.
        if [m.filename for m in members] != [LIST] + [path for path, _, _ in listed]:
            raise Refused("M1")
        if any(m.compress_type != zipfile.ZIP_DEFLATED or m.flag_bits & ~(SIZES_FOLLOW | UTF8_NAME) for m in members):
            raise Refused("M2")
        if any(m.external_attr != PLAIN_FILE for m in members):
            raise Refused("M3")
        if any(m.date_time != PACKED_AT for m in members):
            raise Refused("M4")
        if body(archive, members[0], len(raw_list)) != raw_list:  # only if the caller passed another zip's list
            raise Refused("L3")
        files = []
        for member, (path, size, digest) in zip(members[1:], listed):
            unpacked = body(archive, member, size)
            if hashlib.sha256(unpacked).hexdigest() != digest:
                raise Refused("M5")
            files.append((path, unpacked))
    return entry, files


def sets_folder(root):
    """root's folder of unpacked sets, made if need be. bootstrap.py's safe_root has checked root."""
    sets = os.path.join(root, "sets")
    os.makedirs(sets, mode=0o755, exist_ok=True)
    st = os.lstat(sets)
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid() or st.st_mode & 0o022:
        raise Refused("O1")
    return sets


def write(sets, name, raw_list, files):
    """Writes the files and the list into a new folder in sets, and only when all are written gives it its name. Returns
    its path. If one cannot be written, the new folder is removed."""
    out = None
    try:
        out = tempfile.mkdtemp(prefix=".incoming-", dir=sets)
        for path, data in [(KEPT_LIST, raw_list)] + files:
            dest = os.path.join(out, path)
            os.makedirs(os.path.dirname(dest), mode=0o755, exist_ok=True)
            with os.fdopen(os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644), "wb") as f:
                f.write(data)
        os.chmod(out, 0o755)
        final = os.path.join(sets, name)
        if os.path.lexists(final) and intact(final) is None:  # damaged since an earlier run unpacked it
            os.rename(final, os.path.join(tempfile.mkdtemp(prefix=".old-", dir=sets), "replaced"))
        try:
            os.rename(out, final)
        except OSError:
            if intact(final) is None:  # unless another run finished first
                raise
            shutil.rmtree(out, ignore_errors=True)
        return final
    except BaseException as e:
        if out is not None:
            shutil.rmtree(out, ignore_errors=True)
        if isinstance(e, OSError):
            raise Refused("O1")
        raise


def intact(path):
    """The entry of the unpacked set at path, or None unless its folder is named by its list's sha256 and every listed file
    is there, no link, with the listed size and sha256."""
    try:
        if not (HEX64_RE.fullmatch(os.path.basename(path)) and stat.S_ISDIR(os.lstat(path).st_mode)):
            return None
        with open(os.path.join(path, KEPT_LIST), "rb") as f:
            raw_list = f.read(MAX_LIST_BYTES + 1)
        if set_id(raw_list) != os.path.basename(path):
            return None
        entry, listed = read_list(raw_list)
        for file_path, size, digest in listed:
            at = os.path.join(path, file_path)
            if os.path.islink(at) or os.path.getsize(at) != size:
                return None
            with open(at, "rb") as f:
                if hashlib.sha256(f.read(size + 1)).hexdigest() != digest:
                    return None
        return entry
    except (OSError, Refused):
        return None


def kept(sets):
    """The unpacked sets in sets that are intact, newest first: (id, path, entry). A set was confirmed when it was unpacked,
    and only this user can have changed it since, so this catches damage and no more."""
    found = []
    for name in os.listdir(sets):
        path = os.path.join(sets, name)
        entry = intact(path)
        if entry is not None:
            found.append((os.lstat(path).st_mtime_ns, name, path, entry))
    return [(name, path, entry) for _, name, path, entry in sorted(found, reverse=True)]


def tidy(sets, keep):
    """Removes what cut-off runs left in sets, and unpacked sets other than keep that were unpacked OLD_SET_S ago or earlier.
    Newer sets stay, because an emulator that an earlier run started may still be reading them."""
    for name in os.listdir(sets):
        path = os.path.join(sets, name)
        try:
            age = time.time() - os.lstat(path).st_mtime
        except OSError:
            continue
        if path != keep and age > (600 if name.startswith((".incoming-", ".old-")) else OLD_SET_S):
            shutil.rmtree(path, ignore_errors=True)


def install(root, saved_zips, ask, pause=ASK_PAUSE_S):
    """The folder of a set of the emulator's files that the artifact service confirms now, and the path in it of the
    program's file to run. Takes a set that an earlier run unpacked, else the newest of saved_zips (each a zip's bytes,
    newest first) that the service confirms. ask(id) is True only if the service said yes, which it says only to
    the newest set that it holds and, for some ten minutes, to the one before. That, and no date of a file's, is what keeps an
    old set from coming back. Raises Refused."""
    warnings.simplefilter("ignore")  # a warning from zipfile can carry a member's name to the terminal
    sets = sets_folder(root)
    candidates, refusal = [(name, None, None, (path, entry)) for name, path, entry in kept(sets)[:1]], None
    for data in saved_zips[:MAX_ZIPS_TRIED]:
        try:
            raw_list = list_of(data)
            candidates.append((set_id(raw_list), data, raw_list, None))
        except Refused as e:
            refusal = refusal or e
    if not candidates:
        raise refusal or Refused("F1")
    for attempt in range(ASKS):
        if attempt:
            time.sleep(pause)
        answers = {}  # one question for each id in each round: two zips can hold one list
        for candidate in list(candidates):
            name, data, raw_list, unpacked = candidate
            if name not in answers:
                answers[name] = ask(name)
            if not answers[name]:
                continue
            try:
                if unpacked is None:
                    entry, files = check(data, raw_list)
                    unpacked = write(sets, name, raw_list, files), entry
            except Refused as e:
                if e.code == "O1":
                    raise
                # a genuine list over other files: an older zip may hold the same list over the genuine ones
                refusal = refusal or e
                candidates.remove(candidate)
                continue
            tidy(sets, unpacked[0])
            return unpacked
        if not candidates:
            break
    raise refusal or Refused("F2")
