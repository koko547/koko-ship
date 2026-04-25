---
name: koko-ship-writer
description: >
  Generates build-in-public posts in the user's actual voice. Reads recent
  Claude Code sessions, extracts moments worth sharing, and drafts posts
  through a multi-role pipeline (writer, editor, QA).
  Trigger on: "make a bip post", "bip post", "write a post", "post about this",
  "share this", "tweet this", "write about what I built",
  "make content from this session".
  Requires: voice/ folder (if missing, tells user to run voice setup).
  Also handles: voice evolution via explicit user direction.
---

# Writer

**Shared resources:** `~/.claude/skills/koko-ship-shared/`

## Before anything: check voice profile

Read voice/ files. If voice/ doesn't exist → tell user: "no voice profile found. say 'set up my voice' first." Stop.

Load all 3 readable voice files:
- `voice/profile.md` — signature patterns, anti-patterns, evaluator checklist, vocabulary markers, sentence rhythm, emotional expression
- `voice/marketing-voice.md` — post characteristics (language, length, format), publishable filter, content angles, hashtag rules
- `voice/patterns.md` — thinking style, problem approach, reaction patterns (used for moment selection and angle choice)

## Two voice layers

This skill applies two layers:

1. **User-personal voice** — the 3 voice files above. How this user actually writes.
2. **Writing principles** — what makes a BIP post work. See `~/.claude/skills/koko-ship-shared/references/writing-principles.md`.

When the two layers conflict, **personal voice wins**. The principles are guidelines, not formulas.

## Voice evolution: two paths

### Path 1: Implicit (edit diffs) — runs at start of every post generation

Check `voice/changelog.md` for unprocessed edit diffs.
For each unprocessed diff: extract patterns, log them.
After 3+ occurrences of same pattern: propose update to `voice/profile.md`.
User approves → update profile. User declines → mark as reviewed, don't update.

### Path 2: Explicit (user tells you to change their voice)

If user says things like:
- "I want to sound more casual"
- "stop using parenthetical asides"
- "my voice should be shorter and punchier"
- "change my voice to..."
- "update my voice profile"
- "I don't like how X sounds"

This is NOT a post request. This is a voice evolution command.
→ Update `voice/profile.md` directly (add/remove/modify patterns)
→ Log in `voice/changelog.md` with source: explicit-direction
→ Confirm: "updated your voice profile. [what changed]. next post will reflect this."

If the change is fundamental (e.g., switching from casual to formal, or changing language):
→ Suggest re-running voice setup: "this is a big shift. want me to re-analyze your voice with this direction in mind?"

## Drafting pipeline

Read `~/.claude/skills/koko-ship-shared/references/workflow.md` for the complete step-by-step pipeline. **Always read it before generating any post.**

**Pipeline summary:**
1. Process previous edit diffs (voice evolution implicit path)
2. Detect project context (hashtag, project name)
3. Load voice profile (all 3 files)
4. Check history for repetition
5. Find building sessions (via `~/.claude/skills/koko-ship-shared/scripts/read_project_sessions.py`)
6. Extract postable moments (WHAT happened + WHY)
7. Select best moment (or ask user if multiple)
8. Quality-gate the moment (is it worth posting?)
9. Apply QA filters (read `~/.claude/skills/koko-ship-qa/SKILL.md`)
10. Apply writing principles (`~/.claude/skills/koko-ship-shared/references/writing-principles.md`)
11. Draft 3 versions (vary hook, length, structure)
12. Evaluate all 3 (read `~/.claude/skills/koko-ship-editor/SKILL.md`) → pick winner
13. Deliver to user
14. Save draft for diff tracking
15. On user approval → save to `.bip-history.json`
16. If user edited → capture diff for voice evolution

## Cardinal rules

1. **No project-summary posts.** CLAUDE.md and README describe the project, not the session. Never use them as content sources.
2. **One moment per post.** Never combine. If multiple moments exist, ask the user to pick.
3. **Self-eval gate is required.** No draft is delivered without passing the editor evaluation.
4. **Generic output is failure.** If you can't produce a post that passes in 3 attempts, ask the user for a specific moment instead of delivering weak content.
5. **Drafts only, never auto-publish.** This skill creates drafts. Publishing is always a separate, explicit human action.
6. **Branded hashtag only.** Never use generic hashtags. One per post, trailing line.

## Revision loop

After delivering first draft, accept natural-language feedback.
Re-check voice compliance after every revision.
Approval signals: "go", "ship it", "done", "good" → save to history.
Discard signals: "start over", "different angle" → fresh draft.

## File locations summary

| File | Purpose | Required |
|---|---|---|
| `~/.claude/skills/koko-ship-shared/references/workflow.md` | Detailed generation pipeline | yes |
| `~/.claude/skills/koko-ship-shared/references/writing-principles.md` | 5 writing principles + reference examples | yes |
| `~/.claude/skills/koko-ship-shared/references/eval-rubric.md` | 4-axis quality rubric | yes |
| `~/.claude/skills/koko-ship-shared/references/history-schema.json` | Schema for .bip-history.json | yes |
| `~/.claude/skills/koko-ship-editor/SKILL.md` | Editor — voice + content evaluation | yes |
| `~/.claude/skills/koko-ship-qa/SKILL.md` | QA — security, jargon, platform | yes |
| `voice/profile.md` | User's voice patterns + evaluator checklist | yes |
| `voice/patterns.md` | User's thinking style (deep layer) | yes |
| `voice/marketing-voice.md` | Publishable filter + post characteristics | yes |
| `voice/changelog.md` | Voice evolution tracker | yes |
| `<cwd>/.bip-history.json` | Per-project post history | created on first approval |
| `<cwd>/.bip-drafts/` | Saved AI drafts for diff comparison | created on first draft |
