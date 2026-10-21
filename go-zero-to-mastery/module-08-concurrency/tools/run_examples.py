#!/usr/bin/env python3
"""Run every example program and save its real output.

    python3 tools/run_examples.py            # run all
    python3 tools/run_examples.py ch05 ch12  # run matching directories

Each examples/<name>/ directory holds a main package (or a test). An optional
file RUN in the directory holds a one-line directive:

    [ENV=VAL ...] [timeout=5s] [mode=run|test|race|build|bench|exec|c] [args...]

The combined stdout+stderr is written to examples/<name>/output.txt, prefixed
by the command that was run, so book pages can show it verbatim.
"""
from __future__ import annotations

import os
import re
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
TOOLCHAIN = os.environ.get("GOTOOLCHAIN", "go1.27.3")


def directive(d: Path):
    if (d / "RUN").exists():
        return (d / "RUN").read_text().strip()
    for f in sorted(list(d.glob("*.go")) + list(d.glob("*.c"))):
        first = f.read_text().splitlines()[0] if f.read_text() else ""
        if first.startswith("//run:"):
            return first[len("//run:"):].strip()
    return ""


def run_one(d: Path):
    spec = shlex.split(directive(d))
    env_extra, timeout, mode, args = {}, 20.0, "run", []
    for tok in spec:
        if re.match(r"^[A-Z_][A-Z0-9_]*=", tok):
            k, v = tok.split("=", 1)
            env_extra[k] = v
        elif tok.startswith("timeout="):
            timeout = float(tok.split("=", 1)[1].rstrip("s"))
        elif tok.startswith("mode="):
            mode = tok.split("=", 1)[1]
        else:
            args.append(tok)
    env = dict(os.environ, GOTOOLCHAIN=TOOLCHAIN, GOFLAGS="-mod=mod", **env_extra)
    shown_env = " ".join(f"{k}={v}" for k, v in env_extra.items())
    if mode == "test":
        cmd = ["go", "test", "-v", "-count=1", *args, "."]
        shown = " ".join(["go", "test", "-v", *args, "."])
    elif mode == "bench":
        cmd = ["go", "test", "-count=1", "-run=^$", "-bench=.", "-benchmem", *args, "."]
        shown = " ".join(["go", "test", "-bench=.", "-benchmem", *args])
    elif mode == "race":
        cmd = ["go", "run", "-race", ".", *args]
        shown = "go run -race ." + ("" if not args else " " + " ".join(args))
    elif mode == "vet":
        cmd = ["go", "vet", "."]
        shown = "go vet ."
    elif mode == "build":
        cmd = ["go", "build", "-o", os.devnull, "."]
        shown = "go build ."
    elif mode == "exec":
        # build first, then run the binary with the extra env vars only
        exe = d / "app"
        subprocess.run(["go", "build", "-o", str(exe), "."], cwd=d, env=dict(os.environ, GOTOOLCHAIN=TOOLCHAIN), check=True)
        cmd = [str(exe), *args]
        env = dict(os.environ, **env_extra)
        shown = "go build -o app .\n$ " + (shown_env + " ./app").strip()
        shown_env = ""
    elif mode == "c":
        exe = d / "a.out"
        subprocess.run(["gcc", "-O2", "-pthread", "-o", str(exe), *[str(p) for p in d.glob("*.c")]], check=True)
        cmd = [str(exe), *args]
        shown = "./a.out"
    else:
        cmd = ["go", "run", ".", *args]
        shown = "go run ." + ("" if not args else " " + " ".join(args))
    shown = (shown_env + " " + shown).strip()
    t0 = time.time()
    timed_out = False
    # Run in its own process group so a timeout kills the program itself,
    # not just the `go run` wrapper (an orphaned busy loop would skew every
    # later timing measurement).
    proc = subprocess.Popen(cmd, cwd=d, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    try:
        so, se = proc.communicate(timeout=timeout)
        text = so + se
        code = proc.returncode
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        so, se = proc.communicate()
        text = (so or "") + (se or "")
        text += f"^C   (killed after {timeout:.0f}s: the program never finished)\n"
        code = -1
        timed_out = True
    # Normalise noisy paths so output is stable and readable.
    text = text.replace(str(d) + "/", "./").replace(str(d), ".")
    text = re.sub(r"/root/go/pkg/mod/golang\.org/toolchain@v0\.0\.1-go[\d.]+\.linux-amd64/src/", "$GOROOT/src/", text)
    text = re.sub(r"/tmp/go-build\d+/b\d+/exe/", "/tmp/go-build/", text)
    text = re.sub(r"/tmp/go-build\d+/", "/tmp/go-build/", text)
    (d / "output.txt").write_text(f"$ {shown}\n{text}")
    status = "timeout" if timed_out else f"exit {code}"
    print(f"{d.name:32s} {status:9s} {time.time() - t0:5.1f}s")
    for junk in ("a.out", "app"):
        if d.joinpath(junk).exists():
            d.joinpath(junk).unlink()


def main(filters):
    dirs = sorted(p for p in EX.iterdir()
                  if p.is_dir() and (any(p.glob("*.go")) or any(p.glob("*.c"))))
    for d in dirs:
        if filters and not any(d.name.startswith(f) for f in filters):
            continue
        run_one(d)


if __name__ == "__main__":
    main(sys.argv[1:])
