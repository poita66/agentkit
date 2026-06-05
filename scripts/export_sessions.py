#!/usr/bin/env python3
"""Export opencode sessions to markdown files in prompts/ directory.

Usage:
    python3 scripts/export_sessions.py          # export new sessions only
    python3 scripts/export_sessions.py --all     # re-export all sessions
    python3 scripts/export_sessions.py --clean   # remove non-project / no-work sessions
"""

import json
import os
import re
import subprocess
import sys
import argparse


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")
TMP_DIR = "/tmp/opencode_sessions"

# Sessions to skip: not project development or no work done
SKIP_PATTERNS = [
    r"Activating.*\.venv",
    r"Code quality.*standards",
    r"Export session prompts",
    r"Export transcripts",
    r"Move skill and agent defs",
    r"New session - \d{4}-\d{2}-\d{2}T",
    r"Parallelizable worker subagent spec",
    r"Project constitution principles",
    r"Project principles from technical",
    r"Testing browser automation with DuckDuckGo",
    r"Test the browser automation skill",
]


def run_cmd(cmd, cwd=None):
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=cwd or PROJECT_ROOT
    )
    return result.stdout.strip()


def get_session_ids():
    output = run_cmd("opencode session list")
    if not output:
        return []
    lines = output.split("\n")[2:]  # skip header + separator
    return [line.split()[0] for line in lines if line.strip()]


def export_session(sid):
    """Export session to JSON file, returning the path or None on failure."""
    path = os.path.join(TMP_DIR, f"{sid}.json")
    with open(path, "w") as f:
        subprocess.run(
            ["opencode", "export", sid],
            stdout=f,
            stderr=subprocess.DEVNULL,
            cwd=PROJECT_ROOT,
        )
    # Strip any non-JSON prefix and sanitize
    with open(path) as f:
        content = f.read()
    brace = content.find("{")
    if brace == -1:
        return None
    if brace > 0:
        content = content[brace:]
    content = sanitize_json(content)
    with open(path, "w") as f:
        f.write(content)
    return path


def sanitize_json(text):
    """Escape raw control characters in JSON string values."""
    result = []
    in_string = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '"' and (i == 0 or text[i - 1] != "\\"):
            in_string = not in_string
            result.append(ch)
        elif in_string and ord(ch) < 0x20:
            # Escape all raw control characters
            if ch == "\n":
                result.append("\\n")
            elif ch == "\t":
                result.append("\\t")
            elif ch == "\r":
                result.append("\\r")
            else:
                result.append(f"\\u{ord(ch):04d}")
        else:
            result.append(ch)
        i += 1
    return "".join(result)


def load_session(filepath):
    if not filepath:
        return None
    try:
        with open(filepath) as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def title_to_filename(title):
    safe = re.sub(r"[^\w\s-]", "", title).strip()
    safe = re.sub(r"\s+", "-", safe)[:80]
    return safe + ".md"


def should_skip(title):
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return True
    return False


def extract_messages(session_data):
    messages = []
    for msg in session_data.get("messages", []):
        role = msg["info"]["role"]
        texts = []
        for part in msg.get("parts", []):
            if part.get("type") == "text":
                t = part.get("text", "")
                if t and t.strip():
                    texts.append(t.strip())
        if texts:
            messages.append((role, "\n".join(texts)))
    return messages


def write_markdown(session_data, messages, filename):
    sid = session_data["info"]["id"]
    title = session_data["info"]["title"]
    agent = session_data["info"].get("agent", "N/A")
    model = (
        session_data["info"]["model"]["providerID"]
        + "/"
        + session_data["info"]["model"]["id"]
    )

    filepath = os.path.join(PROMPTS_DIR, filename)
    counter = 1
    while os.path.exists(filepath):
        base, ext = os.path.splitext(filename)
        filepath = os.path.join(PROMPTS_DIR, f"{base}-{counter}{ext}")
        counter += 1

    with open(filepath, "w") as f:
        f.write(f"# Session: {title}\n\n")
        f.write(f"**Session ID:** {sid}\n\n")
        f.write(f"**Agent:** {agent}\n\n")
        f.write(f"**Model:** {model}\n\n")
        f.write(f"**Messages:** {len(messages)}\n\n")
        f.write("---\n\n")
        for i, (role, text) in enumerate(messages):
            role_label = "User" if role == "user" else "Assistant"
            f.write(f"## {role_label} ({i + 1})\n\n")
            f.write(text + "\n\n")
            f.write("---\n\n")

    return os.path.basename(filepath)


def main():
    parser = argparse.ArgumentParser(description="Export opencode sessions to markdown")
    parser.add_argument("--all", action="store_true", help="Re-export all sessions")
    parser.add_argument(
        "--clean", action="store_true", help="Remove non-project / no-work sessions"
    )
    args = parser.parse_args()

    os.makedirs(PROMPTS_DIR, exist_ok=True)
    os.makedirs(TMP_DIR, exist_ok=True)

    if args.clean:
        # Remove files matching skip patterns
        for fname in os.listdir(PROMPTS_DIR):
            if not fname.endswith(".md"):
                continue
            filepath = os.path.join(PROMPTS_DIR, fname)
            with open(filepath) as f:
                first_line = f.readline()
            title = first_line.replace("# Session: ", "")
            if should_skip(title):
                os.remove(filepath)
                print(f"  Removed: {fname}")
        print(f"  Cleaned prompts/ directory")
        return

    session_ids = get_session_ids()
    if not session_ids:
        print("No sessions found.")
        return

    # Get existing filenames to check for new sessions
    existing_filenames = set(os.listdir(PROMPTS_DIR)) if not args.all else set()

    count = 0
    skipped = 0
    for sid in session_ids:
        json_path = export_session(sid)
        session_data = load_session(json_path)
        if not session_data:
            print(f"  Skipping {sid}: failed to export/parse")
            skipped += 1
            continue

        title = session_data["info"]["title"]
        filename = title_to_filename(title)

        if should_skip(title):
            continue

        if not args.all and filename in existing_filenames:
            continue

        messages = extract_messages(session_data)
        if not messages:
            continue

        out_name = write_markdown(session_data, messages, filename)
        count += 1
        print(f"  {out_name} ({len(messages)} messages)")

    # Clean up temp files
    for f in os.listdir(TMP_DIR):
        os.remove(os.path.join(TMP_DIR, f))

    print(
        f"\nDone! {'Exported' if args.all else 'Added'} {count} session(s) to prompts/ ({skipped} failed)"
    )


if __name__ == "__main__":
    main()
