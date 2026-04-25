"""Read past building sessions for the current project from ~/.claude/projects/.

Given a project directory (cwd), finds matching session logs and returns
summaries for user selection.

Usage:
    python3 read_project_sessions.py --cwd /path/to/project [--hours 24] [--fallback-hours 168]

Output: JSON array of session summaries, newest first.

Each summary:
{
  "session_id": "abc123",
  "file": "/path/to/session.jsonl",
  "started_at": "2026-04-10T14:00:00",
  "ended_at": "2026-04-10T16:00:00",
  "duration_minutes": 120,
  "n_user_messages": 15,
  "n_assistant_messages": 18,
  "summary": "one-line summary of what happened",
  "key_actions": ["created login.tsx", "fixed auth bug", "discussed payment flow"],
  "is_excluded": false,
  "exclude_reason": null
}
"""
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CLAUDE_BASE = Path.home() / ".claude/projects"

# Exclusion patterns: koko-ship meta sessions only
EXCLUDE_PATTERNS = [
    re.compile(r"voice\s*(profile|setup|config)", re.I),
    re.compile(r"(install|setup)\s*(koko.?ship|skill)", re.I),
    re.compile(r"\.bip-voice\.json", re.I),
    re.compile(r"setup_voice_from", re.I),
]

# Tags/noise to strip from user messages
TAG_STRIP = re.compile(
    r"<(system-reminder|ide_selection|ide_opened_file|command-name|command-message|"
    r"command-args|local-command-stdout|user-prompt-submit-hook|local-command-stderr)>"
    r".*?</\1>",
    re.S,
)
TAG_OPEN_STRIP = re.compile(
    r"<(system-reminder|ide_selection|ide_opened_file|command-name|command-message|"
    r"command-args|local-command-stdout|user-prompt-submit-hook|local-command-stderr)>.*",
    re.S,
)
DATE_PREFIX = re.compile(r"^\[오늘 날짜:[^\]]*\]\s*")


def cwd_to_project_dirname(cwd: str) -> str:
    """Convert a cwd path to the Claude project directory name format.
    Claude stores project dirs as '-Users-<username>-dev-<project>'
    (the leading slash becomes a leading dash)."""
    return cwd.replace("/", "-")


def find_project_dir(cwd: str) -> Path | None:
    """Find the Claude project directory for a given cwd."""
    target = cwd_to_project_dirname(cwd)
    candidate = CLAUDE_BASE / target
    if candidate.exists():
        return candidate
    # Fuzzy match: maybe trailing slashes differ
    for p in CLAUDE_BASE.iterdir():
        if p.name == target or p.name.startswith(target):
            return p
    return None


def clean_text(text: str) -> str:
    text = TAG_STRIP.sub("", text)
    text = TAG_OPEN_STRIP.sub("", text)
    text = DATE_PREFIX.sub("", text)
    return text.strip()


def extract_user_text(content) -> str | None:
    """Extract displayable user text from message content."""
    if isinstance(content, str):
        return clean_text(content) or None
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                t = clean_text(item.get("text", ""))
                if t and len(t) >= 5:
                    return t
    return None


