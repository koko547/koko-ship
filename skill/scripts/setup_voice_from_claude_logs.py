"""Build a voice profile by analyzing the user's past Claude Code conversations.

Reads ~/.claude/projects/, extracts only the user's own messages (never Claude's
responses, never tool results), filters noise, then derives voice signals:
length, language mix, openers, directive patterns, emoji usage, key phrases.

Usage:
    python3 setup_voice_from_claude_logs.py [--out PATH] [--exclude PROJECT_NAME ...] [--dry-run]

Defaults:
    --out  ~/.bip-voice.json
    Reads all projects under ~/.claude/projects/

Output: a voice profile JSON ready to be used by the koko-ship skill.
"""
import argparse
import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

CLAUDE_BASE = Path.home() / ".claude/projects"

# Patterns for noise filtering
SKIP_PATTERNS = [
    re.compile(r"^Warmup$", re.I),
    re.compile(r"^Caveat:", re.I),
    re.compile(r"^/[a-z\-]+($|\s)"),
    re.compile(r"^\s*[a-zA-Z0-9_\-/.]+\.(md|json|py|js|ts|tsx|sh|txt)\s*$"),
    re.compile(r"^<task-notification>", re.I),
    re.compile(r"^<local-command", re.I),
    re.compile(r"^\[voice\b", re.I),
    re.compile(r"^\[request interrupted", re.I),
    re.compile(r"^\[image #\d", re.I),
    re.compile(r"^\[#image", re.I),
    re.compile(r"^<bash-input>", re.I),
    re.compile(r"^Please continue", re.I),
]

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
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2700-\u27BF]")


def clean(text: str) -> str:
    text = TAG_STRIP.sub("", text)
    text = TAG_OPEN_STRIP.sub("", text)
    text = DATE_PREFIX.sub("", text)
    return text.strip()


def is_noise(text: str) -> bool:
    if len(text) < 10:
        return True
    for p in SKIP_PATTERNS:
        if p.search(text):
            return True
    if not re.search(r"[a-zA-Z가-힣]{3,}", text):
        return True
    return False


def extract_user_texts(content):
    """Yield real user-typed text strings from message content (string or list)."""
    if isinstance(content, str):
        yield content
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                t = item.get("text", "")
                if t:
                    yield t


def collect_messages(exclude_projects=None):
    exclude_projects = set(exclude_projects or [])
    if not CLAUDE_BASE.exists():
        return [], {}

    messages = []
    project_counts = Counter()

    for proj_dir in sorted(CLAUDE_BASE.iterdir()):
        if not proj_dir.is_dir():
            continue
        proj_name = proj_dir.name.replace("-Users-", "/Users/").replace("-", "/")
        # Match against either raw dirname or normalized name
        if proj_dir.name in exclude_projects or proj_name in exclude_projects:
            continue
        for jfile in proj_dir.glob("*.jsonl"):
            try:
                with open(jfile) as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                        except Exception:
                            continue
                        if d.get("type") != "user":
                            continue
                        msg = d.get("message", {})
                        content = msg.get("content")
                        for raw in extract_user_texts(content):
                            text = clean(raw)
                            if is_noise(text):
                                continue
                            messages.append({
                                "project": proj_dir.name,
                                "text": text,
                                "len": len(text),
                            })
                            project_counts[proj_dir.name] += 1
            except Exception:
                continue
    return messages, project_counts


def lang_of(text):
    has_kr = bool(re.search(r"[가-힣]", text))
    has_en = bool(re.search(r"[a-zA-Z]{3,}", text))
    if has_kr and has_en:
        return "mixed"
    if has_kr:
        return "korean"
    return "english"


