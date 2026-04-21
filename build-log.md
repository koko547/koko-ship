# koko-ship 빌드 로그

> 2026-04-09 ~ 04-11 | 기획 → 리서치 → 빌드 → 테스트 → 개선 전 과정 기록

---

## 1. 프로젝트 세팅

- Downloads에 있던 기획 파일들 (CLAUDE.md, docs/, .claude/agents/) → dev/koko-ship으로 이동
- 기존 기획: PM(팀장) + planner + builder agent 구조
- 기존 스펙: docs/project-instructions.md, docs/spec-v1.md, docs/competitor-map.md

---

## 2. 데이터 수집 (Apify 스크래핑)

### 2-1. Viral BIP 트윗 수집
- Apify `apidojo/twitter-scraper-lite` 사용
- 검색어: `#buildinpublic`, `#buildingpublic`, `"build in public"`, `#indiehackers`, `#vibecoding`, `"shipped" "side project"` 등 8개
- 필터: 영문 / Top 정렬 / 최근 6개월
- 1차: min_faves:1000 → 결과 8개 (너무 적음)
- 2차: min_faves:500 → 34개 (여전히 부족)
- 3차: min_faves 빼고 Top 정렬로 긁은 뒤 후처리 → 1,578개 (중복 제거), 79개 (500+ likes)
- 추가 확장 검색어로 2차 스크래핑 → 합산 후 79개 viral 확정

### 2-2. Koko X 포스트 수집
- @ink_young_koko 계정 스크래핑 → 8개 포스트
- MonstAR 프로젝트 관련, 소문자/캐주얼 톤, 💚 이모지 사용

### 2-3. Claude 대화 로그 추출
- ~/.claude/projects/ 4개 프로젝트에서 user 메시지만 추출
- 총 365개 메시지 (노이즈 필터 후)
- 프로젝트별: dev/koko-personal (139), social-automation-fana (102), ai-influencer-socials (81), Desktop/koko-personal (43)

### 2-4. 크리에이터 계정 분석
- @FarzaTV, @levelsio, @thejustinwelsh, @dannypostma 4명 스크래핑
- 각 200개 포스트, 총 516개 (RT/reply 제외)
- FarzaTV가 BIP 관점 가장 참고할 만한 크리에이터로 확인

---

## 3. 패턴 분석

### 3-1. Viral BIP 트윗 분석 결과
- **Hook:** number/stat 리드 (38%), first-person (17%), story (6%)
- **길이:** median 272자, 69%가 멀티라인 (3줄+)
- **이모지:** 21% 사용 (예상보다 적음)
- **해시태그:** 6%만 사용 → generic 해시태그는 viral에 무관
- **미디어:** 비디오 첨부 시 median likes 2.2배 (918 vs 2046)
- **포맷:** 단일 트윗 73%, thread 3%
- **Author tier:** 10k-100k 팔로워 계정이 43% (가장 많음)

### 3-2. Koko Voice 분석 결과
- 언어: 영어 71%, 한영 코드스위칭 22%
- 길이: median 110자 (짧고 직진)
- 톤: 결정형 11%, 탐색형 17%, 한영 코드스위칭 22%
- Top openers: "great", "hmm", "well", "응", "yup"
- 이모지: 거의 안 씀 (4%)

### 3-3. 크리에이터 분석 결과
- **FarzaTV:** "I built this thing called [Name]" 패턴. 첫 줄에 context + 제품명. 비디오 20%
- **levelsio:** 관찰/의견 위주. 이미 유명해서 context 안 넣음. 이모지 32%
- **thejustinwelsh:** thought leadership. "The older I get..." 패턴. 텍스트 only
- **dannypostma:** 짧은 원라이너. personal 비중 높음. engagement 낮음

### 3-4. 핵심 발견 5개
1. 스토리 > 발표 (outcome story가 announcement보다 강함)
2. 구체적 숫자가 무기 ($250k, 11k wishlists, day N)
3. 짧은 줄 + 줄바꿈 (한 줄 = 한 비트)
4. 언더독 프레이밍 (solo dev / $0 budget)
5. generic 해시태그 무의미 → branded hashtag 1개만

---

## 4. Voice Profile 설계