def parse_timestamp(ts_str: str) -> datetime | None:
    """Parse various timestamp formats from session metadata."""
    if not ts_str:
        return None
    for fmt in [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
    ]:
        try:
            return datetime.strptime(ts_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def is_excluded(user_messages: list[str]) -> tuple[bool, str | None]:
    """Check if a session is koko-ship meta (voice setup, skill install)."""
    combined = " ".join(user_messages[:20])
    for pat in EXCLUDE_PATTERNS:
        if pat.search(combined):
            return True, pat.pattern
    return False, None


def summarize_session(user_msgs: list[str], assistant_actions: list[str]) -> str:
    """Create a one-line summary from user messages and assistant actions."""
    # Find the most substantive user messages (skip short ones)
    substantive = [m for m in user_msgs if len(m) > 20 and not m.startswith("<")][:5]
    if not substantive:
        substantive = user_msgs[:3]

    # Look for action patterns in user messages
    actions = []
    patterns = {
        "built": re.compile(r"\b(build|create|make|add|implement|set\s*up)\b", re.I),
        "fixed": re.compile(r"\b(fix|debug|solve|resolve|patch)\b", re.I),
        "discussed": re.compile(r"\b(think|discuss|consider|decide|choose|opinion|thoughts)\b", re.I),
        "configured": re.compile(r"\b(config|setup|install|deploy|connect)\b", re.I),
        "designed": re.compile(r"\b(design|plan|architect|structure|spec)\b", re.I),
        "tested": re.compile(r"\b(test|check|verify|validate|try)\b", re.I),
        "refactored": re.compile(r"\b(refactor|clean|reorganize|restructure|move)\b", re.I),
    }
    for msg in substantive:
        for action, pat in patterns.items():
            if pat.search(msg):
                actions.append(action)
                break

    # Extract key nouns/topics from file operations in assistant actions
    file_actions = []
    for a in assistant_actions[:30]:
        files = re.findall(r"[\w\-]+\.\w{1,5}", a)
        file_actions.extend(files[:3])
    file_actions = list(dict.fromkeys(file_actions))[:5]

    # Build summary
    if substantive:
        # Use first substantive message as base, truncate
        base = substantive[0][:100].rstrip(".")
        if file_actions:
            return f"{base} ({', '.join(file_actions[:3])})"
        return base
    elif file_actions:
        action_word = actions[0] if actions else "worked on"
        return f"{action_word} {', '.join(file_actions[:4])}"
    else:
        return "session with limited context"


def extract_key_actions(user_msgs: list[str], assistant_msgs: list[dict]) -> list[str]:
    """Extract concrete actions from the session."""
    actions = []

    # From assistant tool calls
    for msg in assistant_msgs:
        content = msg.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    tool = item.get("name", "")
                    inp = item.get("input", {})
                    if tool == "Write":
                        fp = inp.get("file_path", "")
                        if fp:
                            actions.append(f"created {Path(fp).name}")
                    elif tool == "Edit":
                        fp = inp.get("file_path", "")
                        if fp:
                            actions.append(f"edited {Path(fp).name}")
                    elif tool == "Bash":
                        cmd = inp.get("command", "")[:60]
                        if cmd and not cmd.startswith(("ls", "cat", "echo")):
                            actions.append(f"ran: {cmd}")

    # Dedupe, keep order
    seen = set()
    unique = []
    for a in actions:
        if a not in seen:
            seen.add(a)
            unique.append(a)
    return unique[:10]


def read_session(filepath: Path) -> dict | None:
    """Read a single session file and return structured summary."""
    user_messages = []
    assistant_raw = []
    assistant_actions_raw = []
    timestamps = []

    try:
        with open(filepath) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except Exception:
                    continue

                msg = d.get("message", {})
                msg_type = d.get("type")

                # Collect timestamps — top-level field on every line
                ts_str = d.get("timestamp")
                if ts_str:
                    ts = parse_timestamp(ts_str)
                    if ts:
                        timestamps.append(ts)

                if msg_type == "user":
                    text = extract_user_text(msg.get("content"))
                    if text:
                        user_messages.append(text)
                elif msg_type == "assistant":
                    assistant_raw.append(msg)
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                if item.get("type") == "tool_use":
                                    assistant_actions_raw.append(json.dumps(item.get("input", {}))[:200])
                                elif item.get("type") == "text":
                                    assistant_actions_raw.append(item.get("text", "")[:200])
    except Exception:
        return None

    if not user_messages:
        return None

    # Use file mtime as fallback timestamp
    mtime = datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc)
    started = timestamps[0] if timestamps else mtime
    ended = timestamps[-1] if timestamps else mtime

    excluded, reason = is_excluded(user_messages)
    key_actions = extract_key_actions(user_messages, assistant_raw)
    summary = summarize_session(user_messages, assistant_actions_raw)

    return {
        "session_id": filepath.stem,
        "file": str(filepath),
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "duration_minutes": min(480, max(1, int((ended - started).total_seconds() / 60))),
        "n_user_messages": len(user_messages),
        "n_assistant_messages": len(assistant_raw),
        "summary": summary,
        "key_actions": key_actions,
        "is_excluded": excluded,
        "exclude_reason": reason,
    }


def get_sessions(cwd: str, hours: int = 24, fallback_hours: int = 168) -> list[dict]:
    proj_dir = find_project_dir(cwd)
    if not proj_dir:
        return []

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)
    fallback_cutoff = now - timedelta(hours=fallback_hours)

    # Read all sessions
    all_sessions = []
    for f in proj_dir.glob("*.jsonl"):
        session = read_session(f)
        if session and not session["is_excluded"]:
            all_sessions.append(session)

    # Filter out trivial sessions (warmups, sub-agents, <3 user messages)
    all_sessions = [s for s in all_sessions if s["n_user_messages"] >= 3]

    # Sort newest first
    all_sessions.sort(key=lambda s: s["ended_at"], reverse=True)

    # Filter by time
    recent = [s for s in all_sessions if s["ended_at"] >= cutoff.isoformat()]

    if recent:
        return recent

    # Fallback: expand to 7 days
    expanded = [s for s in all_sessions if s["ended_at"] >= fallback_cutoff.isoformat()]
    return expanded


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cwd", required=True, help="project directory path")
    ap.add_argument("--hours", type=int, default=24, help="initial time window (default 24)")
    ap.add_argument("--fallback-hours", type=int, default=168, help="expanded window if no recent sessions (default 168 = 7 days)")
    ap.add_argument("--include-excluded", action="store_true", help="include excluded sessions in output")
    args = ap.parse_args()

    sessions = get_sessions(args.cwd, args.hours, args.fallback_hours)

    if not sessions:
        print(json.dumps({"sessions": [], "message": "no sessions found"}))
        sys.exit(0)

    print(json.dumps({"sessions": sessions}, indent=2, default=str))


if __name__ == "__main__":
    main()
