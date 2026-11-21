"""What a tool of the artifact service saved in this session: finding the files, and taking from them the answers about
this user that the emulator needs. bootstrap.py imports this. It prints nothing, runs nothing and fetches nothing.
"""

import calendar
import hashlib
import json
import os
import re
import stat
import tempfile
import time

# Claude Code saves a tool's binary answer under RESULTS, in a folder named by its own id for the session: a UUID that it
# derives from the session's cse_ id (deriveStableSessionIdFromCse in its source), not the UUID inside that id.
RESULTS = "/tmp/claude-tool-results"
UUID_RE = re.compile(r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")
# How claude-code-server (with the eight closing hex digits) and Claude Code (without) name a file saved from an answer of
# the MCP server named claude-artifacts, less the extension. The name only sorts files: it proves nothing about where one came from.
SAVED_STEM = r"mcp-claude-artifacts-blob-[0-9]{1,20}-[A-Za-z0-9]{1,6}(-[0-9a-f]{8})?"
MAX_SAVED_FILES_READ = 64
# The artifact service names a session by a mark: the first 32 hex digits of the SHA-256 of this label and then the name of
# the session's folder, which it derives as Claude Code does. The label must match the service's byte for byte, or nothing
# that it saved is ever found.
MARK_LABEL = b"frame/emulator-session/v1\0"

# The tool's full name, as in SKILL.md's step 1, so that Claude does not take another server's tool for it.
ANSWERS_TOOL = "mcp__claude-artifacts__emulator_caller_answers"
ANSWERS_KIND = "emulator-caller-answers"
ANSWERS_FILE = ".caller-answers.json"  # where the emulator's serve command looks, beside the viewer
MAX_ANSWERS_BYTES = 8 * 1024
# SKILL.md has Claude call the tool just before each run, so an older answer is another run's.
ANSWERS_MAX_AGE_S = 900
ANSWERS_MAX_AHEAD_S = 300  # this machine's clock and the artifact service's may differ
TIME_RE = re.compile(r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]{3}Z")
# Why take_answers found nothing, for whoever debugs it. The sentence holds the code alone, never anything from a file.
NO_RESULTS = "R1"  # RESULTS is missing, is a link, or could be changed by another user
FOLDER_REFUSED = "R2"  # so is a session's folder in it, and nothing was found in the others
NOTHING_SAVED = "R3"  # no file with a saved file's name, of a size that answers can have
NOT_ANSWERS = "R4"  # such files, but none is an answers file of the version that this script knows
ANOTHER_SESSIONS = "R5"  # an answers file whose mark is not that of the folder it lay in
OUT_OF_DATE = "R6"  # an answers file of this session, too old or dated too far ahead


def no_answers(code):
    """What to stop with when take_answers gives None."""
    return (f"no fresh answer of the {ANSWERS_TOOL} tool was found in this session [{code}]. Call that tool, then run this "
            "script once more. If the tool refuses, do as its description says. If it is not listed, or if this happens again, "
            "say that you could not check how the artifact looks, and carry on")


def open_folder(name, dir_fd=None):
    """A descriptor for a real directory (never a link to one) that only root or this user can change, or None."""
    try:
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd)
    except OSError:
        return None
    st = os.fstat(fd)
    if st.st_uid in (0, os.geteuid()) and not st.st_mode & 0o022:
        return fd
    os.close(fd)
    return None


def session_mark(folder):
    return hashlib.sha256(MARK_LABEL + folder.encode("ascii")).hexdigest()[:32]


