# Plan: 인터뷰 STT 자동 처리 에이전트 신설

## Context

**왜 만드나?**
사용자가 `30_interview/interview_STT/` 에 STT 원문 txt 를 쌓아두고 있고, 이를 bundle.html 인터뷰 앱이 읽는 `shared/interview_records/e{사번}_{이름}.json` 양식으로 자동 변환할 필요가 있다. 현재는 수동 정리 중이며 의역·오류가 많아 원문 대조가 병목.

**무엇을 만드나?**
기존 `hr-meeting-processor` (회의 STT → 5섹션 마크다운 요약) 의 골격을 fork 해서 **30_interview 폴더 안에 격리된 새 에이전트** 를 신설한다. 출력은 마크다운이 아니라 **bundle.html 호환 JSON** (Q0~Q4 × 기본/심화 = 10 answers + 자유메모 + 다음단계).

**범위**
- ✅ STT txt → JSON 자동 변환 (이름·차수 인식, 사번 lookup, 5질문 매핑, 스키마 검증)
- ❌ DB 동기화 / 분석 탭 업데이트 (사용자 명시: 본 프로젝트 무관)
- ❌ `30_interview/` 상위 폴더 (사용자 명시: 동작 범위 한정)

---

## 결정 사항 (사용자 확정)

| 항목 | 결정 |
|------|------|
| **사번 매핑** | `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\Interview\archive\data\directory.csv` 에서 성명으로 매칭. 동명이인 시 부서명·법인명 표시 후 사용자 확인 |
| **다회차 처리** | 차수별 별도 파일. **1차는 서픽스 없음** (`e{사번}_{이름}.json`), **2차+ 만 서픽스** (`e{사번}_{이름}_2차.json`) |
| **질문 텍스트 소스** | SKILL 파일에 하드코딩 (`question-spec.md`) |
| **에이전트 격리** | `30_interview/` 폴더 한정, 상위 폴더 비관여 |
| **탭 구성** | 각 질문마다 **3탭** (기본 / 심화 / 꼬리) 지원. `tab_label` 가능 값: `null` (기본) · `"심화"` · `"꼬리"`. 답변이 없는 탭은 항목 자체를 생략 (빈 문자열 강제 생성 금지). answers 최대 15개 |
| **슬래시 커맨드** | `/stt` 신설 (`30_interview/.claude/commands/stt.md`) |

---

## 신설 파일 구조

```
30_interview/
├── CLAUDE.md                                  ← 신설 (격리된 경로 SSoT)
├── .claude/
│   ├── agents/
│   │   └── interview-stt-processor.md         ← 신설 (메인 에이전트)
│   ├── commands/
│   │   └── stt.md                             ← 신설 (/stt 슬래시 커맨드)
│   └── skills/
│       └── interview-summary-generator/
│           ├── SKILL.md                       ← 신설 (지시서)
│           └── references/
│               ├── question-spec.md           ← 신설 (Q0~Q4 × 3탭 본문)
│               ├── format-spec.md             ← 신설 (JSON 스키마 명세 + 예시)
│               └── gotchas.md                 ← 신설 (실패 패턴)
├── interview_STT/                              ← 기존 (입력, Read 전용)
└── shared/
    └── interview_records/                      ← 기존 (출력)
```

기존 `hr-meeting-processor` 와 **공유 자원 없음** (격리 원칙 준수).

---

## 핵심 파일 명세

### 1. `30_interview/CLAUDE.md`

격리된 경로 SSoT. 다음만 정의:
```
BASE      = C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\Smartmeeting - 문서\30_interview
RAW       = {BASE}\interview_STT
OUT       = {BASE}\shared\interview_records
DIRECTORY = C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\Interview\archive\data\directory.csv
SKILL     = {BASE}\.claude\skills\interview-summary-generator
```
- 절대 금지: 원본 STT 수정·이동·삭제, 상위 폴더 접근, JSON 스키마 키 누락

### 2. `interview-stt-processor.md` (에이전트 정의)

`hr-meeting-processor.md` 구조 답습 (frontmatter + 6 STEP):

```yaml
---
name: interview-stt-processor
description: "트리거: interview_STT/*.txt 처리, 'STT 정리해줘', '인터뷰 JSON 만들어줘' 요청.
              동작: STT txt → directory.csv 사번 lookup → 5질문 매핑 → bundle.html 호환 JSON 저장."
tools: Read, Write, Bash, Glob
model: claude-sonnet-4-6
---
```

**6 STEP 파이프라인**:

| STEP | 동작 |
|------|------|
| 0 | SKILL.md + question-spec.md + format-spec.md 로딩, directory.csv 캐싱 |
| 1 | `interview_STT/*.txt` 글로빙 + `shared/interview_records/` 와 비교, 미처리 파일 식별 |
| 2 | 파일명 파싱: `YYYYMMDD_{이름}_{N}차.txt` → (날짜, 이름, 차수). directory.csv 에서 사번 lookup. **동명이인 시 사용자에게 부서·법인 표시 후 disambiguation 요청** |
| 3 | STT 원문 Read. 회의 헤더에서 시작/종료 시각 추출 → ISO8601 변환 |
| 4 | question-spec 기준으로 5질문 × 최대 3탭(기본/심화/꼬리) 매핑. 답변이 없는 탭은 항목 자체 생략(빈 문자열 강제 생성 금지). 자유메모(인사이트성 부가 정보)·다음단계(요점 요약) 추출 |
| 5 | JSON 직렬화 → 출력 파일명 결정 (1차: `e{id}_{이름}.json`, N≥2차: `e{id}_{이름}_{N}차.json`) → Write. **이미 존재 시 사용자에게 알림 후 기본은 스킵** |
| 6 | 스키마 자체 검증 (answers 정확히 10개, question_idx 0~4 각 2개씩, 필수 키 존재) + 원본 보존 확인 + 완료 보고 |

### 3. `SKILL.md`

처리 지시서. 각 STEP 의 의사코드와 출력 형식 예시. 자체 검증 체크리스트 포함.

### 4. `references/question-spec.md`

bundle.html `Hf` 배열에서 추출한 **5질문 × 3탭** 본문(Single Source of Truth):

| idx | 기본 (`tab_label: null`) | 심화 (`tab_label: "심화"`) | 꼬리 (`tab_label: "꼬리"`) |
|-----|-------------------------|-------------------------|-------------------------|
| 0 | 현재 가장 반복적이라고 느끼는 업무 1개를 알려주세요. | 그 업무가 얼마나 표준화되어 있나요? (완전 표준/부분 표준/없음) | 팀 내에서 동일 업무를 하는 사람이 또 있나요? |
| 1 | 그 업무의 월간 소요 시간은 얼마나 됩니까? | 피크 월과 평상 월의 차이가 크나요? | 이 시간 측정이 공식적으로 이루어진 적 있나요? |
| 2 | 지금 사용하는 도구(엑셀/이메일/시스템)를 구체적으로 말씀해주세요. | 도구 간 데이터 이동(복붙)이 발생하나요? | 선호하는 도구가 있다면 무엇인가요? |
| 3 | 추천 과제 중 가장 먼저 해보고 싶은 것은? 이유는? | 성공 기준(KPI)을 본인이 정의한다면? | 도움이 될 협업자가 있나요? |
| 4 | 자동화를 막는 가장 큰 장애물은 무엇입니까? | 장애물이 기술적인가, 조직적인가? | 과거 유사 시도가 실패한 이력이 있나요? |

**매핑 규칙**:
- STT 원문에서 직접 인용 금지 → 항상 재서술
- 답변이 없는 탭(인터뷰어가 묻지 않았거나 시간 부족)은 **항목 자체 생략** (빈 문자열 강제 생성 금지)
- 의미 기반 매칭: 인터뷰어의 실제 발화가 위 본문과 글자가 달라도 의미가 통하면 같은 (idx, tab) 슬롯에 배정
- 어느 슬롯에도 매칭되지 않는 가치 있는 발화는 `freeform_notes` 로 보냄
- tab 분리 신호어 예: "좀 더 구체적으로", "더 자세히", "표준화 정도는?", "동일 업무 하는 분 또 있나요?" 등 — 표 내용 자체를 신호로 활용

### 5. `references/format-spec.md`

`e200002_김혜인.json` 을 골든 샘플로 사용. 스키마 골격:

```json
{
  "schemaVersion": 1,
  "employeeId": <number>,
  "name": "<string>",
  "interview": {
    "employee_id": <number>,
    "interviewer_id": "gian.kim",
    "status": "completed",
    "scheduled_at": null,
    "started_at": "<ISO8601 from STT 헤더>",
    "completed_at": "<ISO8601 from STT 헤더>",
    "agreed_task_id": null,
    "freeform_notes": "<자유 메모 추출>",
    "next_step": "<다음 단계 추출>",
    "id": <epoch_ms of started_at>,
    "created_at": "<ISO8601>",
    "updated_at": "<ISO8601>"
  },
  "answers": [
    { "interview_log_id": <interview.id>, "question_idx": 0, "tab_label": null,    "question_text": "", "answer_text": "...", "id": <unique_ts> },
    { "interview_log_id": <interview.id>, "question_idx": 0, "tab_label": "심화",  "question_text": "", "answer_text": "...", "id": <unique_ts> },
    { "interview_log_id": <interview.id>, "question_idx": 0, "tab_label": "꼬리",  "question_text": "", "answer_text": "...", "id": <unique_ts> },
    ... (최대 15개, 5질문 × 3탭. 답변 없는 탭은 항목 생략)
  ],
  "updatedAt": "<ISO8601>"
}
```

검증 룰:
- `answers.length <= 15` (5질문 × 3탭 상한)
- 각 `question_idx` 별로 같은 `tab_label` 조합 중복 금지 (unique pair)
- `tab_label` 가능 값: `null` · `"심화"` · `"꼬리"` 3종
- `id` 들 모두 unique
- `interview_log_id` === `interview.id`
- `question_text: ""` (기존 패턴 따름 — 질문 본문은 bundle.html 측에서 렌더링)
- 답변 없는 탭은 빈 문자열로 채우지 말고 **항목 자체를 생략**

