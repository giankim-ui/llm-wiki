# 통합 프로젝트 리서치 고도화: Meeting Dashboard × OKR Matrix
> 작성일: 2026-04-21 | 기반: research-v2.1.md → 방향 변경 반영
> 변경: P4a(아티팩트 MVP) 삭제, 퍼스펙티브 스위처 localStorage 복원, 프론트엔드 우선 전략

---

## 0. 프로젝트 맥락 (Why)

풀무원 인사혁신팀은 두 개의 독립적인 로컬 웹앱을 운용 중이다.
- **meeting_dashboard.html**: 회의 TODO 관리 + 검색 + 인사이트 분석 + AX혁신 제언
- **OKR Matrix App**: 개인 OKR 설정 및 아이젠하워 매트릭스 기반 우선순위 관리

현재는 두 앱이 완전히 분리되어 있어 ① 동선이 분산되고, ② 데이터가 통합되지 않으며,
③ 팀 단위 협업(배분·피드백)이 불가능하다. 이번 프로젝트는 이를 하나의 통합 플랫폼으로 묶는 작업이다.

---

## ⚠️ 0-A. 현재 저장 방식 (확인됨)

> **코드 탐색으로 확인된 사실**: 두 앱 모두 **브라우저 localStorage** 사용 중. SQLite 아님.

| 앱 | 저장 방식 | 키 |
|---|---|---|
| meeting_dashboard.html | 브라우저 localStorage | `hr_todos` 등 6개 |
| OKR Matrix App | 브라우저 localStorage | `okr-matrix-v2` 단일 키 |

---

## 1. 현재 앱 현황 분석

### 1-1. meeting_dashboard.html 현황

