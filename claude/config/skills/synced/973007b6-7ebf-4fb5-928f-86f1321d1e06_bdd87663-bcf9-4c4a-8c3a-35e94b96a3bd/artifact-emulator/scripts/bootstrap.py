#!/usr/bin/env python3
"""Fetch the artifact emulator into a cloud session: download the program, check it against its published sha256
hashes, install it under /opt/frame-emulator, write the command /usr/local/bin/frame-emulator, and have the program
fill /opt/frame-emulator/cache with the viewer and runtime. Prints one JSON line saying where everything is.
Where it cannot run it stops with a plain message.
"""

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.parse

RELAY_PREFIX = "/v1/code/agent-proxy/frame"
# The only hosts that are sent the session's token, and the only ones whose program is run.
API_HOST_RE = re.compile(r"api(-[a-z0-9-]+)?\.anthropic\.com")
# The certificate bundle curl trusts and the program is given, whatever the environment says.
CA_BUNDLE = "/etc/ssl/certs/ca-certificates.crt"
PROXY_VARS = ("http_proxy", "https_proxy", "all_proxy", "no_proxy")
DEFAULT_TOKEN_FILE = "/home/claude/.claude/remote/.session_ingress_token"
# Fixed on purpose: the script takes no options, so no caller can point it at another place or program.
ROOT = "/opt/frame-emulator"
COMMAND = "/usr/local/bin/frame-emulator"
# The browser comes from this directory only: its "chromium" link, else the one chromium-<digits> download in it.
BROWSERS = "/opt/pw-browsers"
REVISION_RE = re.compile(r"chromium-[0-9]{1,9}")
# Where a chromium-<digits> download keeps the program on Linux x64: chrome-linux up to Playwright 1.56, chrome-linux64
# from 1.57. arm64's chrome-linux-arm64 (Playwright 1.63 on) is left out: the cloud images this skill runs in are x64.
CHROME_DIRS = ("chrome-linux", "chrome-linux64")
CURL, BUN, PYTHON, NODE = "curl", "bun", "/usr/bin/python3", "node"
# Where Node Playwright may be, first found wins. {prefix} is two levels above the node that was found.
NODE_PLAYWRIGHT = ("/opt/node-tools/node_modules/playwright", "{prefix}/lib/node_modules/playwright",
                   "/usr/local/lib/node_modules_global/playwright")
# bin/node of Node's own linux-x64 releases: sha256 -> size in bytes, both worked out from the archive Node publishes.
# A node that fails trusted()'s check is never run where it is: private_node copies it, and hands back the copy only if
# it is one of these. The list, known_size, private_node and the copy_of hand-over in find_playwright and main can go
# once node passes that check wherever this skill is installed.
NODE_PROGRAMS = {"1bec56ef7cfa9a76f3e0b7c0a87f220eb73f23102b9c0b4c7529a3f7c3ce7c31": 123405064}  # v22.22.0
# A flat file name: no separator, no leading dot. Use fullmatch: match() with a $ would accept a trailing newline.
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
HEX64_RE = re.compile(r"[0-9a-f]{64}")
TOKEN_RE = re.compile(r"[A-Za-z0-9._~+/=-]{8,8192}")
MAX_FILES = 8
MAX_FILE_BYTES = 4 * 1024 * 1024
MAX_JSON_BYTES = 64 * 1024
DEFAULT_ENTRY = "frame-emulator.gen.js"
SAFE_PATH = "/usr/local/bin:/usr/bin:/bin"
PAUSE_S = 2.0
PROGRAM_DEADLINE_S = 240
TOTAL_BUDGET_S = 570  # SKILL.md tells Claude to allow ten minutes
# curl exit codes worth another try: could not resolve or connect, TLS handshake failed, empty reply, connection reset.
RETRY_EXITS = (5, 6, 7, 35, 52, 56)
NOT_HERE = "what this skill needs is not in this session, so it cannot run here. Carry on without it"
WHY = {
    401: "the session's token was refused (401); the session may have ended",
    403: "the artifact service refused this kind of credential (403)",
    404: "the emulator is not switched on for this account, or this version of the artifact service carries no "
         "emulator yet (404). Carry on without it",
    502: "the artifact service keeps answering 502; try once more in a minute, and if it still fails say the check "
         "is unavailable and carry on",
    503: "the artifact service is busy (503); try again in a minute",
    -63: "the artifact service sent more than this script accepts (4 MiB a file, 64 KiB for the file list)",
}


