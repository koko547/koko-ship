# Example: Session → Post

> This walkthrough uses placeholder content to show how the pipeline works.
> Every user's output will be different — that's the point.

## 1. The session

A developer is building a task management dashboard. During this session, they add a "streak counter" feature — tracking consecutive days of completing at least one task. They wire it up, test it, and discover the counter shows 0 even though they've completed tasks for 3 days straight.

User quote from the session:
> "wait. the streak counter is rendering but it's always 0. i've been doing tasks for 3 days. why is it stuck?"

Claude diagnoses: the streak logic reads from the database correctly, but the write operation that increments the streak was never connected — it renders the counter UI but never updates the value.

The user asks Claude to fix it. After the fix, the counter shows 3.

## 2. Moment extraction

- **WHAT:** streak counter showed 0 for 3 days despite completing tasks daily
- **WHY:** the counter could read the database but was never wired to write (from Claude's diagnosis + user's "why is it stuck?" reaction)
- **Resolution:** connected the write operation, counter jumped to 3

## 3. Voice profile applied

From this user's `voice/profile.md`:
- **Language:** English
- **Register:** casual (lowercase default)
- **Signature patterns:** short declarative beats, one idea per line
- **Anti-patterns:** "excited to announce", hype adjectives, engagement questions
- **Vocabulary:** uses contractions, first-person "i" freely
- **Rhythm:** aggressive line breaks, each line = one beat

From `voice/marketing-voice.md`:
- **Length:** 180-260 chars target
- **Hashtag:** one branded, trailing line
- **Emoji:** default none

## 4. Three drafts generated

**Draft 1 (stat/fact lead):**
```
streak counter: 0.
three days of completed tasks. counter stuck at zero the whole time.
turns out it could read the database but never learned to write.
one fix. counter jumped to 3.

#project-name
```
(198 chars)

**Draft 2 (confession hook):**
```
built a streak counter that can't count.
it rendered perfectly. showed 0 every day.
the read worked. the write didn't exist.
3 days of tasks, invisible to my own feature.

#project-name
```
(210 chars)

**Draft 3 (observation hook):**
```
a feature that looks finished but isn't.
streak counter: renders beautifully. always shows 0.
it was reading from the database but nobody told it to write.
fixed it. 0 → 3.

#project-name
```
(204 chars)

## 5. Editor evaluation

| | Draft 1 | Draft 2 | Draft 3 |
|---|---|---|---|
| Hook | 7/10 | 8/10 | 8/10 |
| Story | 8/10 | 8/10 | 7/10 |
| Authenticity | 8/10 | 9/10 | 7/10 |
| Relatability | 8/10 | 8/10 | 8/10 |
| **Total** | **31** | **33** | **30** |

**Winner: Draft 2.** Strongest hook ("built a streak counter that can't count" — specific, tension, self-deprecating). Best authenticity score — "invisible to my own feature" feels like a real reaction. Story arc is clean: built → broke → diagnosed → fixed.

Draft 1 is solid but the hook is flat (just "streak counter: 0"). Draft 3's "a feature that looks finished" is slightly generic.

Voice check: all lowercase, short beats, no hype, no engagement question, branded hashtag. Pattern fidelity: pass. Not-me count: 0.

## 6. QA pass

- **Security:** no API keys, no internal URLs, no PII. Clean.
- **Jargon:** "database" appears — but this user's audience is developers, so acceptable per their `voice/marketing-voice.md`. If the user's audience were non-developers, QA would flag: replace "read from the database" with "check the data."
- **Platform:** 210 chars (within 180-260 target). One branded hashtag, trailing. No engagement bait. Pass.
- **Repetition:** no previous posts in history. Pass.

## 7. Final post

```
POST (210 chars)
---
built a streak counter that can't count.
it rendered perfectly. showed 0 every day.
the read worked. the write didn't exist.
3 days of tasks, invisible to my own feature.

#project-name
```
