# koko-ship eval rubric

This is the canonical 4-axis quality rubric for koko-ship posts. It is used by:

- **The writer skill** — for self-evaluation before delivering a draft to the user
- **The editor skill** (`~/.claude/skills/koko-ship-editor/SKILL.md`) — as a second-pass gate for the publish decision

If you change this rubric, both consumers update automatically. **Single source of truth.**

---

## Core principle

Diagnose, never prescribe. Score what's in front of you. Quote evidence. Don't write the fix — point at the wound.

A **7** on any axis is "minimum acceptable." Not "pretty good." Don't inflate.

---

## The 4 axes

### 1. Hook Strength (1-10)

Does the first line stop the scroll?

| Score | Meaning |
|---|---|
| 1-3 | Generic. Could be anyone's post. No specificity. |
| 4-6 | Has a topic but no tension, surprise, or number. |
| 7-8 | Specific. Creates curiosity or tension. Reader wants to know more. |
| 9-10 | Irresistible. Concrete detail + emotional pull + unexpected angle. |

**Evidence to cite:** Quote the actual first line. Explain why it does or doesn't stop the scroll.

**Hook auto-fail triggers (hard cap at 5):**
- First line is "built/made/created/launched [generic noun]" with no specific name, number, or tension → cap 5
- First line is a marketing phrase ("excited to share", "thrilled to announce") → cap 5
- First line could be the opening of any other indie hacker's post without changing a word → cap 5
- First line contains no specific number, name, moment, or tension → cap 5

**Hook is failing if** any auto-fail trigger matches. These are not subjective — check mechanically.

---

### 2. Story (1-10)

Is there a narrative arc, not just a result announcement or a feature list?

| Score | Meaning |
|---|---|
| 1-3 | Pure announcement or feature list. No process, no journey, no emotional beat. |
| 4-6 | Some context but flat. Missing struggle, turning point, or emotional anchor. |
| 7-8 | Clear arc: intention → attempt → obstacle → resolution. OR a strong articulation arc (named problem, honest vulnerability, real question with stake). |
| 9-10 | Compelling journey. Reader feels the ups and downs. Stakes are real. |

**Three valid arc types** (not just outcome arcs):

1. **Outcome arc** — intent → attempt → struggle → result. The classic shipped/process/lesson story.
2. **Articulation arc** — observed problem → named it → here's how it manifests. Doesn't require resolution. (e.g. "plan doom loop")
3. **Emotional arc** — the moment, the fear/doubt under it, why sharing anyway. Doesn't require a result.

**Evidence to cite:** Identify which story elements are present and which are missing. Name the arc type if there is one.

**Story auto-fail triggers (hard cap at specified score):**
- Post is a feature list: 3+ nouns in parallel/comma structure as the bulk of the post → cap 5
- Post is a project summary with no session moment → cap 5
- Post describes the project (what it IS) instead of showing what happened (what the user DID) → cap 5
- **Post has a result but no WHY** — shows what happened but not why it happened. Result without reason = impression, not story. → cap 6

**Story is failing if** any auto-fail trigger matches. These are not subjective — check mechanically.

**Story scoring guide for WHY:**
- Result + WHY + resolution = 8-10 (full arc)
- Result + WHY + unresolved = 7-8 (honest, incomplete arc is fine)
- Result + WHY only = 7 (minimum passing)
- Result only, no WHY = cap 6 (auto-fail)
- No result, no WHY = cap 4

---

### 3. Authenticity (1-10)

Does it sound like a real person, not AI?

| Score | Meaning |
|---|---|
| 1-3 | Obviously AI. Buzzwords, perfectly parallel structure, no personality. |
| 4-6 | Somewhat human but too polished. No rough edges. |
| 7-8 | Sounds like someone actually typing their experience. Has personality. |
| 9-10 | Unmistakably human. Raw, specific, slightly messy. Voice is distinct. |

**Red flags (any one drops the score):**
- Marketing phrases: `excited to`, `thrilled to`, `proud to`, `humbled`, `blessed`
- Buzzwords: `game-changer`, `next level`, `leverage`, `streamline`, `revolutionary`
- Every sentence the same length
- No contractions where contractions would be natural
- Lists of exactly 3 items with parallel structure (the "rule of three" giveaway)
- Too clean. No personality. No specific small detail.

**The "would anyone else say this?" test:** Could 100 other indie hackers post this exact tweet without changing a word? If yes → max 5/10 on this axis.

**Voice profile compliance:** If a `voice/profile.md` and `voice/marketing-voice.md` exist, the post must respect:
- Language and register (from profile.md → Identity)
- Signature patterns and anti-patterns (from profile.md)
- Vocabulary markers — use freely / avoid (from profile.md)
- Post length and format rules (from marketing-voice.md)
- Hashtag rules (from marketing-voice.md)

Voice violations cap Authenticity at 6.

