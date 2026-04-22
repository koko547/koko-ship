# koko-ship

a Claude Code skill that generates build-in-public posts in your voice — not generic AI voice.

## who this is for

builders who ship with AI and want to talk about it without sounding like everyone else's ChatGPT.

## prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed and logged in (`claude` command works in your terminal)
- Claude Pro subscription or API access
- Python 3.8+ (optional — only needed for image generation features)

## install

```bash
git clone https://github.com/koko547/koko-ship.git
bash koko-ship/skill/install.sh
```

this copies the skill to `~/.claude/skills/koko-ship/`. you can delete the cloned repo after.

## usage

open Claude Code **in any project you're actively building** (not the koko-ship repo):

```bash
cd ~/my-actual-project
claude
```

then tell Claude what you want. these are **prompts to Claude**, not shell commands:

```
> set up my voice
```

walks you through a 2-minute voice setup. scans your past Claude conversations, optional questionnaire, optional paste samples. builds a profile at `~/.bip-voice.json`.

```
> make a bip post
```

reads your recent building sessions, picks a moment, drafts 3 versions internally, scores them, delivers the strongest one.

## the agent team

three agents work behind one command.

**writer** — reads your voice profile and recent sessions. drafts 3 versions. picks the strongest.

**editor** — scores voice accuracy and content quality. sends it back if something's off.

**QA** — catches jargon, repetition, sensitive info. platform-ready check.

## what it does

1. reads your recent Claude Code sessions for this project
2. extracts candidate moments (things that shipped, broke, or surprised you)
3. asks you to pick one moment
4. drafts 3 versions internally with different hooks
5. self-evaluates all 3 on hook / story / authenticity / relatability
6. delivers the strongest one
7. you edit, it learns from the diff for next time

## before / after

without koko-ship:

> Built a cool thing with Claude today! Excited to share my progress on the dashboard. Really loving how AI makes development faster. #buildinpublic #indiehackers

with koko-ship:

> two quality gates. same passing score. that's a bug.
>
> building a voice engine that writes posts in your voice. today i found the gate that picks the best draft and the gate that decides "ready to publish" were using the same threshold.
>
> "good enough to show you" ≠ "good enough to post."
>
> #koko-ship

## two quality gates

every post goes through two checks before you see it:

| gate | what it does | threshold |
|------|-------------|-----------|
| self-eval (1st) | picks best of 3 drafts | all axes ≥ 7/10 |
| evaluator (2nd) | publish decision | voice 32/40+, content 30/40+ |

## voice evolution

the system learns from your edits — every change you make teaches it.

1. AI draft saved before you see it
2. you edit however you want, say "done"
3. next run: diff analysis extracts patterns
4. after 5+ edits with recurring patterns: profile update suggested
5. you approve — voice profile updated
6. next post is sharper

target: post 1-3 you edit ~60%. post 8-10 ~10%. post 15+ you barely touch it.

## voice profile

your voice lives at `~/.bip-voice.json`. it's generated locally, never committed to any repo. stores how you write: tone, vocabulary, length, emoji usage, banned phrases. the profile sharpens over time as you edit posts.

## python dependencies (optional)

image generation and screenshot capture require Playwright:

```bash
pip install playwright && playwright install chromium
```

the core workflow (voice setup + post drafting) works without any Python dependencies.

## uninstall

```bash
rm -rf ~/.claude/skills/koko-ship
```

## license

MIT

---

made by [koko](https://x.com/ink_young_koko)
