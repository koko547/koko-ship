# Log

Append-only. Entry format: `## [YYYY-MM-DD] <op> | <title>` so it stays greppable with `grep "^## \[" log.md`.

---

## [2026-04-11] init | vault scaffolded
Created `CLAUDE.md`, `voice/{profile,marketing-voice,patterns,changelog}.md`, `index.md`, `log.md`, `raw/`. No sources ingested yet. Voice files contain seed hypotheses only.

## [2026-04-12] link | koko-ship dev repo symlinked into raw/
`raw/koko-ship → ~/dev/koko-ship`. Not yet ingested.

## [2026-04-12] ingest | first real pass — 6 sources
Ingested: 원지님 pitch_2311, 성장하기, Founder's story 스크립트, MonstAR founder story (KR+EN), FANA 파운더스 의견, MKT-PROD_IK csv. Replaced all four voice/*.md stubs with observed signals. Key finding: `,,` trailing soft-ender is the highest-signal tic; mode-locking by register is the most important generation constraint. See [[voice/changelog]] for full signal list and known gaps.
