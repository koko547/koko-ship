---
name: koko-ship-qa
disable-model-invocation: true
description: >
  Quality assurance agent for koko-ship. Catches security leaks, jargon,
  repetition, and platform rule violations. Called by the writer skill
  as a reference document — not user-facing. Never triggered directly.
---

# QA

## Security filter

Strip from draft before delivery:
- API keys, secrets (`sk_`, `pk_`, `Bearer`, `token=`)
- DB connection strings, passwords, host:port
- Internal URLs (`localhost`, `*.internal`, raw IPs)
- Other people's PII (emails, phone numbers, real names)

Keep:
- Tech stack and tool names
- Architecture decisions
- Error messages (with credentials masked)
- Process and trial-and-error

## Platform rules (X/Twitter)

- Single tweet: 280 chars max. Target: 180-260.
- Hashtag: exactly one, branded, trailing line. Never generic.
- No engagement bait questions ("what do you think?", "who else?").
- No feature-list format (3+ parallel nouns).
- No thread unless user explicitly asks.

## Jargon check

Cross-reference with `voice/marketing-voice.md`:
- Technical terms: acceptable if user's voice uses them
- Marketing jargon: flag anything in anti-patterns list
- Developer-only terms (database, API, deploy, server, localhost, endpoint, schema, migration, ORM, middleware, webhook, cron, daemon, regex, env var): replace with plain language unless the user's audience is developers
- Acronyms: only if user's audience would know them

## Repetition check

Read `<cwd>/.bip-history.json` if it exists:
- Compare current post topic against `topics_covered`
- Compare hook against previous 3 hooks — vary the hook pattern
- Compare context line against `context_lines_used` — must be a new angle
- Flag if too similar to any recent post

## Privacy check

Cross-reference with `voice/marketing-voice.md`:
- Check "Keep Private" section — flag any private content in draft
- User's own name/handle: OK
- Other people's details: strip unless user explicitly included them
- Internal team dynamics: strip
- Raw financial specifics: strip unless publicly shared