| 항목 | 내용 |
|------|------|
| 경로 | `Smartmeeting - 문서\10_HR_IN_Meeting_DB\meeting_dashboard.html` |
| 기술 스택 | HTML5 / CSS3 / Vanilla JavaScript (빌드 도구 없음) |
| 상태 관리 | 브라우저 localStorage (6개 키) |
| 현재 탭 | TODO / 검색 / 분석+AX혁신 제언 (총 3개) |
| 스타일 | CSS 변수 (`--primary`: #1e3a5f 네이비, `--accent`: #e85d26 오렌지) |
| 제약 | 단일 HTML 파일 유지 필수 |
| 배포 | 파일 저장 = 배포 (OneDrive 자동 동기화) |

**실제 탭 구조 (코드 탐색 확인):**
```
.tabs
  ├── #btn-todo     → #tab-todo      (TODO 관리)
  ├── #btn-search   → #tab-search    (회의록 검색)
  └── #btn-analysis → #tab-analysis  (분석 + AX혁신 제언 포함)
  [신규] #btn-okr   → #tab-okr      ← #btn-analysis 바로 다음 삽입
```

**localStorage 키 (확인됨):**

| 키 | 용도 |
|----|------|
| `hr_todos` | TODO 과제 목록 (주요 데이터) |
| `hr_deleted_default_ids` | 삭제된 기본값 Task ID |
| `hr_last_update` | 마지막 업데이트 타임스탬프 |
| `hr_banner_dismissed` | 아침 배너 무시 상태 |
| `hr_analysis_banner_dismissed` | 분석 탭 배너 무시 카운트 |
| `hr_todo_custom_classification` | 커스텀 과제 분류 JSON |

---

### 1-2. OKR Matrix App 현황

| 항목 | 내용 |
|------|------|
| 경로 | `!Claude\OKR\okr-matrix-app\` |
| 기술 스택 | TypeScript, esbuild, Vanilla DOM |
| 빌드 결과물 | `bundle.html` (84.8KB, 2026-04-17 기준 존재) |
| 빌드 명령어 | `python build_bundle_html.py` (루트 디렉토리) |
| 상태 관리 | 브라우저 localStorage (`okr-matrix-v2`) |

---

### 1-3. 기술 충돌 지점

| 충돌 영역 | meeting_dashboard | OKR App | 해결 방향 |
|-----------|------------------|---------|-----------|
| 기술 스택 | Vanilla JS | TypeScript + esbuild | iframe으로 격리 |
| CSS 시스템 | CSS 변수 | 자체 CSS | iframe 내부 독립 |
| localStorage | 독자적 키 체계 | `okr-matrix-v2` | Supabase 전환 전까지 독립 유지 |

---

## 2. 기능 1: OKR Matrix 탭 통합

### 결정 사항
- **방식**: iframe 분리형
- **이유**: 기술 스택 충돌 없음, 독립적 유지보수, 구현 속도 빠름

### 구현 절차

**Step 1 — bundle.html 빌드 및 배치**
```
OKR 프로젝트 루트에서:
  python build_bundle_html.py
  → bundle.html 생성 (또는 기존 84.8KB 재사용)

복사:
  OKR\okr-matrix-app\bundle.html
  → Smartmeeting - 문서\10_HR_IN_Meeting_DB\okr_matrix.html
```
> ⚠️ file:// 보안 정책으로 다른 폴더 iframe 불가 → 반드시 같은 폴더에 배치

**Step 2 — 탭 버튼 추가**
```html
<!-- .tabs 안, #btn-analysis 바로 다음 삽입 -->
<button class="tab-btn" id="btn-okr" onclick="switchTab('okr')">
  📊 OKR Matrix
</button>
```

**Step 3 — 탭 콘텐츠 추가**
```html
<div id="tab-okr" class="tab-content">
  <iframe
    id="okr-frame"
    src="about:blank"
    style="width:100%; height:calc(100vh - 120px); border:none; display:block;"
    loading="lazy"
  ></iframe>
</div>
```

**Step 4 — switchTab() 함수에 'okr' 케이스 추가**
```javascript
case 'okr':
  const frame = document.getElementById('okr-frame');
  if (!frame.src || frame.src === 'about:blank') {
    frame.src = 'okr_matrix.html';
  }
  break;
```

### 유지보수
OKR 앱 업데이트 시:
1. `python build_bundle_html.py`
2. `bundle.html` → `okr_matrix.html` 덮어쓰기

---

## 3. 기능 2: Supabase 외부 DB 구축

### 통합 DB 스키마

```sql
CREATE TABLE users (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  role       TEXT NOT NULL CHECK (role IN ('팀장', '팀원')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE objectives (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       TEXT NOT NULL,
  description TEXT,
  period      TEXT,
  owner_id    UUID REFERENCES users(id),
  progress    INT DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE key_results (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  objective_id UUID NOT NULL REFERENCES objectives(id) ON DELETE CASCADE,
  title        TEXT NOT NULL,
  target_value NUMERIC,
  current_value NUMERIC DEFAULT 0,
  unit         TEXT,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE initiatives (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key_result_id UUID REFERENCES key_results(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  status        TEXT DEFAULT '대기' CHECK (status IN ('대기', '진행중', '완료')),
  quadrant      TEXT,
  due_date      DATE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE task_assignments (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  initiative_id UUID NOT NULL REFERENCES initiatives(id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES users(id),
  assigned_by   UUID NOT NULL REFERENCES users(id),
  assigned_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE comments (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  initiative_id UUID NOT NULL REFERENCES initiatives(id) ON DELETE CASCADE,
  author_id     UUID NOT NULL REFERENCES users(id),
  content       TEXT NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE todos (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title                TEXT NOT NULL,
  status               TEXT DEFAULT '진행중' CHECK (status IN ('진행중', '완료', '보류')),
  priority             TEXT,
  assignee_id          UUID REFERENCES users(id),
  due_date             DATE,
  linked_initiative_id UUID REFERENCES initiatives(id),
  source               TEXT DEFAULT '회의',
  created_at           TIMESTAMPTZ DEFAULT NOW()
);
```

### localStorage → Supabase 마이그레이션 전략 (P6~P9 시점)

```
1. 브라우저 Console → JSON.stringify(localStorage) → 텍스트 저장
2. 키 매핑:
   hr_todos        → todos 테이블
   okr-matrix-v2   → objectives / key_results / initiatives 테이블
3. Supabase SQL Editor에서 INSERT 또는 마이그레이션 스크립트 실행
4. localStorage 보존 (읽기 성공 시 무시하도록 코드 분기)
```

---

## 4. 기능 3: 팀 OKR 배분 시스템

### 사용자 식별 방식 — 퍼스펙티브 스위처 (localStorage)

사용자 요건: "내 이름 유지가 기본, 팀원·팀장 업무를 자유롭게 볼 수 있어야 함"

→ **퍼스펙티브 스위처 방식** 채택:
- `localStorage`에 현재 사용자 이름 저장 → 앱 재시작 후에도 유지
- 상단 우측 "현재: 김팀장 ▼" 드롭다운 → 다른 구성원 선택 시 해당 뷰로 전환
- 보안 로그인 없음 (동일 로컬 환경 전제)

> **Supabase 이전 후**: localStorage 저장을 `users` 테이블 기반으로 교체. 실시간 동기화 추가.

**팀 구성원 신규 localStorage 키:**
| 키 | 용도 |
|----|------|
| `hr_current_user` | 현재 선택된 사용자 이름 |
| `hr_team_members` | 팀 구성원 목록 JSON |

**UI 배치:**
```
[ 인사혁신팀 회의 DB ]        [ 현재: 김팀장 ▼ ]  ← 우상단
```

### 팀 구성원 설정 초기 화면
```
┌────────────────────────────────────┐
│  👥 팀 구성원 설정                  │
│  팀장: [김OO     ]                  │
│  팀원: [이OO ✕] [박OO ✕] [+ 추가]  │
│                    [ 시작하기 ]     │
└────────────────────────────────────┘
```

### 팀장의 Task 배분 UI

```
[팀장 뷰 — Task 카드]
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
│  배분 단위: ○ Task  ○ 묶음    │
│        [ 배분 저장 ]          │
└──────────────────────────────┘
```

### Task 뷰 개선 (작업자별 필터)

```
[필터] 전체 | 김팀장 | 이팀원A | 박팀원B | 최팀원C

┌──────────────────────────────────────┐
│ 📋 AX 교육 시스템 설계                │
│ 담당: [이팀원A] [박팀원B]             │
│ 상태: 🔵 진행중    마감: 5/15         │
│                          💬 3        │
└──────────────────────────────────────┘
```

---

## 5. 기능 4: Task 코멘트 & 360 피드백 연계

### 코멘트 기능 설계

**트리거**: Task 카드의 💬 아이콘 클릭 — 클릭 전에는 숫자 뱃지만 표시, 내용 미노출

**패널 방식**: 슬라이드-오버 (화면 우측 오버레이)
- Task 목록을 가려도 무방
- 닫기: × 버튼 또는 외부 클릭

```
[클릭 전 — Task 카드]
┌──────────────────────────────────────┐
│ 📋 AX 교육 시스템 설계   💬 3        │
│ 담당: [이팀원A] | 진행중             │
└──────────────────────────────────────┘

[클릭 후 — 슬라이드-오버]
                    ┌──────────────────────────────┐
                    │  💬 AX 교육 시스템 설계 (3) × │
                    ├──────────────────────────────┤
                    │  [김팀장]  4/18 14:30         │
                    │  "방향성 확인 부탁해요"         │
                    │  [이팀원A]  4/19 09:15        │
                    │  "초안 완료했습니다"            │
                    ├──────────────────────────────┤
                    │  [현재: 김팀장 ▼]             │
                    │  ┌──────────────────────┐    │
                    │  │ 코멘트를 입력하세요... │    │
                    │  └──────────────────────┘    │
                    │                   [ 전송 ]   │
                    └──────────────────────────────┘
```

**저장 (프론트 단계)**: localStorage (`hr_comments_{initiativeId}`)
**저장 (Supabase 이전 후)**: `comments` 테이블 + Supabase Realtime

---

## 6. 구현 로드맵 — 프론트엔드 우선

| Phase | 내용 | 복잡도 | 선행 조건 |
|-------|------|--------|---------|
| **P1** | OKR 탭 통합 (iframe) | ★★☆ | bundle.html 존재 확인됨 |
| **P2** | 퍼스펙티브 스위처 UI (localStorage) | ★★☆ | P1 완료 |
| **P3** | 팀원별 Task 뷰 + 작업자 필터 | ★★☆ | P2 완료 |
| **P4** | 팀장 배분 UI (Task 배분 모달) | ★★★ | P2 완료 |
| **P5** | Task 코멘트 (슬라이드-오버 패널) | ★★☆ | P3 완료 |
| **P6** | Supabase 계정·스키마 생성 | ★☆☆ | P5 완료 (프론트 검증 후) |
| **P7** | 기존 데이터 마이그레이션 | ★★☆ | P6 완료 |
| **P8** | TODO → Supabase 연동 | ★★★ | P6, P7 완료 |
| **P9** | OKR → Supabase 연동 | ★★★ | P6, P7 완료 |
| **P10** | 실시간 업데이트 (Supabase Realtime) | ★★★ | P8, P9 완료 |

**실행 순서**: P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10

---

## 7. 기술 리스크 및 완화 방안

| 리스크 | 가능성 | 영향 | 완화 방안 |
|--------|--------|------|---------|
| iframe 브라우저 차단 (file://) | 높음 | 높음 | bundle.html을 반드시 같은 폴더에 복사 |
| 퍼스펙티브 스위처 데이터 충돌 (같은 PC 다른 사용자) | 낮음 | 낮음 | 로컬 환경 전제 — Supabase 이전 후 해소 |
| Supabase 무료 플랜 한도 | 낮음 | 중간 | 500MB / 50K MAU → 팀 규모로 충분 |
| localStorage 스키마 ↔ Supabase 불일치 | 높음 | 중간 | 키 이름 확인됨 (마이그레이션 사전 매핑) |
| OKR 앱 빌드 오류 | 중간 | 중간 | `npm run build` 타입 체크 후 번들 |
| 실시간 충돌 (동시 편집) | 중간 | 중간 | 낙관적 업데이트 + 타임스탬프 충돌 감지 |

---

## 8. 실제 파일 현황 (탐색 완료)

| 파일 | 상태 | 확인 내용 |
|------|------|---------|
| meeting_dashboard.html 탭 구조 | ✅ | 3탭, analysis 다음에 OKR 삽입 |
| meeting_dashboard.html localStorage | ✅ | 6개 키 전부 확인 |
| OKR bundle.html | ✅ | 84.8KB 존재 (2026-04-17) |
| OKR localStorage 키 | ✅ | `okr-matrix-v2` 단일 키 |
| 빌드 스크립트 | ✅ | `python build_bundle_html.py` |
| AX혁신 제언 데이터 방식 | ⚠️ | P1 착수 시 탭 내부 구조 재확인 필요 |

---

## 9. 미결 사항

1. **팀 구성원 이름**: 실제 팀원 이름 → 설정 UI에서 직접 입력 (하드코딩 없음)
2. **AX혁신 제언 데이터 방식**: 하드코딩 여부 → P1 착수 시 확인
3. **Supabase Realtime 범위**: 코멘트 + Task 상태 변경만 권장 (P10 시점 결정)

---

## 실행 시 참조 파일

```
meeting_dashboard.html
  경로: Smartmeeting - 문서\10_HR_IN_Meeting_DB\meeting_dashboard.html
  수정 범위: .tabs + tab-content + switchTab() + 퍼스펙티브 스위처 UI

okr_matrix.html (신규)
  경로: Smartmeeting - 문서\10_HR_IN_Meeting_DB\okr_matrix.html
  생성: OKR\okr-matrix-app\에서 python build_bundle_html.py → 복사

OKR Matrix 앱 소스
  경로: !Claude\OKR\okr-matrix-app\
  수정 범위: P9 이후 Supabase 연동 시
```
