#!/usr/bin/env python3
"""The artifact emulator's automatic look, run by Claude Code hooks at the end of a turn that published an artifact.

A look opens an artifact's files in the artifact emulator (a local copy of the real artifact viewer), saves one
picture of its first screen, and collects its console errors and an outline of what can be clicked in it.

In sessions where the cloud-container service turns this on (two flags, one per trigger), it installs two Claude Code
hooks that run this file, and sets EMULATOR_LOOK_TRIGGERS to "first", "republish" or "first,republish":
  post-tool  after every tool call: notes an Artifact tool publish for this turn (a first publish, or a later one),
             an Artifact or ArtifactCheck call whose result holds a rendered preview, and a Read of a picture an
             earlier look saved.
             It uses no network and never starts the emulator.
  stop       at the end of the turn: looks at each of up to three artifacts the turn published, and no preview
             has shown since, at its final state, and hands Claude a short summary of each look: the paths of its
             picture and of a file holding what the page showed, whether it finished starting, and how many errors it
             logged.
The page's own text never goes into what Claude is handed: Claude can Read the file, and so meets it as a tool result.
The text handed to Claude is read from auto_look_message.txt beside this file; without it, nothing happens. If no look
succeeds, or the input is not recognized, it prints nothing and exits 0, so the turn ends as it would have.
The fourth mode, flush, which the stop mode starts as a detached child when it ends, posts the counted events to the
artifact service's POST /track.

The look mode,
  look --source <page file or folder>
  look --type-files <folder> --project <folder> --contract <version>
runs one look for another program. It runs this skill's bootstrap.py, then the look script of SKILL.md (or of
look-node.md, where bootstrap.py names Node Playwright) with its placeholder lines filled in. It prints one JSON line,
{"format": 1, "pictures": [path], "marks": [...], "errors": [...], "outline": "..."}, and exits 0; prints nothing and
exits 1 if the look could not be made; and exits 2 with a usage message on wrong arguments. The errors and outline may
contain text from the page. The format goes up whenever a program reading the line would have to change.
"""

import fcntl
import json
import os
import re
import signal
import stat
import sys
import time

# subprocess, tempfile and argparse are imported where they are used: run as a hook, this file starts after every tool
# call, and most of those runs need none of them.

HERE = os.path.dirname(os.path.realpath(__file__))
SKILL_DIR = os.path.dirname(HERE)
BOOTSTRAP = os.path.join(HERE, "bootstrap.py")
PYTHON = "/usr/bin/python3"
SELF = os.path.realpath(__file__)
MESSAGE = os.path.join(HERE, "auto_look_message.txt")
MESSAGE_SLOT = "{{LOOK_RESULTS_JSON}}"  # where the message file takes the look's results, exactly once
STATE_DIR = os.path.join(os.path.expanduser("~"), ".claude", "emulator-look")

# True leaves artifacts made from a type (Slides, Design) out of the automatic look; each one left out is counted
# as "skipped_type".
LEAVE_OUT_TYPED = False

BUDGET_S = 90          # a look command, or the whole stop mode, bootstrap.py included
LOOK_S = 45            # one run of the look script, at most
LOOK_RESERVE_S = 35    # seconds kept back from bootstrap.py's limit so that the first look can still start
STOP_GRACE_S = 12      # between SIGTERM and SIGKILL when a run's process group is stopped, for the server to clean up
SETTLE_S = STOP_GRACE_S + 3  # what a run cut off at its limit may still take
LOOK_FORMAT = 1        # the "format" in the look command's JSON line (see the look mode above)
MAX_OUT = 1 << 20
MAX_STDIN = 32 << 20   # a hook's input: a Read of an image carries the image in base64
CONTRACT_VERSION_RE = re.compile(r"[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}")
LONE_SURROGATE_RE = re.compile("[\ud800-\udfff]")
TRIGGERS = ("first", "republish")
MODES = {"first": "first_publish", "republish": "republish"}  # a turn's trigger, as counted
MAX_ARTIFACTS = 3      # looks in one turn
BOOT_BACKOFF_S = 600   # after bootstrap.py passes its time limit in the stop mode, no look is tried for this long
MAX_STATE = 256 << 10
MAX_MESSAGE = 1500
MAX_CONTEXT = 9000     # Claude Code passes Claude at most 10,000 characters of a hook's text, else only a preview
KEEP = {"notes": 30, "previews": 30, "instances": 50, "several": 50, "pictures": 60, "events": 60, "looked": 20,
        "timeouts": 5}
