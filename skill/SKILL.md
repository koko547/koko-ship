---
name: koko-ship
description: Generate build-in-public X (Twitter) posts from your current Claude Code session. Use whenever the user wants to share what they built today, create a BIP/build-in-public update, draft a tweet about coding progress, post about a feature they just shipped, summarize a session for social media, or generate dev content for X. Works for both developers and non-developers (vibe coders) — translates the session's intent, process, struggle, and outcome into a tweet that sounds like the user, not like a marketing intern.
---

# koko-ship — build-in-public post generator

Turn the current Claude Code session into a single, voice-aligned X post. Optionally render a card image to attach.

**Default behavior:** generate ONE strong single-tweet post with media suggestion. Threads only when the user explicitly asks. Never auto-publish.

## When to use this skill

Trigger on phrases like:
- "make a BIP post about today"
- "tweet about what we just built"
- "share this on X"
- "write a build-in-public update"
- "summarize today for twitter"
- "post about this"
- any request that maps a coding session → social content

## Two voice layers (read these before drafting)

This skill applies two layers:

1. **User-personal voice** — how the user actually writes
   - Read `references/voice-profile-default.json` (bundled generic fallback)
   - If `<cwd>/.bip-voice.json` exists, use it instead (project-local override)
   - If `~/.bip-voice.json` exists, use it (user-global override)
   - Profile priority: project-local > user-global > bundled default

2. **Writing principles** — what makes a BIP post work
   - See `references/writing-principles.md` — 5 principles, no rigid templates
   - Reference examples from real viral posts and top creators for inspiration

When the two layers conflict, **personal voice wins**. The principles are guidelines, not formulas.

## Step 0: Voice profile gate (ALWAYS runs first)

Before doing anything else, check if a voice profile exists in this priority order:

1. `<cwd>/.bip-voice.json` (project-local)
2. `~/.bip-voice.json` (user-global)
3. `references/voice-profile-default.json` (bundled generic)

**If #1 or #2 exists** → voice is set up. Proceed to Step 1.

**If only #3 exists (user has never set up their voice)** → enter **Voice Setup Mode** before generating anything. Do not skip.

Exact behavior:

> before i can generate posts that sound like you, i need a couple minutes to learn your voice.
>
> by default i'll learn from:
>
>   ✅ your past Claude Code conversations
>   (i'll only read your messages, not Claude's — and only to learn how you write)
>
> want to add more sources for stronger accuracy? (optional, pick any)
>   [ ] 1. quick questionnaire (2 min — 5 questions about your style)
>   [ ] 2. your X account (coming in v1.1)
>   [ ] 3. paste 3-5 of your own writings (posts, messages, anything you wrote)
>
> reply: 'go' to use defaults / add numbers like '1 and 3' / or 'skip' to use generic voice

**If user says "go"** → run `scripts/setup_voice_from_claude_logs.py` with no flags → saves `~/.bip-voice.json` → confirm what was found → proceed to Step 1.

**If user adds optional sources** → run the corresponding scripts:
  - `1` → walk through the 5 questions interactively (see `scripts/setup_voice_questionnaire.py --print-questions` for the exact questions). Collect answers. Run the script with `--answers-json`.
  - `2` → inform them this is coming in v1.1. Offer the other paths instead.
  - `3` → ask them to paste 3-5 samples of their own writing (tweets, messages, posts — anything that sounds like them). Collect the samples. Run `scripts/setup_voice_from_paste.py --samples-json`.

