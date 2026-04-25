---
name: koko-ship-voice-setup
description: >
  Set up a personal voice profile for koko-ship. Creates the voice/ folder
  that all other koko-ship skills read. Two paths: import a seed file from
  the website quiz, or generate from scratch using writing samples.
  Trigger on: "set up my voice", "voice setup", "create voice profile",
  "use this as my voice profile", or when writer detects no voice/ folder.
---

# Voice Setup

**Shared resources:** `~/.claude/skills/koko-ship-shared/`

## When this runs

- User explicitly asks to set up voice
- Writer skill detects no voice/ folder and redirects here
- User drops a voice.md seed file and says "use this"

## Voice profile gate

Check for existing voice profile:
1. `<cwd>/voice/profile.md` (project-local)
2. `~/.koko-ship/voice/profile.md` (user-global)

If found → voice is set up. Tell the user and exit.
If not found → enter setup mode.

## Setup modes

### Case 1: Seed file import (user came from website quiz)

If user has a `voice.md` file (downloaded from koko-ship.com quiz):
- Read the seed file
- Read the template: `~/.claude/skills/koko-ship-shared/references/voice-profile-template.md`
- Expand into full voice/ folder:
  - voice/profile.md — from quiz analysis (fill template)
  - voice/patterns.md — starter (thin — quiz gives limited data)
  - voice/marketing-voice.md — from quiz results
  - voice/changelog.md — empty, starts tracking from here
- Tell user:

> your starter voice profile is set up from the quiz.
> it'll get sharper as you post and edit.
> say "make a bip post" to try it.

### Case 2: No seed file (user found koko-ship on GitHub)

Offer 3 options:
- **Default:** scan past Claude Code conversations
  Run: `python3 ~/.claude/skills/koko-ship-shared/scripts/setup_voice_from_claude_logs.py --out-dir voice`
- **Option A:** paste 3-5 writing samples
  Run: `python3 ~/.claude/skills/koko-ship-shared/scripts/setup_voice_from_paste.py --out-dir voice`
- **Option B:** 5-question questionnaire
  Run: `python3 ~/.claude/skills/koko-ship-shared/scripts/setup_voice_questionnaire.py --out-dir voice`

User says "go" → run default.
User picks option → run selected script.

All scripts output to `<cwd>/voice/` (4 files: profile.md, patterns.md, marketing-voice.md, changelog.md).
Confirm what was found (language, tone, signature patterns).

### Migration from old format

If `.bip-voice.json` exists but voice/ does not:
- Offer to migrate: "found an older voice profile. want me to upgrade it to the new format?"
- Run: `python3 ~/.claude/skills/koko-ship-shared/scripts/setup_voice_from_claude_logs.py --out-dir voice`
  (The script auto-detects and migrates .bip-voice.json)
- Keep .bip-voice.json as backup

## "set up my voice" — re-run at any time

Re-entering setup mode replaces voice/ files. Changelog is preserved (renamed to changelog-backup.md before setup, restored after).
