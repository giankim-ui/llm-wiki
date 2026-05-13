# 통합 프로젝트 리서치 고도화: Meeting Dashboard × OKR Matrix
> 작성일: 2026-04-21 | 기반: research-v2.md | 업데이트: 수정 노트 5건 반영 + 코드 탐색 사실 정정

---

## 0. 프로젝트 맥락 (Why)

풀무원 인사혁신팀은 두 개의 독립적인 로컬 웹앱을 운용 중이다.
- **meeting_dashboard.html**: 회의 TODO 관리 + 검색 + 인사이트 분석 + AX혁신 제언
- **OKR Matrix App**: 개인 OKR 설정 및 아이젠하워 매트릭스 기반 우선순위 관리

현재는 두 앱이 완전히 분리되어 있어 ① 동선이 분산되고, ② 데이터가 통합되지 않으며,
③ 팀 단위 협업(배분·피드백)이 불가능하다. 이번 프로젝트는 이를 하나의 통합 플랫폼으로 묶는 작업이다.

---

## ⚠️ 0-A. 현재 저장 방식 정정

> **코드 탐색으로 확인된 사실**: 두 앱 모두 SQLite가 아닌 **브라우저 localStorage**를 사용 중이다.

| 앱 | 실제 저장 방식 | 비고 |
|---|---|---|
| meeting_dashboard.html | 브라우저 localStorage | 6개 키 (hr_todos 등) |
| OKR Matrix App | 브라우저 localStorage | 단일 키 `okr-matrix-v2` (전체 상태 JSON) |

SQLite, sql.js, IndexedDB — 두 앱 모두 사용 없음. 코드 전수 검색 결과.

---

## 1. 현재 앱 현황 분석

### 1-1. meeting_dashboard.html 현황