### 4-1. 첫 버전 (.bip-voice.json)
- 3개 소스 통합: viral 패턴 + Koko X 포스트 + Claude 대화 로그
- 언어: English only (글로벌 타겟)
- 톤: lowercase, 직진, no hype
- 길이: 180-260자 / 3-6줄
- 이모지: default none (데이터 쌓이면 학습)
- 해시태그: branded only (#koko-ship), trailing line

### 4-2. Voice 관련 결정 로그
- 해시태그: "branded TOC용으로만 쓰자" → generic 해시태그 전면 금지
- 이모지: "내 시그니처 아니야. 데이터 쌓이면 학습하자" → default zero
- 템플릿 vs 자유형: "너무 formulaic" → 5개 원칙 기반 자유 작성으로 전환
- Voice 우선: voice profile과 viral 구조가 충돌하면 voice 우선
- 혼합 언어: 세션에서 한국어 섞여도 포스트는 English only

---

## 5. Skill 빌드

### 5-1. v1 (초기)
- SKILL.md + 5개 템플릿 + voice profile + image generator
- install.sh (symlink to ~/.claude/skills/)
- 첫 테스트: koko-personal에서 트리거
- **문제 발견:** 현재 세션만 읽음. 세션이 비면 CLAUDE.md 읽고 generic 요약 뱉음

### 5-2. v2 (quality gates)
- **eval-rubric.md:** 4-axis 평가 (Hook/Story/Authenticity/Relatability)
- **self-eval gate:** 모든 draft 7점+ 통과해야 deliver
- **session triage:** 과거 세션 읽기 (read_project_sessions.py)
  - 최근 24h → 없으면 7일로 확장
  - warmup/sub-agent 제외 (<3 msgs)
  - koko-ship 메타 세션만 제외 (voice setup, skill install)
- **moment quality gate:** config only / no progress / 중복 토픽 → "nothing worth posting. keep building."

### 5-3. Voice Setup (유저 온보딩)
- **Hard gate:** voice profile 없으면 setup 먼저. 생성 거부
- **Default:** Claude 대화 로그 자동 스캔 (opt-out 가능)
- **Optional:** questionnaire (5문답) / paste (3-5개 글) / X scrape (v1.1 stub)
- **Skip:** 확인 한 번 더 → 그 세션만 generic, 다음에 또 물어봄
- share-able: default voice profile에서 Koko 개인정보 제거

### 5-4. 템플릿 → 원칙 전환
- **기존:** 8개 rigid 템플릿에서 선택
- **변경:** 5개 writing principles (Hook First / Context Fast / One Moment / Specific > Clever / End When It Lands)
- **추가 원칙:** WHY > WHAT / Quote the Session / Imperfection / History Variety
- **reference examples:** viral data + 크리에이터 data에서 영감용으로만 제공

---

## 6. 테스트 → 문제 발견 → 개선 사이클

### 테스트 1: koko-personal 첫 트리거
- **결과:** "built a personal OS with claude. 8-bit dashboard. boss HP. XP system. streaks. voice agent."
- **문제:** CLAUDE.md 읽고 프로젝트 설명을 요약함. 세션에 새 작업 없었음
- **진단:** 현재 세션만 읽는 구조 + 프로젝트 설명이 content source가 됨
- **Fix:** session triage (과거 세션 읽기) + no-session abort rule + "CLAUDE.md는 content source 아님" 명시

### 테스트 2: session triage 적용 후
- **결과:** 세션 리스트 표시 → 유저가 선택 → "phoenix mode" 포스트 생성
- **문제:** 포스트가 매력적이지 않음. "결과만 있고 이유(WHY)가 없음"
- **진단:** result → 감상으로 끝남. 왜 그런 결과가 나왔는지가 빠짐
- **Fix:** WHY > WHAT 원칙 추가. "result 뒤에 반드시 WHY 1-2줄". eval-rubric에 "WHY 없으면 Story cap 6"

### 테스트 3: WHY 원칙 적용 후
- **결과:** "checked my dashboard. 5 tasks, XP bars. checked the database. 0 rows."
- **개선:** WHY 들어옴 ("agent could read but not create")
- **문제:** "database", "0 rows" = 개발자 전용 용어. 비개발자 못 알아들음
- **Fix:** Relatability auto-fail trigger 추가. 개발 용어 25+ 단어 리스트. "설명 말고 대체하라" 원칙

### 테스트 4: jargon rule 적용 후
- **결과:** "my dashboard had a task panel. opened the data. zero tasks. ever."
- **개선:** jargon 제거됨. 비개발자도 이해 가능
- **문제:** 스크린샷이 포스트와 모순 (포스트는 "broken" 인데 스크린샷은 "working")
- **진단:** HTML 파일 직접 열어서 캡처 → JS 안 돌아서 실제 화면과 다름 + 이미 해결된 상태 캡처
- **Fix:** localhost 우선 캡처 + screenshot timing rule (포스트 결론 시점과 일치)

### 테스트 5: context line 누락
- **문제:** 첫 방문자가 "이 사람이 뭘 만들고 있는지" 모름
- **Fix:** context line variation — 매 포스트마다 한 줄 context 필수, 같은 line 반복 금지, history에 기록

### 테스트 6: "built X" 패턴 논쟁
- **초기 룰:** "첫 줄에 built X 금지"
- **크리에이터 데이터 반증:** FarzaTV가 "I built this thing called Clicky" 로 15,085♥
- **결론:** "built X"가 문제가 아님. X가 generic인 게 문제. 구체적 이름 있으면 OK
- **Fix:** "이름 + 한 줄 설명이면 첫 줄 context OK" 룰로 수정

### 테스트 7: voice style 충돌
- **문제:** Koko의 짧은 beat 나열 ("8-bit dashboard. boss HP. XP.") 이 anti-tagline 룰에 걸림
- **결론:** "그건 내 voice야"
- **Fix:** voice 우선 원칙 재확인. beat 나열 = OK (story를 서빙). feature list tagline = NG (story를 대체)

### 테스트 8: write 3 pick 1 도입
- **문제:** 첫 draft가 항상 deliver됨. self-eval이 자기한테 관대
- **Fix:** 내부적으로 3개 draft → self-eval → 가장 강한 1개만 deliver. auto-fail triggers 추가 (hook/story/auth/relat 각 hard cap)

---

## 7. 미디어 캡처 시스템

### 구현
- **capture_screenshot.py:** Playwright 기반
  - `--detect`: 프로젝트에서 캡처 가능한 소스 자동 감지 (localhost > HTML)
  - `--url`: live dev server 스크린샷/비디오
  - `--file`: HTML 파일 스크린샷/비디오
  - `--video`: 페이지 열리고 스크롤하는 3-5초 녹화

### 캡처 룰
- localhost (live server) 항상 우선. HTML 파일은 fallback
- Screenshot timing rule: 포스트 결론 시점과 스크린샷 시점 일치 필수
- UI 없는 프로젝트: text-only 기본. 유저가 원하면 구체적 캡처 가이드 제공
- "take a screenshot" 같은 vague 안내 금지. 뭘, 어떤 상태에서, 왜 찍는지 명시

---

## 8. 최종 Skill 구조

```
skills/koko-ship/
├── SKILL.md                              (메인 instructions, ~580줄)
├── install.sh                            (symlink installer)
├── references/
│   ├── eval-rubric.md                    (4-axis 평가 + auto-fail triggers)
│   ├── history-schema.json               (포스트 히스토리 + context lines)
│   ├── voice-profile-default.json        (generic default, share-able)
│   └── writing-principles.md             (9개 원칙 + reference examples)
└── scripts/
    ├── capture_screenshot.py             (스크린샷/비디오 캡처)
    ├── generate_image.py                 (카드 이미지 생성)
    ├── read_project_sessions.py          (과거 세션 읽기 + triage)
    ├── setup_voice_from_claude_logs.py   (default voice setup)
    ├── setup_voice_from_paste.py         (paste samples voice setup)
    ├── setup_voice_from_x.py            (v1.1 stub)
    └── setup_voice_questionnaire.py      (5-question voice setup)
```

---

## 9. 미결 / 다음 단계

### 바로 다음
- [ ] 실전 X 발행 첫 포스트
- [ ] 다른 프로젝트 (fana, ai-influencer 등)에서 voice generalization 테스트
- [ ] git init + 첫 커밋

### v1.1
- [ ] Hosted Apify endpoint (Vercel) — X 계정 스크래핑 서비스
- [ ] Invite token 시스템 (beta gate)
- [ ] setup_voice_from_x.py 완성

### v2 (web app)
- [ ] koko-ship.com — voice builder 웹 UI (docs/web-app-spec.md 참조)
- [ ] 성과 대시보드
- [ ] 피드백 루프 (80/20 experimental content)
- [ ] X API 연동 (댓글/답글/성과 수집)
- [ ] README.md (beta launch 시)

### 비즈니스
- [ ] 5월: 무료 skill 배포 → 외부 유저 10명
- [ ] 6월: 유료 전환 5명 + 성과 시그널
- [ ] 결제 모듈 결정 (Stripe vs Lemon Squeezy vs Paddle)
