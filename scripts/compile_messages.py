"""Pure-Python `.po` -> `.mo` compiler.

Django's built-in `compilemessages` shells out to GNU `msgfmt`, which is not
shipped with the Python interpreter on Windows. To keep the project setup
friction-free, this small utility reads every `django.po` under `locale/` and
emits a matching `django.mo` next to it using only the standard library.

Usage:

    python scripts/compile_messages.py
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path
from typing import Iterable


def _parse_po(path: Path) -> dict[str, str]:
    """Parse a minimal `.po` file. Supports msgid/msgstr (single + multi-line)
    and skips fuzzy/obsolete entries. Empty msgstr values are ignored so the
    source string is shown instead of an empty translation.
    """
    msgs: dict[str, str] = {}
    msgid: list[str] = []
    msgstr: list[str] = []
    state: str | None = None

    def flush() -> None:
        if state is None:
            return
        key = "".join(msgid)
        value = "".join(msgstr)
        if value:
            msgs[key] = value

    with path.open("r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                if state is not None:
                    flush()
                    msgid, msgstr, state = [], [], None
                continue
            if line.startswith("msgid "):
                if state is not None:
                    flush()
                msgid, msgstr = [_unquote(line[len("msgid "):])], []
                state = "id"
            elif line.startswith("msgstr "):
                msgstr = [_unquote(line[len("msgstr "):])]
                state = "str"
            elif line.startswith('"'):
                chunk = _unquote(line)
                if state == "id":
                    msgid.append(chunk)
                elif state == "str":
                    msgstr.append(chunk)
        if state is not None:
            flush()
    return msgs


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        value = value[1:-1]
    return (
        value.replace("\\n", "\n")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def _generate_mo(messages: dict[str, str]) -> bytes:
    """Build the GNU MO binary from a {msgid: msgstr} dict."""
    keys = sorted(messages)
    offsets: list[tuple[int, int, int, int]] = []
    ids = b""
    strs = b""

    for key in keys:
        encoded_key = key.encode("utf-8")
        encoded_value = messages[key].encode("utf-8")
        offsets.append((len(ids), len(encoded_key), len(strs), len(encoded_value)))
        ids += encoded_key + b"\x00"
        strs += encoded_value + b"\x00"

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    koffsets: list[int] = []
    voffsets: list[int] = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    offsets_buf = struct.pack("Ii" * len(keys) * 2, *(koffsets + voffsets))

    output = struct.pack(
        "Iiiiiii",
        0x950412DE,
        0,
        len(keys),
        7 * 4,
        7 * 4 + len(keys) * 8,
        0,
        0,
    )
    return output + offsets_buf + ids + strs


def _iter_po_files(root: Path) -> Iterable[Path]:
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith(".po"):
                yield Path(dirpath) / name


def main(root: str | None = None) -> int:
    target_root = Path(root or Path(__file__).resolve().parent.parent / "locale")
    if not target_root.exists():
        print(f"locale folder not found: {target_root}")
        return 1

    compiled = 0
    for po in _iter_po_files(target_root):
        messages = _parse_po(po)
        mo_path = po.with_suffix(".mo")
        mo_path.write_bytes(_generate_mo(messages))
        compiled += 1
        print(f"compiled {po} -> {mo_path} ({len(messages)} entries)")

    print(f"done: {compiled} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
