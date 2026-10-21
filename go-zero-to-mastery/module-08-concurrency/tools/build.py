#!/usr/bin/env python3
"""Build the Module 8 graphic book.

    python3 tools/build.py number            # write book/pages.json
    python3 tools/build.py render [FILTER..] # render pages (all, or ch03, ch03:ClassName)
    python3 tools/build.py pdf               # pages/*.png -> Module-08-Concurrency.pdf
    python3 tools/build.py html              # pages/*.png -> index.html viewer
    python3 tools/build.py all               # number + render + pdf + html

Every page is a ManimGL Scene in book/chNN_*.py. Pages are numbered in the
order the classes appear in the files (files sorted by name). Classes whose
names start with "_" are helpers, not pages.
"""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
PAGES = ROOT / "pages"
PDF = ROOT / "Module-08-Concurrency.pdf"
RES = "2560x1440"
DISPLAY = ":97"


def chapter_files():
    return sorted(p for p in BOOK.glob("ch*.py"))


def classes_in(path: Path):
    tree = ast.parse(path.read_text())
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            attrs = {}
            for st in node.body:
                if isinstance(st, ast.Assign) and len(st.targets) == 1 and \
                        isinstance(st.targets[0], ast.Name) and isinstance(st.value, ast.Constant):
                    attrs[st.targets[0].id] = st.value.value
            bases = [getattr(b, "id", getattr(b, "attr", "")) for b in node.bases]
            out.append((node.name, attrs, bases))
    return out


def number():
    pages, order, chapters, titles = {}, [], {}, {}
    n = 0
    for f in chapter_files():
        for name, attrs, bases in classes_in(f):
            n += 1
            pages[name] = n
            order.append([f.stem, name])
            if "Opener" in bases and "NUM" in attrs:
                chapters[attrs["NUM"]] = {"page": n, "name": attrs.get("NAME", "")}
            titles[name] = attrs.get("TITLE") or attrs.get("NAME") or name
    data = {"pages": pages, "order": order, "chapters": chapters, "titles": titles, "count": n}
    (BOOK / "pages.json").write_text(json.dumps(data, indent=1))
    print(f"numbered {n} pages in {len(chapter_files())} files")
    return data