class Stop(Exception):
    pass


def say(msg):
    print(msg, file=sys.stderr, flush=True)


def why(code):
    """Plain words for a fetch result: an HTTP status, or minus curl's own exit code when it got no answer."""
    if code < 0 and code not in WHY:
        return "no answer from the artifact service (the connection failed or was too slow); try again in a minute"
    return WHY.get(code, f"the artifact service answered HTTP {code}")


def only_ours(path, what):
    """Stop unless path and every directory above it can be changed only by this user or root
    (sticky directories such as /tmp excepted). Returns the real path."""
    real = step = os.path.realpath(path)
    while True:
        st = os.stat(step)
        sticky_dir = stat.S_ISDIR(st.st_mode) and st.st_mode & stat.S_ISVTX
        if st.st_uid not in (0, os.geteuid()) or (st.st_mode & 0o022 and not sticky_dir):
            raise Stop(f"{step} can be changed by another user, so {what} cannot be trusted")
        if step == os.path.dirname(step):
            return real
        step = os.path.dirname(step)


def owner_only(path, what):
    """Stop if anyone but path's owner may write to it: the owner itself is for only_ours or tree_ours to check. Unlike
    only_ours, a sticky bit excuses nothing: for a directory that holds programs, where nobody else creates entries."""
    if os.stat(path).st_mode & 0o022:
        raise Stop(f"{os.path.realpath(path)} can be changed by another user, so {what} cannot be trusted")


def lookup(name):
    """Where a program is, or None. A name with no slash is looked up on SAFE_PATH, never $PATH."""
    found = shutil.which(name, path=SAFE_PATH) if os.sep not in name else name
    return found if found and os.access(found, os.X_OK) else None


def trusted(name):
    """Real path of a program found with lookup and checked with only_ours."""
    found = lookup(name)
    if not found:
        raise Stop(f"{name} is not installed here: {NOT_HERE}")
    only_ours(os.path.dirname(os.path.abspath(found)), name)
    return only_ours(found, name)


def tree_ours(top, what):
    """Stop unless everything in the directory tree at top belongs to root or this user and can be written by its owner
    alone, and nothing in it is a link: a link can pass through places this walk never sees, so the tree may hold none."""
    def unread(error):
        raise Stop(f"{error.filename} cannot be read, so {what} cannot be checked")

    for parent, dirs, files in os.walk(top, onerror=unread):
        for path in [parent] + [os.path.join(parent, name) for name in dirs + files]:
            st = os.lstat(path)
            if stat.S_ISLNK(st.st_mode):
                raise Stop(f"{path} is a link, and {top} may hold none, so {what} cannot be trusted")
            if st.st_uid not in (0, os.geteuid()) or st.st_mode & 0o022:
                raise Stop(f"{path} can be changed by another user, so {what} cannot be trusted")


