# koko-ship

a content engine that writes in your voice — not generic AI tone.

## the difference

every AI content tool sounds the same. koko-ship sounds like you.

**without koko-ship:**
> Built a cool thing with Claude today! Excited to share my progress on the dashboard. Really loving how AI makes development faster. #buildinpublic

**with koko-ship:**
> two validation checks. same threshold. that's a bug.
>
> the check that picks the best draft and the check that decides
> "ready to publish" were using the same score.
>
> "good enough to show you" ≠ "good enough to post."

## how it works

```
Your real writing ──→ Voice Profile (4 files, 20+ signals)
                           │
                    ┌──────┴──────┐
                    │   Writer    │  reads sessions, drafts 3 versions
                    └──────┬──────┘
                    ┌──────┴──────┐
                    │   Editor    │  scores against your voice profile
                    └──────┬──────┘
                    ┌──────┴──────┐
                    │     QA      │  catches leaks, jargon, platform issues
                    └──────┬──────┘
                           │
                    Best draft ──→ You
                           │
                    Your edits ──→ Voice Evolution
                           │         (learns from every edit)
                           ↓
                    Next post is sharper
```

## your voice profile

koko-ship doesn't ask you to "describe your brand tone." it reads how you actually write and extracts patterns into 4 files:

```
voice/
├── profile.md          what you sound like (evaluator checklist)
├── patterns.md         how you think (deep layer)
├── marketing-voice.md  what's publishable (public filter)
└── changelog.md        how your voice evolves over time
```

every post is checked against your profile. if it doesn't sound like you, it gets rewritten before you see it.

## get started

**path 1: take the quiz (recommended)**
1. go to [koko-ship.com](https://koko-ship.com) and take the voice quiz
2. download your `voice.md` file
3. open Claude Code in your project and say "use this as my voice profile"
4. koko-ship expands it into your full voice profile
5. say "make a bip post"

**path 2: set up from scratch**
1. install koko-ship (see below)
2. open Claude Code in your project
3. say "set up my voice"
4. koko-ship scans your Claude Code sessions, or you paste writing samples, or answer 5 questions
5. say "make a bip post"

## install

```
git clone https://github.com/koko547/koko-ship.git
bash koko-ship/install.sh
```

## usage

```
> set up my voice              ← first time (or "use this as my voice profile" with quiz file)
> make a bip post              ← generate a post from your recent sessions
> I want to sound more casual  ← update your voice profile directly
```

## two quality gates

| gate | what it checks | threshold |
|------|---------------|-----------|
| editor | voice accuracy + content quality | voice 32/40+, content axes ≥ 7/10 |
| QA | security, jargon, platform rules | clean pass required |

if both fail 3 times → asks you for a specific moment instead of delivering weak content.

## voice evolution

your voice profile gets sharper two ways:

**from your edits:** every time you edit an AI draft and say "ship it," koko-ship captures the diff. after 3+ recurring patterns, it suggests profile updates. you approve what sticks.

**from your direction:** tell koko-ship how you want to sound. "stop using parenthetical asides." "I want shorter posts." "more self-deprecating humor." it updates your profile immediately and logs the change.

## the skill suite

```
skills/
├── voice-setup/    creates your voice profile (quiz import or from scratch)
├── writer/         the main content engine
├── editor/         internal — scores voice + content quality
└── qa/             internal — security, jargon, platform checks
```

## prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (`claude` command works)
- Claude Pro or API access

## examples

- [`examples/session-to-post.md`](examples/session-to-post.md) — full pipeline walkthrough

## before / after

**without:**
> Launched a new feature for our project management tool today. Dark mode is now available for all users.

**with koko-ship:**
> shipped dark mode at 2am because i couldn't stop staring at my own white screen. turns out 47% of our users had the same complaint. sometimes the best product decisions start with your own eyeballs hurting.

---

**without:**
> Released an update to our API documentation with improved error handling.

**with koko-ship:**
> broke the API. again. third time this month. but this time i actually wrote down what went wrong before fixing it. the doc is better than the code now. not sure if that's a win.

## uninstall

```
rm -rf ~/.claude/skills/koko-ship-writer
rm -rf ~/.claude/skills/koko-ship-editor
rm -rf ~/.claude/skills/koko-ship-qa
rm -rf ~/.claude/skills/koko-ship-voice-setup
rm -rf ~/.claude/skills/koko-ship-shared
```

## license

MIT

---

made by [koko](https://x.com/ink_young_koko)
