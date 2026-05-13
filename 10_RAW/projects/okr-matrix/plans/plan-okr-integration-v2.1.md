# 구현 계획 v2.1 — 회의록 대시보드 × OKR Matrix 통합

> **작성일**: 2026-04-21
> **버전**: v2.1 (v2.0 대비 Supabase/Postgres 호환 스키마 섹션 추가, 저장 경로 반영)
> **저장 위치(원본)**: `C:\Users\Pulmuone\.claude\plans\composed-squishing-wolf.md`
> **저장 위치(사용자 지정 복사본)**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\interg-m-o\plan\`

---

## 1. 배경 (왜 이 작업을 하는가)

풀무원 인사혁신팀은 두 개의 독립된 웹 앱을 사용하고 있다:

- **`meeting_dashboard.html`** — 회의 기반 TO-DO 관리 (팀 전체가 공유)
- **`okr_matrix.html`** — OKR(성과목표/핵심결과) 관리 (**개인별**로 작성·관리)

현재는 두 앱이 완전히 분리되어 있어 아래 문제가 발생한다:

1. TO-DO 에서 팀원에게 업무를 배분해도 **그 팀원의 OKR 에는 자동 반영되지 않음**
2. 동일 Task 를 여러 팀원에게 공동 배분해도 **각자 따로 관리**되어 진행 상황이 엇갈림
3. 팀장이 다른 팀원의 OKR 진척도를 **한 화면에서 확인할 수 없음**
4. 코멘트 배지 숫자가 입력해도 올라가지 않는 **잠재 버그**
5. 코멘트 **삭제·초기화 기능 부재**

---

## 2. 이번 통합의 목표

1. TO-DO 에서 배분하면 **해당 팀원의 OKR Task 로 자동 연결**
2. 동일 Task 가 여러 팀원에게 배분된 경우 **한 명이 수정하면 다른 팀원에게도 실시간 반영** (양방향 동기화)
3. OKR 탭에서 **다른 사용자로 전환**해 각자의 OKR workflow 확인 가능
4. 코멘트 배지 버그 수정 + **삭제/초기화 기능 추가**
5. **추후 Supabase 마이그레이션이 용이하도록** 데이터 스키마를 Postgres 표준 타입에 맞춰 설계

---

## 3. 확정된 설계 결정

| 항목 | 결정 | 근거 |
|------|------|------|
| TO-DO 탭 | 전체 공유. 사용자 전환과 무관 | TO-DO 는 팀 단위 할일 목록 |
| OKR 탭 | 사용자별 분리. 스위처로 전환 | OKR 은 개인별 관리 원칙 |
| 배분 단위 | OKR **Task** 레벨 | SubTask 는 각 사용자가 내부에서 세분화 |
| 공유 Task | 공용 창고에 1개만 존재, 각 사용자 OKR 은 **참조만** | 양방향 동기화의 단일 원본 확보 |
| 동기화 방식 | 공유 저장소 + 앱 간 알림 신호 | 수정 시 즉시 반영, 서버·외부 API 불필요 |
| 저장 엔진 | **localStorage 유지** (SQLite/IndexedDB 전환은 범위 밖) | 단일 HTML 제약 + 외부 의존성 추가 금지 원칙 |
| 스키마 정규화 | Postgres 표준 타입에 매핑되는 JSON 구조로 재설계 | 추후 Supabase 이관 시 1:1 매핑 가능 |
| 코멘트 배지 | 카드 그리는 함수 상단에서 카운트 계산 후 주입 | 기존 버그(IIFE 내부 치환 미발생) 근본 해결 |
| 코멘트 삭제 | 작성자 본인만 | 다른 사람 발언 무단 삭제 방지 |
| 코멘트 초기화 | 팀장(구성원 목록 첫 번째)만 | 조직적 관리 권한 부여 |

---

## 4. 데이터 저장소 구조 (비개발자용)

브라우저 내 저장소(=사용자 PC 에만 저장되는 영역)에 아래 6개 공간이 생긴다. **저장 값은 Postgres 표준 타입 매핑이 가능한 JSON 스키마**로 구성 (상세 스키마는 §13 참조).

```
[브라우저 로컬 저장소]
│
├── hr_team_members            : 팀 구성원 목록 (기존)
├── hr_current_user            : 현재 로그인한 사용자 (기존)
├── hr_todos                   : TO-DO 전체 목록 (팀 공유, 기존)
├── hr_comments                : TO-DO 코멘트 전체 (팀 공유, 기존)
│
├── hr_shared_tasks            : ★신규★ OKR Task 공용 창고
│     └─ 여러 팀원에게 공유된 Task 의 "본문 원본" 한 벌만 보관
│        { taskId: {제목, 진행률, 메모, 배정자목록, 수정시각} }
│
└── okr-matrix-v2:{사용자명}   : ★사용자별 분리★ 각 사람의 OKR 구조
      └─ KR 안의 tasks 배열에는 taskId 만 저장
         (제목·진행률은 hr_shared_tasks 에서 매번 조회)