When multiple sources are selected, run all of them, then **merge** the results: use the Claude logs analysis as the base, then overlay any stronger signals from the other sources (e.g., if paste samples show consistent emoji usage that Claude logs don't, adopt the paste signal for emoji).

Save the merged profile to `~/.bip-voice.json`. Confirm to the user:

> ✓ voice profile built from [N sources].
> found [M] messages across [K] projects.
> your voice: [primary_lang], [casual/formal], [emoji_pct]% emoji, median [N] chars.
> top phrases: [list].
>
> now generating your post...

Then proceed to Step 1.

**If user says "skip"** → confirm once more:

> heads up — without a voice profile, posts will sound like generic AI, not like you.
> are you sure? (yes to continue with generic voice for this session, or 'set up' to start voice setup)

If confirmed → use bundled default profile for **this session only**. Next session, ask again. Never write anything to disk when skipped — the gate will trigger again next time.

**"set up my voice"** — at any time, in any session, the user can say this phrase to re-enter Voice Setup Mode and rebuild their voice profile from scratch.

---

## How to draft a post

Follow these steps in order. Skip steps that don't apply to the session.

### Step 0.5: Process previous edit diffs (runs before drafting)

Before generating anything, check if the user edited a previous post:

1. Read `<cwd>/.bip-history.json`
2. Find entries where `was_edited: true` AND `diff_processed: false`
3. For each unprocessed edit:
   a. Compare `draft_text` vs `final_text`
   b. Extract patterns using the diff analysis prompt in `references/voice-evolution-v2.md` → Step 4
   c. Categorize changes: REMOVED / REPLACED / SHORTENED / ADDED / STRUCTURAL / KEPT
   d. Append entry to `voice/changelog.md` with the diff patterns
   e. Set `diff_processed: true` in `.bip-history.json`
4. After 5+ changelog entries from edits, propose profile updates to the user (see `references/voice-evolution-v2.md` → Step 6). Only add to `voice/profile.md` with user approval. Require 3+ occurrences of a pattern before proposing.

If no unprocessed edits exist, skip to Step 1.

### Step 1: Detect project context

Determine the branded hashtag for the post:

1. Read `<cwd>/.bip-config.json` → `hashtag` field, if present
2. Else read `<cwd>/CLAUDE.md` for an explicit project name
3. Else read `<cwd>/package.json` → `name` field
4. Else use the basename of cwd
5. Format as `#<project-name>` (preserve hyphens, lowercase)

The branded hashtag goes on its own trailing line at the end of the post. Always exactly one. Never use generic hashtags like `#buildinpublic` `#indiehackers` `#vibecoding` — the voice profile bans them.

### Step 2: Load voice profile

Read the voice profile (priority order in section above). Pay attention to:
- `language.primary` — generate in this language
- `tone.do` and `tone.dont`
- `length.target_chars` and `length.optimal_lines`
- `personal_vocabulary.phrases_koko_uses` — borrow these naturally
- `personal_vocabulary.phrases_banned` — never use these
- `emoji.current_default` — usually "none"; only insert if the moment truly calls for it
- `hashtags.product_map` — may pre-define the hashtag for this project

### Step 3: Check history (avoid repetition)

If `<cwd>/.bip-history.json` exists, read it and:
- Note `context_lines_used` — you must write a **new** context line from a different angle (see writing-principles.md → CONTEXT LINE VARIATION)
- Note `topics_covered` — don't post about the same topic as a recent post
- Note hooks from the last 3 posts — vary the hook pattern
- If 5+ posts exist, apply the history variety principle (writing-principles.md #8)

### Step 4: Find and select building sessions

The skill reads past building sessions from this project, not just the current conversation. This is the core step.

#### Step 4.1: Load sessions from disk

Run the session reader to find recent building sessions for this project:

```bash
python3 "${SKILL_DIR}/scripts/read_project_sessions.py" --cwd "$(pwd)" --hours 24 --fallback-hours 168
```

This script:
- Finds the Claude project directory for the current cwd in `~/.claude/projects/`
- Reads all `.jsonl` session files
- Filters out trivial sessions (warmups, sub-agents, <3 user messages)
- Filters out koko-ship meta sessions (voice setup, skill install)
- Keeps everything else — including simple Q&A/conversations (those contain "why I wanted to build this" context for non-dev users)
- Returns sessions within the last 24 hours. If none found, expands to 7 days.

Parse the JSON output. Each session has: `session_id`, `file`, `started_at`, `ended_at`, `duration_minutes`, `n_user_messages`, `summary`, `key_actions`.

#### Step 4.2: Present sessions to user

**If 0 sessions found:**

> no recent building sessions found for this project (last 7 days). what's one thing you worked on recently that you'd want to share? describe the moment and i'll draft a post.

Wait for user's reply. Use their description as the single moment for Step 5+.

**If 1 session found:**

Read that session file fully, extract moments (see Step 4.3), then proceed. Note in output: `source: 1 session from [time ago]`.

**If 2+ sessions found:**

List them for the user, newest first, one-line summary each:

> found [N] recent building sessions:
>
> 1. [summary] ([time ago])
> 2. [summary] ([time ago])
> 3. [summary] ([time ago])
> ...
>
> which ones? (numbers, or 'all')

Wait for user's reply. They can select 1, multiple, or all. Read only the selected session file(s).

#### Step 4.3: Extract moments from selected session(s)

Now read the actual `.jsonl` file(s) the user selected. Your job is **not** to summarize the project — look at what happened in the selected session(s). Extract a list of **candidate moments**.

For each moment, extract TWO things: the **WHAT** (result) and the **WHY** (cause). A moment without a WHY is not ready for a post (see writing-principles.md #6 "WHY > WHAT").

**Outcome moments** (preferred):
- A shipped file, feature, or decision
- A specific number that came out of the session (count, time, money, percent)
- A struggle that got resolved
- A small detail the user explicitly noticed or cared about
- A specific exchange between user and Claude (user said X, Claude did Y, user adjusted with Z)

**No-outcome moments** (fallback when no outcomes):
- A named obstacle the user articulated
- An honest emotional beat the user expressed (doubt, fear, hesitation)
- A real question the user is sitting with

**For every moment, find the WHY. Search the session in this priority order:**

1. **User's own reaction** (most authentic) — look for the user expressing surprise, frustration, realization. Phrases like "아 왜 이러지?", "wait what", "oh that's why", "huh", or explicit diagnosis ("this is a bug", "i designed this wrong"). This is the best WHY source because it's the user's actual words.

2. **Claude's diagnosis** — look for Claude explaining what went wrong or why something happened. Technical explanations ("XP renders but never writes to the database"), root cause analysis, or debugging conclusions. Good WHY source but needs to be translated into the user's voice for the post.

3. **The fix / resolution** — look for what changed after the problem was identified. Code changes, design changes, the user asking Claude to fix it. The fix implies the WHY ("asked claude to wire the XP to the database" → implies it wasn't wired).

**Minimum: at least 1 WHY source must exist for a moment to be postable.** If you find a result (streak: 0) but no WHY in the session (no reaction, no diagnosis, no fix), the moment is incomplete — flag it to the user: "i see [result] but can't find why it happened in the session. what was the reason?"

**Always exclude as content sources:**
- CLAUDE.md, README, package.json descriptions — those describe the project, not the session
- Tool calls and tool results as standalone content — focus on what the user said and decided
- Boilerplate ("hi", "ok", "thanks")

#### Step 4.4: Moment selection (if multiple)

After extracting moments from the selected session(s):

**0 moments** → tell the user the selected sessions are mostly setup/boilerplate. Ask: "what's one specific thing from these sessions you'd want to share?"

**1 moment** → use it directly. Note: `picked: <moment summary>`.

**2-3 moments** → show numbered list, user picks.

**4+ moments** → ask: "big session — what felt the most surprising or hardest? we'll focus on that one thing."

**Never combine multiple moments into one post.** One post = one moment. If the user wants multiple posts, generate them as separate tweets.

#### Step 4.5: Moment quality gate

Before drafting, evaluate whether the selected moment is actually worth posting. Not every session produces a postable moment. Honest "nothing to post" is better than a weak post.

**Postable moments (proceed to Step 5):**
- New feature working (something that didn't exist before now does)
- Something broke and got fixed (struggle → resolution arc)
- Unexpected discovery (tried X, learned Y instead)
- Numbers changed (users, revenue, metrics, streak count, anything measurable)
- Lesson learned (specific, not generic — "learned that X" not "learned a lot")
- Real emotional beat (honest fear, doubt, surprise — not performed)
- A question whose answer would change what you build next

**NOT postable (tell the user, don't draft):**
- Config changes only (installed dependencies, set up env vars, renamed files)
- No meaningful progress from last post (same state, different day)
- Topic too similar to the last post in `.bip-history.json` (check `topics_covered`)
- Session is all boilerplate (Claude doing routine tasks, no user decisions or reactions)

**When not postable, be honest:**

> looked through the session. it's mostly [config / setup / routine work] — nothing that would make someone stop scrolling. keep building and trigger me when something breaks, ships, or surprises you.

This is not a failure. Most building days don't produce posts. Forcing a post from a thin session is how you get generic AI output.

**If the user disagrees** ("no, I want to post about this anyway") — respect it. They might see an angle you don't. Ask them what specifically they want to highlight, then draft from their direction.

#### For non-developer / vibe coder sessions

Lean heavily into the **conversation moments**: what exact words the user said to Claude, what came back, what the user asked Claude to change. That's the unique angle and the basis for the `ai_credit_story` template. Keep simple Q&A conversations — they contain the "why" context.

### Step 5: Apply security filter

Strip from the draft:
- API keys, secrets (`sk_…`, `pk_…`, `Bearer …`, `token=…`)
- DB connection strings, passwords, host:ports
- Internal URLs (`localhost:port`, `*.internal`, raw IPs)
- Other people's PII (emails, phone numbers, real names — the user themselves is fine)

Keep:
- Tech stack and tool names (Claude, Supabase, Vercel, Apify, etc.)
- Architecture and design decisions
- Trial-and-error process
- Error messages (with credentials masked)
- Screenshot/video guidance

### Step 6: Apply writing principles

Read `references/writing-principles.md`. There are no rigid templates — apply these 5 principles and let the post take whatever shape fits the moment:

1. **HOOK FIRST** — first line stops the scroll. Name/number/tension/surprise.
2. **CONTEXT FAST** — reader doesn't know this project. Tell them what it is within 1-2 lines after the hook. Don't skip context, don't dump features.
3. **ONE MOMENT** — one post = one thing that happened. Not a summary.
4. **SPECIFIC > CLEVER** — real numbers, real words, real names. Nothing generic.
5. **END WHEN IT LANDS** — punchline hits, stop. No explanation, no takeaway, no engagement question.

The reference examples in that file are for inspiration, not imitation. Don't copy shapes — absorb the energy.

**Voice profile still governs tone.** The principles define WHAT to write (structure). The voice profile defines HOW to write (tone, vocabulary, emoji, length, hashtags). When in doubt, voice wins.

### Step 7: Draft the post (write 3, pick 1)

Internally write THREE different drafts of the post. Do not show all three to the user — pick the strongest one and deliver only that.

**Why three:** The first draft is for structure. The second is for voice. The third is for polish. The best one is rarely the first.

**How to make them different:**
- Vary the hook (different first line each time — different angle on the same moment)
- Vary the length (one tight ~180 chars, one medium ~230, one full ~260)
- Vary the structure (one linear, one with a flip/contrast, one starting from the punchline)

**For each draft, apply:**
- The 5 writing principles from Step 6
- The voice profile (tone, vocabulary, length, emoji, hashtags)
- **Session quote injection:** if the user said something specific and memorable in the session (an exact phrase they typed to Claude, a reaction, a decision in their own words), try to include it verbatim in at least one draft. Quoted real words are the most authentic material available.
- **Imperfection:** don't make every line the same length or same weight. Let one line be unexpectedly short. Let a filler word ("honestly", "idk", "kinda") land naturally if it fits the user's voice. AI posts fail because they're too symmetrical.

**Then self-evaluate all three** (Step 7.5) and pick the one with the highest combined score. If two are close, pick the one that sounds more like a real person typed it on their phone.

### Step 7.5: Self-evaluation gate (REQUIRED before delivery)

**This is the 1st gate — candidate filter.** It picks the best draft of three. The evaluator agent (`.claude/agents/evaluate.md`) is the 2nd gate with stricter thresholds for the publish decision. This gate asks "is this good enough to show the user?" The evaluator asks "is this good enough to publish?"

Score ALL THREE drafts from Step 7 against the 4-axis rubric in `references/eval-rubric.md`. This is the single most important step in this skill — it is what separates koko-ship from generic AI output.

For each draft, score:

1. **Hook Strength** (1-10) — does the first line stop the scroll?
2. **Story** (1-10) — is there a real arc (outcome / articulation / emotional)?
3. **Authenticity** (1-10) — does it sound like a real person, not AI?
4. **Relatability** (1-10) — would a non-developer get the moment?

A 7 is the floor, not "pretty good." Don't inflate.

**Auto-fail triggers** (hard cap at 5, regardless of your subjective score):
- Hook capped at 5 if: first line is "built/made/created/launched [generic noun]" with no name, number, or tension
- Story capped at 5 if: post is a feature list (3+ nouns in parallel) or a project summary with no session moment
- Authenticity capped at 5 if: any banned phrase present, or every line is the same length/structure (too symmetrical)
- Any axis capped at 5 if: "would 100 other indie hackers say this?" test fails

**Specificity gate** (also required):
- Does the post contain at least 2 of: a concrete number, a user action verb, a small specific detail unique to this session?
- Is there exactly one moment (not a feature list / tagline)?

**Pick the winner:**
- Among drafts that pass all gates (all axes ≥ 7 + specificity pass), pick the one with the highest combined score
- If two are close, pick the one that sounds more human (less symmetrical, has a filler word or irregular beat)
- If ALL THREE fail → write 3 more (different hooks, different angles). You get 2 rounds total (6 drafts max)
- If all 6 fail → escalate to user:

> i drafted several versions and none passed my quality bar — they kept coming out [generic / vague / too AI-sounding]. can you tell me one specific moment? a phrase you said, a thing that broke, a small detail. just one.

Wait for their reply, then go back to Step 5 with the new input.

### Step 8: Deliver the draft

Output the post in this format:

```
POST (XXX chars)
---
[the post text]

METADATA
moment: <one-line description of the chosen moment>
session_source: <which session(s) this came from — time + summary>
hook: "<first line>"
length: <chars>
hashtag: <#tag>
media_suggestion: <video | screenshot | card_image | none + what to capture>

EVAL (self-scored)
hook: X/10  story: X/10  auth: X/10  relat: X/10
specificity_gate: PASS
attempts: N/3
```

Then tell the user:

> edit it however you want — every edit teaches me your voice better.
> when you're happy with it, say "done" or "ship it."

**Before showing the draft, save it** to `<cwd>/.bip-drafts/draft-<YYYY-MM-DD>-<seq>.md` with frontmatter:

```yaml
---
date: <YYYY-MM-DD>
seq: <NNN>
context: <session context summary>
source: <session log description>
evaluator_score:
  voice: <score>
  content: <score>
---
```

This saved draft is the baseline for diff analysis if the user edits before approving.

### Step 8.5: Capture & suggest media

For every post, try to auto-capture media from the project before falling back to suggestions.

**Step 8.5.1: Auto-detect capturable sources**

Run the capture script in detect mode:

```bash
python3 "${SKILL_DIR}/scripts/capture_screenshot.py" --detect --cwd "$(pwd)"
```

This returns: `urls` (running dev servers — always first priority), `html_files` (local HTML pages), `dev_command` (how to start the server).

**Step 8.5.2: Auto-capture if sources exist**

If the post is about a visual feature (dashboard, UI, page, component), and a capturable source exists:

**Always prefer live URL over static HTML file.** A running dev server renders the real UI with real data. A static HTML file may render without JS/data and look different from the actual product.

```bash
# From running dev server (PREFERRED — real UI with real data)
python3 "${SKILL_DIR}/scripts/capture_screenshot.py" --url http://localhost:3000 --out .bip-images/<slug>.png

# Short video with scroll
python3 "${SKILL_DIR}/scripts/capture_screenshot.py" --url http://localhost:3000 --video --duration 4 --out .bip-images/<slug>.webm

# From HTML file (FALLBACK — only if no server running)
python3 "${SKILL_DIR}/scripts/capture_screenshot.py" --file <html_path> --out .bip-images/<slug>.png
```

Tell the user what was captured and where it was saved. Show the image if possible.

**Step 8.5.3: Priority order (if auto-capture not possible)**

1. **Auto-captured screenshot/video** (from step above) — strongest, real product
2. **User's own screenshot** — ask them to capture something specific
3. **Generated card image** (Step 9) — stats/numbers visualization, fallback only
4. **None** — only if the post is purely a thought, not a build update

Be specific about WHAT to capture. Not "screenshot of result" but "screenshot of the dashboard showing the streak at 0 with boss HP bars visible."

**Step 8.5.4: Screenshot timing rule**

The screenshot must match the post's conclusion — never contradict it.

- Post ends with **resolution** ("wired the missing tool. now it works.") → screenshot shows the **working state** (proof it's fixed)
- Post ends with **the problem** ("zero tasks. ever. looked great tho.") → screenshot shows the **broken state** (if still visible). If already fixed → skip screenshot, go text-only. Don't show working when the post says broken.

**Step 8.5.5: No-UI projects (agent, CLI, backend, script)**

If the project has no web UI (no localhost, no HTML files):
- Default to **text-only post** (no media)
- If the user wants a screenshot, give them a **specific capture guide** based on the post content:
  - Tell them exactly what screen to open
  - Tell them what state to show (matching the post's conclusion — see timing rule)
  - Tell them what the visual punchline is ("the terminal showing 11 real tasks after it was showing 0")
  - Give the shortcut: `cmd+shift+4 → drag over the window`
  - Tell them to save to `.bip-images/` and give you the filename

Never say just "take a screenshot." Always say exactly what to capture, in what state, and why that specific frame supports the post.

### Step 9: (Optional) Generate a card image


If the user wants a card image — or if there's no other media available and the post has clear stats to feature — call the generator:

```bash
python3 "${SKILL_DIR}/scripts/generate_image.py" --slug <post-slug> --json '<json-payload>'
```

The script accepts a JSON payload like:

```json
{
  "label": "day 1 of koko-ship",
  "title": "voice profile, built from data",
  "subtitle": "fed viral patterns + my own writing into one ruleset",
  "stats": [
    {"num": "79", "label": "viral BIP posts", "detail": "filter: 500+ likes, last 6mo"},
    {"num": "8", "label": "of my own X posts", "detail": "@ink_young_koko"},
    {"num": "365", "label": "messages to claude", "detail": "from 4 personal projects"}
  ],
  "code_lines": [
    "{",
    "  \"language\": \"en\",",
    "  \"tone\": \"direct, lowercase\",",
    "  ...",
    "}"
  ],
  "footer_left": "build-in-public, day 1",
  "hashtag": "#koko-ship"
}
```

The script renders a 1600px @2x dark-mode PNG to `<cwd>/.bip-images/<slug>.png`. Tell the user where it landed.

### Step 10: Append to history (only after user approves the post)

If the user approves the post for publishing, update `<cwd>/.bip-history.json`:

1. Compare the approved post against the saved draft (from Step 8). Determine if the user edited it.
2. Append to `posts`:
```json
{
  "date": "<YYYY-MM-DD>",
  "type": "single",
  "topic": "<one-line summary>",
  "hook": "<first line>",
  "context_line": "<the one-line project context used in this post>",
  "text": "<full post>",
  "media": "<video|image|none>",
  "session_source": "<session id>",
  "engagement": null,
  "draft_file": "drafts/draft-<YYYY-MM-DD>-<seq>.md",
  "draft_text": "<original AI draft text>",
  "final_text": "<user-approved final text>",
  "was_edited": true | false,
  "diff_processed": false
}
```

3. Append the context line to `context_lines_used` (for future variation)
4. Append the topic to `topics_covered` (for future dedup)
5. Update `stats.total_posts` and `stats.last_post_date`

If the file doesn't exist, create it with the schema in `references/history-schema.json`.

**Voice evolution:** If `was_edited: true`, the diff will be analyzed at the start of the next session (Step 0.5). This keeps the current session fast — no analysis during the approval flow. See `references/voice-evolution-v2.md` for the full spec.

## Revision loop (after first draft)

After delivering the first draft, the user will often want changes. Treat their feedback as **plain natural language** — there is no fixed vocabulary. Parse the intent and rewrite. Examples of the kinds of things users will say (do not require these exact words — accept any phrasing):

- "tighter", "shorter", "cut to ~220", "trim line 3"
- "more casual", "less hype", "sounds too AI", "more like me"
- "try a different template", "use the underdog one", "show me all 5"
- "different hook", "swap line 2 and 4", "merge the last two lines"
- "add the part about scraping 1500 first", "remove the marketing intern bit"
- "replace 'kinda works' with 'just shipped'"
- "no hashtag this time", "render the card image"

The user might also paste their **own edited version** of the post and ask you to save it. In that case, validate it against the voice profile (lengths, banned phrases, hashtag rule) and either save it as-is or flag any rule violations and ask before saving.

After every revision:

1. Re-check voice compliance (length, banned phrases, hashtag rule, structure)
2. Output the new version in the same POST/METADATA format
3. Briefly note what changed (one line, e.g. "tightened to 218 chars, swapped to underdog_flex template")
4. Ask if more revisions are needed or if the user wants to ship it

**Approval signals** (any of these means save to history): "go", "ship it", "good", "save this", "yes", "looks good". Approval saves to `.bip-history.json`. **Approval never publishes** — koko-ship drafts only, never auto-posts.

**Discard signals**: "discard", "scrap it", "start over", "different angle". On discard, draft a fresh post (different template if possible) without saving the previous one.

## Template selection — auto, but user can override

By default you pick the template based on the session shape (see Step 6 + `references/templates.md`) and rotate based on history. **Always state which template you picked and why** in one line, so the user can intervene before approving.

The user can override at any time, in any phrasing:

- Pre-trigger: "make a BIP post about today using ai_credit_story"
- Post-draft: "try underdog_flex instead", "use a different template", "this should be a process_day_n"
- Comparison: "show me 3 variants in different templates", "give me a four_line and an underdog version side by side"

When the user asks for multiple variants, output them in the same response with a short label per variant (`### variant 1 — four_line_minimalist` etc.) and let them pick.

## Output format example

When the skill triggers, your response to the user should look like:

> Read your session and drafted a post. Detected project: `koko-ship` → tag `#koko-ship`. Last 3 posts used story types `[process, shipped, lesson]` so I picked `four_line_minimalist`.
>
> ```
> POST (242 chars)
> ---
> 79 viral BIP posts (500+ likes, last 6 months).
> 8 of my own X posts.
> 365 of my messages to claude.
>
> fed it all into a voice profile so AI writes posts that sound like me, not a marketing intern.
>
> day 1 of koko-ship. just testing, kinda works.
>
> #koko-ship
> ```
>
> **Media suggestion:** screen recording of the terminal output showing the analysis numbers, OR a generated card image (want me to render it?).
>
> Want me to tweak the tone, try a different template, or render the image?

## Things NOT to do

- Don't auto-publish anywhere. This skill drafts only.
- Don't generate threads unless the user explicitly asks. Single tweet wins (73% of viral BIP posts are single).
- Don't use generic hashtags (`#buildinpublic`, `#indiehackers`, etc.). The voice profile bans them.
- Don't pad to 280 chars. Tight beats are better than full lines.
- Don't use marketing voice ("excited to announce", "thrilled to share", "proud to introduce").
- Don't fish for engagement with questions to the audience ("what do you think?").
- Don't insert emoji as decoration. Default is zero. Only when the moment genuinely calls for one.

## File locations summary

| File | Purpose | Required |
|---|---|---|
| `references/voice-profile-default.json` | Bundled generic fallback voice profile | yes |
| `references/writing-principles.md` | 5 writing principles + reference examples | yes |
| `references/eval-rubric.md` | Canonical 4-axis quality rubric for self-eval | yes |
| `references/history-schema.json` | Schema for `.bip-history.json` | yes |
| `references/voice-evolution-v2.md` | Voice evolution spec — diff analysis + learning loop | yes |
| `scripts/generate_image.py` | Render a card PNG from a JSON payload | yes |
| `<cwd>/.bip-voice.json` | Project-local voice override | optional |
| `<cwd>/.bip-config.json` | Project-local config (hashtag etc.) | optional |
| `<cwd>/.bip-history.json` | Per-project post history + edit diffs | created on first approval |
| `<cwd>/.bip-drafts/` | Saved AI drafts for diff comparison | created on first draft |
| `~/.bip-voice.json` | User-global voice override | optional |

## Cardinal rules (these never bend)

1. **No project-summary posts.** CLAUDE.md and README describe the project, not the session. Never use them as content sources.
2. **One moment per post.** Never combine. If multiple moments exist, ask the user to pick.
3. **Self-eval gate is required.** No draft is delivered without passing the 4-axis rubric and specificity gate.
4. **Generic output is failure.** If you can't produce a post that passes the gates in 3 attempts, ask the user for a specific moment instead of delivering anything weak.
5. **Drafts only, never auto-publish.** This skill creates drafts. Publishing is always a separate, explicit human action.
6. **Branded hashtag only.** Never use generic hashtags. One per post, trailing line.