def find_chromium():
    """Real path of the browser, from a closed list: the "chromium" link in BROWSERS, else the one
    chromium-<digits>/<a CHROME_DIRS folder>/chrome there. Whichever it is must resolve to a program of that very shape
    in BROWSERS, and is checked like curl and bun, with no allowance for a sticky bit from BROWSERS down.
    Nothing a caller could set, an option or a variable, is read."""
    link, what = os.path.join(BROWSERS, "chromium"), "the browser"
    if os.path.lexists(BROWSERS) and not (stat.S_ISDIR(os.lstat(BROWSERS).st_mode)):
        raise Stop(f"{BROWSERS} is not a real directory: {NOT_HERE}")
    if os.path.exists(link):
        found = [link]
    else:
        try:
            names = sorted(os.listdir(BROWSERS))
        except OSError:
            names = []
        found = [p for p in (os.path.join(BROWSERS, n, folder, "chrome") for n in names if REVISION_RE.fullmatch(n)
                             for folder in CHROME_DIRS)
                 if os.path.exists(p)]
    if not found:
        raise Stop(f"no browser under {BROWSERS}: {NOT_HERE}")
    if len(found) > 1:
        raise Stop(f"{len(found)} browsers under {BROWSERS} and nothing to say which to use: {NOT_HERE}")
    only_ours(os.path.dirname(found[0]), what)
    real, inside = only_ours(found[0], what), os.path.realpath(BROWSERS)
    revision, *rest = os.path.relpath(real, inside).split(os.sep)
    if not (REVISION_RE.fullmatch(revision) and rest in [[folder, "chrome"] for folder in CHROME_DIRS]
            and os.path.isfile(real) and os.access(real, os.X_OK)):
        raise Stop(f"{found[0]} is not a chromium-<digits>/chrome-linux/chrome program in {BROWSERS}: {NOT_HERE}")
    for step in (real, os.path.dirname(real), os.path.dirname(os.path.dirname(real)), inside):
        owner_only(step, what)
    return real


def find_playwright():
    """What SKILL.md's step 3 drives the browser with. Python Playwright, if this interpreter has it: returns {}.
    Else node (checked like bun; if it fails that check, private_node's copy of it, which main makes) and the playwright-core
    that node would load for the first Node Playwright found in NODE_PLAYWRIGHT: returns both paths; where node failed the
    check, "node" is None and "copy_of" holds (its real path, the Stop) for main to hand to private_node and remove.
    look-node.md's script loads from that one tree only, so only root or this user may be able to change it. Never
    $NODE_PATH, npx or an install."""
    if importlib.util.find_spec("playwright") is not None:
        return {}
    what = "Node Playwright"
    if lookup(NODE):
        refused = None
        try:
            node = at = trusted(NODE)
        except Stop as e:
            # node is then never run where it is: only as private_node's copy, which main makes once every check has passed
            node, at, refused = None, os.path.realpath(lookup(NODE)), e
            known_size(os.stat(at), refused)  # a first look: a node of no known size stops here, before anything is fetched
        for place in NODE_PLAYWRIGHT:
            if refused and "{prefix}" in place:  # no place is worked out from the path of a node that failed the check
                continue
            place = place.format(prefix=os.path.dirname(os.path.dirname(at)))
            if not os.path.isfile(os.path.join(place, "package.json")):
                continue
            only_ours(os.path.dirname(place), what)
            real = only_ours(place, what)
            above = os.path.dirname(real)  # node looks inside the package first, then beside it
            beside = above if os.path.basename(above) == "node_modules" else os.path.join(above, "node_modules")
            found = next((c for c in (os.path.join(real, "node_modules", "playwright-core"),
                                      os.path.join(beside, "playwright-core"))
                          if all(os.path.isfile(os.path.join(c, name)) for name in ("package.json", "index.js"))), None)
            if found is None:
                continue
            only_ours(os.path.dirname(found), what)
            core = only_ours(found, what)
            for directory in (os.path.dirname(place), above, os.path.dirname(found), os.path.dirname(core)):
                owner_only(directory, what)
            tree_ours(core, what)
            return {"node": node, "playwright": core, **({"copy_of": (at, refused)} if refused else {})}
    raise Stop(f"neither Python Playwright (for {sys.executable}) nor Node Playwright is installed: {NOT_HERE}")