```

### 왜 공용 창고 구조인가?

```
[옛 방식: 각자 복사본]              [새 방식: 공용 창고]
팀원 A OKR: Task "X" (진행률 40%)    팀원 A OKR: Task #1 참조
팀원 B OKR: Task "X" (진행률 30%)    팀원 B OKR: Task #1 참조
  ↑ 같은 Task 인데 진행률 달라짐           ↓
                                     hr_shared_tasks[Task #1] = 40%
                                     ↑ 원본 1개 → 누가 보든 같은 값
```

---

## 5. 앱 간 데이터 전달 방식 (결정 확정)

### 선택: **공유 저장소 + 앱 간 알림 신호 하이브리드**

#### 동작 원리

1. **저장**: Task 를 새로 만들거나 수정하면 `hr_shared_tasks` 에 저장 (여기가 원본)
2. **알림**: 회의록 화면(부모) 과 그 안에 삽입된 OKR 화면(iframe) 사이에 "데이터 바뀜" 신호를 전달
3. **재조회**: 신호 받은 쪽은 `hr_shared_tasks` 에서 최신 데이터를 다시 읽어 화면 새로 그림

#### 실제 사용 시나리오

> **예시**: 팀장이 "ERP 명부 정리" TO-DO 를 팀원 A, B 에게 공동 배분

| 단계 | 일어나는 일 |
|------|-----------|
| 1 | 팀장이 배분 버튼 클릭 → A, B 체크, 각자 어느 KR 로 보낼지 선택 |
| 2 | `hr_shared_tasks["task_001"] = { title: "ERP 명부 정리", assignees: ["A","B"], progress: 0 }` 저장 |
| 3 | 팀원 A 의 OKR KR 과 팀원 B 의 OKR KR 에 `"task_001"` 표지판만 꽂힘 |
| 4 | 팀원 A 가 OKR 탭에서 진행률 0→60% 수정 → `hr_shared_tasks["task_001"].progress = 60` |
| 5 | "Task 001 변경됨" 알림 신호 발송 |
| 6 | 스위처로 팀원 B 화면 전환 시 즉시 **60% 로 표시** (같은 원본 참조) |

#### 이 방식을 선택한 이유

- 두 앱이 같은 브라우저 창에서 동작 → 브라우저 저장소 공유 자연스러움
- 공용 원본 1개 → 수정 시 충돌·불일치 원천 차단
- 서버·외부 API 필요 없음 → 오프라인 환경에서도 동작

---

## 6. 실행 단계

### Step 1 — TO-DO 탭 롤백 (사용자 전환 영향 제거)

- `switchUser()` 함수에서 `currentAssigneeFilter` 수정 로직 제거
- TO-DO 탭의 팀원 필터 버튼(`#team-filter-group`) DOM 제거
- 헤더 스위처는 OKR 탭 활성화 시에만 표시 (TO-DO 탭 시 회색/숨김)

### Step 2 — 코멘트 배지 버그 수정

**원인**: `_taskRow()` 함수 내부 1964~1968라인의 IIFE 안에서 `'${t.id}'` 가 리터럴 문자열로 해석되어 항상 카운트 0 반환.

**수정안**:
- IIFE 제거
- 함수 진입 직후 상단에서 `const commentCount = comments.filter(c => c.taskId === t.id).length;` 계산
- Template literal 에 `${commentCount}` 로 주입

### Step 3 — 코멘트 삭제·초기화 기능

- 각 코멘트 항목 옆 `×` 버튼
  - 표시 조건: `c.author === localStorage.getItem('hr_current_user')` (본인 글만)
  - 클릭 시 `hr_comments` 에서 해당 id 제거 → `renderComments()` + `renderTodos()`
- 코멘트 패널 하단 "전체 초기화" 버튼
  - 표시 조건: `hr_current_user === hr_team_members[0]` (팀장만)
  - 클릭 시 `hr_comments` 에서 해당 taskId 전부 제거 → 배지 0 으로 갱신
- 삭제 전 `confirm()` 다이얼로그로 오조작 방지

### Step 4 — OKR Matrix 사용자별 분리

- `okr_matrix.html` 내부 저장/로드 키 변경
  - 기존: `'okr-matrix-v2'`
  - 변경: `'okr-matrix-v2:' + currentUser`
- 첫 실행 시 기존 `'okr-matrix-v2'` 데이터 → `'okr-matrix-v2:{팀장이름}'` 자동 이관 (1회성 마이그레이션)
- URL 파라미터 `?user=홍길동` 수신 → `currentUser` 설정

### Step 5 — 공유 Task 창고 도입

- OKR Matrix 의 Task 처리 로직 수정
  - **쓰기**: Task 본문은 `hr_shared_tasks[taskId]` 에 기록
  - **읽기**: KR.tasks[] 의 taskId → `hr_shared_tasks` 에서 본문 조회 후 렌더링
- 기존 사용자 OKR 안에 끼어있던 Task 들 → 마이그레이션 시 `hr_shared_tasks` 로 이관

### Step 6-0 — 배분 모달 텍스트 줄 바꿈 수정 (UI Hotfix)

**증상**: 팀원 이름(예: "남혁주")과 "Task 개별" 레이블이 2줄로 표시
**원인**: `.modal-content`에 고정 폭 없음 → 모달이 최소 폭으로 수축 + `white-space` 미설정으로 텍스트 노드 줄 바꿈 허용
**수정 파일**: `meeting_dashboard.html`

| # | 위치 | 변경 내용 |
|---|------|---------|
| 1 | `#distribute-modal .modal-content` CSS (line 187) | `width: 300px` 추가 |
| 2 | `#assignee-checkboxes label` CSS (line 193) | `white-space: nowrap` 추가 |
| 3 | "Task 개별" 라디오 `<label>` 인라인 스타일 (line 915) | `white-space:nowrap` 추가 |

---

### Step 6 — 배분 모달 확장 (팀원 + KR 선택)

- 배분 모달 UI 변경
  - 팀원 체크박스 (기존 유지)
  - 체크된 각 팀원 옆에 **해당 팀원의 OKR KR 드롭다운** 표시
  - 예: `☑ 팀원 A [KR 1.2: HR 데이터 정리 ▼]`
- "배분" 저장 시 아래 4개 동작 수행
  1. TO-DO 의 `task.assignments` 업데이트
  2. `hr_shared_tasks[새taskId]` 에 Task 본문 기록 (assignees 배열 포함)
  3. 각 팀원의 OKR `okr-matrix-v2:{팀원명}` 읽어 선택한 KR.tasks 에 taskId 추가
  4. 열려있는 OKR iframe 에 postMessage 로 "데이터 변경" 알림 발송

### Step 7 — 부모 ↔ iframe 알림 파이프라인

- **부모 → iframe**: `iframe.contentWindow.postMessage({type:'OKR_USER_CHANGE', user}, '*')`
- **iframe → 부모**: `window.parent.postMessage({type:'OKR_TASK_UPDATED', taskId}, '*')`
- 양쪽 모두 수신 시 `event.origin` 화이트리스트 검증 (file:// 또는 same-origin)

### Step 8 — 스위처와 iframe 재로드 연동

- 헤더 스위처에서 사용자 선택 → 현재 탭이 OKR 이면 iframe `src` 를 `okr_matrix.html?user={선택자}` 로 재로드
- TO-DO 탭 활성 시 스위처 드롭다운 회색 처리(클릭 무효)

---

## 7. 대상 파일

| 파일 | 경로 | 변경 유형 |
|------|------|---------|
| `meeting_dashboard.html` | `10_HR_IN_Meeting_DB/meeting_dashboard.html` | 수정 (롤백 + 신규 기능) |
| `okr_matrix.html` | `10_HR_IN_Meeting_DB/okr_matrix.html` | 수정 (사용자별 분리 + 공유 창고) |

---

## 8. 위험 평가

| 위험 | 대응 방안 |
|------|---------|
| 기존 OKR 데이터 손실 | 첫 실행 시 `okr-matrix-v2` → `okr-matrix-v2:{팀장}` 자동 이관 (1회성) |
| Task 중복 생성 | 동일 TO-DO 재배분 시 기존 taskId 재사용 (assignments 덮어쓰기) |
| postMessage 보안 | 수신 시 `event.origin` 검증 (same-origin 만 허용) |
| KR 삭제 시 고아 Task 발생 | KR 삭제 시 `hr_shared_tasks` 의 assignees 에서 해당 사용자 제거, 빈 배열이면 Task 삭제 |
| 구현 규모 증가 (500줄 초과 가능) | Step 단위로 분할 실행, 각 Step 후 백업 생성 |
| 스키마 변경 후 Supabase 이관 시 타입 불일치 | §13 매핑표 기반 DDL 자동 생성 스크립트로 검증 |

---

## 9. 검증 계획

| # | 검증 항목 | 합격 기준 |
|---|---------|---------|
| 1 | TO-DO 전체 공유 | 사용자 A → B 전환해도 TO-DO 목록 동일 |
| 2 | OKR 개인별 분리 | 사용자 A → B 전환 시 각자 OKR 로드 |
| 3 | 공유 Task 동기화 | 팀원 A 에서 Task 제목 수정 → 팀원 B 전환 시 수정 반영 |
| 4 | 이중 배분 | 팀원 A, B 동시 배분 시 두 사람 OKR 에 동일 Task 표시 |
| 5 | 코멘트 배지 | 코멘트 입력 즉시 💬 숫자 증가 확인 (TO-DO "ERP 명부" 로 재현 테스트) |
| 6 | 코멘트 삭제 권한 | 본인 코멘트에만 × 버튼 표시 |
| 7 | 코멘트 초기화 권한 | 팀장 로그인 시에만 "전체 초기화" 버튼 표시 |
| 8 | 회귀 테스트 | TODO 편집, 검색, 분석 탭 정상 동작 |
| 9 | Postgres 호환 JSON 구조 | 각 localStorage 값이 §13 스키마와 일치 (JSON.parse 후 필드 유효성 확인) |

---

## 10. 예상 규모

| Step | 라인 증감 |
|------|--------|
| Step 1 (TO-DO 롤백) | -40 |
| Step 2 (배지 버그 수정) | +5 |
| Step 3 (코멘트 삭제/초기화) | +60 |
| Step 4 (OKR 사용자별 분리) | +80 |
| Step 5 (공유 Task 창고) | +120 |
| Step 6 (배분 모달 확장) | +100 |
| Step 7 (postMessage 파이프라인) | +40 |
| Step 8 (스위처 재연동) | +20 |
| **합계** | **+385** |

- meeting_dashboard.html: 2,577 → 약 2,690줄
- okr_matrix.html: 기존 약 2,100줄 → 약 2,300줄

---

## 11. 백업

- 백업 ID: **RP-20260421-{실행시각}**
- 백업 파일
  - `.claude/backups/meeting_dashboard_{YYYYMMDD-HHMMSS}.html`
  - `.claude/backups/okr_matrix_{YYYYMMDD-HHMMSS}.html`
- Execute 실패 시 이 파일들로 롤백

---

## 12. 이 계획 마크다운 저장 경로

### 원본 저장 경로 (플랜 시스템 기본)
```
C:\Users\Pulmuone\.claude\plans\composed-squishing-wolf.md
```

### 사용자 지정 복사본 저장 경로 (프로젝트 아카이브용)
```
C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\interg-m-o\plan\plan-okr-integration-v2.1.md
```

두 경로 모두 동일 내용을 담는다. 원본은 플랜 모드 시스템이 관리하고, 복사본은 OneDrive 동기화로 팀 아카이브에 보관된다. (복사 작업은 플랜 승인 후 Execute 단계 진입 시 자동 수행)

---

## 13. Supabase / Postgres 호환 스키마 설계 (이번 기회에 정규화)

> **목적**: 현재는 localStorage 기반이지만, 추후 Supabase (Postgres) 로 이관 시 1:1 매핑이 가능하도록 **JSON 값의 필드 타입을 Postgres 표준 타입에 맞춰** 설계한다.

### 13.1 엔진 선택 검토 결과

| 후보 | 결론 | 사유 |
|------|------|------|
| **SQLite (sql.js)** | ❌ 범위 밖 | 단일 HTML 제약 + 외부 CDN 의존성 도입 (사용자 승인 필요) |
| **IndexedDB** | ❌ 범위 밖 | 비동기 API 전면 전환 → 기존 코드 대폭 재작성 필요 |
| **localStorage + Postgres 호환 JSON** | ✅ 채택 | 현재 구조 유지 + 스키마만 정규화 → 마이그레이션 비용 최소 |

> SQLite 전환은 "추후 로드맵" 으로 분리. 이번 범위에서는 **스키마 정규화만** 수행.

### 13.2 Postgres 타입 매핑 원칙

| JSON 필드 형태 | Postgres 타입 | 비고 |
|--------------|-------------|------|
| 문자열 ID (UUID v4) | `UUID` | `gen_random_uuid()` 대응 |
| 일반 문자열 | `TEXT` | VARCHAR 대신 TEXT 통일 |
| 정수 | `INTEGER` | 진행률 등 0~100 범위는 `SMALLINT` 도 가능 |
| 실수 | `NUMERIC(5,2)` | 백분율 정밀도 필요 시 |
| ISO-8601 타임스탬프 문자열 | `TIMESTAMPTZ` | UTC + 타임존 포함 |
| 참/거짓 | `BOOLEAN` | |
| 배열/객체 | `JSONB` | 정규화 어려운 구조 |
| 외래키 참조 | `UUID REFERENCES ...` | Supabase RLS 적용 가능 |

### 13.3 localStorage 키 ↔ Postgres 테이블 매핑

#### (1) `hr_team_members` → `team_members`
```sql
CREATE TABLE team_members (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL UNIQUE,
  role       TEXT NOT NULL CHECK (role IN ('lead', 'member')),
  sort_order INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```
**JSON 형태** (localStorage):
```json
[
  { "id": "uuid", "name": "김상일", "role": "lead", "sort_order": 0 },
  { "id": "uuid", "name": "박지은", "role": "member", "sort_order": 1 }
]
```
> 현재 구조는 단순 문자열 배열 `["팀장","팀원A"]` → 객체 배열로 **업그레이드 필요**. 첫 번째 항목 role='lead' 컨벤션.

#### (2) `hr_current_user` → (세션 상태, 마이그레이션 대상 아님)
Supabase 에서는 `auth.uid()` 로 대체됨.

#### (3) `hr_todos` → `todos`
```sql
CREATE TABLE todos (
  id          UUID PRIMARY KEY,
  subject     TEXT NOT NULL,
  detail      TEXT,
  status      TEXT NOT NULL CHECK (status IN ('미시작','진행중','완료','보류')),
  progress    SMALLINT NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  source      TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE todo_assignments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  todo_id     UUID NOT NULL REFERENCES todos(id) ON DELETE CASCADE,
  assignee    TEXT NOT NULL REFERENCES team_members(name),
  assigned_by TEXT NOT NULL REFERENCES team_members(name),
  assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (todo_id, assignee)
);
```
**JSON 형태** (localStorage):
```json
[
  {
    "id": "uuid",
    "subject": "ERP 명부 정리",
    "detail": "...",
    "status": "진행중",
    "progress": 40,
    "source": "20260403_01",
    "created_at": "2026-04-03T10:00:00Z",
    "updated_at": "2026-04-21T14:30:00Z",
    "assignments": [
      { "assignee": "박지은", "assigned_by": "김상일", "assigned_at": "2026-04-21T14:30:00Z" }
    ]
  }
]
```

#### (4) `hr_comments` → `task_comments`
```sql
CREATE TABLE task_comments (
  id          UUID PRIMARY KEY,
  task_id     UUID NOT NULL,  -- todos.id 또는 shared_tasks.id 참조
  author      TEXT NOT NULL REFERENCES team_members(name),
  content     TEXT NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_comments_task ON task_comments(task_id);
```
**JSON 형태** (이미 스키마 일치 상태):
```json
[
  { "id": "uuid", "task_id": "uuid", "author": "박지은", "content": "...", "created_at": "..." }
]
```
> 필드명 `taskId` → `task_id` (snake_case) 로 통일 권장.

#### (5) `hr_shared_tasks` → `shared_tasks` + `shared_task_assignees`
```sql
CREATE TABLE shared_tasks (
  id            UUID PRIMARY KEY,
  title         TEXT NOT NULL,
  memo          TEXT,
  progress      SMALLINT NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  is_operational BOOLEAN NOT NULL DEFAULT false,
  origin_todo_id UUID REFERENCES todos(id),  -- TO-DO에서 배분된 경우 역추적
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE shared_task_assignees (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id      UUID NOT NULL REFERENCES shared_tasks(id) ON DELETE CASCADE,
  assignee     TEXT NOT NULL REFERENCES team_members(name),
  kr_id        UUID REFERENCES key_results(id),  -- 어느 KR 에 할당되었는지
  assigned_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (task_id, assignee)
);
```
**JSON 형태** (localStorage):
```json
{
  "task_001": {
    "id": "task_001",
    "title": "ERP 명부 정리",
    "memo": "",
    "progress": 40,
    "is_operational": false,
    "origin_todo_id": "todo_xyz",
    "created_at": "...",
    "updated_at": "...",
    "assignees": [
      { "assignee": "박지은", "kr_id": "kr_aaa", "assigned_at": "..." },
      { "assignee": "이호찬", "kr_id": "kr_bbb", "assigned_at": "..." }
    ]
  }
}
```

#### (6) `okr-matrix-v2:{사용자명}` → `okrs` + `key_results` + `sub_tasks`
```sql
CREATE TABLE okrs (
  id          UUID PRIMARY KEY,
  owner       TEXT NOT NULL REFERENCES team_members(name),
  objective   TEXT NOT NULL,
  period      TEXT,  -- '2026-Q2' 등
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (owner, period)
);

CREATE TABLE key_results (
  id          UUID PRIMARY KEY,
  okr_id      UUID NOT NULL REFERENCES okrs(id) ON DELETE CASCADE,
  kr_no       SMALLINT NOT NULL,
  title       TEXT NOT NULL,
  progress    SMALLINT NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  sort_order  SMALLINT NOT NULL DEFAULT 0
);

-- Task 는 shared_tasks 로 통합 (중복 제거)
-- KR → Task 관계는 shared_task_assignees.kr_id 로 관리

CREATE TABLE sub_tasks (
  id           UUID PRIMARY KEY,
  task_id      UUID NOT NULL REFERENCES shared_tasks(id) ON DELETE CASCADE,
  title        TEXT NOT NULL,
  em_quadrant  TEXT CHECK (em_quadrant IN ('Q1','Q2','Q3','Q4')),
  sort_order   SMALLINT NOT NULL DEFAULT 0,
  start_date   DATE,
  due_date     DATE,
  is_completed BOOLEAN NOT NULL DEFAULT false
);
```

### 13.4 마이그레이션 경로 (추후 로드맵)

| 단계 | 내용 | 도구 |
|------|------|------|
| Phase 1 | 현 localStorage 스키마를 §13.3 구조로 정규화 (**이번 구현 범위**) | 본 플랜 Step 1~8 |
| Phase 2 | 브라우저에서 Supabase JS Client 추가 + 이중 저장(local + remote) | 별도 작업 |
| Phase 3 | localStorage → Supabase 일회성 마이그레이션 스크립트 | `pg_dump` + 커스텀 스크립트 |
| Phase 4 | RLS(Row Level Security) 정책 설정 | Supabase Dashboard |
| Phase 5 | localStorage 제거, Supabase 단일 소스화 | 별도 작업 |

### 13.5 이번 구현 시 적용할 구체적 네이밍 규칙

1. **필드명**: 모든 신규 JSON 필드는 `snake_case` (Postgres 관례)
   - 예: `createdAt` → `created_at`, `taskId` → `task_id`, `isOperational` → `is_operational`
2. **ID**: 모든 ID 는 UUID v4 문자열
3. **타임스탬프**: ISO-8601 + 'Z' (UTC) — 예: `"2026-04-21T14:30:00Z"`
4. **상태 enum**: 한글 그대로 유지 (현재 UI 와 호환), Postgres 에서는 `CHECK` 제약으로 구현
5. **기존 필드 호환**: 기존 camelCase 필드가 있는 항목은 **쓰기는 snake_case, 읽기는 둘 다 허용** (dual-read 헬퍼 함수 도입)
   ```javascript
   function getField(obj, name) {
     return obj[name] ?? obj[camelize(name)];  // snake_case 우선
   }
   ```

### 13.6 이번 스키마 정규화의 구현 범위

| 적용 여부 | 항목 |
|---------|------|
| ✅ 적용 | `hr_shared_tasks` (신규) — 처음부터 snake_case JSONB 구조로 작성 |
| ✅ 적용 | `hr_comments` 의 `taskId` → `task_id` 로 리네이밍 + 기존 데이터 마이그레이션 |
| ✅ 적용 | `hr_team_members` 를 객체 배열 `[{name, role, sort_order}]` 로 업그레이드 |
| ✅ 적용 | `hr_todos.assignments` 의 `assignedAt/assignedBy` → `assigned_at/assigned_by` 리네이밍 |
| ⏸ 보류 | OKR Matrix 내부 스키마 (`okr-matrix-v2:*`) 의 전면 리네이밍 — 분량이 커서 별도 Phase |
| ⏸ 보류 | SQLite/IndexedDB 엔진 전환 — 외부 의존성 승인 필요, 범위 밖 |

---
