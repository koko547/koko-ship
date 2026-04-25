"""Build a voice profile from pasted writing samples.

The user (via the koko-ship skill) provides 3-5 examples of text that they
wrote and feel sounds like them. This script analyzes the samples and
produces 4 voice markdown files.

Usage:
    python3 setup_voice_from_paste.py --samples-json '<json array of strings>' [--out-dir DIR]
    python3 setup_voice_from_paste.py --samples-file samples.json [--out-dir DIR]
"""
import argparse
import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2700-\u27BF]")


def lang_of(text):
    has_kr = bool(re.search(r"[가-힣]", text))
    has_en = bool(re.search(r"[a-zA-Z]{3,}", text))
    if has_kr and has_en:
        return "mixed"
    if has_kr:
        return "korean"
    return "english"


def analyze(samples):
    if not samples:
        return None

    lengths = [len(s) for s in samples]
    line_counts = [s.count("\n") + 1 for s in samples]
    lang_counts = Counter(lang_of(s) for s in samples)
    primary = "ko" if lang_counts.get("korean", 0) + lang_counts.get("mixed", 0) > lang_counts.get("english", 0) else "en"

    # Lowercase rate (excluding sentence-initial)
    lowercase_rate = 0
    sentence_count = 0
    for s in samples:
        for sent in re.split(r"[.!?]\s+", s):
            sent = sent.strip()
            if not sent:
                continue
            sentence_count += 1
            if sent[0].islower():
                lowercase_rate += 1
    lowercase_pct = round(100 * lowercase_rate / sentence_count) if sentence_count else 0

    # Emoji
    all_emojis = Counter()
    emoji_msgs = 0
    for s in samples:
        found = EMOJI_RE.findall(s)
        if found:
            emoji_msgs += 1
        for e in found:
            all_emojis[e] += 1

    # Hashtags
    hashtag_re = re.compile(r"#\w+")
    hashtag_msgs = sum(1 for s in samples if hashtag_re.search(s))
    all_hashtags = Counter()
    for s in samples:
        for h in hashtag_re.findall(s):
            all_hashtags[h.lower()] += 1

    # Contractions
    contraction_re = re.compile(r"\b\w+'\w+\b")
    contractions = Counter()
    for s in samples:
        for c in contraction_re.findall(s.lower()):
            contractions[c] += 1

    # Frequent words (filtered)
    STOP = {"the", "a", "an", "and", "but", "or", "for", "of", "in", "on", "at",
            "to", "is", "are", "was", "were", "be", "been", "being", "have", "has",
            "had", "do", "does", "did", "will", "would", "should", "could", "this",
            "that", "these", "those", "i", "me", "my", "you", "your", "it", "its",
            "we", "us", "our", "they", "them", "their"}
    word_counts = Counter()
    for s in samples:
        for w in re.findall(r"[a-zA-Z']+|[가-힣]+", s.lower()):
            if w not in STOP and len(w) >= 3:
                word_counts[w] += 1
    top_words = [w for w, c in word_counts.most_common(20) if c >= 2]

    return {
        "n_samples": len(samples),
        "median_length": int(statistics.median(lengths)),
        "median_lines": int(statistics.median(line_counts)),
        "primary_lang": primary,
        "lowercase_pct": lowercase_pct,
        "emoji_pct": round(100 * emoji_msgs / len(samples)),
        "top_emojis": [e for e, _ in all_emojis.most_common(10)],
        "top_hashtags": [h for h, _ in all_hashtags.most_common(10)],
        "uses_contractions": len(contractions) > 0,
        "top_contractions": [c for c, _ in contractions.most_common(8)],
        "top_words": top_words,
    }