| 항목 | 내용 |
|------|------|
| 경로 | `Smartmeeting - 문서\10_HR_IN_Meeting_DB\meeting_dashboard.html` |
| 기술 스택 | HTML5 / CSS3 / Vanilla JavaScript (빌드 도구 없음) |
| 상태 관리 | 브라우저 localStorage (6개 키) |
| 현재 탭 | TODO / 검색 / 분석+AX혁신 제언 (총 3개) |
| 스타일 | CSS 변수 시스템 (`--primary`: #1e3a5f 네이비, `--accent`: #e85d26 오렌지) |
| 제약 | 단일 HTML 파일 유지 필수, 외부 CDN 추가 시 사용자 승인 필요 |
| 배포 | 파일 저장 = 배포 (OneDrive 자동 동기화) |

**실제 탭 HTML 구조 (코드 탐색으로 확인):**
```
.tabs
  ├── #btn-todo     → #tab-todo      (TODO 관리)
  ├── #btn-search   → #tab-search    (회의록 검색)
  └── #btn-analysis → #tab-analysis  (분석 + AX혁신 제언 포함)
  [신규] #btn-okr   → #tab-okr      ← #btn-analysis 바로 다음에 삽입
```

> ⚠️ v2.0 수정: AX혁신 제언은 별도 탭이 아니라 분석 탭 내부에 포함됨. 탭 총 3개.

**localStorage 키 목록 (코드 탐색으로 확인):**

| 키 이름 | 용도 |
|---------|------|
| `hr_todos` | TODO 과제 목록 (주요 데이터) |
| `hr_deleted_default_ids` | 삭제된 기본값 Task ID 목록 |
| `hr_last_update` | 마지막 업데이트 타임스탬프 |
| `hr_banner_dismissed` | 아침 9:10 배너 무시 상태 |
| `hr_analysis_banner_dismissed` | 분석 탭 배너 무시 카운트 |
| `hr_todo_custom_classification` | 커스텀 과제 분류 설정 JSON |

---

### 1-2. OKR Matrix App 현황

| 항목 | 내용 |
|------|------|
| 경로 | `!Claude\OKR\okr-matrix-app\` |
| 기술 스택 | TypeScript, esbuild, Vanilla DOM (React 아님) |
| 빌드 결과물 | `bundle.html` (단일 파일, 84.8KB, 2026-04-17 기준 존재) |
| 빌드 명령어 | `python build_bundle_html.py` (루트 디렉토리 실행) |
| 상태 관리 | 브라우저 localStorage (`okr-matrix-v2` 단일 키) |
| 현재 구조 | 단일 사용자, 개인 OKR + 아이젠하워 매트릭스 |

> ⚠️ v2.0 수정: 빌드 명령어는 `bash scripts/bundle-artifact.sh`가 아니라 `python build_bundle_html.py`.
> 빌드 동작: CSS 3개(`styles.css`, `okr-section.css`, `task-section.css`) + `bundle.js` → 인라인 삽입 → `bundle.html` 생성.

---

### 1-3. 두 앱의 기술 충돌 지점

| 충돌 영역 | meeting_dashboard | OKR App | 해결 방향 |
|-----------|------------------|---------|-----------|
| 기술 스택 | Vanilla JS | TypeScript + esbuild | iframe으로 격리 |
| CSS 시스템 | CSS 변수 (네이비/오렌지) | 자체 CSS 시스템 | iframe 내부 독립 |
| localStorage 키 | 독자적 키 체계 | `okr-matrix-v2` | Supabase로 통합 후 각 앱 독립 유지 |
| 파일 위치 | `Smartmeeting - 문서\10_HR_IN_Meeting_DB\` | `!Claude\OKR\okr-matrix-app\` | bundle.html 복사본 동일 폴더 배치 |

---

## 2. 기능 1: OKR Matrix 탭 통합

### 결정 사항
- **방식**: iframe 분리형 (사용자 확인 완료)
- **이유**: 기술 스택 충돌 없음, 각 앱 독립적 유지보수, 구현 속도 빠름

### 구현 절차

**Step 1 — bundle.html 빌드 및 배치**
```
OKR 프로젝트 폴더 루트에서:
  python build_bundle_html.py
  → bundle.html 생성 (또는 기존 84.8KB 파일 재사용)

생성된 bundle.html을 아래 경로로 복사:
  Smartmeeting - 문서\10_HR_IN_Meeting_DB\okr_matrix.html
```
> ⚠️ 복사 이유: 브라우저는 `file://` 프로토콜에서 다른 폴더의 파일을 iframe으로 불러오는 것을 보안상 차단한다. 반드시 meeting_dashboard.html과 **같은 폴더**에 있어야 한다.

**Step 2 — meeting_dashboard.html에 탭 버튼 추가**
```html
<!-- .tabs 안, 분석 탭 버튼 바로 다음에 삽입 -->
<button class="tab-btn" id="btn-okr" onclick="switchTab('okr')">
  📊 OKR Matrix
</button>
```

**Step 3 — 탭 콘텐츠 영역 추가**
```html
<!-- 기존 탭 콘텐츠들 다음에 추가 -->
<div id="tab-okr" class="tab-content">
  <iframe
    id="okr-frame"
    src="about:blank"
    style="width:100%; height:calc(100vh - 120px); border:none; display:block;"
    loading="lazy"
  ></iframe>
</div>
```

**Step 4 — switchTab() 함수에 'okr' 케이스 등록**
```javascript
// 기존 switchTab 함수에 'okr' 추가
// lazy load: 탭 최초 클릭 시에만 iframe src 설정
case 'okr':
  const frame = document.getElementById('okr-frame');
  if (!frame.src || frame.src === 'about:blank') {
    frame.src = 'okr_matrix.html';
  }
  break;
```

### 유지보수 시나리오
OKR 앱이 업데이트될 때마다:
1. `python build_bundle_html.py` 실행
2. 생성된 `bundle.html`을 `okr_matrix.html`로 복사 (덮어쓰기)

> **자동화 옵션**: Windows 배치 파일로 이 두 단계를 원클릭 처리 가능 (Phase 2에서 구현)

### 리스크
| 리스크 | 원인 | 완화 방안 |
|--------|------|-----------|
| iframe 로딩 느림 | 번들 크기 (~85KB) | `src="about:blank"` + 최초 클릭 시 로드 |
| 탭 전환 시 OKR 앱 상태 초기화 | iframe DOM 재생성 | display:none으로 숨기고 제거하지 않음 |
| Supabase 연동 후 데이터 공유 | iframe ↔ 부모 간 직접 변수 접근 불가 | postMessage API 또는 Supabase 실시간 구독으로 해결 |

---

## 2-A. Claude.ai 공유 아티팩트 기능 분석 (P4a 기반)

### 핵심 특성

| 항목 | 내용 | 설계 영향 |
|------|------|---------|
| **localStorage** | CSP 정책으로 **사용 불가** | 아티팩트 전용 스토리지 API로 대체 |
| **개인 스토리지** | 사용자별 독립 데이터 (최대 20MB) | 각 팀원의 개인 상태 유지 가능 |
| **공유 스토리지** | 모든 사용자가 같은 데이터를 읽고 쓸 수 있음 | 팀 공유 TODO/OKR 데이터에 적합 |
| **플랜 요구사항** | Persistent storage = Pro/Max/Team/Enterprise 필요 | P4a 전 플랜 확인 필수 |
| **실시간 동기화** | 네이티브 실시간 동기화 없음 | 새로고침 시 최신 공유 데이터 반영 (준실시간) |
| **공유 방식** | 공개 링크 (Claude 계정 없이도 접속 가능) | 팀원 누구나 URL로 접속·입력 가능 |

### P4a 구현 방식
- 공유 스토리지(shared storage) 사용 → 팀원 전체가 같은 TODO/OKR 열람·편집
- 초기 데이터: localStorage에서 JSON 추출 → 아티팩트에 붙여넣기로 시드
- 사용자 식별: 공유 스토리지에 `currentUser` 저장 (드롭다운 선택)
- 한계 명시: 실시간 동기화 없음, 새로고침으로 최신 상태 확인

---

## 3. 기능 2: Supabase 외부 DB 구축

### 통합 DB 스키마 설계

```sql
-- ① 팀 구성원 테이블
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  role        TEXT NOT NULL
                CHECK (role IN ('팀장', '팀원')),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ② OKR 목표(Objective) 테이블
CREATE TABLE objectives (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       TEXT NOT NULL,
  description TEXT,
  period      TEXT,
  owner_id    UUID REFERENCES users(id),
  progress    INT  DEFAULT 0
                CHECK (progress BETWEEN 0 AND 100),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ③ 핵심결과(Key Result) 테이블
CREATE TABLE key_results (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  objective_id    UUID NOT NULL REFERENCES objectives(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  target_value    NUMERIC,
  current_value   NUMERIC DEFAULT 0,
  unit            TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ④ Task / Initiative 테이블
CREATE TABLE initiatives (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key_result_id   UUID REFERENCES key_results(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  status          TEXT DEFAULT '대기'
                    CHECK (status IN ('대기', '진행중', '완료')),
  quadrant        TEXT,
  due_date        DATE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ⑤ Task 배분 테이블 (팀장 → 팀원, 다대다)
CREATE TABLE task_assignments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  initiative_id   UUID NOT NULL REFERENCES initiatives(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES users(id),
  assigned_by     UUID NOT NULL REFERENCES users(id),
  assigned_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ⑥ 코멘트 테이블 (360 피드백 기반 데이터)
CREATE TABLE comments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  initiative_id   UUID NOT NULL REFERENCES initiatives(id) ON DELETE CASCADE,
  author_id       UUID NOT NULL REFERENCES users(id),
  content         TEXT NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ⑦ 회의 TODO 테이블
CREATE TABLE todos (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title                 TEXT NOT NULL,
  status                TEXT DEFAULT '진행중'
                          CHECK (status IN ('진행중', '완료', '보류')),
  priority              TEXT,
  assignee_id           UUID REFERENCES users(id),
  due_date              DATE,
  linked_initiative_id  UUID REFERENCES initiatives(id),
  source                TEXT DEFAULT '회의',
  created_at            TIMESTAMPTZ DEFAULT NOW()
);
```

**ERD 관계 요약:**
```
users
  ├─[1:N]─ objectives (owner_id)
  ├─[M:N]─ initiatives (task_assignments)
  ├─[1:N]─ comments (author_id)
  └─[1:N]─ todos (assignee_id)

objectives
  └─[1:N]─ key_results
              └─[1:N]─ initiatives
                          ├─[M:N]─ users (task_assignments)
                          └─[1:N]─ comments
```

### localStorage → Supabase 마이그레이션 전략

```
마이그레이션 절차:
1. 브라우저 개발자도구 Console에서 localStorage 데이터 추출
   → JSON.stringify(localStorage) 실행 → 결과를 텍스트 파일로 저장

2. 데이터 구조 매핑:
   hr_todos → todos 테이블
   okr-matrix-v2 (JSON 파싱) → objectives / key_results / initiatives 테이블

3. Supabase SQL Editor에서 직접 INSERT 또는 마이그레이션 스크립트(JS) 실행

4. 이전 완료 후 localStorage는 삭제하지 않고 보존
   (앱이 Supabase에서 읽기 성공하면 localStorage 무시하도록 코드 분기)
```

---

## 4. 기능 3: 팀 OKR 배분 시스템

### 사용자 식별 방식 — 2단계 전략

**사용자 요건**: "실시간으로 여러 사람이 볼 수 있고 수정할 수 있어야 함"

→ **2단계 구현 전략**:

| 단계 | 방식 | 실시간 동기화 | 선행 조건 |
|------|------|-------------|---------|
| **P4a (MVP)** | Claude.ai 공유 아티팩트 + 공유 스토리지 | 준실시간 (새로고침) | Claude Pro/Team 플랜 |
| **P4 (정식)** | Supabase `users` 테이블 + Realtime | 완전 실시간 | P2 완료 |

> ⚠️ localStorage 기반 사용자 식별(로컬 저장) 방식 **폐기**: localStorage는 아티팩트 환경에서 동작하지 않으며, 팀 공유 요건을 충족할 수 없음.

**P4a UI (아티팩트 공유 스토리지 기반):**
```
[ 인사혁신팀 회의 DB ]        [ 현재: 김팀장 ▼ ]  ← 공유 스토리지에 저장
```
- 드롭다운 선택 → 공유 스토리지의 `currentUser` 업데이트
- 다른 팀원이 새로고침 시 변경된 사용자 뷰 확인 가능

---

### 팀 구조 설정 흐름

처음 앱을 열면 (또는 팀 구성원 없을 때):
```
팀 구성원 설정 화면:
┌────────────────────────────────────┐
│  👥 팀 구성원 설정                  │
│  팀장: [김OO     ]                  │
│  팀원: [이OO ✕] [박OO ✕] [+ 추가]  │
│                    [ 시작하기 ]     │
└────────────────────────────────────┘
```
→ 설정값은 Supabase `users` 테이블에 저장 (P4a에서는 공유 스토리지에 임시 저장)

---

### 팀장의 Task 배분 UI/UX 흐름

```
[팀장 뷰]
OKR Matrix의 Task/Initiative 카드에 "배분" 버튼 추가:

┌─────────────────────────────────────┐
│ 📌 [Task 제목]                [배분] │
│    진행중 | 마감: 5/15               │
│    담당: 이팀원A, 박팀원B             │
└─────────────────────────────────────┘

[배분] 클릭 시 모달:
┌──────────────────────────────┐
│  담당자 선택                  │
│  ☑ 이팀원A  ☑ 박팀원B         │
│  ☐ 최팀원C                   │
│  ─────────────────────────   │
│  배분 단위: ○ Task  ○ 묶음    │
│        [ 배분 저장 ]          │
└──────────────────────────────┘
```

### OKR Matrix 내 Task 뷰 개선

```
[작업자별 필터] 전체 | 김팀장 | 이팀원A | 박팀원B | 최팀원C

[Task 카드 — 업무별 담당자 표기]
┌──────────────────────────────────────┐
│ 📋 AX 교육 시스템 설계                │
│ 담당: [이팀원A] [박팀원B]             │
│ 상태: 🔵 진행중    마감: 5/15         │
│                          💬 3        │  ← 코멘트 수만 표시
└──────────────────────────────────────┘
```

---

## 5. 기능 4: Task 코멘트 & 360 피드백 연계

### 코멘트 기능 설계

**트리거**: Task 카드의 💬 아이콘 클릭 (클릭 전에 코멘트 내용 미표시, 숫자 뱃지만 노출)

**패널 방식**: 슬라이드-오버 (화면 오른쪽에서 밀려 나오는 오버레이 패널)
- Task 목록 위에 오버레이 — 목록을 가려도 무방
- 닫기: × 버튼 또는 패널 외부 클릭

**코멘트 패널 UI:**
```
[💬 클릭 전 — Task 카드]
┌──────────────────────────────────────┐
│ 📋 AX 교육 시스템 설계   💬 3        │  ← 숫자만 표시
│ 담당: [이팀원A] | 진행중             │
└──────────────────────────────────────┘

[💬 클릭 후 — 슬라이드-오버 패널]
                    ┌──────────────────────────────┐
                    │  💬 AX 교육 시스템 설계 (3) × │
                    ├──────────────────────────────┤
                    │  [김팀장]  4/18 14:30         │
                    │  "방향성 확인 부탁해요"         │
                    │                              │
                    │  [이팀원A]  4/19 09:15        │
                    │  "초안 작성 완료했습니다"       │
                    ├──────────────────────────────┤
                    │  [현재: 김팀장 ▼]             │
                    │  ┌──────────────────────┐    │
                    │  │ 코멘트를 입력하세요... │    │
                    │  └──────────────────────┘    │
                    │                   [ 전송 ]   │
                    └──────────────────────────────┘
```

**저장 구조 (Supabase):**
- `comments` 테이블에 `initiative_id` + `author_id` + `content` 저장
- Supabase Realtime으로 실시간 코멘트 업데이트

### 360 피드백 활용 방안

분기말/반기말 시점에 코멘트 데이터를 집계:
```
[360 피드백 리포트 (미래 기능)]
- 팀원별 받은 코멘트 수
- 팀장이 남긴 피드백 패턴
- 협업 횟수 (task_assignments 기준)
→ 향후 별도 "360 진단" 탭으로 확장 가능
```

---

## 6. 구현 로드맵 (Phase별)

| Phase | 내용 | 예상 복잡도 | 선행 조건 |
|-------|------|------------|-----------|
| **P1** | OKR 탭 통합 (iframe) | ★★☆ | bundle.html 이미 존재 (84.8KB) |
| **P2** | Supabase 계정·스키마 생성 | ★☆☆ | (없음) |
| **P4a** | 아티팩트 공유 MVP (Claude.ai 공유 스토리지) | ★★☆ | P1 완료, Pro/Team 플랜 확인 |
| **P3** | 기존 데이터 마이그레이션 | ★★☆ | P2 완료 + localStorage 키 확인됨 |
| **P4** | 사용자 식별·퍼스펙티브 스위처 (Supabase) | ★★☆ | P2 완료 |
| **P5** | TODO → Supabase 연동 | ★★★ | P2, P4 완료 |
| **P6** | OKR → Supabase 연동 | ★★★ | P2, P4 완료 |
| **P7** | 팀장 배분 기능 (Task 배분 UI) | ★★★ | P4, P6 완료 |
| **P8** | Task 코멘트 기능 (슬라이드-오버 패널) | ★★☆ | P5 또는 P6 완료 |
| **P9** | 실시간 업데이트 (Supabase Realtime) | ★★★ | P5, P6 완료 |

**권장 실행 순서**: P1 → P2 → P4a → P3 → P4 → P5 → P6 → P7 → P8 → P9

---

## 7. 기술 리스크 및 완화 방안

| 리스크 | 발생 가능성 | 영향도 | 완화 방안 |
|--------|-----------|--------|-----------|
| iframe 브라우저 차단 (file:// 보안) | 높음 | 높음 | bundle.html을 반드시 같은 폴더에 복사 |
| Claude.ai Pro/Team 플랜 미보유 | 중간 | 중간 | P4a 전 플랜 확인; 미보유 시 P4a 스킵 후 직접 Supabase |
| localStorage → 아티팩트 스토리지 전환 | 중간 | 중간 | localStorage 코드는 아티팩트 외부(HTML 앱)에서만 유지 |
| Supabase 무료 플랜 한도 초과 | 낮음 | 중간 | 500MB / 50K MAU → 팀 내 사용이면 충분 |
| React/TS 앱 수정 시 TypeScript 빌드 오류 | 중간 | 중간 | 빌드 전 `npm run build` 오류 체크 |
| 실시간 데이터 충돌 (동시 편집) | 중간 | 중간 | Supabase 낙관적 업데이트 + 타임스탬프 기반 충돌 감지 |
| localStorage 스키마와 Supabase 스키마 불일치 | 높음 | 중간 | 마이그레이션 전 실제 키 확인됨 (6개 + okr-matrix-v2) |

---

## 8. 실제 파일 현황 (탐색 완료)

| 파일 | 상태 | 비고 |
|------|------|------|
| `meeting_dashboard.html` 탭 구조 | ✅ 확인 | 3탭 (todo, search, analysis) |
| `meeting_dashboard.html` localStorage 키 | ✅ 확인 | 6개 키 전부 확인 |
| `OKR/okr-matrix-app/bundle.html` | ✅ 존재 | 84.8KB, 2026-04-17 |
| `OKR/okr-matrix-app/src/` 구조 | ✅ 확인 | 10개 TS 파일 |
| OKR localStorage 키 | ✅ 확인 | `okr-matrix-v2` 단일 키 |
| 빌드 스크립트 | ✅ 확인 | `python build_bundle_html.py` |
| AX혁신 제언 데이터 방식 | ⚠️ P1 시 재확인 | analysis 탭 내부 구조 상세 확인 필요 |

---

## 9. 미결 사항

1. **Claude.ai 플랜 확인**: Pro/Team 플랜이어야 아티팩트 공유 스토리지 사용 가능
   → P4a 착수 전 반드시 확인

2. **AX혁신 제언 데이터 방식**: 하드코딩인지 로컬 파일 기반인지 확인
   → P1 착수 시 analysis 탭 내부 코드 읽기 필요

3. **팀 구성원 이름**: 실제 팀 구성원 이름을 `users` 테이블에 입력 방식
   → 설정 UI에서 직접 입력 (코드에 하드코딩 안 함)

4. **Supabase Realtime 범위**: 모든 데이터 실시간 동기화 vs 코멘트+Task 상태만
   → 권장: 코멘트 + Task 상태 변경만 Realtime (성능·복잡도 균형)

---

## 실행 시 참조 파일 요약

```
meeting_dashboard.html
  경로: Smartmeeting - 문서\10_HR_IN_Meeting_DB\meeting_dashboard.html
  수정 범위: .tabs 영역 + tab-content 영역 + switchTab() 함수

okr_matrix.html (신규 생성)
  경로: Smartmeeting - 문서\10_HR_IN_Meeting_DB\okr_matrix.html
  생성 방법: OKR\okr-matrix-app\ 에서 python build_bundle_html.py → 복사

OKR Matrix 앱 소스
  경로: !Claude\OKR\okr-matrix-app\
  수정 범위: P6 이후 Supabase 연동 시 (TS 소스 수정)
```
