"""
Find image files under frontend/assets/imgs/ not referenced from code.

Scans:
  frontend/, templates/, apps/, config/

Normalized reference form: imgs/...relative/path.ext

Usage:
  python scripts/audit_unused_imgs.py
  python scripts/audit_unused_imgs.py --delete
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMGS_ROOT = ROOT / "frontend" / "assets" / "imgs"

SCAN_EXT = {".html", ".htm", ".js", ".css", ".py", ".json", ".md", ".svg", ".txt"}

EXT = r"(?:svg|png|jpg|jpeg|gif|webp|ico|bmp)"
# Matches imgs/foo/bar.ext (inside strings, markup, Django static paths)
PLAIN_IMGS_RE = re.compile(rf"(?:assets/)?(?P<p>imgs/[\w./-]+\.{EXT})", flags=re.I)
# Absolute web path
SLASH_ASSETS_IMGS_RE = re.compile(rf"(?P<p>/assets/imgs/[\w./-]+\.{EXT})", flags=re.I)
# CSS url( ../imgs/... or imgs/...)
URL_IMGS_RE = re.compile(rf"""url\s*\(\s*['\"]?(?P<p>(?:\.\./)*imgs/[\w./-]+\.{EXT})""", flags=re.I)
# Django: {% static 'imgs/...' %}
DJANGO_STATIC_IMGS_RE = re.compile(r"{%\s*static\s+['\"](?P<p>imgs/[\w./-]+\." + EXT + r")['\"]", flags=re.I)


def iter_scan_files():
    for base in (ROOT / "frontend", ROOT / "templates", ROOT / "apps", ROOT / "config"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in SCAN_EXT:
                yield path


def normalize_to_relative_imgs(segment: str) -> str | None:
    segment = segment.replace("\\", "/").strip().strip("\"' ")
    while segment.startswith("../"):
        segment = segment[3:]
    if segment.startswith("imgs/"):
        return segment
    if segment.startswith("assets/imgs/"):
        return "imgs/" + segment[len("assets/imgs/") :]
    if segment.startswith("/assets/imgs/"):
        return "imgs/" + segment[len("/assets/imgs/") :]
    return None


def _maybe_external_url_fragment(text: str, match_start: int) -> bool:
    """Avoid counting matches inside absolute URLs like https://.../assets/imgs/...."""
    head = text[max(0, match_start - 120) : match_start]
    return "://" in head


def collect_referenced_relative_paths() -> set[str]:
    referenced: set[str] = set()
    for path in iter_scan_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for rx in (PLAIN_IMGS_RE, SLASH_ASSETS_IMGS_RE, URL_IMGS_RE, DJANGO_STATIC_IMGS_RE):
            for m in rx.finditer(text):
                rel = normalize_to_relative_imgs(m.group("p"))
                if rel and rx is not DJANGO_STATIC_IMGS_RE:
                    # Django static tags can't be buried in arbitrary external URLs anyway.
                    if _maybe_external_url_fragment(text, m.start("p")):
                        continue
                if rel:
                    referenced.add(rel)
    return referenced


def list_all_images_under_imgs_root() -> list[str]:
    fixed: list[str] = []
    image_suffixes = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp"}
    for p in IMGS_ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.name in {".DS_Store", "Thumbs.db"}:
            continue
        if p.suffix.lower() not in image_suffixes:
            continue
        fixed.append(p.relative_to(IMGS_ROOT).as_posix())
    return sorted(set(fixed))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete", action="store_true", help="Delete unreferenced img files.")
    args = parser.parse_args()

    if not IMGS_ROOT.exists():
        print(f"imgs root missing: {IMGS_ROOT}", file=sys.stderr)
        return 1

    referenced = collect_referenced_relative_paths()
    all_paths = list_all_images_under_imgs_root()

    normalized_files = {"imgs/" + p for p in all_paths}

    unused_normalized = sorted(normalized_files - referenced)

    # Verify referenced paths exist on disk (relative imgs/x -> frontend/assets/x)
    missing_on_disk_fixed: list[str] = []
    for rel in referenced:
        rel_file = rel.removeprefix("imgs/")
        fp = IMGS_ROOT / rel_file
        if not fp.is_file():
            missing_on_disk_fixed.append(rel)

    print(f"TOTAL_IMAGE_FILES_UNDER_IMGS/: {len(all_paths)}")
    print(f"REFERENCED_PATHS_UNIQUE:       {len(referenced)}")
    print(f"UNUSED_DELETABLE_IF_SAFE:       {len(unused_normalized)}")
    if missing_on_disk_fixed:
        print("REFERENCED_PATHS_WITHOUT_FILE:")
        for m in sorted(missing_on_disk_fixed):
            print(" ", m)

    audit_out = ROOT / "scripts" / "_unused_imgs_audit.txt"
    audit_out.write_text("\n".join(u.removeprefix("imgs/") for u in unused_normalized) + "\n", encoding="utf-8")

    if args.delete:
        deleted = 0
        for u in unused_normalized:
            # u is imgs/theme/foo.svg -> frontend/assets/imgs/theme/foo.svg
            rel = u.removeprefix("imgs/")
            fp = IMGS_ROOT / rel
            if fp.is_file():
                fp.unlink()
                deleted += 1
                # remove empty dirs (best-effort)
        # prune empty directories under imgs root
        for d in sorted((p for p in IMGS_ROOT.rglob("*") if p.is_dir()), reverse=True):
            try:
                d.rmdir()
            except OSError:
                pass
        print(f"DELETED_FILES: {deleted}")
    print(f"wrote audit list: {audit_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
