# koko-ship

AI made building easy. it made marketing boring.

a voice agent that learns how you write and generates build-in-public posts that sound like you, not like everyone else's AI.

---

## what this is

koko-ship reads your past building sessions, extracts the one moment worth sharing, and drafts a post in your voice. it scores every draft on voice accuracy and content quality before showing it to you. when you edit a draft, it learns from the diff — so each post gets sharper.

not a template. not a prompt wrapper. a voice engine that compounds.

## quick start

### 1. clone

```bash
git clone https://github.com/koko547/koko-ship.git
cd koko-ship
```

### 2. install the skill

```bash
bash skill/install.sh
```

this creates a symlink in `~/.claude/skills/` so Claude Code can find it.

### 3. set up your voice

open any project in Claude Code and say:

```
set up my voice
```

the skill walks you through it. options:
- **default:** scans your past Claude Code conversations (reads your messages only)
- **questionnaire:** 5 quick questions about how you write
- **paste samples:** drop in 3-5 things you've written (tweets, messages, notes)

takes ~2 minutes. builds a voice profile at `~/.bip-voice.json`.

### 4. make your first post

in any project directory:

```
make a bip post
```

the skill reads your recent building sessions, picks a moment, drafts 3 versions internally, scores them, and delivers the strongest one.

## how it works

```
"make a bip post"
    → reads past sessions (24h, fallback 7d)
    → extracts candidate moments
    → you pick one (or it picks if there's only one)
    → drafts 3 versions with different hooks
    → self-evaluates all 3 (hook / story / authenticity / relatability)
    → delivers the winner
    → you edit → say "done"
    → diff saved → patterns extracted next run
    → voice profile sharpens over time
```

**two quality gates:**

| gate | what it checks | threshold |
|------|---------------|-----------|
| self-eval (1st) | picks best of 3 drafts | all axes ≥ 7/10 (28/40) |
| evaluator (2nd) | publish decision | voice 32/40+, content 30/40+ |

## voice evolution

the system learns from your edits — every change you make teaches it.

1. AI draft saved before you see it
2. you edit however you want, say "done"
3. next run: diff analysis extracts patterns (removed / replaced / shortened / added / kept)
4. `changelog.md` accumulates learnings
5. after 5+ entries with recurring patterns: profile update suggested
6. you approve — evaluator checklist updated
7. next post is sharper

target: post 1-3 you edit ~60%. post 8-10 you edit ~10%. post 15+ it just sounds like you.

## file structure

```
skill/
├── SKILL.md                  — main instructions (~600 lines)
├── install.sh                — symlink installer
├── scripts/                  — voice setup, session reader, capture, image gen
└── references/               — writing principles, eval rubric, voice evolution spec

~/.bip-voice.json             — your voice profile (generated locally)

<your-project>/
├── .bip-history.json         — post history + edit diffs
└── .bip-drafts/              — AI originals for diff comparison
```

voice data is gitignored. it's personal. you generate it locally.

## the voice engine

**profile.md** — how you write. signature patterns, sentence rhythm, vocabulary, emotional expression. the evaluator's primary reference.

**patterns.md** — how you think. problem approach, reaction style, framing habits, values. drives content angle selection.

**marketing-voice.md** — the publishable filter. what transfers to public posts, what stays private, post characteristics, worked examples.

**changelog.md** — voice evolution tracker. every update logged with what changed, why, and which patterns were affected.

## writing principles

no rigid templates. 5 principles that let each post take its own shape:

1. **hook first** — first line stops the scroll
2. **context fast** — reader knows what this project is within 2 lines
3. **one moment** — one post = one thing that happened
4. **specific > clever** — real numbers, real words, real names
5. **end when it lands** — punchline hits, stop

plus: WHY > WHAT, quote the session, imperfection is authenticity, history variety.

## requirements

- Claude Code (CLI, desktop app, or VS Code extension)
- Claude Pro subscription or API access
- works with Opus and Sonnet

## faq

**"how is this different from prompting ChatGPT to write like me?"**

chatgpt matches surface patterns. koko-ship extracts deeper signals — sentence rhythm, humor timing, how you handle emotion, what you'd never say. and it has an evaluator that catches when patterns feel forced.

**"what data do you need?"**

only what you give it — writing samples, session logs, past posts. nothing leaves your machine except API calls to generate content.

**"does it get better over time?"**

yes. every edit you make teaches the system. by post 10, you'll edit less. by post 15, it just sounds like you.

**"can I use this outside Claude Code?"**

the skill files are .md — they work in any Claude project, or any agent that reads markdown instructions.

**"what if I have no session logs?"**

the skill asks you what you worked on. describe a moment and it drafts from there. paste samples and the questionnaire work too.

## license

MIT

---

made by [koko](https://x.com/ink_young_koko) — building this in public.
