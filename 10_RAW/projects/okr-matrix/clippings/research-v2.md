# 통합 프로젝트 리서치 고도화: Meeting Dashboard × OKR Matrix
> 작성일: 2026-04-20 | 대상 파일: `interg-m-o/plan/research.md`

---

## 0. 프로젝트 맥락 (Why)

풀무원 인사혁신팀은 두 개의 독립적인 로컬 웹앱을 운용 중이다.
- **meeting_dashboard.html**: 회의 TODO 관리 + 검색 + 인사이트 분석 + AX혁신 제언
- **OKR Matrix App**: 개인 OKR 설정 및 아이젠하워 매트릭스 기반 우선순위 관리

현재는 두 앱이 완전히 분리되어 있어 ① 동선이 분산되고, ② 데이터가 통합되지 않으며,
③ 팀 단위 협업(배분·피드백)이 불가능하다. 이번 프로젝트는 이를 하나의 통합 플랫폼으로 묶는 작업이다.

---

## 1. 현재 앱 현황 분석

### 1-1. meeting_dashboard.html 현황

| 항목 | 내용 |
|------|------|
| 경로 | `Smartmeeting - 문서\10_HR_IN_Meeting_DB\meeting_dashboard.html` |
| 기술 스택 | HTML5 / CSS3 / Vanilla JavaScript (빌드 도구 없음) |
| 상태 관리 | localStorage + 인라인 JS 변수 |
| 현재 탭 | TODO / 검색 / 분석 / AX혁신 제언 (총 4개 이상) |
| 스타일 | CSS 변수 시스템 (`--primary`: #1e3a5f 네이비, `--accent`: #e85d26 오렌지) |
| 제약 | 단일 HTML 파일 유지 필수, 외부 CDN 추가 시 사용자 승인 필요 |
| 배포 | 파일 저장 = 배포 (OneDrive 자동 동기화) |

**현재 탭 HTML 구조 (추정 — 구현 전 확인 필요):**
```
.tabs
  ├── #btn-todo     → #tab-todo
  ├── #btn-search   → #tab-search
  ├── #btn-analysis → #tab-analysis
  └── #btn-ax       → #tab-ax  ← "AX혁신 제언" (CSS 'D8' 주석으로 확인됨)
  [신규] #btn-okr   → #tab-okr  ← 이 위치에 삽입
```

### 1-2. OKR Matrix App 현황

| 항목 | 내용 |
|------|------|
| 경로 | `!Claude\OKR\okr-matrix-app\` |
| 기술 스택 | React 18, TypeScript, Tailwind CSS, shadcn/ui |
| 빌드 결과물 | `bundle.html` (단일 파일로 컴파일) |
| 빌드 명령어 | `bash scripts/bundle-artifact.sh` |
| 상태 관리 | localStorage (React state + persist) |
| 현재 구조 | 단일 사용자, 개인 OKR + 아이젠하워 매트릭스 |

### 1-3. 두 앱의 기술 충돌 지점

| 충돌 영역 | meeting_dashboard | OKR App | 해결 방향 |
|-----------|------------------|---------|-----------|
| 기술 스택 | Vanilla JS | React 18 + TS | iframe으로 격리 |
| CSS 시스템 | CSS 변수 (네이비/오렌지) | Tailwind + shadcn/ui | iframe 내부 독립 |
| localStorage 키 | 독자적 키 체계 | 독자적 키 체계 | Supabase로 통합 후 각 앱 독립 유지 |
| 파일 위치 | `Smartmeeting - 문서\10_HR_IN_Meeting_DB\` | `!Claude\OKR\okr-matrix-app\` | bundle.html 복사본 동일 폴더 배치 |

---

## 2. 기능 1: OKR Matrix 탭 통합

### 결정 사항
- **방식**: iframe 분리형 (사용자 확인 완료)
- **이유**: 기술 스택 충돌 없음, 각 앱 독립적 유지보수, 구현 속도 빠름

### 구현 절차

**Step 1 — bundle.html 빌드 및 배치**
```
OKR 프로젝트 폴더에서:
  bash scripts/bundle-artifact.sh
  → bundle.html 생성

생성된 bundle.html을 아래 경로로 복사:
  Smartmeeting - 문서\10_HR_IN_Meeting_DB\okr_matrix.html
```
> ⚠️ 복사 이유: 브라우저는 `file://` 프로토콜에서 다른 폴더의 파일을 iframe으로 불러오는 것을 보안상 차단한다. 반드시 meeting_dashboard.html과 **같은 폴더**에 있어야 한다.

**Step 2 — meeting_dashboard.html에 탭 버튼 추가**
```html
<!-- .tabs 안, AX혁신 제언 탭 바로 다음에 삽입 -->
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
    src="okr_matrix.html"
    style="width:100%; height:calc(100vh - 120px); border:none; display:block;"
    loading="lazy"
  ></iframe>
</div>
```

**Step 4 — switchTab() 함수에 'okr' 케이스 등록**
```javascript
// 기존 switchTab 함수에 'okr' 추가
// (lazy load: 탭 최초 클릭 시에만 iframe src 설정)
case 'okr':
  const frame = document.getElementById('okr-frame');
  if (!frame.src || frame.src === 'about:blank') {
    frame.src = 'okr_matrix.html';
  }
  break;
```

### 유지보수 시나리오
OKR 앱이 업데이트될 때마다:
1. `bash scripts/bundle-artifact.sh` 실행
2. 생성된 bundle.html을 `okr_matrix.html`로 복사 (덮어쓰기)

> **자동화 옵션**: Windows 배치 파일로 이 두 단계를 원클릭 처리 가능 (Phase 2에서 구현)

### 리스크
| 리스크 | 원인 | 완화 방안 |
|--------|------|-----------|
| iframe 로딩 느림 | React 번들 크기 (보통 500KB~2MB) | `loading="lazy"` + 최초 클릭 시 로드 |
| 탭 전환 시 OKR 앱 상태 초기화 | iframe DOM 재생성 | display:none으로 숨기고 제거하지 않음 |
| Supabase 연동 후 데이터 공유 | iframe ↔ 부모 간 직접 변수 접근 불가 | postMessage API 또는 Supabase 실시간 구독으로 해결 |

---

## 3. 기능 2: Supabase 외부 DB 구축

### 통합 DB 스키마 설계

```sql
-- ① 팀 구성원 테이블
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,            -- '김팀장', '이팀원A' 등
  role        TEXT NOT NULL             -- '팀장' | '팀원'
                CHECK (role IN ('팀장', '팀원')),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ② OKR 목표(Objective) 테이블
CREATE TABLE objectives (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       TEXT NOT NULL,
  description TEXT,
  period      TEXT,                     -- 예: '2026-Q2'
  owner_id    UUID REFERENCES users(id),
  progress    INT  DEFAULT 0            -- 0~100
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
  unit            TEXT,                 -- '%', '건', '점' 등
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ④ Task / Initiative 테이블
CREATE TABLE initiatives (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key_result_id   UUID REFERENCES key_results(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  status          TEXT DEFAULT '대기'
                    CHECK (status IN ('대기', '진행중', '완료')),
  quadrant        TEXT,                 -- 아이젠하워 사분면
                    -- 'urgent_important' | 'not_urgent_important'
                    -- | 'urgent_not_important' | 'not_urgent_not_important'
  due_date        DATE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ⑤ Task 배분 테이블 (팀장 → 팀원, 다대다)
CREATE TABLE task_assignments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  initiative_id   UUID NOT NULL REFERENCES initiatives(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES users(id),
  assigned_by     UUID NOT NULL REFERENCES users(id),   -- 배분한 팀장
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
  assignee_id           UUID REFERENCES users(id),  -- 담당 팀원
  due_date              DATE,
  linked_initiative_id  UUID REFERENCES initiatives(id), -- OKR로 연결된 경우
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

사용자 결정: **기존 데이터 이전 (migrate)**

```
마이그레이션 절차:
1. 브라우저 개발자도구 Console에서 localStorage 데이터 추출
   → JSON.stringify(localStorage) 실행 → 결과를 텍스트 파일로 저장

2. 데이터 구조 파악 후 스키마에 맞게 매핑
   (실제 localStorage 키 이름은 아래 '추가 파일 읽기 필요' 항목 참고)

3. Supabase SQL Editor에서 직접 INSERT 또는
   마이그레이션 스크립트(JS) 실행

4. 이전 완료 후 localStorage 는 삭제하지 않고 보존
   (앱이 Supabase에서 읽기 성공하면 localStorage 무시하도록 코드 분기)
```

---

## 4. 기능 3: 팀 OKR 배분 시스템

### 사용자 식별 방식 (결정 사항)

사용자 답변: ㄷ**"내 이름 유지가 기본, 자유롭게 팀원·팀장 업무를 실시간으로 볼 수 있어야 함"**

→ **퍼스펙티브 스위처(Perspective Switcher)** 방식 채택: <사용자 선택은 실시간으로 여러사람이 볼 수 있고 수정할수 있어야 함. 수파베이스 구축 전에는 아티팩트 공유로 대체 가능한지 검토 팔요.>
- localStorage에 현재 사용자 이름 저장 → 앱 재시작해도 유지(로컬스토리지는 본 기능 구현시 고려하지 않음)
- 상단 우측에 "현재: 김팀장 ▼" 드롭다운 → 클릭하면 다른 구성원 선택
- 다른 구성원 선택 시 해당 구성원의 OKR/TODO 뷰로 실시간 전환
- 보안 로그인 없음 (동일 PC/로컬 환경 전제)

**UI 배치:**
```
[ 인사혁신팀 회의 DB ]        [ 현재: 김팀장 ▼ ]  ← 우상단에 추가
```

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
→ 설정값은 Supabase `users` 테이블에 저장

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
│  배분 단위: ○ Task  ○ 묶음(initiative)    │
│        [ 배분 저장 ]          │
└──────────────────────────────┘
```

### OKR Matrix 내 Task 뷰 개선

현재: 진행중 / 완료 토글
변경 후:
```
[작업자별 필터] 전체 | 김팀장 | 이팀원A | 박팀원B | 최팀원C

[Task 카드 — 업무별 담당자 표기]
┌──────────────────────────────────────┐
│ 📋 AX 교육 시스템 설계                │
│ 담당: [이팀원A] [박팀원B]             │
│ 상태: 🔵 진행중    마감: 5/15         │
│                              [💬 3]  │
└──────────────────────────────────────┘
```

---

## 5. 기능 4: Task 코멘트 & 360 피드백 연계

### 코멘트 기능 설계

**트리거**: Task 카드의 💬 아이콘 클릭<task 목록이 어수선하지 않게 아이콘 클릭시에만 코멘트 창이 뜨도록 함>

**코멘트 패널 UI:**
```
┌──────────────────────────────────────────┐
│  💬 [Task 제목] 코멘트 (3)               │
├──────────────────────────────────────────┤
│  [김팀장]  4/18 14:30                    │
│  "방향성 확인 부탁해요. 목요일 리뷰 예정"  │
│                                          │
│  [이팀원A]  4/19 09:15                   │
│  "네, 초안 작성 완료했습니다. 확인해주세요"│
├──────────────────────────────────────────┤
│  [현재: 김팀장 ▼]                        │
│  ┌──────────────────────────────────┐   │
│  │ 코멘트를 입력하세요...            │   │
│  └──────────────────────────────────┘   │
│                              [ 전송 ]   │
└──────────────────────────────────────────┘
```

**저장 구조 (Supabase):**
- `comments` 테이블에 `initiative_id` + `author_id` + `content` 저장
- Supabase Realtime으로 실시간 코멘트 업데이트

### 360 피드백 활용 방안

분기말/반기말 시점에 코멘트 데이터를 집계:
```
[360 피드백 리포트 생성 (미래 기능)]
- 팀원별 받은 코멘트 수
- 팀장이 남긴 피드백 패턴
- 협업 횟수 (task_assignments 기준)
→ 향후 별도 "360 진단" 탭으로 확장 가능
```

---

## 6. 구현 로드맵 (Phase별)

| Phase | 내용 | 예상 복잡도 | 선행 조건 |
|-------|------|------------|-----------|
| **P1** | OKR 탭 통합 (iframe) | ★★☆ | bundle.html 빌드 완료 |
| **P2** | Supabase 계정·스키마 생성 | ★☆☆ | (없음) |
| **P3** | 기존 데이터 마이그레이션 | ★★☆ | P2 완료 + localStorage 키 파악 |
| **P4** | 사용자 식별·퍼스펙티브 스위처 | ★★☆ | P2 완료 |
| **P5** | TODO → Supabase 연동 | ★★★ | P2, P4 완료 |  <아티팩트 공유 적용 고려 할것>
| **P6** | OKR → Supabase 연동 | ★★★ | P2, P4 완료 (React 앱 수정) |<아티팩트 공유 적용 고려 할것>
| **P7** | 팀장 배분 기능 (Task 배분 UI) | ★★★ | P4, P6 완료 |
| **P8** | Task 코멘트 기능 | ★★☆ | P5 또는 P6 완료 |
| **P9** | 실시간 업데이트 (Supabase Realtime) | ★★★ | P5, P6 완료 |

**권장 실행 순서**: P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9

---

## 7. 기술 리스크 및 완화 방안

| 리스크 | 발생 가능성 | 영향도 | 완화 방안 |
|--------|-----------|--------|-----------|
| iframe 브라우저 차단 (file:// 보안) | 높음 | 높음 | bundle.html을 반드시 같은 폴더에 복사 |
| Supabase 무료 플랜 한도 초과 | 낮음 | 중간 | 500MB / 50K MAU → 팀 내 사용이면 충분 |
| React 앱 수정 시 TypeScript 빌드 오류 | 중간 | 중간 | 빌드 전 `npm run build` 오류 체크 |
| 실시간 데이터 충돌 (동시 편집) | 중간 | 중간 | Supabase 낙관적 업데이트 + 타임스탬프 기반 충돌 감지 |
| 기존 localStorage 스키마와 Supabase 스키마 불일치 | 높음 | 중간 | 마이그레이션 전 실제 localStorage 구조 확인 필수 |
| OKR 앱 업데이트 시 bundle.html 복사 누락 | 중간 | 낮음 | Windows 배치 파일로 빌드+복사 자동화 |

---

## 8. 추가 파일 읽기가 필요한 경우 (사유 명시)

아래 파일들은 **현재 시점에는 읽지 않았으나**, 각 Phase 진입 시 반드시 확인이 필요하다.

| 파일 | 읽어야 할 Phase | 이유 |
|------|----------------|------|
| `meeting_dashboard.html` 150~400행 | P1 (탭 통합) | 현재 탭 HTML 구조(버튼·콘텐츠 div ID)와 `switchTab()` 함수 구현 방식을 확인해야 정확한 삽입 위치를 알 수 있음 |
| `meeting_dashboard.html` 400~끝 | P3, P5 | localStorage에 사용 중인 실제 키 이름(예: `todos`, `meetings` 등)을 알아야 마이그레이션 매핑 가능 |
| `OKR/okr-matrix-app/` 디렉토리 | P1 | bundle.html 실제 경로 및 빌드 결과물 존재 여부 확인 |
| `OKR/okr-matrix-app/src/` 소스 | P3, P6 | React 앱의 localStorage 키·데이터 구조 파악 필요 (마이그레이션 + Supabase 연동 시) |
| `OKR/okr-matrix-app/package.json` | P6 | 의존성 버전 확인 (Supabase JS 클라이언트 추가 시 충돌 검토) |
| `.claude/PROJECT_CONTEXT.md` (Smartmeeting) | P1 시작 전 | 파이프라인 Setup 상태 확인 (오케스트레이터 규칙 준수) |

---

## 9. 미결 사항 (구현 전 확인 필요)

1. **bundle.html 현재 상태**: OKR 앱의 bundle.html이 이미 빌드되어 있는가?
   → `OKR/okr-matrix-app/` 디렉토리 내용 확인 필요

2. **meeting_dashboard.html 실제 탭 목록**: AX혁신 제언 외에 탭이 더 있는가?
   → 파일 150행 이후 읽기 필요 (P1 착수 시)

3. **localStorage 키 이름**: 두 앱의 실제 localStorage 저장 키 이름이 무엇인가?
   → 마이그레이션 전 반드시 확인

4. **팀 구성원 이름**: 실제 팀 구성원 이름을 `users` 테이블에 어떻게 입력할 것인가?
   → 설정 UI에서 직접 입력 (코드에 하드코딩 안 함)

5. **Supabase 실시간(Realtime) 범위**: 모든 데이터를 실시간 동기화할 것인가,
   아니면 코멘트와 배분 이벤트만 실시간으로 할 것인가?
   → 권장: 코멘트 + Task 상태 변경만 Realtime (성능·복잡도 균형)

---

## 실행 시 참조 파일 요약

```
meeting_dashboard.html
  경로: Smartmeeting - 문서\10_HR_IN_Meeting_DB\meeting_dashboard.html
  수정 범위: .tabs 영역 + tab-content 영역 + switchTab() 함수 + <head> CDN

okr_matrix.html (신규 생성)
  경로: Smartmeeting - 문서\10_HR_IN_Meeting_DB\okr_matrix.html
  생성 방법: OKR\okr-matrix-app\bundle.html 복사

OKR Matrix 앱 소스
  경로: !Claude\OKR\okr-matrix-app\
  수정 범위: P6 이후 Supabase 연동 시 (React 소스 수정)
```