EVENT = "frame_emulator_look"
TRACK_PATH = "/track"
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
ID_RE = re.compile(r"[A-Za-z0-9._:-]{1,200}")
CONTRACT_RE = re.compile(r'contract\s+`"(' + CONTRACT_VERSION_RE.pattern + r')"`')
ASSET_KEYS = ("asset_upload", "asset_uploads", "asset_copy")

# Placeholder lines in the look scripts of SKILL.md and look-node.md. look_command() replaces each exactly once, so they
# must match those files exactly.
PY_PATHS = '"<command>", "<shellDir>", "<runtimeDir>", "<workDir>"'
PY_SOURCE = 'SOURCE, EXTRA = "<a plain page: its .html file or folder, absolute>", []'
PY_TYPED = 'TYPE_FILES, PROJECT = "", ""'
JS_PATHS = '["<command>", "<shellDir>", "<runtimeDir>", "<workDir>"]'
JS_PLAYWRIGHT = 'const PLAYWRIGHT = "<playwright>";'
JS_SOURCE = 'let SOURCE = "<a plain page: its .html file or folder, absolute>", EXTRA = [];'
JS_TYPED = 'const TYPE_FILES = "", PROJECT = "";'


def plain_path(value):
    """value normalised, if it is an absolute path of at most 4096 characters with no control characters; else None."""
    if (isinstance(value, str) and 1 < len(value) <= 4096 and os.path.isabs(value)
            and not any(ord(c) < 32 or c == "\x7f" for c in value)):
        return os.path.normpath(value)
    return None


def inside(path, folder):
    """path with every symbolic link resolved, if path is a plain absolute path (see plain_path) to a file and
    resolves to somewhere inside folder, which must end in os.sep; else None."""
    # isfile() follows the path as given, as the kernel will; realpath would return a missing or looping path partly
    # unresolved. Resolve the path as given too: normalising first cancels a '..' against the symbolic link before it.
    path = plain_path(path) and os.path.isfile(path) and plain_path(os.path.realpath(path))
    return path if path and path.startswith(folder) else None


def drain_stdin():
    """Standard input read to its end, of which the first MAX_STDIN + 1 bytes are kept."""
    kept = bytearray()
    while block := sys.stdin.buffer.read(1 << 20):
        if len(kept) <= MAX_STDIN:
            kept += block[:MAX_STDIN + 1 - len(kept)]
    return bytes(kept)


def script_block(name, fence):
    with open(os.path.join(SKILL_DIR, name), encoding="utf-8") as f:
        parts = f.read().split("```" + fence + "\n")
    if len(parts) != 2:
        raise ValueError(name)
    return parts[1].split("```")[0]


def fill(script, changes):
    for old, new in changes:
        if script.count(old) != 1:
            raise ValueError(old)
        script = script.replace(old, new)
    return script


def look_command(boot, shown):
    """The look script with its first lines filled in, and how to run it, as the skill says."""
    source, type_files, project, contract = shown
    extra = ["--contract", contract, "--caps-from-meta"] if type_files else []
    js = lambda v: json.dumps(v, ensure_ascii=True)  # a quoted value, never text spliced into code
    paths = [boot["command"], boot["shellDir"], boot["runtimeDir"], boot["workDir"]]
    if boot.get("node") and boot.get("playwright"):
        script = fill(script_block("look-node.md", "javascript"), [
            (JS_PATHS, js(paths)), (JS_PLAYWRIGHT, "const PLAYWRIGHT = %s;" % js(boot["playwright"])),
            (JS_SOURCE, "let SOURCE = %s, EXTRA = %s;" % (js(source), js(extra))),
            (JS_TYPED, "const TYPE_FILES = %s, PROJECT = %s;" % (js(type_files), js(project)))])
        env = {**os.environ, "HOME": "/", "NODE_OPTIONS": "", "NODE_PATH": "", "NODE_COMPILE_CACHE": "",
               "NODE_DISABLE_COMPILE_CACHE": "1"}
        return [boot["node"], "-"], script, env
    script = fill(script_block("SKILL.md", "python"), [
        (PY_PATHS, ", ".join(map(repr, paths))), (PY_SOURCE, "SOURCE, EXTRA = %r, %r" % (source, extra)),
        (PY_TYPED, "TYPE_FILES, PROJECT = %r, %r" % (type_files, project))])
    return [PYTHON, "-I", "-"], script, dict(os.environ)


