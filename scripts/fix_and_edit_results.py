#!/usr/bin/env python3
"""
fix_and_edit_results.py — Safe JSON editor for data/results.json

Modes:
  --check              Validate the JSON file and report status
  --fix                Fix unescaped double-quotes inside full_answer fields
  --add <entry.json>   Add a new entry from a JSON file (merges safely)
  --add-inline <json>  Add a new entry from an inline JSON string
  --set-field <id> <field> <value>  Set a scalar field on an existing entry by id

All modes validate the result before writing. Backup is created as results.json.bak
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

RESULTS_PATH = Path(__file__).parent.parent / "data" / "results.json"


# ─── helpers ──────────────────────────────────────────────────────────────────

def load_or_fix(path: Path) -> list:
    """Load JSON, or if invalid, attempt to fix unescaped quotes in full_answer."""
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON invalid: {e}")
        print("Attempting auto-fix of unescaped quotes in full_answer values...")
        fixed = fix_raw(raw)
        try:
            data = json.loads(fixed)
            print(f"✅ Auto-fix succeeded ({len(data)} entries)")
            return data
        except json.JSONDecodeError as e2:
            print(f"❌ Auto-fix failed: {e2}")
            sys.exit(1)


def fix_raw(raw: str) -> str:
    """
    For every full_answer string value in the raw JSON text, escape any
    bare (non-escaped) ASCII double-quotes that appear inside the value.

    Strategy: find `"full_answer": "` then scan char-by-char until the
    matching closing quote, escaping bare " along the way.
    """
    result = []
    i = 0
    pattern = re.compile(r'"full_answer"\s*:\s*"')

    while i < len(raw):
        m = pattern.search(raw, i)
        if not m:
            result.append(raw[i:])
            break

        # Append everything up to and including the opening quote of the value
        result.append(raw[i:m.end()])
        i = m.end()

        # Now scan the string value, escaping bare "
        value_chars = []
        while i < len(raw):
            ch = raw[i]
            if ch == "\\" and i + 1 < len(raw):
                # Keep existing escape sequences intact
                value_chars.append(ch)
                value_chars.append(raw[i + 1])
                i += 2
            elif ch == '"':
                # This closes the string
                result.append("".join(value_chars))
                result.append('"')
                i += 1
                break
            else:
                value_chars.append(ch)
                i += 1

    return "".join(result)


def save(data: list, path: Path):
    """Validate + write; create .bak first."""
    # Final validation
    serialised = json.dumps(data, ensure_ascii=False, indent=2)
    json.loads(serialised)  # will raise if still broken

    bak = path.with_suffix(".json.bak")
    shutil.copy2(path, bak)
    path.write_text(serialised + "\n", encoding="utf-8")
    print(f"✅ Written to {path}  (backup: {bak})")


# ─── commands ─────────────────────────────────────────────────────────────────

def cmd_check(args):
    raw = RESULTS_PATH.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        print(f"✅ Valid JSON — {len(data)} entries")
        for entry in data:
            fa_len = len(entry.get("full_answer") or "")
            print(f"  {entry.get('id', '?'):40s}  full_answer={fa_len} chars")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)


def cmd_fix(args):
    raw = RESULTS_PATH.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
        print(f"✅ Already valid ({len(data)} entries), nothing to fix.")
        return
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON invalid: {e}")

    fixed_raw = fix_raw(raw)
    try:
        data = json.loads(fixed_raw)
    except json.JSONDecodeError as e:
        print(f"❌ Fix failed: {e}")
        sys.exit(1)

    save(data, RESULTS_PATH)
    print(f"Fixed and saved ({len(data)} entries).")


def cmd_add(args):
    # Parse new entry
    if args.inline:
        try:
            new_entry = json.loads(args.inline)
        except json.JSONDecodeError as e:
            print(f"❌ Cannot parse inline JSON: {e}")
            sys.exit(1)
    else:
        entry_path = Path(args.entry_file)
        if not entry_path.exists():
            print(f"❌ File not found: {entry_path}")
            sys.exit(1)
        try:
            new_entry = json.loads(entry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"❌ Cannot parse entry file: {e}")
            sys.exit(1)

    data = load_or_fix(RESULTS_PATH)

    new_id = new_entry.get("id")
    if not new_id:
        print("❌ Entry must have an 'id' field.")
        sys.exit(1)

    # Check duplicate
    existing_ids = [e.get("id") for e in data]
    if new_id in existing_ids:
        print(f"⚠️  Entry with id '{new_id}' already exists. Overwriting.")
        data = [e for e in data if e.get("id") != new_id]

    data.append(new_entry)
    save(data, RESULTS_PATH)
    print(f"Added entry '{new_id}' ({len(data)} total entries)")


def cmd_set_field(args):
    data = load_or_fix(RESULTS_PATH)

    target_id = args.entry_id
    field = args.field
    value_str = args.value

    # Try to parse value as JSON (so numbers/bools/objects work), fall back to string
    try:
        value = json.loads(value_str)
    except json.JSONDecodeError:
        value = value_str

    matched = False
    for entry in data:
        if entry.get("id") == target_id:
            entry[field] = value
            matched = True
            break

    if not matched:
        print(f"❌ No entry with id '{target_id}' found.")
        sys.exit(1)

    save(data, RESULTS_PATH)
    print(f"Set {target_id}.{field} = {value!r}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Safe JSON editor for data/results.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="Validate the JSON file")
    sub.add_parser("fix", help="Fix unescaped quotes in full_answer fields")

    p_add = sub.add_parser("add", help="Add a new entry")
    p_add.add_argument("entry_file", nargs="?", help="Path to entry JSON file")
    p_add.add_argument("--inline", metavar="JSON", help="Inline JSON string for the entry")

    p_set = sub.add_parser("set-field", help="Set a field on an existing entry")
    p_set.add_argument("entry_id", help="Entry id")
    p_set.add_argument("field", help="Field name")
    p_set.add_argument("value", help="New value (parsed as JSON, fallback to string)")

    args = parser.parse_args()

    if args.command == "check":
        cmd_check(args)
    elif args.command == "fix":
        cmd_fix(args)
    elif args.command == "add":
        if not args.entry_file and not args.inline:
            print("❌ Provide either a file path or --inline <json>")
            sys.exit(1)
        cmd_add(args)
    elif args.command == "set-field":
        cmd_set_field(args)


if __name__ == "__main__":
    main()