def preflight():
    token_file = os.path.abspath(os.environ.get("CLAUDE_SESSION_INGRESS_TOKEN_FILE") or DEFAULT_TOKEN_FILE)
    if not os.path.isfile(token_file):
        raise Stop(f"no session token file at {token_file}: {NOT_HERE}")
    if not os.access(token_file, os.R_OK):
        raise Stop(f"cannot read the session token file at {token_file}, so the emulator cannot be fetched")
    tools = {"chromium": find_chromium(), "driver": find_playwright()}
    tools.update({"curl": trusted(CURL), "bun": trusted(BUN), "python": trusted(PYTHON)})
    base_url = (os.environ.get("ANTHROPIC_BASE_URL") or "").rstrip("/")
    u = urllib.parse.urlsplit(base_url)
    if not u.hostname or "@" in u.netloc or "?" in base_url or "#" in base_url or u.scheme not in ("https", "http"):
        raise Stop("ANTHROPIC_BASE_URL is not set to a plain URL, so the artifact service cannot be found")
    if u.scheme != "https":
        raise Stop("refusing to send the session token over plain http")
    try:
        port_ok = u.port in (None, 443)
    except ValueError:
        port_ok = False
    if not (API_HOST_RE.fullmatch(u.hostname) and u.path == "" and port_ok):
        raise Stop(f"ANTHROPIC_BASE_URL is {base_url}, which is not an Anthropic API host: refusing to send it the "
                   "session token or to run what it serves")
    if not os.path.isfile(CA_BUNDLE):
        raise Stop(f"no certificate bundle at {CA_BUNDLE}: {NOT_HERE}")
    tools["ca"] = only_ours(CA_BUNDLE, "the certificate bundle")
    # Rebuilt from the parts just checked, so curl is never given a string it could read differently from the checks.
    return "https://" + u.hostname + RELAY_PREFIX, token_file, tools


def read_token(token_file):
    with open(token_file, encoding="ascii", errors="replace") as f:
        token = f.read(8200).strip()
    if not TOKEN_RE.fullmatch(token):
        raise Stop("the session token file does not hold a single plain token")
    return token