def build_profile(samples, analysis):
    is_lower = analysis["lowercase_pct"] > 30

    profile = {
        "$schema_version": "1.1",
        "$built_from": "user_writing_samples",
        "$built_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "$source_stats": {
            "n_samples": analysis["n_samples"],
            "median_length_chars": analysis["median_length"],
        },

        "language": {"primary": analysis["primary_lang"], "rule": "Generate in the user's primary language."},

        "tone": {
            "summary": (
                "Direct, lowercase, casual. Beats over speeches."
                if is_lower
                else "Conversational, properly punctuated when needed."
            ),
            "do": [
                ("lowercase by default" if is_lower else "sentence case where natural"),
                "short declarative beats — one idea per line",
                "first-person 'i' freely",
                ("use contractions naturally" if analysis["uses_contractions"] else "avoid contractions"),
                "concrete numbers and specific outcomes",
            ],
            "dont": [
                "no marketing voice",
                "no hype adjectives",
                "no questions to fish for engagement",
            ],
        },

        "specificity_rules": {
            "$comment": "Inherited from koko-ship default.",
            "one_moment_rule": {"description": "One post = one moment. Never combine."},
            "anti_tagline_rule": {"description": "Forbidden: three or more nouns in parallel structure as a feature list."},
            "would_anyone_else_say_this_test": {"description": "If 100 other indie hackers could post the same text, reject."},
            "show_dont_summarize_rule": {"description": "Required: a specific moment from the actual session."},
            "specificity_gate": {
                "description": "The post must contain at least 2 of:",
                "checks": [
                    "at least one concrete number",
                    "at least one user action verb",
                    "at least one small specific detail unique to this session",
                ],
            },
        },

        "length": {
            "target_chars": [max(150, analysis["median_length"] - 50), min(280, analysis["median_length"] + 80)],
            "max_chars": 280,
            "optimal_lines": [max(2, analysis["median_lines"] - 1), min(8, analysis["median_lines"] + 2)],
        },

        "structure": {
            "preferred_format": "single_tweet",
            "thread_use": "rarely — only when explicitly asked",
            "line_breaks": {"use": "aggressive", "rule": "Each line = one beat."},
        },

        "hooks": {
            "rule": "First line stops the scroll.",
            "preferred_patterns": [
                "outcome_story", "stat_lead", "underdog_frame",
                "ai_credit_story", "named_problem", "vulnerability_confession",
            ],
            "avoid_patterns": ["question_to_audience", "shipped_announcement", "marketing_intro"],
        },

        "emoji": {
            "use": "data_driven_learning",
            "current_default": "occasional" if analysis["emoji_pct"] >= 20 else "none",
            "max_per_post": 2 if analysis["emoji_pct"] >= 30 else (1 if analysis["emoji_pct"] >= 10 else 0),
            "preferred": analysis["top_emojis"][:5],
            "avoid": ["🚀", "🎉", "💯", "🔥"],
            "rule": f"Detected {analysis['emoji_pct']}% emoji usage in your samples.",
        },

        "hashtags": {
            "use": "branded_toc_only",
            "max_per_post": 1,
            "position": "trailing",
            "format": "newline_before",
            "skip_generic": True,
            "generic_to_avoid": ["#buildinpublic", "#indiehackers", "#vibecoding", "#100daysofcode", "#startup", "#dev", "#coding"],
            "rule": "One branded hashtag, trailing line.",
            "$detected_hashtags_in_samples": analysis["top_hashtags"],
        },

        "media": {
            "priority": ["video_screen_recording", "before_after_image", "single_screenshot", "code_screenshot", "generated_card_image", "none"],
            "rule": "Always suggest media. Video > image.",
        },

        "personal_vocabulary": {
            "$comment": "Auto-extracted from your writing samples.",
            "phrases_you_use_freely": analysis["top_words"][:15],
            "your_contractions": analysis["top_contractions"],
            "phrases_banned": [
                "i'm excited to", "thrilled", "humbled", "blessed",
                "game-changer", "next level", "leveling up", "leverage",
                "streamline", "revolutionary", "amazing", "incredible",
            ],
        },

        "security_filter": {
            "remove": [
                "API keys / secrets",
                "DB connection strings",
                "internal URLs",
                "PII for other people",
            ],
            "keep": ["tech stack", "architecture decisions", "process and trial-and-error"],
        },
    }
    return profile


def main():
    from voice_output import write_voice_markdown

    ap = argparse.ArgumentParser()
    ap.add_argument("--samples-json", help="JSON array of sample strings")
    ap.add_argument("--samples-file", help="path to JSON array of samples")
    ap.add_argument("--out-dir", default="voice",
                    help="output directory for voice files (default: <cwd>/voice/)")
    args = ap.parse_args()

    if args.samples_json:
        samples = json.loads(args.samples_json)
    elif args.samples_file:
        samples = json.loads(Path(args.samples_file).read_text())
    else:
        print("error: provide --samples-json or --samples-file", file=sys.stderr)
        sys.exit(1)

    if not isinstance(samples, list) or not all(isinstance(s, str) for s in samples):
        print("error: samples must be a JSON array of strings", file=sys.stderr)
        sys.exit(1)

    if len(samples) < 1:
        print("error: at least 1 sample required (3-5 recommended)", file=sys.stderr)
        sys.exit(1)

    analysis = analyze(samples)
    profile = build_profile(samples, analysis)

    out_dir = Path(args.out_dir).expanduser()
    write_voice_markdown(profile, out_dir, source_label="writing-samples")
    print(f"✓ voice profile written → {out_dir}/")
    print(f"  created: profile.md, patterns.md, marketing-voice.md, changelog.md")
    print(f"  analyzed {analysis['n_samples']} samples")
    print(f"  median length: {analysis['median_length']} chars")
    print(f"  primary lang: {analysis['primary_lang']}")
    print(f"  lowercase: {analysis['lowercase_pct']}%")
    print(f"  emoji: {analysis['emoji_pct']}%")


if __name__ == "__main__":
    main()
