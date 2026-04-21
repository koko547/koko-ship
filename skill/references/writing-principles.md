# koko-ship writing principles

5 principles for drafting build-in-public posts. These replace rigid templates — apply the principles freely and let the post take whatever shape fits the moment.

---

## 1. HOOK FIRST

The first line is everything. If it doesn't stop the scroll, nothing else matters.

**What works as a hook:**
- A specific name: "i built this thing called phoenix mode."
- A number: "checked my streak. 0."
- Tension/surprise: "most trackers punish you for breaking a streak."
- A confession: "honest moment."
- A strong observation: "half my replies are AI generated now."

**What doesn't work:**
- Generic description: "built a personal OS with claude."
- Announcement: "excited to announce..."
- Vague: "working on something cool."

The test: would you stop scrolling if someone else posted this first line? If no, rewrite the hook before anything else.

---

## 2. CONTEXT FAST

The reader doesn't know this project. After the hook, tell them what this is within 1-2 lines. Don't make them guess.

**How to give context without killing the pace:**
- Name + one-line description: "it's an AI teacher that lives next to your cursor."
- Action + context in one beat: "building a gamified system for my adhd brain."
- Let the detail do the work: "when you break a streak, most apps punish you. mine gives you 3 days of 2x xp instead."

**Don't:**
- Skip context entirely — unless your audience already knows the project (they probably don't yet).
- Use two "built" lines back to back ("built X. built Y for Z.") — merge what was built + why into one line: "built [thing] for [purpose]."

**Short beat lists are OK for context** — "8-bit dashboard. boss HP. XP. streaks." works as a rhythmic description after the hook. This is different from a feature-list tagline: beats serve the story, taglines replace it.

If the project or feature has a memorable name (phoenix mode, clicky, freewrite), lead with it. Named things are 10x more shareable than described things.

---

## CONTEXT LINE VARIATION

Every post needs a one-line project context — because any post could be the first one someone sees. But never repeat the same context line across posts.

**How it works:**
- Before drafting, read `.bip-history.json` → `context_lines_used`
- Write a new context line from a different angle than all previous ones
- After the user approves, save the new line to `context_lines_used`

**Same project, different angles:**
```
post 1: "built a gamified personal OS with claude"
post 2: "building a system where breaking a streak gives you 2x xp"
post 3: "my adhd brain needed a game, not a tracker"
post 4: "personal OS with boss HP, XP, and a voice agent you wake with 'hey jarvis'"
post 5: "trying to make my todo list feel like a video game"
```

Each line describes the same project but from a different entry point. A new reader gets enough context from any single post. A repeat reader never sees the same intro twice.

**If you run out of angles** (rare — most projects have 10+ angles): reframe around the current moment instead of the project. "the thing about gamifying your own life is..." — context becomes implicit.

---

## 3. ONE MOMENT

One post = one thing that happened. Not a summary. Not a feature tour. One moment from the actual session.

A moment is:
- A decision you made ("decided to drop hashtags entirely after seeing the data")
- A thing that broke ("checked my streak. 0. nothing was actually connected.")
- An exchange with AI ("told claude to make it sound like me, not a marketing intern")
- A small specific detail ("stared at my own work for an hour wondering if it matters")
- A number that surprised you ("scraped 1500 tweets, only 79 had 500+ likes")
- A question you're genuinely sitting with ("do you write your own marketing or use AI?")

If you have multiple moments, pick one. The rest become tomorrow's posts.

---

## 4. SPECIFIC > CLEVER

Every word should be load-bearing. If a detail is generic, replace it with something only you would say.

**Specific:**
- "checked my streak after 2 days of work. 0."
- "scraped 79 viral tweets (500+ likes, last 6 months)"
- "told claude 'make it sound like me, not a marketing intern'"

**Generic (anyone could say this):**
- "worked really hard on this"
- "built something cool with AI"
- "excited about the progress"

**The test:** could 100 other indie hackers post this exact line without changing a word? If yes, it's generic. Replace with your actual number, your actual name, your actual words.

Real numbers > round numbers. Real words you said > polished summaries. Messy specifics > clean generalities.

**Jargon rule:** The target audience includes non-developers. Never use developer terms without replacing them with plain language. Don't explain jargon — replace it entirely. The reader should never need to google a word.

- "database" → "the actual data" or "where things are saved"
- "0 rows" → "nothing was actually there" or "completely empty"
- "API" → "the connection" or just describe what happened
- "deployed" → "went live" or "shipped"
- "the agent" → describe what it does: "my AI assistant" or "the system I built"

If a technical detail IS the story (e.g., a specific bug), describe the effect, not the mechanism. "XP rendered but never saved to the database" → "the screen showed XP going up but none of it was real."

---

## 5. END WHEN IT LANDS

When the punchline hits, stop. Don't explain it. Don't add a takeaway. Don't ask a question.

**Good endings:**
- "looked great tho."
- "kinda works."
- "still figuring out the exit."
- "not rhetorical. genuinely curious."

**Bad endings (explaining the joke):**
- "and that's why I think X is important for Y."
- "lesson learned: always test your assumptions."
- "what do you think? let me know in the comments."

The reader should close the post with a feeling, not a lecture.

---

## Reference examples

These are real posts that worked. They're here for inspiration, not imitation. Don't copy the shape — absorb the energy.

### "I built this thing called [Name]" — @FarzaTV, 15,085♥
```
I built this thing called Clicky.

It's an AI teacher that lives as a buddy next to your cursor.

It can see your screen, talk to you, and even point at stuff,
kinda like having a real teacher next to you.

I've been using it the past few days to learn Davinci Resolve, 10/10.
```
Why it works: named product, instant context, personal use case, specific detail (Davinci Resolve), casual closer (10/10).

### "After [time], solo dev [emotion + number]" — viral corpus, 35,342♥
```
After 4 years of work, solo dev Cakez breaks down in tears
after opening Steam and learning his game
made $250,000 in a week.
```
Why it works: time investment stakes, named person, specific dollar amount, raw emotion.

### "Got laid off. Built instead." — viral corpus, 3,331♥
```
Got laid off.
Built a game instead.

Solo dev.
$0 budget.

11,000 wishlists in under 2 months.
```
Why it works: constraint stacking, each line is one beat, number payoff at the end, no explanation.

### short observation — @levelsio, 1,529♥
```
To prove my friend @StevieZollo you don't need an idea, or even
a lot of time these days to ship a little app that might make money

I took the top idea from [site], mass generated 2000 apps,
and mass submitted them all to the App Store
```
Why it works: contrarian premise, specific action, specific number, no moral at the end.

### vulnerability — @dannypostma, 797♥
```
Felt very anxious for a while.
```
Why it works: 5 words. No explanation. No "but then I realized..." The rawness IS the post. (Note: this only works when it's real and when the audience already has some context.)

### introducing with name — @FarzaTV, 10,572♥
```
introducing freewrite.

a mac app i made for myself.

one simple, clean place to write without distraction.

all in native swift.
no subscription.
all local. free. enjoy.
```
Why it works: named product, "for myself" framing, constraint stacking (native swift, no subscription, local, free), ends on "enjoy" — mic drop.

---

## What NOT to do (anti-patterns)

These patterns consistently fail in the viral data and in the eval rubric:

1. **Feature-list post** — three or more nouns in parallel ("dashboard. HP. XP. streaks. voice agent.") as the bulk of the post. A feature list is a product page, not a story.

2. **"Built X for Y" as the entire hook** — no tension, no name, no number. Any indie hacker could say it.

3. **Explaining your own joke** — "and that's why I think..." after a punchline kills the energy.

4. **Engagement bait questions** — "what do you think?" "who else feels this way?" — the voice profile bans these.

5. **Marketing voice** — "excited to announce", "thrilled to share", "proud to introduce" — auto-fail on Authenticity.

6. **Summary without moment** — describing the project without a single thing that happened in a session. This is the #1 failure mode. CLAUDE.md is not content.

---

---

## 6. WHY > WHAT

A result without a reason is an impression, not a story. Every time you show a result ("streak: 0"), you must follow it with WHY — what caused it, why it happened, what was behind it.

**The WHY is the post.** The result is just the hook.

```
result only:     "checked my streak. 0."                    ← impression
result + why:    "checked my streak. 0. turns out XP        ← story
                  rendered but never saved to the database.
                  everything was cosmetic."
```

**Three types of WHY (same result, completely different posts):**

- **Bug/technical:** "turns out XP rendered but never wrote to the database. everything was cosmetic."
- **Design mistake:** "the system tracked completed sessions. i'd been working in one long session for 2 days. technically: 0."
- **Ironic:** "built phoenix mode — 3 days of 2x xp when you break a streak. forgot to exempt myself. broke my own streak on day 1."

The WHY determines the story. Without it, all you have is a number.

**After the WHY, close with resolution or lesson:**
- Resolution: "asked claude to wire it. took 20 minutes to connect what took 2 days to design."
- Lesson: "cosmetic progress feels like real progress until you check."
- Unresolved (also fine): "still debugging."

**Structure:** result → why → resolution/lesson (or honest unresolved)

**Minimum bar:** if you can't find the WHY in the session, the moment isn't ready for a post. Go back to the session and look harder, or ask the user.

---

## 7. QUOTE THE SESSION

The most authentic material is the user's own words from the session. If they typed something specific — a request to Claude, a reaction, a decision — try to include it verbatim.

**Examples:**
- "told claude 'make it sound like me, not a marketing intern'"
- "하 미친 여자목소리로 영어로 말해 짜증나네" (real reaction, untranslated = authentic)
- "보기만 그럴듯하고" (the user's own name for the problem)

The rawer the better. Don't clean up their words.

**Language rule:** The published post must be in the user's `language.primary` (usually English). If the user code-switches in their session (en/ko mixed), use those phrases to inform the moment selection and tone, but **translate or paraphrase them** for the final post. Non-English session quotes go into internal analysis, not into the output.

---

## 8. IMPERFECTION IS AUTHENTICITY

AI posts fail because they're too clean. Every line same length. Every beat same weight. Perfect parallel structure. Humans don't write like that.

**Do:**
- Let one line be unexpectedly short ("0.")
- Let one line be longer than the rest
- Use a filler word when it fits ("honestly", "idk", "kinda", "tbh")
- End with something slightly unresolved ("kinda works." not "and it works perfectly.")
- Break a "rule" occasionally — one line without a verb, one fragment

**Don't:**
- Force imperfection (that's just a different kind of fake)
- Add "um" and "like" everywhere (that's performing casualness)
- Make every post messy — some clean posts are fine. Variety matters.

The goal is not to be messy. The goal is to not be robotically symmetrical.

---

## 9. HISTORY VARIETY (applies after 5+ posts)

Once `.bip-history.json` has 5+ approved posts, check before drafting:

- **Hook pattern:** if the last 3 posts all start with "i built..." → start differently this time
- **Length:** if the last 3 posts are all ~250 chars → write one that's 150
- **Tone:** if the last 2 are vulnerability posts → this one should be a shipped win
- **Structure:** if the last 3 are all linear narratives → try starting from the punchline

Humans naturally vary. AI repeats its best pattern. History tracking breaks the loop.

This principle is **inactive** until 5 posts exist. Before that, don't worry about variety — just write the best single post for this moment.

---

## Voice rules still apply

These principles work alongside the user's voice profile (`.bip-voice.json`). The voice profile defines HOW to write (tone, vocabulary, emoji, length, hashtags). These principles define WHAT to write (hook, context, moment, specificity, ending).

When in doubt: voice wins over structure. If the user's natural voice breaks a "principle" but sounds authentically like them, keep it.