def curl(url, dest, ctx, max_bytes):
    """GET url into dest with the session token as a bearer.
    Returns the HTTP status, or minus curl's exit code when there was no answer."""
    if not url.startswith(ctx["base"] + "/emulator/"):
        raise Stop(f"refusing to fetch outside the artifact service's emulator routes: {url}")
    token = read_token(ctx["token_file"])
    # The token travels in a config read from stdin: never in argv, the environment or a file.
    config = f'oauth2-bearer = "{token}"\n'
    cmd = [ctx["curl"], "-q", "-sS", "--globoff", "--proto", "=https", "--max-redirs", "0",
           "--connect-timeout", "10", "--speed-limit", "1024", "--speed-time", "20", "--max-time", "100",
           "--cacert", ctx["ca"], "--max-filesize", str(max_bytes), "-K", "-", "-o", dest, "-w", "%{http_code}", url]
    env = {k: v for k, v in os.environ.items() if k.lower() in PROXY_VARS}  # a proxy may carry it, never choose whom to trust
    p = subprocess.run(cmd, input=config, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        say(f"  curl exit {p.returncode}: {p.stderr.strip().replace(token, '[token]')[:200]}")
        return -p.returncode
    return int(p.stdout.strip() or 0)


def fetch(url, dest, ctx, max_bytes, tries=4):
    for attempt in range(tries):
        if time.monotonic() > ctx["deadline"]:
            raise Stop("downloading the emulator took too long; try again in a minute")
        code = curl(url, dest, ctx, max_bytes)
        if code not in (502, 503) and -code not in RETRY_EXITS:
            return code
        if attempt < tries - 1:
            time.sleep(ctx["pause"] * (attempt + 1))
    return code


def read_file_list(ctx, tmp):
    dest = os.path.join(tmp, "latest.json")
    code = fetch(ctx["base"] + "/emulator/program/latest", dest, ctx, MAX_JSON_BYTES)
    if code != 200:
        raise Stop(why(code))
    try:
        if os.path.getsize(dest) > MAX_JSON_BYTES:
            raise ValueError("too large")
        with open(dest, encoding="utf-8") as f:
            latest = json.load(f)
        files, entry = latest["files"], latest.get("entry", DEFAULT_ENTRY)
        ok = (type(latest["v"]) is int and latest["v"] == 1 and HEX64_RE.fullmatch(latest["id"])
              and latest["base"] == latest["id"] + "/" and isinstance(entry, str)
              and isinstance(files, dict) and 0 < len(files) <= MAX_FILES and entry in files
              and all(NAME_RE.fullmatch(n) and HEX64_RE.fullmatch(e["sha256"]) and type(e["bytes"]) is int
                      and 0 <= e["bytes"] <= MAX_FILE_BYTES for n, e in files.items()))
    except Exception:
        ok = False
    if not ok:
        raise Stop("the emulator's file list is not in the form this script knows; the skill may be out of date")
    return latest["id"], files, entry


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def matches(directory, files):
    return all(os.path.isfile(os.path.join(directory, n)) and not os.path.islink(os.path.join(directory, n))
               and os.path.getsize(os.path.join(directory, n)) == e["bytes"]
               and sha256_of(os.path.join(directory, n)) == e["sha256"] for n, e in files.items())


def safe_root(root):
    program_root = os.path.join(root, "program")
    os.makedirs(program_root, mode=0o755, exist_ok=True)
    only_ours(root, "what is installed there")
    for d in (root, program_root):
        st = os.lstat(d)
        if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid():
            raise Stop(f"{d} must be a real directory owned by this user")
    for name in os.listdir(program_root):  # what an interrupted earlier run left behind
        try:
            st = os.lstat(os.path.join(program_root, name))
        except OSError:
            continue
        if name.startswith((".incoming-", ".old-")) and stat.S_ISDIR(st.st_mode) and time.time() - st.st_mtime > 600:
            shutil.rmtree(os.path.join(program_root, name), ignore_errors=True)
    os.makedirs(os.path.join(root, "cache"), mode=0o755, exist_ok=True)
    os.makedirs(os.path.join(root, "run"), mode=0o700, exist_ok=True)
    return program_root


def known_size(st, refused):
    """Raises Stop with refused's words plus what was found, unless st is of a regular file whose size is in NODE_PROGRAMS."""
    if not stat.S_ISREG(st.st_mode) or st.st_size not in NODE_PROGRAMS.values():
        size = f"{st.st_size} bytes" if stat.S_ISREG(st.st_mode) else "not a regular file"
        raise Stop(f"{refused} (the node found is {size}: not one this skill knows)")


def private_node(found, refused):
    """Path of a private copy of the node program at found, if THE COPY is one of NODE_PROGRAMS. Otherwise raises Stop, with
    refused's words plus what was found. The copy is kept in ROOT/node, which only this user can enter. Once its sha256 has
    matched, who owns found, or can write to it, no longer matters to what is run: found itself never is. (A later run still
    takes find_playwright's first look at found, and stops there if its size is by then not a known one, copy or no copy.)"""
    staging = tempfile.mkdtemp(prefix=".incoming-", dir=safe_root(ROOT))  # where safe_root clears what a cut-off run leaves
    home, fresh = os.path.join(os.path.realpath(ROOT), "node"), os.path.join(staging, "node")
    copy = os.path.join(home, "node")
    try:
        os.makedirs(home, mode=0o700, exist_ok=True)
        st = os.lstat(home)
        if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.geteuid() or st.st_mode & 0o077:
            raise Stop(f"{home} must be a real directory that only this user can enter")
        if os.path.lexists(copy):  # an earlier run's copy: reused if it still hashes to a known release, else deleted first
            known = not os.path.islink(copy) and os.path.isfile(copy) and NODE_PROGRAMS.get(sha256_of(copy))
            if known and known == os.path.getsize(copy):
                return copy
            os.unlink(copy)
        with os.fdopen(os.open(found, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW), "rb") as src, open(fresh, "wb") as dst:
            st = os.fstat(src.fileno())
            known_size(st, refused)  # asked again, of the open file: the answer that counts
            # one byte past that known size and no further: a file that grows meanwhile fails the check below
            # instead of being copied without end
            left = st.st_size + 1
            while left and (block := src.read(min(left, 1 << 20))):
                left -= dst.write(block)
        digest = sha256_of(fresh)
        if NODE_PROGRAMS.get(digest) != os.path.getsize(fresh):
            raise Stop(f"{refused} (the node found has sha256 {digest}: not one this skill knows)")
        os.chmod(fresh, 0o500)
        os.rename(fresh, copy)
        return copy
    except OSError as e:
        raise Stop(f"{refused} (and it could not be copied to be checked: {e.strerror or e})")
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def install_program(ctx, root):
    """Download the program into <root>/program/<id>/, verified and atomically. Returns (dir, entry).
    The file list and every file in it are one unit: a 404 on a file restarts the unit, until the deadline."""
    program_root = safe_root(root)
    for attempt in itertools.count():  # ends at ctx["deadline"]: fetch() and the missing-file branch below both check it
        tmp = tempfile.mkdtemp(prefix=".incoming-", dir=program_root)
        try:
            prog_id, files, entry = read_file_list(ctx, tmp)
            os.remove(os.path.join(tmp, "latest.json"))
            final = os.path.join(program_root, prog_id)
            if os.path.isdir(final) and matches(final, files):
                say(f"emulator {prog_id[:12]} is already here and matches its hashes")
                return final, entry
            missing = False
            for name in sorted(files):
                dest = os.path.join(tmp, name)
                if os.path.dirname(os.path.realpath(dest)) != os.path.realpath(tmp):
                    raise Stop(f"refusing to write outside the download directory: {name!r}")
                code = fetch(f"{ctx['base']}/emulator/program/{prog_id}/{name}", dest, ctx, MAX_FILE_BYTES)
                if code == 404:
                    missing = True  # the list and the file came from different versions of the service
                    break
                if code != 200:
                    raise Stop(f"{name} could not be downloaded: " + why(code))
                os.chmod(dest, 0o644)
            if missing:
                delay = min(ctx["pause"] * 3 * (attempt + 1), 30)
                if time.monotonic() + delay > ctx["deadline"]:
                    raise Stop("the artifact service is mid-deploy (its file list and its files keep disagreeing); "
                               "try again in a few minutes")
                say("  a file the service listed was not found (it may be mid-deploy); asking again")
                time.sleep(delay)
                continue
            if not matches(tmp, files):
                raise Stop("a downloaded file does not match the sha256 or size in the file list; nothing was installed")
            os.chmod(tmp, 0o755)
            try:
                if os.path.isdir(final) and not matches(final, files):
                    os.rename(final, os.path.join(tempfile.mkdtemp(prefix=".old-", dir=program_root), "replaced"))
                os.rename(tmp, final)
            except OSError:
                if not matches(final, files):  # unless another run finished first
                    raise
            say(f"emulator {prog_id[:12]} installed: {len(files)} files, each checked against its sha256")
            return final, entry
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


WRAPPER = """#!{python} -I
# written by the artifact-emulator skill's bootstrap; safe to delete
import os, sys
# The program starts from a fixed environment plus the caller's proxy variables: nothing else the caller's
# environment says (where to find a program, whom to trust, what to preload) reaches it. And from /, because
# bun reads configuration from the working directory and every directory above it.
env = {{k: v for k, v in os.environ.items() if k.lower() in {proxy_vars!r}}}
env.update({fixed!r})
os.chdir("/")
os.execve({bun!r}, [{bun!r}, "--config=/dev/null", "--no-env-file", "--no-install", {entry!r}, *sys.argv[1:]], env)
"""


def write_wrapper(path, bun, python, program_dir, entry, root, ca, chromium):
    # FRAME_EMULATOR_CHROMIUM: the program runs the browser this script checked, and never looks for one itself.
    fixed = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "HOME": "/", "LANG": "C.UTF-8",
             "NODE_EXTRA_CA_CERTS": ca, "BUN_RUNTIME_TRANSPILER_CACHE_PATH": "0", "FRAME_EMULATOR_CACHE": root + "/cache",
             "FRAME_EMULATOR_CHROMIUM": chromium}
    body = WRAPPER.format(python=python, proxy_vars=PROXY_VARS, fixed=fixed, bun=bun,
                          entry=program_dir + "/" + entry)
    only_ours(os.path.dirname(path), "a command installed there")
    fd, tmp = tempfile.mkstemp(prefix=".frame-emulator-", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w") as f:
            f.write(body)
        os.chmod(tmp, 0o755)
        os.rename(tmp, path)
    except OSError:
        os.unlink(tmp)
        raise
    return os.path.realpath(path)


def run_bundle(command, ctx, timeout):
    """Ask the program to download the viewer, which it checks against the viewer's manifest, and the runtime."""
    cmd = [command, "bundle", "--shell-latest", ctx["base"], "--runtime-url", ctx["base"] + "/emulator/runtime",
           "--token-file", ctx["token_file"]]
    token = read_token(ctx["token_file"])  # only to keep it out of anything printed below
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd="/", timeout=timeout)
    except subprocess.TimeoutExpired:
        raise Stop("downloading the viewer and runtime took too long; run this again")
    if p.returncode != 0:
        tail = p.stderr.strip().replace(token, "[token]")
        try:
            tail = tail.replace(read_token(ctx["token_file"]), "[token]")  # it may have been refreshed meanwhile
        except (Stop, OSError):
            pass
        tail = tail[-800:]
        raise Stop("the emulator could not download the viewer and runtime:\n" + tail)
    try:
        out = json.loads(p.stdout)
        shell_dir, runtime_dir = out["shellDir"], out["runtimeDir"]
        if not (isinstance(shell_dir, str) and isinstance(runtime_dir, str)):
            raise TypeError
    except Exception:
        raise Stop("the emulator's bundle command did not print the directories it filled")
    return shell_dir, runtime_dir


