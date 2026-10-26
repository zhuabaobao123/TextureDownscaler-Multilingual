#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate TextureDownscaler.json for every language, with full validation.

Reads ../keys.json (authoritative key list, produced by extract_keys.py) and
every translations/<lang>.py exposing T = { english_key: localized_text }.
'en' is the identity (value == key), except the vformat-fed keys, which get
explicit numbered placeholders in English too.

The vformat keys are special: std::vformat auto-numbers placeholders
positionally, and it types each argument by index (int / std::string_view /
double). If a translation drops a middle placeholder the indices shift and a
'{:.0f}' lands on a string argument -> std::format_error -> crash (seen in the
field). So for those keys the generator resolves every placeholder's index
(auto or explicit) and checks the referenced argument type is compatible.

Output: out/<code>/SKSE/Plugins/TextureDownscaler.json (UTF-8, no BOM, CRLF).

    python localization/generate_json.py
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRANS_DIR = HERE / "translations"
KEYS_FILE = HERE.parent / "keys.json"
OUT_ROOT = HERE / "out"

LANGUAGES = [
    ("en", "en"), ("zh-CN", "zh-CN"), ("ja", "ja"), ("ko", "ko"),
    ("ru", "ru"), ("fr", "fr"), ("de", "de"), ("es", "es"),
]

PLACEHOLDER_RE = re.compile(r"\{([0-9]*)((?::[^{}]*)?)\}")
PERCENT_RE = re.compile(r"%[a-zA-Z]+")

# vformat-fed keys, with the C++ argument type per placeholder index.
DYNAMIC_ARGS = {
    "{} texture{} loaded at a reduced size this session, about {:.0f} MB smaller in total.": ["int", "str", "double"],
    "Video memory: {:.1f} of {:.1f} GB ({}%)": ["double", "double", "int"],
    "Textures are being reduced (threshold {}%).": ["int"],
    "Textures load at full size until video memory reaches {}%.": ["int"],
    "Rules ({})": ["int"],
}

# English values for the dynamic keys: explicit indices, so a translation can
# drop an argument without shifting the rest.
EN_OVERRIDES = {
    "{} texture{} loaded at a reduced size this session, about {:.0f} MB smaller in total.":
        "{0} texture{1} loaded at a reduced size this session, about {2:.0f} MB smaller in total.",
    "Video memory: {:.1f} of {:.1f} GB ({}%)":
        "Video memory: {0:.1f} of {1:.1f} GB ({2}%)",
    "Textures are being reduced (threshold {}%).":
        "Textures are being reduced (threshold {0}%).",
    "Textures load at full size until video memory reaches {}%.":
        "Textures load at full size until video memory reaches {0}%.",
    "Rules ({})":
        "Rules ({0})",
}


def placeholders(text):
    return [m.group(0) for m in PLACEHOLDER_RE.finditer(text)]


def load_keys():
    keys = json.loads(KEYS_FILE.read_text(encoding="utf-8"))
    if len(keys) != len(set(keys)):
        raise SystemExit("keys.json contains duplicate keys!")
    return keys


def load_lang(stem):
    spec = importlib.util.spec_from_file_location("lang_" + stem, TRANS_DIR / f"{stem}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(mod.T)


def check_dynamic(text, key, problems, lang):
    """Type-check the placeholders of a vformat-fed translation."""
    arg_types = DYNAMIC_ARGS[key]
    phs = PLACEHOLDER_RE.findall(text)  # list of (index_or_empty, spec)
    auto = any(idx == "" for idx, _ in phs)
    manual = [idx for idx, _ in phs if idx != ""]
    if auto and manual:
        problems.append(f"[{lang}] dynamic key {key!r}: mixes auto '{{}}' and "
                        f"numbered '{{N}}' placeholders")
        return
    for i, (idx, spec) in enumerate(phs):
        index = i if auto else int(idx)
        if index >= len(arg_types):
            problems.append(f"[{lang}] dynamic key {key!r}: placeholder index {index} "
                            f"out of range ({len(arg_types)} args)")
            continue
        expected = arg_types[index]
        if expected == "str":
            if spec and re.search(r"[a-zA-Z]", spec):
                problems.append(f"[{lang}] dynamic key {key!r}: non-empty spec {spec!r} "
                                f"on string arg (plural at index {index})")
        else:
            if expected == "int" and spec and "f" in spec:
                problems.append(f"[{lang}] dynamic key {key!r}: float spec {spec!r} on "
                                f"int arg at index {index}")
            if expected == "double" and not ("f" in spec or spec == ""):
                problems.append(f"[{lang}] dynamic key {key!r}: unsupported spec {spec!r} "
                                f"on double arg at index {index}")


def check_placeholders(lang, table, keys, problems):
    for k in keys:
        en_phs = placeholders(k)
        tr_phs = placeholders(table[k])
        if k in DYNAMIC_ARGS:
            check_dynamic(table[k], k, problems, lang)
            continue
        # Non-dynamic keys: no new placeholders, counts must not exceed English.
        for ph in tr_phs:
            if tr_phs.count(ph) > en_phs.count(ph):
                problems.append(f"[{lang}] too many {ph!r} in key {k!r}")
            if ph not in en_phs:
                problems.append(f"[{lang}] new placeholder {ph!r} in key {k!r}")
        # percent specifiers must match exactly (they are positional)
        en_pct = PERCENT_RE.findall(k)
        tr_pct = PERCENT_RE.findall(table[k])
        if tr_pct != en_pct:
            problems.append(f"[{lang}] percent specifier mismatch in key {k!r}: "
                            f"{tr_pct} vs {en_pct}")


def main():
    keys = load_keys()
    problems = []
    print(f"keys.json: {len(keys)} keys")

    for code, stem in LANGUAGES:
        if code == "en":
            table = {k: k for k in keys}
            table.update(EN_OVERRIDES)
        else:
            table = load_lang(stem)

        missing = set(keys) - set(table)
        extra = set(table) - set(keys)
        if missing:
            problems.append(f"[{code}] missing keys: {sorted(missing)}")
        if extra:
            problems.append(f"[{code}] extra keys: {sorted(extra)}")

        check_placeholders(code, table, keys, problems)

        if missing or extra:
            continue

        out = OUT_ROOT / code / "SKSE" / "Plugins" / "TextureDownscaler.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        doc = {k: table[k] for k in keys}
        text = json.dumps(doc, ensure_ascii=False, indent=4).replace("\n", "\r\n") + "\r\n"
        out.write_bytes(text.encode("utf-8"))
        print(f"[{code}] wrote {out} ({len(doc)} entries)")

    if problems:
        print("\n=== VALIDATION PROBLEMS ===")
        for p in problems:
            print(" -", p)
        return 1

    print("\nAll languages validated: exact key set, placeholders ok, dynamic keys type-checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
