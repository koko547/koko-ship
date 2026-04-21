# koko-ship — voice agent for marketing

A voice agent that learns how someone writes, understands what they're building, and generates build-in-public posts in their voice. Target: indie hackers and vibe coders who built something but are lost in the marketing phase.

**The first user (inkyungko) tests quality here. The format is designed to work for any user.**

**Everything in this project exists to answer one question:**
> "Does this post sound like this specific person?"

---

## Hot cache (update every session)

- **Currently building:** koko-ship voice agent for marketing
- **Current stage:** voice profile format redesigned, project consolidated, next is auto-generation pipeline
- **Current tone:** direct, asks lots of questions, mixes Korean and English, hates bullshit, focuses on essence over polish
- **Recent focus:** voice quality on first use — can a new user's first post sound like them?
- **Last updated:** 2026-04-18

→ Weight recent data (1-2 weeks) heavier than older data. Voice NOW matters more than voice 6 months ago.

If the hot cache is 3+ days stale, ask: "anything new?"

---

## Project structure

```
koko-ship-demo/
├── CLAUDE.md                ← this file. Project schema.
├── build-log.md             ← full build history
├── index.md                 ← content catalog
├── log.md                   ← chronological activity log
│
├── voice/                   ← voice profile (4 files, universal format)
│   ├── profile.md           ← how this person writes + evaluator checklist
│   ├── patterns.md          ← how this person thinks (deep layer)
│   ├── marketing-voice.md   ← publishable filter + post characteristics
│   └── changelog.md         ← voice evolution tracker
│
├── raw/                     ← immutable voice source material
│
├── skill/                   ← the koko-ship Claude Code skill
│   ├── SKILL.md             ← skill instructions (~600 lines)
│   ├── install.sh           ← symlink installer
│   ├── scripts/             ← voice setup, session reader, capture, image gen
│   └── references/          ← writing principles, eval rubric, defaults, voice-evolution-v2
│
├── research/                ← data that informed the voice + skill design
│   ├── bip-tweets-*.json    ← viral BIP tweet corpus (79 viral, 500+ likes)
│   ├── koko-*.json          ← Koko's X posts + Claude conversation corpus
│   ├── voice-pattern-analysis.json
│   ├── creators/            ← FarzaTV, levelsio, dannypostma, thejustinwelsh
│   └── post-images/
│
└── .claude/
    └── agents/
        └── evaluate.md      ← evaluator agent v2 (voice accuracy + content quality)
```

---

## Core mechanism

The voice engine is invisible infrastructure that does three things:

1. **Collects raw signals** from multiple sources — writing samples, social posts, Claude Code conversations, questionnaire answers, anything the user has written. These go into `raw/` (immutable, read-only) or arrive via connected accounts.
2. **Extracts and compounds** voice signals into a living profile. Every new source sharpens the profile — it never rebuilds from scratch. Signals are: how they think, how they express, what patterns they repeat, what they'd never say. This produces the four `voice/` files.
3. **Gets sharper over time** without the user doing anything extra. First post uses whatever data is available. By post 10, the voice is distinct. The profile is a living document, not a snapshot.

For Koko (first user): raw sources are manually added to the vault, LLM extracts and curates.
For other users: connected accounts + questionnaire feed in automatically, `~/.koko-ship/` holds their profile invisibly. They never manage the voice engine — they just build, and the voice compounds from how they already work.

**The voice profile is the product's core asset.** The skill generates posts. The evaluator checks quality. But the voice profile is what makes output sound like a specific person instead of generic AI.

---

## Layers

1. **Voice profile** → `voice/` — four files in universal format. Works for any user. The evaluator and skill both read from here. This is the output of the compound process.
2. **Raw sources** → `raw/` — immutable. Notes, memos, chat logs, project docs. Read-only. Voice signals are extracted from here into `voice/`. This is the input to the compound process.
3. **Skill** → `skill/` — the Claude Code skill that generates BIP posts. Reads `voice/` at generation time.
4. **Evaluator** → `.claude/agents/evaluate.md` — scores output on voice accuracy (does it sound like them?) and content quality (is it a good post?). Loads checkable patterns from `voice/profile.md` at runtime.
5. **Research** → `research/` — data corpus that informed the skill design. Not read at generation time.
6. **Schema** → this file (`CLAUDE.md`). Co-evolved with the user.

---

## The `/voice/` directory (four files, universal format)

These four files are the voice engine's core. They work for any person — the structure is universal, the content is unique to each user.

For Koko (first user): manually curated from raw sources in this vault.
For other users: auto-generated from connected accounts + questionnaire + Claude logs.

Always maintain all four files. Compound them — don't rebuild from scratch.

### `voice/profile.md` — how this person writes (current snapshot)

The evaluator's primary reference. Everything checkable lives here.

- **Signature patterns** — named, with examples, frequency, context, and force risk
- **Sentence rhythm** — how their sentences flow
- **Vocabulary markers** — current domain terms, filler words, phrases they reach for
- **Emotional expression** — how they show excitement, frustration, humor, doubt
- **Mode-locking** — register table (which tics belong to which context)
- **Anti-patterns (not-me list)** — expressions that auto-fail if present
- **Evaluator checklist** — must-have / enhancers / never-use, loaded by evaluator at runtime

