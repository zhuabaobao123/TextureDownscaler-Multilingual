#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract every _T("...") key from src/*.cpp into keys.json.

The result is the authoritative key list consumed by generate_json.py.
Run from anywhere: paths are resolved relative to this file.

    python localization/extract_keys.py
"""
import json
import re
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "src"
OUT = HERE.parent / "keys.json"


def parse_string_literals(text, i):
    """Parse one or more adjacent "..." literals starting at i. Returns (value, end) or None."""
    parts = []
    n = len(text)
    while i < n:
        while i < n and text[i] in " \t\r\n":
            i += 1
        if i >= n or text[i] != '"':
            break
        i += 1
        buf = []
        while i < n:
            c = text[i]
            if c == "\\":
                i += 1
                e = text[i]
                mapping = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
                           "n": "\n", "r": "\r", "t": "\t"}
                if e in mapping:
                    buf.append(mapping[e]); i += 1
                elif e == "u":
                    buf.append(chr(int(text[i + 1:i + 5], 16))); i += 5
                else:
                    raise ValueError("bad escape " + e)
            elif c == '"':
                i += 1
                break
            else:
                buf.append(c); i += 1
        else:
            raise ValueError("unterminated string")
        parts.append("".join(buf))
    return ("".join(parts), i) if parts else None


def main():
    keys = []
    for path in sorted(SRC.glob("*.cpp")):
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"_T\(", text):
            start = m.end()
            parsed = parse_string_literals(text, start)
            if not parsed:
                print(f"!! cannot parse at {path.name}:{text[:m.start()].count(chr(10)) + 1}")
                continue
            value, end = parsed
            # the macro must close right after the literal
            j = end
            while j < len(text) and text[j] in " \t\r\n":
                j += 1
            if j >= len(text) or text[j] != ")":
                print(f"!! macro does not close after literal at {path.name}:{text[:start].count(chr(10)) + 1}")
            keys.append(value)

    seen = {}
    for k in keys:
        seen[k] = seen.get(k, 0) + 1

    print("total _T calls:", len(keys), "distinct:", len(seen))
    for k, v in seen.items():
        if v > 1:
            print(f"  used {v}x: {k}")

    OUT.write_text(json.dumps(list(seen.keys()), ensure_ascii=False, indent=2), encoding="utf-8")
    print("written", OUT)


if __name__ == "__main__":
    main()
