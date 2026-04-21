# Voice Evolution v2 — Implementation Instructions

## What this does
When a user edits an AI-generated post before publishing, we capture the diff and learn from it. Over time, the voice profile becomes more accurate, and the user needs to edit less.

This is the core value loop: use → edit → learn → better output → less editing.

---

## File structure changes

Add to existing `~/.koko-ship/` (or wherever the skill stores data):

```
~/.koko-ship/
├── voice/
│   ├── profile.md          ← existing, will be updated via suggestions
│   ├── patterns.md         ← existing
│   ├── marketing-voice.md  ← existing
│   └── changelog.md        ← NEW: auto-generated, tracks all diffs
├── history/
│   ├── .bip-history.json   ← existing
│   └── drafts/             ← NEW: stores AI original drafts
│       ├── draft-2026-04-20-001.md
│       └── draft-2026-04-21-002.md
└── raw/
```

---

## Implementation steps

### Step 1: Save AI draft before showing to user

In the Writer agent (SKILL.md), after generating the final draft:

```
Before (current):
  Writer generates post → shows to user → done

After:
  Writer generates post → saves to drafts/ folder → shows to user
```

Save format (`drafts/draft-{date}-{seq}.md`):
```markdown
---
date: 2026-04-20
seq: 001
context: building + active
source: session log — redesigned landing page
evaluator_score:
  voice: 34
  content: 32
---

asked my AI 'wasn't yesterday also the last day of phoenix mode?' 
it was. built a gamified system for my ADHD brain. when you break 
a streak, you get 3 days of double points instead of punishment. 
building the game is one thing. catching your own bugs while 
playing it,,
```

Tell the user:
```
here's your post. edit it however you want — 
every edit teaches me your voice better.

when you're happy with it, say "done" or "ship it."
```

### Step 2: Capture the final version

When user says "done" or "ship it":
- Read the current post content (user may have edited inline or told you what to change)
- Save final version to `.bip-history.json` as usual
- Also store the final text alongside the draft for comparison

In `.bip-history.json`, add field:
```json
{
  "date": "2026-04-20",
  "draft_file": "drafts/draft-2026-04-20-001.md",
  "draft_text": "original AI draft text...",
  "final_text": "user-edited final text...",
  "was_edited": true,
  "diff_processed": false
}
```

### Step 3: Diff analysis on next run

At the START of the next `make a bip post` run, Orchestrator checks:

```
1. Read .bip-history.json
2. Find entries where was_edited: true AND diff_processed: false
3. For each unprocessed edit:
   a. Compare draft_text vs final_text
   b. Extract patterns (see analysis prompt below)
   c. Write to changelog.md
   d. Mark diff_processed: true
```

### Step 4: Pattern extraction prompt

Use this prompt for the diff analysis (Orchestrator runs this internally):

```
Compare the AI draft and the user's final version below.

AI DRAFT:
{draft_text}

USER FINAL:
{final_text}

Extract specific patterns. For each change, categorize:

REMOVED — expressions the user deleted entirely
  format: "deleted expression" → never use this
  
REPLACED — expressions the user swapped
  format: "AI version" → "user version" (what this tells us)

SHORTENED — where the user cut length
  format: "original sentence" → "shortened version" (by ~X%)

ADDED — things the user inserted that weren't in the draft
  format: "added expression" → user tends to include this

STRUCTURAL — changes to post structure
  format: description of structural change

KEPT — what the user did NOT change (equally important)
  format: "kept expression" → this pattern works

Output as a changelog entry. Be specific. Quote exact text.
Do not generalize — every pattern must reference the actual words.
```

### Step 5: Write to changelog.md

Append to `voice/changelog.md`:

```markdown
## 2026-04-20 — post #3

### removed
- "excited to share" → never use (user deleted this opener)

### replaced  
- "built a system" → "got the thing working" (generic verb → casual specific)
- "productivity tool" → "thing for my ADHD brain" (formal → personal)

### shortened
- paragraph 2 cut from 3 sentences to 1 (user prefers shorter mid-sections)

### added
- trailing ",," at the end (signature pattern — already in profile)
- self-deprecating closing line (not in draft, user added)

### kept
- opening question hook (this format works)
- lowercase throughout (confirmed preference)

### meta
- edit intensity: moderate (3 replacements, 1 deletion, 1 addition)
- draft voice score was 34/40 — user edits suggest score should require 36+ for auto-publish confidence
```

### Step 6: Profile update suggestions

After 5+ changelog entries, Orchestrator proposes profile updates:

```
Trigger: changelog.md has 5+ unprocessed entries

Action:
1. Read all changelog entries
2. Find recurring patterns (appears 3+ times)
3. Propose additions to profile.md

Output to user:
"i've noticed some patterns from your edits:

  1. you always remove 'excited to share' type openers (5/5 posts)
  2. you shorten mid-section paragraphs by ~40% (4/5 posts)  
  3. you add self-deprecating closers when they're missing (3/5 posts)

  want me to add these to your voice profile? 
  they'll be checked in every future post."

User: "yes" / "yes to 1 and 3, not 2" / "no"

→ Update profile.md accordingly
→ Add to evaluator checklist (must-have / enhancer)
→ Mark changelog entries as processed
```

### Step 7: Update evaluator integration

When profile.md gets new patterns from user edits:

Add to the evaluator checklist section of profile.md:
```markdown
## evaluator checklist (updated via user edits)

### must-have (from edits — appeared 3+ times)
- [ ] no "excited to share" type openers
- [ ] mid-section paragraphs ≤ 2 sentences
- [ ] self-deprecating closer present

### learned preferences (from edits — appeared 2 times, monitoring)
- [ ] uses specific tool/feature names over generic descriptions
- [ ] prefers question-form hooks
```

Editor agent should read these and score against them.

---

## What NOT to do

- Don't auto-update profile without user approval
- Don't treat one-time edits as permanent patterns (need 3+ occurrences)
- Don't store the full post content in changelog — only the diff patterns
- Don't run diff analysis during the current session — do it at the START of the next session (keeps current session fast)
- Don't overwrite existing profile patterns — only ADD new ones from edits

---

## Testing plan

```
Test 1: Basic draft save
  - Run "make a bip post"
  - Check drafts/ folder has the file
  - Edit the post, say "done"
  - Check .bip-history.json has both draft and final text

Test 2: Diff analysis
  - Run "make a bip post" again
  - Check that previous edit was analyzed
  - Check changelog.md was created with correct patterns

Test 3: Accumulation
  - Do 5 posts with edits
  - Check that profile update suggestion appears
  - Approve some patterns
  - Check profile.md was updated

Test 4: Quality improvement
  - After profile update, generate new post
  - Compare: does the new post already include learned patterns?
  - Measure: did user edit less than before?
```

---

## Success metric

```
Post 1-3:  user edits ~60% of content
Post 4-7:  user edits ~30% of content  
Post 8-10: user edits ~10% of content
Post 15+:  user rarely edits — "it just sounds like me"

Track via: edit_intensity field in changelog
```