RUNNING = None  # the child run() has in flight, for stop_on_signal


def run(cmd, stdin, timeout, env=None):
    """(exit code, standard output) of cmd, in a process group of its own that is stopped whole at the time limit.
    The exit code is None if cmd was stopped there, or not started because less than a second was left."""
    import subprocess
    global RUNNING
    if timeout <= 1:
        return None, ""
    p = RUNNING = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   cwd="/", env=env, start_new_session=True)
    try:
        try:
            out, _ = p.communicate(stdin.encode() if stdin else None, timeout=timeout)
        except subprocess.TimeoutExpired:
            stop_group(p)
            return None, ""
        try:
            os.killpg(p.pid, 0)  # succeeds only if something it started still runs, such as an emulator server
            stop_group(p)
        except (ProcessLookupError, PermissionError):  # PermissionError: only another user's processes are left
            pass
        return p.returncode, out[:MAX_OUT].decode("utf-8", "replace")
    finally:
        RUNNING = None  # its group id is no longer ours to signal


def stop_group(p):
    """SIGTERM to the whole group, so the emulator's server can stop its browser and remove its files, then SIGKILL to
    whatever is left of the group after STOP_GRACE_S."""
    import subprocess
    try:
        os.killpg(p.pid, signal.SIGTERM)
        end = time.monotonic() + STOP_GRACE_S
        while time.monotonic() < end:
            os.killpg(p.pid, 0)
            p.poll()
            time.sleep(0.2)
        os.killpg(p.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:  # bounded: a descendant that left the group could still hold the output pipe open
        p.communicate(timeout=2)
    except subprocess.TimeoutExpired:
        p.kill()


def stop_on_signal(signum, frame):
    """For SIGTERM or SIGINT while a look runs: stop the run in flight and everything in its process group, as at a
    time limit, then exit. Without this the look script, its emulator server and its browser would outlive us."""
    for again in (signal.SIGTERM, signal.SIGINT):  # a second signal must not start the grace over
        signal.signal(again, signal.SIG_IGN)
    if RUNNING is not None:
        try:
            os.killpg(RUNNING.pid, signal.SIGTERM)
            end = time.monotonic() + STOP_GRACE_S
            while time.monotonic() < end:
                os.killpg(RUNNING.pid, 0)
                RUNNING.poll()
                time.sleep(0.2)
            os.killpg(RUNNING.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
    os._exit(128 + signum)


class TimedOut(Exception):
    """bootstrap.py did not finish inside the time it was given."""


def bootstrap(deadline):
    code, out = run([PYTHON, "-I", BOOTSTRAP], "", deadline - LOOK_RESERVE_S - SETTLE_S - time.monotonic())
    if code is None:
        raise TimedOut()
    lines = out.strip().splitlines()
    if code != 0 or not lines:
        return None
    boot = json.loads(lines[-1])
    keys = ("command", "shellDir", "runtimeDir", "workDir") + (("node", "playwright") if "node" in boot else ())
    if not all(plain_path(boot.get(k)) for k in keys):
        return None
    return boot


def read_look(out):
    """What a look script printed, as one dict: the object on its first line merged with the one between its two fence lines,
    which name the same marker; the opening line may add a colon and more words after it. Where both have a key, the first
    line's value is kept. Raises ValueError on any other shape."""
    first, begin, rest = out.partition("\n=== BEGIN PAGE REPORT ")
    opening, _, rest = rest.partition(" ===\n")
    marker = opening[:8]
    report, end, after = rest.partition("\n=== END PAGE REPORT " + marker + " ===")
    if not (begin and end and re.fullmatch("[0-9a-f]{8}", marker) and opening[8:9] in ("", ":")) or after.strip() or "\n" in first + opening:
        raise ValueError("fence")
    first, report = json.loads(first), json.loads(report)
    if not (isinstance(first, dict) and isinstance(report, dict)):
        raise ValueError("fence")
    return {**report, **first}


def look(boot, shown, deadline):
    """What one look saw, or None. The errors and outline may contain text from the page."""
    cmd, script, env = look_command(boot, shown)
    code, out = run(cmd, script, min(LOOK_S, deadline - SETTLE_S - time.monotonic()), env)
    if code != 0:
        return None
    seen = read_look(out)
    work = os.path.realpath(boot["workDir"]) + os.sep
    pictures = seen.get("screenshots")
    pictures = [inside(p, work) for p in pictures] if isinstance(pictures, list) else []
    if not (pictures and all(pictures)):
        return None
    text = lambda x, size: LONE_SURROGATE_RE.sub("\ufffd", str(x)[:size])  # a lone surrogate could not be encoded later
    strings = lambda v, n, size: [text(x, size) for x in v[:n]] if isinstance(v, list) else []
    return {"pictures": pictures[:1], "marks": strings(seen.get("marks"), 30, 60),
            "errors": strings(seen.get("errors"), 10, 700), "outline": text(seen.get("outline") or "", 3000)}


def look_cli(argv):
    import argparse
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, stop_on_signal)
    ap = argparse.ArgumentParser(prog="auto_look.py look", description="One look at an artifact's files in the "
                                 "emulator: one JSON line on success (exit 0), nothing on failure (exit 1).")
    ap.add_argument("--source", help="for a plain page (not made from a type): its absolute .html path, or an absolute "
                    "folder with index.html at the top")
    ap.add_argument("--type-files", help="for an artifact made from a type: absolute path of the folder holding the "
                    "type's own files")
    ap.add_argument("--project", help="for an artifact made from a type: absolute path of its project/ folder")
    ap.add_argument("--contract", help="for an artifact made from a type: the contract version named in the type's "
                    "SKILL.md, such as 0.2.47")
    args = ap.parse_args(argv)
    typed = (args.type_files, args.project, args.contract)
    if args.source and not any(typed) and plain_path(args.source):
        shown = (plain_path(args.source), "", "", "")
    elif (not args.source and all(typed) and plain_path(args.type_files) and plain_path(args.project)
          and CONTRACT_VERSION_RE.fullmatch(args.contract)):
        shown = ("", plain_path(args.type_files), plain_path(args.project), args.contract)
    else:
        ap.error("give either --source for a plain page, or all three of --type-files, --project and --contract for an "
                 "artifact made from a type. Paths must be absolute, and the contract version looks like 0.2.47.")
    deadline = time.monotonic() + BUDGET_S
    try:
        boot = bootstrap(deadline)
        seen = boot and look(boot, shown, deadline)
    except Exception:
        seen = None
    if not seen:
        return 1
    sys.stdout.write(json.dumps({"format": LOOK_FORMAT, **seen}) + "\n")
    return 0


class Quiet(Exception):
    """Stop here, print nothing, exit 0."""


def triggers():
    asked = [t.strip() for t in os.environ.get("EMULATOR_LOOK_TRIGGERS", "").split(",") if t.strip()]
    if not asked or any(t not in TRIGGERS for t in asked):
        return set()
    return set(asked)


def read_input(data):
    if len(data) > MAX_STDIN:
        raise Quiet()
    inp = json.loads(data)
    if not isinstance(inp, dict):
        raise Quiet()
    return inp


def artifact_id(*values):
    for value in values:
        if isinstance(value, str):
            found = UUID_RE.findall(value.lower())
            if found:
                return found[-1]
    return None


def token_id(value):
    return value if isinstance(value, str) and ID_RE.fullmatch(value) else None


def state_dir():
    os.makedirs(STATE_DIR, mode=0o700, exist_ok=True)
    st = os.lstat(STATE_DIR)
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid() or st.st_mode & 0o077:
        raise Quiet()
    return STATE_DIR


class State:
    """The state file under an exclusive lock: with State() as s: s.data[...]; saved on a clean exit."""

    def __enter__(self):
        directory = state_dir()
        self.path = os.path.join(directory, "state.json")
        self.lock = os.open(os.path.join(directory, "lock"), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        deadline = time.monotonic() + 1  # short, so a hook with a time limit gives up cleanly rather than being killed
        while True:
            try:
                fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > deadline:
                    os.close(self.lock)
                    raise Quiet()
                time.sleep(0.05)
        self.data = self.load()
        return self

    def load(self):
        empty = {key: [] for key in KEEP}
        try:
            fd = os.open(self.path, os.O_RDONLY | os.O_NOFOLLOW)
        except FileNotFoundError:
            return empty
        with os.fdopen(fd, "rb") as f:
            raw = f.read(MAX_STATE + 1)
        try:
            data = json.loads(raw) if len(raw) <= MAX_STATE else None
        except ValueError:
            data = None
        if not isinstance(data, dict):
            return empty
        return {k: [x for x in data[k] if isinstance(x, str if k in ("looked", "several") else dict)]
                if isinstance(data.get(k), list) else [] for k in empty}

    def __exit__(self, kind, error, tb):
        global PENDING
        try:
            if kind is None:
                PENDING = bool(self.data["events"])
                for key, keep in KEEP.items():
                    self.data[key] = self.data[key][-keep:]
                import tempfile
                fd, tmp = tempfile.mkstemp(prefix=".state-", dir=os.path.dirname(self.path))
                try:
                    with os.fdopen(fd, "w") as f:
                        json.dump(self.data, f)
                    os.replace(tmp, self.path)
                except BaseException:
                    os.unlink(tmp)
                    raise
        finally:
            os.close(self.lock)
        return False


PENDING = False  # whether counted events wait to be posted, as of the last save


def count(state, mode, via, slug=None):
    state.data["events"].append({"mode": mode, "via": via, **({"slug": slug} if slug else {})})


def post_tool(inp):
    name, args, result = inp.get("tool_name"), inp.get("tool_input"), inp.get("tool_response")
    if name == "Read" and isinstance(args, dict):
        opened = plain_path(args.get("file_path"))
        if opened and re.fullmatch(r"look(-[0-9]+)?\.png", os.path.basename(opened)):  # the look scripts' names
            with State() as state:
                for picture in state.data["pictures"]:
                    if isinstance(picture, dict) and picture.get("path") == opened and not picture.get("opened"):
                        picture["opened"] = True
                        count(state, picture.get("mode"), "picture_opened", picture.get("slug"))
        return
    if name not in ("Artifact", "ArtifactCheck") or not isinstance(args, dict) or not isinstance(result, dict):
        return
    for key in ("preview", "emulatorPreview"):  # the local preview, and the emulator's own
        if isinstance(result.get(key), dict):
            note_preview(inp, args, result[key], key == "emulatorPreview")
            return
    if name != "Artifact" or any(key in result for key in ASSET_KEYS):
        return  # not a publish: an ArtifactCheck call without a preview, or an upload of a picture or a font
    if result.get("created_from_type") is True:
        # already_created: an earlier attempt of this same call created it, so this is not a first publish
        kind = "republish" if result.get("already_created") is True else "first"
        slug, typed = artifact_id(result.get("url")), True
    elif isinstance(result.get("updated"), bool):
        kind = "republish" if result["updated"] else "first"
        slug, typed = artifact_id(result.get("artifact_id"), result.get("url")), False
    else:
        return
    if not slug:
        return
    turn = token_id(inp.get("prompt_id"))
    root, file_path = plain_path(args.get("root")), plain_path(args.get("file_path"))
    if root and file_path and file_path.startswith(os.path.join(root, "project") + os.sep):
        typed = True  # a files-only publish to an artifact made from a type: its content is root's project/ folder
    with State() as state:
        instances = state.data["instances"]
        earlier = next((i for i in instances if isinstance(i, dict) and i.get("slug") == slug), None)
        if typed:  # remembered past this turn: a later turn's publish to it may not say it was made from a type
            kept = {"slug": slug, "root": root or (earlier or {}).get("root")}
            instances[:] = [i for i in instances if i is not earlier] + [kept]
        typed = typed or bool(earlier)
        if args.get("files") and not typed and slug not in state.data["several"]:  # remembered for its later publishes
            state.data["several"].append(slug)
        if not turn:
            return
        unchanged = result.get("unchanged") is True  # the artifact service made no new version
        note = next((n for n in state.data["notes"] if n.get("turn") == turn and n.get("slug") == slug), None)
        if note is None:
            note = {"turn": turn, "slug": slug, "kind": kind, "unchanged": unchanged}
            state.data["notes"].append(note)
        else:
            note["kind"] = "first" if kind == "first" else note["kind"]
            note["unchanged"] = note.get("unchanged") and unchanged
        note["typed"] = typed
        note["several_files"] = slug in state.data["several"]
        note["at"] = time.time_ns()
        scratch = plain_path(inp.get("scratchpad_dir"))
        for key, value in (("root", root or (earlier or {}).get("root")), ("file_path", file_path),
                           ("scratch", scratch and os.path.join(scratch, "artifact-files", slug))):
            if value:
                note[key] = value


def note_preview(inp, args, preview, emulator):
    """Notes a preview that rendered, so the stop mode skips an artifact a preview has shown since its last publish.
    preview is the local preview's result ("shots"), or with emulator the emulator preview's ("outcome", "pictures")."""
    turn = token_id(inp.get("prompt_id"))
    shots = preview.get("pictures" if emulator else "shots")
    rendered = isinstance(shots, list) and any(
        isinstance(s, dict) and s.get("path") and not s.get("error") for s in shots)
    rendered = rendered and (preview.get("outcome") == "looked" if emulator else "renderError" not in preview)
    if not (turn and rendered):
        return
    seen = {"turn": turn, "at": time.time_ns(), "slug": artifact_id(args.get("url"), preview.get("url")),
            "path": plain_path(preview.get("file")) or plain_path(args.get("file_path"))}
    if seen["path"] or seen["slug"]:
        with State() as state:
            state.data["previews"].append(seen)


def previewed(note, previews):
    """Whether any of previews showed this artifact after its last publish."""
    return any(p.get("at", 0) > note.get("at", 0) and ((p.get("slug") and p["slug"] == note["slug"])
               or (p.get("path") and p["path"] in (note.get("file_path"), note.get("root")))) for p in previews)


def message():
    """The text handed to Claude, from the file beside this one: None if it is missing or not of the expected form."""
    try:
        with open(MESSAGE, encoding="utf-8") as f:
            text = f.read(MAX_MESSAGE + len(MESSAGE_SLOT) + 1).strip()
    except OSError:
        return None
    if text.count(MESSAGE_SLOT) != 1 or len(text) - len(MESSAGE_SLOT) > MAX_MESSAGE:
        return None
    return text


def what_to_show(note):
    """(SOURCE, TYPE_FILES, PROJECT, contract) for the look script, or None if it cannot be worked out from disk."""
    if not note.get("typed"):  # a plain page is its file_path, published as the artifact's index.html
        source = note.get("file_path")
        return (source, "", "", "") if source and os.path.isfile(source) else None
    root = note.get("root")
    if not root or not os.path.isdir(os.path.join(root, "project")):
        return None
    # the type's own page files: beside project/, or where an earlier read of the artifact saved them
    for folder in (root, note.get("scratch")):
        if folder and os.path.isfile(os.path.join(folder, "index.html")) and not os.path.islink(folder):
            try:
                with open(os.path.join(folder, "SKILL.md"), encoding="utf-8", errors="replace") as f:
                    found = CONTRACT_RE.search(f.read(200_000))
            except OSError:
                found = None
            if found:
                return ("", folder, os.path.join(root, "project"), found.group(1))
    return None


def several_files(note):
    """Whether a plain page was published with supporting files, which a look at its one file would not show."""
    return not note.get("typed") and bool(note.get("several_files"))


def not_html(note):
    """Whether a plain page's file is not an .html page, which the look script cannot show."""
    return not note.get("typed") and not (note.get("file_path") or "").lower().endswith((".html", ".htm"))


def backing_off(state):
    """Whether bootstrap.py passed its time limit at the end of a turn within the last BOOT_BACKOFF_S seconds."""
    now = time.time()
    ages = [now - t["at"] for t in state.data["timeouts"] if isinstance(t.get("at"), (int, float))]
    return any(0 <= age < BOOT_BACKOFF_S for age in ages)  # a time ahead of the clock does not count


def keep_results(note, seen):
    """The summary of one look that Claude is handed. What the page showed (its outline, errors and marks) is written to
    an owner-only file beside the picture, for Claude to Read as a tool result; the summary holds none of it."""
    picture = seen["pictures"][0]
    path = os.path.join(os.path.dirname(picture), "look.json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"artifact": note["slug"], **seen}, f, ensure_ascii=False, indent=1)
    return {"artifact": note["slug"], "published_this_turn": "first" if note["kind"] == "first" else "again",
            "picture": picture, "results": path, "ready": "ready" in seen["marks"], "errors": len(seen["errors"])}


def as_text(template, summaries):
    """The message with the summaries in its slot as one JSON value, if it fits in MAX_CONTEXT UTF-16 code units (as
    Claude Code counts); else None."""
    text = template.replace(MESSAGE_SLOT, json.dumps(summaries, ensure_ascii=True, indent=1))
    return text if len(text.encode("utf-16-le")) // 2 <= MAX_CONTEXT else None


def stop(inp, wanted):
    deadline = time.monotonic() + BUDGET_S
    turn = token_id(inp.get("prompt_id"))
    template = message()
    with State() as state:
        notes = [n for n in state.data["notes"] if turn and n.get("turn") == turn and isinstance(n.get("slug"), str)
                 and n.get("kind") in TRIGGERS]
        previews = [p for p in state.data["previews"] if turn and p.get("turn") == turn]
        state.data["notes"] = [n for n in state.data["notes"] if n not in notes]  # this turn's are used up
        state.data["previews"] = [p for p in state.data["previews"] if p not in previews]
        mode = MODES["first" if any(n.get("kind") == "first" for n in notes) else "republish"]
        if not notes or template is None or ("first" if mode == "first_publish" else "republish") not in wanted:
            return None
        for why, skip in (("skipped_unchanged", lambda n: n.get("unchanged")),
                          ("skipped_previewed", lambda n: previewed(n, previews)),
                          ("skipped_type", lambda n: LEAVE_OUT_TYPED and n.get("typed")),
                          ("skipped_several_files", several_files), ("skipped_not_html", not_html)):
            for n in notes:
                if skip(n):
                    count(state, mode, why, n["slug"])
            notes = [n for n in notes if not skip(n)]
        notes = notes[:MAX_ARTIFACTS]
        if not notes:
            return None
        if inp.get("stop_hook_active") is True:
            # counted only when another Stop hook set it: after this script's own look, its own output set it
            if turn not in state.data["looked"] and not backing_off(state):
                count(state, mode, "skipped_other_stop_hook")
            return None
        if backing_off(state):
            for n in notes:
                count(state, mode, "skipped_emulator_backoff", n["slug"])
            return None
        for n in notes:
            count(state, mode, "started", n["slug"])
    outcomes = []
    try:
        boot = bootstrap(deadline)
    except TimedOut:
        with State() as state:
            state.data["timeouts"].append({"at": time.time()})
            for n in notes:
                count(state, mode, "failed_bootstrap_timeout", n["slug"])
        return None
    except Exception:
        boot = None
    for n in notes:
        try:
            shown = boot and what_to_show(n)
            seen = shown and look(boot, shown, deadline)
            outcomes.append((n, seen and keep_results(n, seen)))
        except Exception:
            outcomes.append((n, None))
    summaries = [summary for n, summary in outcomes if summary]
    text = summaries and as_text(template, summaries)
    try:  # the counts must not cost Claude a look that worked
        with State() as state:
            for n, summary in outcomes:
                via = "looked" if summary and text else "failed_too_long" if summary else "failed"
                count(state, mode, via, n["slug"])
                if summary and text:
                    state.data["pictures"].append({"path": os.path.normpath(summary["picture"]), "mode": mode,
                                                   "slug": n["slug"]})
            if text:
                state.data["looked"].append(turn)
    except Exception:
        pass
    if not text:
        return None
    return {"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": text}}


def start_flush():
    import subprocess
    subprocess.Popen([PYTHON, "-I", SELF, "flush"], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd="/", start_new_session=True)


def load_bootstrap():
    import importlib.util
    spec = importlib.util.spec_from_file_location("artifact_emulator_bootstrap", BOOTSTRAP)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def flush():
    with State() as state:
        events, state.data["events"] = state.data["events"], []
    events = [{"event_name": EVENT, **{k: e[k] for k in ("slug", "mode", "via") if isinstance(e.get(k), str)}}
              for e in events if isinstance(e, dict)]
    if not events:
        return
    boot = load_bootstrap()
    try:
        # the session's proxy to the artifact service (base URL, token file, curl and CA paths), found the way
        # bootstrap.py finds it
        base, token_file, tools = boot.preflight()
    except (boot.Stop, OSError):
        return  # the emulator cannot run here: nothing is sent, and the counts taken out are dropped
    batches, batch = [], []
    for event in events:  # the artifact service's batch form takes at most 20 events, naming at most 2 artifacts
        slugs = {e.get("slug") for e in batch + [event] if e.get("slug")}
        if len(batch) == 20 or len(slugs) > 2:
            batches.append(batch)
            batch = []
        batch.append(event)
    batches.append(batch)
    env = {k: v for k, v in os.environ.items() if k.lower() in boot.PROXY_VARS}
    import subprocess
    sent = 0
    for batch in batches[:4]:
        token = boot.read_token(token_file)
        # As bootstrap.py does: the token travels in a config read from stdin, never on the command line, in the
        # environment, or in a file this script writes.
        cmd = [tools["curl"], "-q", "-sS", "--proto", "=https", "--max-redirs", "0", "--connect-timeout", "3",
               "--max-time", "8", "--cacert", tools["ca"], "-K", "-", "-H", "Content-Type: application/json",
               "--data-binary", json.dumps({"events": batch}), "-o", os.devnull, base + TRACK_PATH]
        try:
            subprocess.run(cmd, input='oauth2-bearer = "%s"\n' % token, capture_output=True, text=True, env=env,
                           timeout=12)
        except subprocess.TimeoutExpired:  # it may have arrived: not sent again, so nothing is counted twice
            sent += 1
            break
        sent += 1
    unsent = [event for batch in batches[sent:] for event in batch]
    if unsent:  # never tried: left for the next flush, ahead of anything counted since
        with State() as state:
            state.data["events"][:0] = [{k: e[k] for k in ("slug", "mode", "via") if k in e} for e in unsent]


def main(argv):
    if argv[1:2] == ["look"]:
        return look_cli(argv[2:])
    mode = argv[1] if len(argv) == 2 else ""
    data = b"" if mode == "flush" else drain_stdin()  # read whole: Claude Code reports a hook that leaves input unread
    wanted = triggers()
    if mode not in ("post-tool", "stop", "flush") or not wanted:
        return 0
    os.umask(0o077)
    try:
        if mode == "flush":
            flush()
            return 0
        if not os.path.isfile(MESSAGE):
            return 0  # no text to hand Claude: take no notes and look at nothing
        # Not a tool this script notes: skip parsing what may be a large input. The cloud-container service's
        # post-tool hook applies the same two tests before it starts Python (emulatorLookNoteMarkers in
        # api-go/ccr/internal/emulatorlook/emulatorlook.go): change the two together.
        if mode == "post-tool" and b"Artifact" not in data and b'"Read"' not in data:
            return 0
        inp = read_input(data)
        if mode == "post-tool":
            post_tool(inp)
            return 0
        for signum in (signal.SIGTERM, signal.SIGINT):  # the service may stop a stop hook that runs too long
            signal.signal(signum, stop_on_signal)
        out = stop(inp, wanted)
        if out is not None:
            sys.stdout.write(json.dumps(out))
            sys.stdout.flush()
    except Exception:
        return 0
    finally:
        if mode == "stop" and PENDING:
            try:
                start_flush()
            except Exception:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