### `voice/patterns.md` — how this person thinks (deep layer)

Not for direct pattern checking — for content angle selection and framing decisions.

- **Problem approach** — people-first? system-first? numbers-first?
- **Reaction style** — how they handle success, failure, surprise
- **What excites / frustrates them** — energy signals
- **Framing style** — metaphors, binaries, questions, stories
- **What they skip** — reveals expertise and identity
- **Values that surface in writing** — observed, not stated

### `voice/marketing-voice.md` — the publishable filter

What works for public content. Generation-time reference for tone calibration.

- **Public register** — which voice elements transfer to public posts
- **Keep private** — what's too intimate, raw, or risky for public
- **Post characteristics** — opener style, closer style, length, structure, media philosophy
- **Content angles** — what this person would naturally share, what they'd avoid
- **Worked examples** — on-voice and off-voice examples with annotation

### `voice/changelog.md` — voice evolution tracker

- Date + what changed + what triggered the change + which patterns affected
- Every `/voice/` update MUST be logged here. No silent changes.

---

## Evaluator agent

Lives at `.claude/agents/evaluate.md`. Two-level scoring:

**Level 1 — Voice Accuracy (/40):** Distinctiveness, Pattern fidelity, Naturalness, Consistency, Not-me count.
Pattern fidelity checklist is loaded from `voice/profile.md` → Evaluator checklist section at runtime.

**Level 2 — Content Quality (/40):** Hook, Story arc, Authenticity, Relatability.

Pass: both levels pass. Needs work: auto-fix up to 3 attempts. Fail: escalate to human.

The evaluator calibrates through use — Phase A on Koko's voice, Phase B on other voices.

---

## Ingest rules

1. **Every new raw data ingested → update all four `/voice/` files.** Compound, don't rebuild from scratch.
2. **Hot cache stale 3+ days → ask "anything new?"**
3. **Separate "how I talk to AI" from "how I talk to people."**
   - Marketing voice = people-facing side.
   - AI-facing data = thinking patterns, problem-framing.
   - Both useful, differently.
4. **Don't over-polish.** Messy writing, mixed languages, fragments — that's all data. Capture as-is.
5. **When ingesting, focus on extracting voice signals:**
   - NOT "what did this person write about" (content)
   - YES "how does this person write" (style, tone, patterns)
6. **`changelog.md` must be updated with every `/voice/` update.** Every evolution logged with date, what changed, what triggered it, which patterns affected.

---

## Operations

### Ingest
User drops a new source into `raw/` and asks to process it. Flow:
1. Read the source.
2. Discuss key voice signals with the user (not content — style/tone/patterns).
3. Write a short summary page in `raw/summaries/` if useful.
4. Update all four `voice/` files with the new signals.
5. Append an entry to `voice/changelog.md`.
6. Append an entry to `log.md`.
7. Update `index.md` if new pages were created.

### Query
User asks a voice question ("how would I tweet about X?", "rewrite this in my voice"). Flow:
1. Read relevant `voice/` pages.
2. Synthesize answer grounded in the voice files.
3. If the answer is valuable and reusable, file it back into the voice files.

### Evaluate
After any post is generated (by skill or manually):
1. Evaluator agent loads `voice/profile.md` → Evaluator checklist.
2. Scores on Voice Accuracy (/40) + Content Quality (/40).
3. Pass → ready for human review. Needs work → auto-fix (3 attempts). Fail → escalate.

### Lint
Periodically health-check:
- contradictions between voice files
- stale claims superseded by newer data
- orphan pages
- voice signals mentioned but not yet codified
- evaluator checklist items that are never present or always forced

---

## Indexing and logging

- **`index.md`** — content-oriented catalog. Every page: link + one-line summary. Updated on every ingest.
- **`log.md`** — chronological, append-only. Entry format: `## [YYYY-MM-DD] <op> | <title>` so it stays greppable.
- **`build-log.md`** — full build history of the koko-ship product (research, decisions, test cycles).

---

## Conventions

- Wiki is a flat markdown vault. Use `[[wikilinks]]` for cross-references (Obsidian-native).
- Keep pages short and linkable rather than long and monolithic.
- Use YAML frontmatter on voice pages (updated date, source count).
- Favor recent data. When old and new conflict, flag it in `changelog.md` and prefer new.
- Voice files use a universal format — same structure works for any user, not just Koko.

---

## Current plan

**Phase 1 (now): Voice quality on first use.**
- ✅ Voice profile format redesigned (identity → expression → formatting, evaluator-checkable)
- ✅ Project consolidated (vault + skill + evaluator + research in one repo)
- Next: auto-generation pipeline (questionnaire + connected accounts + Claude logs → 4 voice files)
- Next: update skill to read new voice format
- Next: test with 2-3 real indie hackers

**Phase 2: Content quality.**
- Conversational content extraction ("what did you ship today?" + session evidence)
- Evaluator calibration on Koko's voice, then other voices

**Phase 3: Ship to others.**
- Zero-config voice setup for new users
- `~/.koko-ship/` as invisible vault for each user

**Phase 4: Media + expansion.**
- Auto-capture, screen recording, multi-language
