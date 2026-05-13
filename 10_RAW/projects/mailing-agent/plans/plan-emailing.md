# Mailing Agent 실행 계획

> 기준 문서: `research2-mailing.md` | 작성일: 2026-04-15

---

## 초회 구동 참고 파일

**참고 파일 경로:** `C:\Users\Pulmuone\OneDrive - 풀무원\!Mailing\`
이 폴더 내 파일만 참고로 활용. 추가 파일이 필요할 경우 사용자에게 먼저 확인.

DB가 없는 초회 구동 시 아래 3개 파일을 cold start 시드 데이터로 활용:

| 순서 | 파일명 | 역할 |
|------|--------|------|
| 1 | `consulted.txt` | 최초 기준 예시 메일 (톤앤매너 분석 대상) |
| 2 | `draft.md` | Claude가 최초로 제공한 초안 |
| 3 | `[결재] Claude Team Plan 구매 건(안).eml` | 사용자가 최종 수정 후 발송한 실제 메일 |

---

## 전체 구현 단계 개요

| 단계 | 내용 | 산출물 |
|------|------|--------|
| Phase 1 | 프로젝트 뼈대 구축 | 디렉토리 + CLAUDE.md |
| Phase 2 | DB 및 설정 파일 | database.py + tone_profiles.json |
| Phase 3 | 에이전트 + 스킬 파일 | 4개 에이전트, 2개 스킬 |
| Phase 4 | 슬래시 명령어 | /analyze, /draft, /optimize |
| Phase 5 | Python 로직 | analyzer.py, generator.py, optimizer.py |
| Phase 6 | 첫 실행 + 검증 | 샘플 초안 생성 + DB 확인 |

---

## Phase 1. 프로젝트 뼈대 구축

**목표:** 디렉토리 구조 생성 + 프로젝트 컨텍스트 파일 작성

### 1-1. 디렉토리 생성
```
mailing-agent/
├── .claude/
│   ├── agents/
│   ├── skills/
│   └── commands/
├── data/
│   ├── emails/      ← 참조 이메일 저장소 (.eml)
│   ├── drafts/      ← AI 초안 저장소 (.md, Claude 자동 저장)
│   ├── sent/        ← 최종 발송본 저장소 (.eml, 사용자 수동 투입)
│   └── templates/   ← 톤앤매너 JSON 프로필
├── src/
└── config/
```

### 1-2. CLAUDE.md 작성
- 목적: 사용자 맞춤형 업무 메일 초안 자동 생성
- 톤앤매너 기본 원칙 (비즈니스 포멀, 간결, 명확)
- 이모지 사용 절대 금지 명시
- 민감 정보 처리 규칙
- 초안 저장 경로 규칙: `data/drafts/{YYYYMMDD}_{제목요약}.md`

---

## Phase 2. DB 및 설정 파일

**목표:** SQLite DB 초기화 + 기본 톤앤매너 프로필 생성

### 2-1. src/database.py
4개 테이블 생성 + `--init` 실행 옵션:

| 테이블 | 역할 |
|--------|------|
| `email_drafts` | Claude가 생성한 초안 기록 |
| `sent_emails` | 사용자 최종 발송본 기록 |
| `reference_emails` | 참조 이메일 원본 저장 |
| `tone_profiles` | 톤앤매너 프로필 + 성과 지표 |

핵심 컬럼:
- `email_drafts.matched_sent_id` → sent_emails FK (초안↔최종본 연결)
- `email_drafts.match_confidence` → 매칭 신뢰도 (0~1)
- `sent_emails.file_path` → data/sent/ 내 .eml 경로
- `sent_emails.edit_ratio` → 초안 대비 변경률

### 2-2. config/tone_profiles.json
기본 프로필 3종 생성:
- `formal`: 공식 보고, 외부 거래처
- `semi-formal`: 내부 협조, 팀 내 소통
- `urgent`: 긴급 요청, 기한 강조

### 2-3. Cold Start 시드 데이터 적재 (초회 1회만 실행)
DB 초기화 직후, 참고 파일 3종으로 초기 학습 데이터 1건 생성:

**Step 1 — `consulted.txt` 분석**
- `/analyze` 실행 → `reference_emails` 테이블 등록
- 톤앤매너 프로필 추출 → `data/templates/` 저장
- 이 분석 결과가 이후 초안 작성의 기준 프로필이 됨

**Step 2 — `draft.md` 등록**
- `email_drafts` 테이블에 수동 등록
- 초안 파일을 `data/drafts/`에 복사

**Step 3 — `[결재] Claude Team Plan 구매 건(안).eml` 등록 + 매칭**
- `sent_emails` 테이블에 등록, 파일을 `data/sent/`에 복사
- `draft.md`와 자동 매칭 → `edit_ratio` 계산 → DB 저장
- 결과: 시스템 최초 실행 시점에 이미 1건의 학습 데이터 보유

---

## Phase 3. 에이전트 + 스킬 파일

**목표:** 4개 에이전트 + 2개 스킬 파일 작성

### 3-1. .claude/agents/tone-analyzer.md
- 역할: 참조 .eml 분석 → 문체/어조/인사말 패턴 추출
- 출력: `data/templates/{프로필명}.json`
- tools: Read, Write, Glob
- 개인정보 마스킹 필수 명시

### 3-2. .claude/agents/db-manager.md
- 역할: SQLite DB CRUD 관리
- tools: Read, Write, Bash
- 제약: SELECT는 자동 실행, INSERT/UPDATE는 사용자 확인 후 실행

### 3-3. .claude/agents/optimizer.md
- 역할: 초안↔최종본 비교 분석 + 자동 고도화
- tools: Read, Write, Bash
- **핵심 플로우:**
  1. data/sent/에 새 .eml 감지 → 미매칭 초안과 매칭 시도
  2. 매칭 기준: 제목 유사도(최우선) → 본문 유사도 → 시간 순서
  3. 후보 1개 → 자동 연결 / 복수 → 사용자 확인
  4. 매칭 완료 → diff 분석 → edit_ratio 계산 → DB 저장
  5. 동일 수정 패턴 3건 이상 → 톤앤매너/에이전트 업데이트 제안
- triggers: data/sent/ 파일 감지 시 / `/optimize` 수동 실행 시

### 3-4. .claude/agents/draft-writer.md
- 역할: 키워드 + DB 참조 데이터 기반 초안 생성
- tools: Read, Write
- skills: tone-analyzer, db-manager 활용
- 출력 포맷:
  - 제목 3개 옵션 (추천 1개 포함)
  - 본문 + 인사말/맺음말 자동 매칭
  - [확인필요] 태그 + 검토 체크리스트
  - 생성 즉시 `data/drafts/` 자동 저장
  - 완료 후 1-5점 피드백 수집 → DB 저장

### 3-5. .claude/skills/email-parsing.md
- .eml 파일에서 제목/발신자/수신자/본문 파싱
- .eml은 텍스트 기반이므로 Read 도구로 직접 읽기 가능
- 개인정보(이름, 이메일 주소) 마스킹 처리 후 출력

### 3-6. .claude/skills/keyword-extract.md
- 메일 본문에서 핵심 키워드 추출
- 수신자 유형, 상황, 일정, 요청사항 분류

---

## Phase 4. 슬래시 명령어

**목표:** 사용자 진입점 명령어 3종 작성

### 4-1. .claude/commands/analyze.md → `/analyze`
- 인수: `[이메일 파일 경로]`
- 동작: tone-analyzer 호출 → 분석 결과 JSON 저장 → 결과 요약 출력

### 4-2. .claude/commands/draft.md → `/draft`
- 인수: `[상황 키워드]` (선택)
- 대화형 입력 흐름:
  1. 메일 유형 선택 (미팅요청/보고/요청/협조/인사/기타)
  2. 수신자, 목적, 주요내용, 기한, 톤 입력
  3. 참고 메일 경로 입력 (선택)
  4. draft-writer 에이전트 실행 → 초안 제시

### 4-3. .claude/commands/optimize.md → `/optimize`
- 인수: 없음
- 동작: optimizer 에이전트 수동 실행
  - data/sent/ 신규 파일 스캔
  - 매칭 → diff 분석 → 패턴 감지 → 개선 제안

---

## Phase 5. Python 로직

**목표:** 에이전트가 호출하는 실제 처리 로직 구현

### 5-1. src/analyzer.py
- `analyze_tone(file_path: str) -> dict`: .eml 파싱 + 톤앤매너 분석
- `save_profile(profile_name: str, analysis: dict)`: templates/ JSON 저장

### 5-2. src/generator.py
- `generate_draft(context: dict) -> str`: 키워드 + 프로필 기반 초안 생성
- `save_draft(content: str, subject: str) -> str`: data/drafts/ 저장, 파일경로 반환

### 5-3. src/optimizer.py
- `scan_sent_folder() -> list`: data/sent/ 신규 .eml 탐지
- `match_draft(sent_eml_path: str) -> dict`: 제목+본문 유사도 매칭
- `calc_edit_ratio(draft: str, sent: str) -> float`: difflib 기반 변경률 계산
- `analyze_patterns(n: int = 10) -> dict`: 최근 n건 수정 패턴 분석

---

## Phase 6. 첫 실행 + 검증

**목표:** cold start 데이터로 전체 플로우 동작 확인

### 6-1. DB 초기화
```bash
python src/database.py --init
```

### 6-2. Cold start 시드 적재 (Phase 2-3 실행)
- `consulted.txt` 분석 → 톤앤매너 프로필 생성 확인
- `draft.md` → `email_drafts` 등록 확인
- `[결재] Claude Team Plan 구매 건(안).eml` → `sent_emails` 등록 + 매칭 확인
- DB에 1건의 초안↔최종본 데이터가 생성되었는지 확인

### 6-3. 초회 매칭 검증
- `/optimize` 실행
- `draft.md` ↔ `[결재]...eml` 매칭 결과 확인
- `edit_ratio` (변경률) 수치 확인
- 수정 패턴 분석 결과 출력 확인

### 6-4. 첫 신규 초안 작성
```
/draft
```
- 대화형 입력 → 초안 출력 확인 (이미 1건의 DB 참조 데이터 활용)
- `data/drafts/` 에 .md 파일 자동 저장 확인
- 피드백 점수 입력 → DB 저장 확인

---

## 구현 우선순위 판단 기준

| 우선순위 | 항목 | 이유 |
|---------|------|------|
| 필수 (즉시) | Phase 1~3 | 핵심 기능 없으면 사용 불가 |
| 필수 (즉시) | `/draft` 명령어 | 주 사용 진입점 |
| 권장 | `/analyze` 명령어 | DB 없이도 즉시 효과 |
| 권장 | optimizer.md | 누적 데이터 후 효과 발생 |
| 나중 | Phase 5 Python | Claude가 직접 처리 가능한 초기엔 생략 가능 |
| Phase 2 후보 | Outlook 연동 | 발송 자동화 (수동 투입 먼저 검증 후) |

---

## 파일 생성 체크리스트

### 즉시 생성
- [x] `mailing-agent/CLAUDE.md`
- [x] `mailing-agent/.claude/agents/tone-analyzer.md`
- [x] `mailing-agent/.claude/agents/db-manager.md`
- [x] `mailing-agent/.claude/agents/optimizer.md`
- [x] `mailing-agent/.claude/agents/draft-writer.md`
- [x] `mailing-agent/.claude/skills/email-parsing.md`
- [x] `mailing-agent/.claude/skills/keyword-extract.md`
- [x] `mailing-agent/.claude/commands/draft.md`
- [x] `mailing-agent/.claude/commands/analyze.md`
- [x] `mailing-agent/.claude/commands/optimize.md`
- [x] `mailing-agent/src/database.py`
- [x] `mailing-agent/config/tone_profiles.json`

### 초기 데이터 이후 생성
- [x] `mailing-agent/src/analyzer.py`
- [x] `mailing-agent/src/generator.py`
- [x] `mailing-agent/src/optimizer.py`