def saved_files(extension, max_bytes, most=MAX_SAVED_FILES_READ, refused=None):
    """What the artifact service's tools saved under RESULTS with this extension, newest first: a list of pairs, the mark of
    the session whose folder it lay in, and the file's bytes. Takes only regular files, never links, of 1 to max_bytes
    bytes, the newest `most` of them, in folders that open_folder accepts. Changes nothing. Given a list as `refused`, adds
    NO_RESULTS or FOLDER_REFUSED to it for each folder that open_folder did not accept."""
    name_re, opened, listed, found = re.compile(SAVED_STEM + re.escape(extension)), {}, [], []
    refused = [] if refused is None else refused
    try:
        opened[""] = top = open_folder(RESULTS)
        if top is None:
            refused.append(NO_RESULTS)
        for session in os.listdir(top) if top is not None else ():
            if not UUID_RE.fullmatch(session):
                continue
            opened[session] = folder = open_folder(session, top)
            if folder is None:
                refused.append(FOLDER_REFUSED)
            before = len(listed)
            for name in os.listdir(folder) if folder is not None else ():
                try:
                    st = os.stat(name, dir_fd=folder, follow_symlinks=False) if name_re.fullmatch(name) else None
                except OSError:  # gone since it was listed
                    continue
                if st and stat.S_ISREG(st.st_mode) and 0 < st.st_size <= max_bytes:
                    listed.append((st.st_mtime_ns, name, session))
            if folder is not None and len(listed) == before:  # only a folder with something to read stays open
                os.close(opened.pop(session))
        for _, name, session in sorted(listed, reverse=True)[:most]:
            try:
                # O_NONBLOCK: what was a regular file when listed may be a pipe by now, and opening one must not wait
                with os.fdopen(os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=opened[session]), "rb") as f:
                    data = f.read(max_bytes + 1) if stat.S_ISREG(os.fstat(f.fileno()).st_mode) else b""
            except OSError:
                continue
            if 0 < len(data) <= max_bytes:
                found.append((session_mark(session), data))
    except OSError:
        pass
    finally:
        for fd in opened.values():
            if fd is not None:
                os.close(fd)
    return found


def whats_wrong(data, mark, now):
    """An empty string if data is an answers file of the session with this mark, fetched at most ANSWERS_MAX_AGE_S before
    now; otherwise the code that says why not. A member that this script does not know is passed over, so that the service can add one.
    This catches mix-ups only: the file is not signed, and whoever can see the folder's name can write one."""
    try:
        answers = json.loads(data.decode("utf-8"))
        if not (type(answers["v"]) is int and answers["v"] == 1 and answers["kind"] == ANSWERS_KIND):
            return NOT_ANSWERS
        fetched = calendar.timegm(time.strptime(TIME_RE.fullmatch(answers["fetchedAt"])[1], "%Y-%m-%dT%H:%M:%S"))
        if answers["s"] != mark:
            return ANOTHER_SESSIONS
        return "" if -ANSWERS_MAX_AHEAD_S <= now - fetched <= ANSWERS_MAX_AGE_S else OUT_OF_DATE
    except Exception:
        return NOT_ANSWERS


def take_answers():
    """A pair: the bytes of the newest saved file in which whats_wrong finds nothing, and "". Or None and a code for
    no_answers: of what was wrong with the files, the one that came nearest; with no files, why there were none."""
    now, refused = time.time(), []
    wrong = []
    for mark, data in saved_files(".bin", MAX_ANSWERS_BYTES, refused=refused):
        wrong.append(whats_wrong(data, mark, now))
        if not wrong[-1]:
            return data, ""
    return None, max(wrong or refused or [NOTHING_SAVED])


def write_answers(viewer_dir, data):
    """Puts take_answers' bytes, unchanged, where the emulator's serve command looks for them: beside the viewer. Written
    whole under another name first, so that serve never finds half a file, and nothing at that name is written through."""
    fd, partial = tempfile.mkstemp(prefix=ANSWERS_FILE + ".", suffix=".partial", dir=viewer_dir)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(partial, 0o644)
        os.rename(partial, os.path.join(viewer_dir, ANSWERS_FILE))
    except BaseException:
        if os.path.lexists(partial):  # it is gone if the script was told to stop just after the rename
            os.unlink(partial)
        raise