def ensure_display():
    lock = Path(f"/tmp/.X{DISPLAY[1:]}-lock")
    if lock.exists():
        return None
    proc = subprocess.Popen(["Xvfb", DISPLAY, "-screen", "0", "1920x1080x24", "-nolisten", "tcp"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.5)
    return proc


def optimise(png: Path):
    """RGB + palette quantisation (pngquant): ~4x smaller, visually identical."""
    from PIL import Image
    Image.open(png).convert("RGB").save(png)
    if shutil.which("pngquant"):
        subprocess.run(["pngquant", "--quality=85-98", "--speed", "1", "--strip", "--force",
                        "--output", str(png), str(png)], check=False)


def render_file(stem: str, scenes: list[str], data):
    out = Path(tempfile.mkdtemp(prefix=f"render_{stem}_"))
    cmd = ["manimgl", str(BOOK / f"{stem}.py"), *scenes, "-w", "-s", "-r", RES, "--video_dir", str(out)]
    if not scenes:
        cmd.insert(2, "-a")
    env = dict(os.environ, DISPLAY=DISPLAY, PYTHONPATH=str(BOOK))
    t0 = time.time()
    r = subprocess.run(cmd, cwd=BOOK, env=env, capture_output=True, text=True)
    ok = r.returncode == 0
    made = []
    for png in out.glob("*.png"):
        name = png.stem
        n = data["pages"].get(name)
        if n is None:
            continue
        for old in PAGES.glob(f"*-{name}.png"):
            old.unlink()
        dest = PAGES / f"{n:03d}-{name}.png"
        shutil.move(str(png), dest)
        optimise(dest)
        made.append(dest.name)
    shutil.rmtree(out, ignore_errors=True)
    msg = f"[{stem}] {len(made)} page(s) in {time.time() - t0:.1f}s"
    warns = [l for l in (r.stdout + r.stderr).splitlines() if "LAYOUT-WARN" in l]
    if warns:
        msg += "\n  " + "\n  ".join(sorted(set(w.split("LAYOUT-WARN ", 1)[1] for w in warns)))
    if not ok:
        tail = "\n".join((r.stderr or r.stdout).strip().splitlines()[-25:])
        msg += f"  FAILED\n{tail}"
    print(msg, flush=True)
    return ok


def render(filters):
    data = number()
    PAGES.mkdir(exist_ok=True)
    # drop pages whose class no longer exists
    valid = {f"{n:03d}-{c}.png" for c, n in data["pages"].items()}
    jobs = {}
    for stem, cls in data["order"]:
        want = not filters
        for flt in filters:
            if ":" in flt:
                fs, fc = flt.split(":", 1)
                want |= stem.startswith(fs) and cls == fc
            else:
                want |= stem.startswith(flt)
        if want:
            jobs.setdefault(stem, []).append(cls)
    xv = ensure_display()
    try:
        with ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "4"))) as ex:
            futs = []
            for stem, classes in jobs.items():
                all_in_file = [c for s, c in data["order"] if s == stem]
                scenes = [] if classes == all_in_file else classes
                futs.append(ex.submit(render_file, stem, scenes, data))
            results = [f.result() for f in futs]
    finally:
        if xv:
            xv.terminate()
    # renumber existing files if page numbers moved
    for png in PAGES.glob("*.png"):
        name = png.stem.split("-", 1)[1]
        n = data["pages"].get(name)
        if n is None:
            png.unlink()
            continue
        want = PAGES / f"{n:03d}-{name}.png"
        if png != want:
            png.rename(want)
    if not all(results):
        sys.exit(1)


def pdf():
    import img2pdf
    files = [str(f) for f in sorted(PAGES.glob("*.png"))]
    w_pt, h_pt = img2pdf.in_to_pt(13.333), img2pdf.in_to_pt(7.5)
    layout = img2pdf.get_layout_fun((w_pt, h_pt))
    PDF.write_bytes(img2pdf.convert(files, layout_fun=layout,
                                    title="Go: Zero to Mastery - Module 8: The Concurrency Model",
                                    author="Go: Zero to Mastery",
                                    subject="Goroutines, Channels, and the Scheduler"))
    print(f"wrote {PDF.name}: {len(files)} pages, {PDF.stat().st_size / 1e6:.1f} MB")


def optimise_all():
    for f in sorted(PAGES.glob("*.png")):
        optimise(f)


def html():
    data = json.loads((BOOK / "pages.json").read_text())
    files = sorted(PAGES.glob("*.png"))
    items = []
    for f in files:
        name = f.stem.split("-", 1)[1]
        items.append({"src": f"pages/{f.name}", "n": data["pages"].get(name), "title": data["titles"].get(name, name)})
    chapters = [{"num": k, "page": v["page"], "name": v["name"]} for k, v in
                sorted(data["chapters"].items(), key=lambda kv: kv[1]["page"])]
    tpl = (ROOT / "tools" / "viewer.html").read_text()
    out = tpl.replace("/*PAGES*/[]", json.dumps(items)).replace("/*CHAPTERS*/[]", json.dumps(chapters))
    (ROOT / "index.html").write_text(out)
    print(f"wrote index.html with {len(items)} pages")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    args = sys.argv[2:]
    if cmd == "number":
        number()
    elif cmd == "render":
        render(args)
    elif cmd == "pdf":
        pdf()
    elif cmd == "optimise":
        optimise_all()
    elif cmd == "html":
        html()
    elif cmd == "all":
        render(args)
        pdf()
        html()
    else:
        print(__doc__)
        sys.exit(2)