### 6. `references/gotchas.md`

- ❌ STT 원문 직접 인용 → ✅ 재서술 필수
- ❌ 동명이인을 무시하고 첫 매칭 사번 사용 → ✅ 반드시 사용자 확인
- ❌ 답변이 5질문 어디에도 매칭 안 되는 발화 강제 분류 → ✅ `freeform_notes` 로 보냄
- ❌ STT 헤더 없는 비표준 파일 자동 진행 → ✅ 사용자 알림 후 중단
- ❌ JSON 스키마 키 임의 추가/제거 → ✅ format-spec 골격 엄수
- ❌ 답변이 없는 탭(특히 꼬리)에 빈 문자열 항목 강제 생성 → ✅ 항목 자체 생략
- ❌ 꼬리 탭을 심화와 합쳐 처리 → ✅ tab_label 3종 분리 유지

### 7. `commands/stt.md` (신설 슬래시 커맨드)

`/stt [파일명?]` 호출 시 `interview-stt-processor` 에이전트를 명시적으로 트리거.

```markdown
---
description: "interview_STT 미처리 txt → bundle.html 호환 JSON 자동 변환"
---

`30_interview/.claude/agents/interview-stt-processor.md` 에이전트를 호출한다.

## 인자
- `$ARGUMENTS` 가 비어있으면: `interview_STT/*.txt` 전체 스캔 후 미처리 파일 자동 탐지·일괄 처리
- 파일명이 주어지면: 해당 단일 파일만 처리 (예: `/stt 20260428_김혜인_1차.txt`)

## 진행 흐름
에이전트의 6 STEP 파이프라인 (STEP 0 명세 로딩 → STEP 1 미처리 탐지 → STEP 2 사번 lookup → STEP 3 STT 읽기 → STEP 4 5×3 매핑 → STEP 5 JSON 저장 → STEP 6 검증·보고) 그대로 실행.

## 안전장치
- 동명이인 발견 시 사용자 disambiguation 응답 대기 (자동 진행 금지)
- 출력 파일 이미 존재 시 기본 스킵, '덮어써줘' 신호 시에만 덮어쓰기
- 원본 STT 파일 절대 수정·이동 금지
```

---

## 사용자 호출 예시

```
/stt
→ interview_STT/*.txt 전체 스캔, 미처리 파일 자동 탐지·일괄 처리

/stt 20260428_김혜인_1차.txt
→ 단일 파일 처리

"interview_STT 처리해줘"
→ 자연어 트리거 (에이전트 description 매칭)
```

---

## 검증 (Phase 5 / Validate 시)

본 프로젝트는 단일 HTML 파일 검증 규칙(브라우저 수동)이 아니라 **JSON 산출물 검증** 으로 재정의:

| 항목 | 확인 방법 |
|------|---------|
| 신설 파일 5개 모두 생성 | `Glob 30_interview/.claude/**/*.md` |
| 에이전트 frontmatter 유효 | YAML 파싱 가능, name·tools·model 키 존재 |
| 골든 샘플 비교 | 김혜인 1차 STT 로 시범 실행 → 기존 e200002_김혜인.json 과 구조적 동등성 확인 (사람이 답변 텍스트만 차이 인지) |
| 신규 파일 탐지 | 김영진 1차 STT 처리 후 `e{사번}_김영진.json` 생성 확인 |
| 동명이인 fallback | directory.csv 동명이인 케이스 (있다면) 시뮬레이션 |
| 원본 보존 | `interview_STT/*.txt` mtime 변화 없음 |

**Phase 6 (Deploy) 는 OneDrive 동기화 = 비가역**이므로 사용자 최종 확인 필수.

---

## 영향 받는 파일

**신설 (총 7개)**:
- `30_interview/CLAUDE.md`
- `30_interview/.claude/agents/interview-stt-processor.md`
- `30_interview/.claude/commands/stt.md`
- `30_interview/.claude/skills/interview-summary-generator/SKILL.md`
- `30_interview/.claude/skills/interview-summary-generator/references/question-spec.md`
- `30_interview/.claude/skills/interview-summary-generator/references/format-spec.md`
- `30_interview/.claude/skills/interview-summary-generator/references/gotchas.md`

**기존 파일 수정 없음** (격리 원칙).

**참조만** (Read 전용):
- `directory.csv` (사번 lookup)
- 기존 `hr-meeting-processor.md` (구조 참조)
- `e200002_김혜인.json` (골든 샘플)

---

## 다음 단계

ExitPlanMode 승인 후:
1. Phase 3 (Split): 7개 신설 파일을 1개 트랜잭션으로 일괄 작성 (의존성 없음, 병렬 가능)
2. Phase 4 (Execute): Write 7회 + 검증
3. Phase 5 (Validate): 위 검증 표 항목 실행 (시범 실행은 별도 사용자 요청 시)
4. Phase 6 (Deploy): 사용자 확인 후 저장 = OneDrive 동기화로 배포 완료