def main():
    ap = argparse.ArgumentParser(description="Fetch the artifact emulator into this cloud session: the program "
                                 "(checked here against its published sha256 hashes), then the viewer and runtime "
                                 "(fetched by the program). Prints one JSON line: command, shellDir, runtimeDir, workDir, "
                                 "and node and playwright where SKILL.md's step 3 is to use Node Playwright. "
                                 "Safe to run again. Takes no options other than -h.")
    ap.parse_args()  # -h prints the description; anything else is refused before a file is read or a request sent
    os.umask(0o022)
    start = time.monotonic()
    try:
        base, token_file, tools = preflight()
        ctx = {"base": base, "token_file": token_file, "pause": PAUSE_S, "curl": tools["curl"], "ca": tools["ca"],
               "deadline": time.monotonic() + PROGRAM_DEADLINE_S}
        program_dir, entry = install_program(ctx, ROOT)
        if "copy_of" in tools["driver"]:  # only now, with every check passed and the emulator granted and installed
            tools["driver"]["node"] = private_node(*tools["driver"].pop("copy_of"))
        command = write_wrapper(COMMAND, tools["bun"], tools["python"], program_dir, entry, ROOT, tools["ca"],
                                tools["chromium"])
        shell_dir, runtime_dir = run_bundle(command, ctx, max(60, TOTAL_BUDGET_S - (time.monotonic() - start)))
    except (Stop, OSError) as e:
        say(f"artifact-emulator: stopped: {e}")
        return 1
    except Exception as e:
        say(f"artifact-emulator: stopped: unexpected error ({type(e).__name__})")
        try:  # the details, for whoever debugs it, where only this user can read them
            with open(os.path.join(ROOT, "run", "last-error.txt"), "w") as f:
                traceback.print_exc(file=f)
        except OSError:
            pass
        return 1
    say("the emulator downloaded the viewer and runtime")
    print(json.dumps({"command": command, "shellDir": shell_dir, "runtimeDir": runtime_dir,
                      "workDir": os.path.join(os.path.realpath(ROOT), "run"), **tools["driver"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