**Authenticity auto-fail triggers (hard cap at 5):**
- Any phrase from `phrases_banned` in the voice profile → cap 5
- Every line in the post is the same length (±10 chars) and same structure → cap 5 (too symmetrical = AI giveaway)
- "Would 100 other indie hackers say this?" test fails for the entire post → cap 5

**Authenticity bonus (add +1, max 10):**
- Post contains a verbatim quote from the user's session (their actual typed words) → +1
- Post includes a natural filler word from the user's vocabulary (kinda, tbh, honestly) → +1

**Evidence to cite:** Quote specific phrases that feel AI-generated, OR specific phrases that feel authentic.

---

### 4. Relatability (1-10)

Would a non-developer read this and think "I want to try that too" — or at least understand the moment?

| Score | Meaning |
|---|---|
| 1-3 | Only developers would understand. Heavy jargon, no translation. |
| 4-6 | Somewhat accessible but assumes technical knowledge. |
| 7-8 | Non-developer can follow the story and feel the moment. Technical details are contextualized. |
| 9-10 | A complete beginner reads this and thinks "I could do that with AI." |

**Relatability auto-fail triggers (hard cap at 6):**
- Post contains developer jargon without translation: `database`, `table`, `rows`, `query`, `API`, `endpoint`, `deploy`, `server`, `localhost`, `migration`, `schema`, `env`, `config`, `repository`, `commit`, `merge`, `branch`, `pipeline`, `container`, `instance`, `payload`, `token`, `webhook`, `SDK`, `CLI`, `runtime`, `dependency` → cap 6 unless the term is immediately explained in plain language
- Post assumes the reader knows what an "agent" does without explaining → cap 6
- Post uses acronyms without expansion (DB, XP is OK if contextually clear, but API/SDK/CLI are not) → cap 6

**How to fix jargon without dumbing down:**
- "checked the database. 0 rows." → "the task list was empty the whole time."
- "create tool didn't exist" → "the AI could check tasks off but couldn't actually add new ones"
- "pushed to production" → "went live"
- "API returned 500" → "the connection broke"
- Don't explain tech terms — replace them. The reader should never need to google a word.

**Evidence to cite:** Identify any unexplained jargon, OR moments that are accessible.

---

## Pass criteria

This rubric is used by two gates with different thresholds:

**Gate 1 — Skill self-eval (candidate filter):**
- All 4 axes ≥ 7 → **PASS** (= 28/40 minimum)
- Any axis < 7 → **FAIL** + diagnostic report
- Purpose: pick the best of 3 drafts to show the user

**Gate 2 — Evaluator agent (publish decision):**
- Voice Accuracy: 32/40+ AND not-me count = 0 → **PASS**
- Content Quality: 30/40+ → **PASS**
- Purpose: decide if the post is ready for human review and publishing
- A draft can pass Gate 1 but fail Gate 2

---

## Diagnostic report format

Use this exact structure when reporting (whether the skill is reporting to itself in self-eval, or the Evaluate Agent is reporting to the Build Agent):

```
POST EVALUATION
━━━━━━━━━━━━━━━━
Hook:          X/10  [PASS|FAIL]
Story:         X/10  [PASS|FAIL]
Authenticity:  X/10  [PASS|FAIL]
Relatability:  X/10  [PASS|FAIL]
━━━━━━━━━━━━━━━━
Overall:       PASS|FAIL

DIAGNOSIS (failing axes only):

[Axis name]: X/10
Evidence: "[exact quote from the post]"
Problem: [what's wrong, specifically — no prescription]

[Axis name]: X/10
Evidence: "[exact quote from the post]"
Problem: [what's wrong, specifically — no prescription]
━━━━━━━━━━━━━━━━
Attempt: N/3
```

---

## Retry / escalation rule

The skill (or Build Agent) gets **3 attempts** to pass. After the 3rd failure → escalate.

**Escalation when used inside the skill:**
> Show the user the score history and ask: "I keep failing on [axis]. The session may be too thin, or I'm missing context. Can you tell me one specific moment from today — a decision, a struggle, or a small detail I should focus on?"

**Escalation when used inside the project (PM workflow):**
> Bundle attempts 1/2/3 with score history → return to PM → PM reports to Koko.

---

## Critical rules (apply always)

1. **Diagnose, never prescribe.** "Hook is weak because it's generic" ✓. "Change the hook to start with a number" ✗.
2. **Quote evidence.** Every diagnosis must reference specific text from the post.
3. **Be harsh but fair.** Don't inflate. A 7 is the floor.
4. **Compare to voice profile if present.** Voice violations cap Authenticity at 6.
5. **Check security filter.** Flag if any credentials, PII, or sensitive URLs leaked through. Security failures are an automatic FAIL regardless of scores.

## What this rubric does NOT do

- Rewrite the post
- Suggest a different template
- Decide posting strategy or scheduling
- Evaluate the user's business decisions
- Talk to the user directly (the skill or PM relays)