def analyze(messages):
    if not messages:
        return None

    lengths = [m["len"] for m in messages]
    lang_counts = Counter(lang_of(m["text"]) for m in messages)

    primary_lang = "en"
    if lang_counts.get("korean", 0) + lang_counts.get("mixed", 0) > lang_counts.get("english", 0):
        primary_lang = "ko"

    # Openers
    opener_words = Counter()
    for m in messages:
        first = m["text"].split()
        if first:
            opener_words[first[0].lower().rstrip(".,?!:")] += 1

    # Filter out boilerplate-y openers
    OPENER_BLACKLIST = {"the", "a", "an", "i", "this", "that", "it", "and", "but", "for", "in", "on", "at", "to", "of"}
    meaningful_openers = [(w, c) for w, c in opener_words.most_common(40) if w not in OPENER_BLACKLIST]
    top_openers = [w for w, _ in meaningful_openers[:12]]

    # Directive patterns
    DIRECTIVES = {
        "decisive": re.compile(r"\b(go|let'?s|hop on|do it|ship it|just do)\b", re.I),
        "preference": re.compile(r"\b(good|nice|great|love|like this|perfect|yup)\b", re.I),
        "rejection": re.compile(r"\b(no|not|don'?t|skip|stop|hate|nope)\b", re.I),
        "exploration": re.compile(r"\b(why|how|what|which|where|when)\b", re.I),
    }
    directive_counts = {}
    for name, pat in DIRECTIVES.items():
        directive_counts[name] = sum(1 for m in messages if pat.search(m["text"]))

    # Emoji usage
    emoji_counter = Counter()
    emoji_msgs = 0
    for m in messages:
        found = EMOJI_RE.findall(m["text"])
        if found:
            emoji_msgs += 1
            for e in found:
                emoji_counter[e] += 1
    emoji_pct = round(100 * emoji_msgs / len(messages))

    # Frequent short phrases (2-3 word collocations)
    bigram_counts = Counter()
    for m in messages:
        words = re.findall(r"[a-zA-Z']+|[가-힣]+", m["text"].lower())
        for i in range(len(words) - 1):
            bg = " ".join(words[i:i + 2])
            bigram_counts[bg] += 1
    BIGRAM_BLACKLIST = {"of the", "to the", "in the", "is a", "i am", "i have", "i was"}
    top_bigrams = [bg for bg, c in bigram_counts.most_common(40)
                   if bg not in BIGRAM_BLACKLIST and c >= 3][:15]

    # Question vs statement
    question_pct = round(100 * sum(1 for m in messages if m["text"].rstrip().endswith("?")) / len(messages))

    # Code-switching detection
    mixed_pct = round(100 * lang_counts.get("mixed", 0) / len(messages))

    return {
        "n_messages": len(messages),
        "median_length": int(statistics.median(lengths)),
        "mean_length": int(statistics.mean(lengths)),
        "primary_lang": primary_lang,
        "lang_distribution": {k: round(100 * v / len(messages)) for k, v in lang_counts.most_common()},
        "code_switching_pct": mixed_pct,
        "top_openers": top_openers,
        "directive_counts": directive_counts,
        "emoji_pct": emoji_pct,
        "top_emojis": [e for e, _ in emoji_counter.most_common(10)],
        "top_phrases": top_bigrams,
        "question_pct": question_pct,
    }


