"""STUB — coming in koko-ship v1.1.

Will scrape the user's X account via a hosted Apify endpoint (free tier,
invite-token gated) and analyze their last 50 tweets to derive a voice
profile.

For v1.0 beta:
  - Use one of the other voice setup paths instead:
    - setup_voice_from_claude_logs.py  (default — recommended)
    - setup_voice_from_paste.py        (paste 3-5 of your own writings)
    - setup_voice_questionnaire.py     (5-question interview)

  - If you really want X-based voice now, you can DIY:
      1. Use the bundled scrape script in /scripts/upload_to_sheets.py as a
         template (requires your own Apify token)
      2. Then feed the resulting tweets to setup_voice_from_paste.py
"""
import sys


def main():
    print("=" * 60)
    print("setup_voice_from_x.py is a STUB — coming in koko-ship v1.1")
    print("=" * 60)
    print()
    print("for now, use one of:")
    print("  - setup_voice_from_claude_logs.py  (default, no setup needed)")
    print("  - setup_voice_from_paste.py        (paste your own writings)")
    print("  - setup_voice_questionnaire.py     (5-question interview)")
    print()
    print("see SKILL.md > Voice Setup Mode for details.")
    sys.exit(0)


if __name__ == "__main__":
    main()
