"""Build a voice profile from a 5-question interview.

This script writes a starter questionnaire JSON file that the user fills in,
then converts it to 4 voice markdown files. Most users won't run this directly —
the koko-ship skill walks them through the questions interactively, then
calls this script with the answers.

Usage:
    # Direct (skill calls this with answers JSON):
    python3 setup_voice_questionnaire.py --answers-json '<json>' [--out-dir DIR]

    # Manual (rare):
    python3 setup_voice_questionnaire.py --print-template
    python3 setup_voice_questionnaire.py --answers-file my-answers.json
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

QUESTIONS = [
    {
        "id": "primary_language",
        "ask": "what language do you usually post in? (en / ko / mixed)",
        "default": "en",
    },
    {
        "id": "casualness",
        "ask": "lowercase casual or proper sentence case? (casual / proper / mixed)",
        "default": "casual",
    },
    {
        "id": "favorite_phrases",
        "ask": "list 3-5 phrases or words you actually use (e.g. 'kinda', 'just shipped', 'tbh'). comma-separated.",
        "default": "",
    },
    {
        "id": "emoji_use",
        "ask": "how often do you use emoji? (never / rarely / sometimes / often)",
        "default": "rarely",
    },
    {
        "id": "things_you_hate",
        "ask": "list 3-5 phrases that make you cringe in other people's posts (e.g. 'excited to announce', 'leverage', 'game-changer'). comma-separated.",
        "default": "excited to announce, thrilled, leverage, game-changer, next level",
    },
]


def template():
    return {q["id"]: q.get("default", "") for q in QUESTIONS}


def build_profile(answers):
    casualness = answers.get("casualness", "casual").lower()
    emoji_use = answers.get("emoji_use", "rarely").lower()
    primary_lang = answers.get("primary_language", "en").lower()
    if primary_lang == "mixed":
        primary_lang = "en"  # default to English for posting

    fav = [p.strip() for p in (answers.get("favorite_phrases") or "").split(",") if p.strip()]
    bans = [p.strip() for p in (answers.get("things_you_hate") or "").split(",") if p.strip()]
    bans += [
        "i'm excited to", "thrilled", "humbled", "blessed",
        "game-changer", "next level", "leveraging", "streamline",
        "revolutionary", "amazing", "incredible", "unprecedented",
    ]
    bans = list(dict.fromkeys(bans))  # dedupe preserve order

    emoji_default = "none" if emoji_use in ("never", "rarely") else "occasional"
    emoji_max = 0 if emoji_use == "never" else (1 if emoji_use == "rarely" else 2)

    is_lower = casualness in ("casual", "mixed")

    return {
        "$schema_version": "1.1",
        "$built_from": "questionnaire",
        "$built_at": datetime.now().strftime("%Y-%m-%d %H:%M"),

        "language": {"primary": primary_lang, "rule": "Generate in the user's primary language."},

        "tone": {
            "summary": (
                "Direct, lowercase, casual. Beats over speeches."
                if is_lower
                else "Conversational but properly punctuated."
            ),
            "do": [
                ("lowercase by default" if is_lower else "sentence case is fine"),
                "short declarative beats — one idea per line",
                "first-person 'i' freely",
                "concrete numbers",
                "use contractions naturally",
            ],
            "dont": [
                "no marketing voice",
                "no hype adjectives",
                "no questions to fish for engagement",
            ],
        },

        "specificity_rules": {
            "$comment": "Inherited from koko-ship default. Prevents generic AI output.",
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

        "length": {"target_chars": [180, 260], "max_chars": 280, "optimal_lines": [3, 6]},

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
            "current_default": emoji_default,
            "max_per_post": emoji_max,
            "preferred": [],
            "avoid": ["🚀", "🎉", "💯", "🔥"],
            "rule": f"User said they use emoji '{emoji_use}'. Default {emoji_default}.",
        },

        "hashtags": {
            "use": "branded_toc_only",
            "max_per_post": 1,
            "position": "trailing",
            "format": "newline_before",
            "skip_generic": True,
            "generic_to_avoid": ["#buildinpublic", "#indiehackers", "#vibecoding", "#100daysofcode", "#startup", "#dev", "#coding"],
            "rule": "One branded hashtag, trailing line.",
        },

        "media": {
            "priority": ["video_screen_recording", "before_after_image", "single_screenshot", "code_screenshot", "generated_card_image", "none"],
            "rule": "Always suggest media. Video > image.",
        },

        "personal_vocabulary": {
            "$comment": "From questionnaire answers.",
            "phrases_you_use_freely": fav,
            "phrases_banned": bans,
        },

        "security_filter": {
            "remove": [
                "API keys / secrets",
                "DB connection strings, passwords",
                "internal URLs (localhost:port, .internal)",
                "PII for other people",
            ],
            "keep": ["tech stack", "architecture decisions", "process and trial-and-error"],
        },
    }


def main():
    from voice_output import write_voice_markdown

    ap = argparse.ArgumentParser()
    ap.add_argument("--answers-json", help="JSON string with answers")
    ap.add_argument("--answers-file", help="path to JSON file with answers")
    ap.add_argument("--print-template", action="store_true", help="print empty answer template")
    ap.add_argument("--print-questions", action="store_true", help="print the questions")
    ap.add_argument("--out-dir", default="voice",
                    help="output directory for voice files (default: <cwd>/voice/)")
    args = ap.parse_args()

    if args.print_template:
        print(json.dumps(template(), indent=2))
        return

    if args.print_questions:
        for i, q in enumerate(QUESTIONS, 1):
            print(f"{i}. {q['ask']}")
        return

    if args.answers_json:
        answers = json.loads(args.answers_json)
    elif args.answers_file:
        answers = json.loads(Path(args.answers_file).read_text())
    else:
        print("error: provide --answers-json or --answers-file", file=sys.stderr)
        print("       (or use --print-questions / --print-template)", file=sys.stderr)
        sys.exit(1)

    profile = build_profile(answers)
    out_dir = Path(args.out_dir).expanduser()
    write_voice_markdown(profile, out_dir, source_label="questionnaire")
    print(f"✓ voice profile written → {out_dir}/")
    print(f"  created: profile.md, patterns.md, marketing-voice.md, changelog.md")


if __name__ == "__main__":
    main()