def build_voice_profile(analysis, source_name="claude_session_corpus"):
    """Convert analysis stats into a koko-ship voice profile JSON."""
    if not analysis:
        return None

    # Tone derivation: short directive messages with low formality = casual
    is_casual = analysis["median_length"] < 200 and analysis["directive_counts"].get("decisive", 0) > 5

    profile = {
        "$schema_version": "1.1",
        "$built_from": source_name,
        "$built_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "$source_stats": {
            "n_messages_analyzed": analysis["n_messages"],
            "median_length_chars": analysis["median_length"],
        },

        "language": {
            "primary": analysis["primary_lang"],
            "rule": "Generate in the user's primary language. Code-switching is OK if natural.",
        },

        "tone": {
            "summary": (
                "Direct, lowercase, casual. Decisive but unpretentious. Beats over speeches."
                if is_casual
                else "Thoughtful, conversational. Mix of casual and considered."
            ),
            "do": [
                "lowercase by default",
                "short declarative beats — one idea per line",
                f"use natural openers like: {', '.join(analysis['top_openers'][:6]) if analysis['top_openers'] else 'i, today, hmm'}",
                "first-person 'i' freely",
                "concrete numbers and specific outcomes",
                "use contractions naturally" if analysis["primary_lang"] == "en" else "use casual register naturally",
            ],
            "dont": [
                "no marketing voice ('excited to announce', 'thrilled to share', 'proud to introduce')",
                "no hype adjectives ('amazing', 'incredible', 'game-changing')",
                "no formal capitalization of every sentence",
                "no questions to fish for engagement",
            ],
        },

        "specificity_rules": {
            "$comment": "These rules prevent generic AI output. Inherited from koko-ship default.",
            "one_moment_rule": {"description": "One post = one moment. Never combine."},
            "anti_tagline_rule": {"description": "Forbidden: three or more nouns in parallel structure as a feature list."},
            "would_anyone_else_say_this_test": {"description": "If 100 other indie hackers could post the same text, reject."},
            "show_dont_summarize_rule": {"description": "Forbidden: 'built X for Y'. Required: a specific moment from the actual session."},
            "specificity_gate": {
                "description": "The post must contain at least 2 of:",
                "checks": [
                    "at least one concrete number from the actual session",
                    "at least one user action verb (asked, tried, broke, fixed, picked)",
                    "at least one small specific detail unique to this session",
                ],
            },
        },

        "length": {
            "target_chars": [180, 260],
            "max_chars": 280,
            "optimal_lines": [3, 6],
        },

        "structure": {
            "preferred_format": "single_tweet",
            "thread_use": "rarely — only when explicitly asked",
            "line_breaks": {"use": "aggressive", "rule": "Each line = one beat."},
        },

        "hooks": {
            "rule": "First line stops the scroll.",
            "preferred_patterns": [
                "outcome_story",
                "stat_lead",
                "underdog_frame",
                "ai_credit_story",
                "named_problem",
                "vulnerability_confession",
            ],
            "avoid_patterns": [
                "question_to_audience (unless real question with stake)",
                "shipped_announcement",
                "marketing_intro",
            ],
            "openers_ok": analysis["top_openers"][:10],
            "openers_to_avoid": ["Excited to", "Thrilled to", "Proud to", "Hey everyone", "Announcing"],
        },

        "emoji": {
            "use": "data_driven_learning",
            "current_default": "none" if analysis["emoji_pct"] < 10 else "occasional",
            "max_per_post": 2,
            "preferred": analysis["top_emojis"][:5],
            "avoid": ["🚀", "🎉", "💯", "🔥"],
            "rule": (
                f"Detected {analysis['emoji_pct']}% emoji usage in your past messages. "
                "Default to no emoji unless the moment really calls for one."
            ),
        },

        "hashtags": {
            "use": "branded_toc_only",
            "max_per_post": 1,
            "position": "trailing",
            "format": "newline_before",
            "skip_generic": True,
            "generic_to_avoid": ["#buildinpublic", "#indiehackers", "#vibecoding", "#100daysofcode", "#startup", "#dev", "#coding"],
            "rule": "Always append project's branded hashtag on its own trailing line. Auto-detect from .bip-config.json → CLAUDE.md → package.json → cwd basename.",
        },

        "media": {
            "priority": ["video_screen_recording", "before_after_image", "single_screenshot", "code_screenshot", "generated_card_image", "none"],
            "rule": "Always suggest media. Video > image. Be specific about what to capture.",
        },

        "personal_vocabulary": {
            "$comment": "Auto-extracted from your past Claude conversations. Top phrases you actually use.",
            "phrases_you_use_freely": analysis["top_phrases"][:20],
            "phrases_banned": [
                "i'm excited to", "thrilled", "humbled", "blessed",
                "game-changer", "next level", "leveling up", "leverage",
                "streamline", "revolutionary", "amazing", "incredible",
                "unprecedented", "delighted to share", "stoked",
            ],
        },

        "security_filter": {
            "remove": [
                "API keys / secrets (sk_, pk_, ot_, Bearer, token=)",
                "DB connection strings, passwords, host:port",
                "internal URLs (localhost:port, .internal, raw IPs)",
                "PII for other people (emails, phone numbers, real names)",
            ],
            "keep": [
                "tech stack and tool names",
                "architecture decisions",
                "error messages (with credentials masked)",
                "full process and trial-and-error",
            ],
        },
    }
    return profile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path.home() / ".bip-voice.json"))
    ap.add_argument("--exclude", action="append", default=[],
                    help="exclude project directory name(s) (repeatable)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print analysis without writing the file")
    args = ap.parse_args()

    if not CLAUDE_BASE.exists():
        print(f"error: {CLAUDE_BASE} does not exist", file=sys.stderr)
        sys.exit(1)

    print(f"scanning {CLAUDE_BASE}...")
    messages, project_counts = collect_messages(exclude_projects=args.exclude)
    if not messages:
        print("no user messages found. nothing to learn from.", file=sys.stderr)
        sys.exit(2)

    print(f"\nfound {len(messages)} user messages across {len(project_counts)} projects:")
    for p, c in project_counts.most_common(10):
        print(f"  {c:5d}  {p}")
    if len(project_counts) > 10:
        print(f"  ... and {len(project_counts) - 10} more")

    print("\nanalyzing voice...")
    analysis = analyze(messages)
    profile = build_voice_profile(analysis)

    print(f"\n=== voice signals detected ===")
    print(f"  primary language:  {analysis['primary_lang']}")
    print(f"  median length:     {analysis['median_length']} chars")
    print(f"  code-switching:    {analysis['code_switching_pct']}%")
    print(f"  emoji usage:       {analysis['emoji_pct']}%")
    print(f"  top openers:       {', '.join(analysis['top_openers'][:8])}")
    print(f"  top phrases:       {', '.join(analysis['top_phrases'][:6])}")

    if args.dry_run:
        print("\n--dry-run: not writing file")
        return

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False))
    print(f"\n✓ voice profile written → {out_path}")
    print("\nyou can now generate posts. try:")
    print("  'make a BIP post about today'")


if __name__ == "__main__":
    main()
