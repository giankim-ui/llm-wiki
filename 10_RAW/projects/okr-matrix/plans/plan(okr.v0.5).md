# OKR-Matrix 웹 애플리케이션 개발 계획서

> **문서 버전**: 1.0  
> **작성일**: 2026-04-09  
> **기반 문서**: research.md (OKR + Eisenhower Matrix 통합 리서치)

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [핵심 기능 정의](#2-핵심-기능-정의)
3. [기술 스택 및 아키텍처](#3-기술-스택-및-아키텍처)
4. [데이터 모델 설계](#4-데이터-모델-설계)
5. [UI/UX 컴포넌트 설계](#5-uiux-컴포넌트-설계)
6. [개발 단계별 계획](#6-개발-단계별-계획)
7. [성능 최적화 전략](#7-성능-최적화-전략)
8. [테스트 및 품질 보증](#8-테스트-및-품질-보증)
9. [배포 및 유지보수](#9-배포-및-유지보수)
10. [리스크 관리](#10-리스크-관리)

---

## 1. 프로젝트 개요

### 1.1 프로젝트 목적

OKR(Objectives and Key Results)과 아이젠하워 매트릭스(Eisenhower Matrix)를 통합한 웹 애플리케이션 개발. 목표 설정, 태스크 우선순위 지정, 진행 상황 추적을 단일 플랫폼에서 수행할 수 있도록 한다.

### 1.2 핵심 가치 제안

| 구분 | 설명 |
|------|------|
| **목표 정렬** | OKR 프레임워크를 통한 조직/개인 목표의 체계적 관리 |
| **우선순위화** | 아이젠하워 매트릭스 기반 태스크 중요도/긴급도 분류 |
| **진행 추적** | 실시간 진행률 계산 및 시각화 |
| **단순성** | Vanilla JS 기반 최소 기술 스택으로 가벼운 운영 |

### 1.3 비즈니스 목표 예시 (YouTube 사례)

리서치 문서에서 제시된 예시 목표:
- **Objective**: "세계인이 매일 10억 시간 동안 유튜브를 시청하게 만든다"
- **Key Result 1**: 사용자의 하루 평균 시청 시간을 20% 늘린다
- **Key Result 2**: 모바일 트래픽을 2배로 증가시킨다

---

## 2. 핵심 기능 정의

### 2.1 OKR 관리 기능

#### 2.1.1 Objective (목표) 관리
- [x] Objective 생성/수정/삭제
- [x] Objective 상태 관리 (활성/완료/보류)
- [x] 기간 설정 (분기별/월별/사용자 정의)
- [x] 진행률 대시보드

#### 2.1.2 Key Results (핵심 결과) 관리
- [x] KR 생성/수정/삭제 (Objective당 1:N 관계)
- [x] KR 수동 추가 기능
- [x] 진행률 자동 계산 (하위 Task 달성도 기반)
- [x] KR 번호 부여 및 순서 관리

#### 2.1.3 Task (태스크) 관리
- [x] Task 생성/수정/삭제 (KR당 1:N 관계)
- [x] 시작일/마감일 설정
- [x] 메모 기능
- [x] 드래그 앤 드롭 순서 변경

#### 2.1.4 Sub-Task (하위 태스크) 관리
- [x] Sub-Task 생성/수정/삭제 (Task당 1:N 관계, 최소 단위)
- [x] 완료 상태 토글
- [x] 순서(order) 관리
- [x] 개별 기간 설정

### 2.2 아이젠하워 매트릭스 기능

#### 2.2.1 4사분면 분류
```
         긴급함              긴급하지 않음
      ┌─────────────────┬─────────────────┐
 중요  │   Q1: DO        │   Q2: SCHEDULE  │
 함    │   즉시 실행     │   일정 계획     │
      ├─────────────────┼─────────────────┤
 중요  │   Q3: DELEGATE  │   Q4: ELIMINATE │
 하지  │   위임          │   제거/보류     │
 않음  └─────────────────┴─────────────────┘
```

- [x] 드래그 앤 드롭으로 사분면 간 이동
- [x] Task-매트릭스 연동 (OKR Task ↔ Matrix)
- [x] 사분면별 태스크 카운트 표시
- [ ] 자동 분류 추천 (옵션)

### 2.3 실시간 동기화

- [x] OKR 섹션 ↔ Task 섹션 양방향 동기화
- [x] 변경 사항 즉시 반영
- [x] Local Storage 기반 데이터 영속성
- [x] 저장 상태 표시 (저장 중/저장 완료)

---

## 3. 기술 스택 및 아키텍처

### 3.1 기술 스택

| 영역 | 기술 | 선택 이유 |
|------|------|----------|
| **마크업** | HTML5 | 시맨틱 구조, 접근성 |
| **스타일** | CSS3 | 커스텀 프로퍼티, Grid/Flexbox |
| **로직** | Vanilla JavaScript (ES6+) | 의존성 최소화, 빠른 로딩 |
| **저장소** | Local Storage | 서버 불필요, 오프라인 지원 |
| **빌드** | 없음 (또는 선택적 번들러) | 개발 복잡도 최소화 |

### 3.2 디렉토리 구조

```
okr-matrix-app/
├── index.html              # 메인 HTML (단일 페이지)
├── css/
│   ├── styles.css          # 메인 스타일시트
│   ├── okr-section.css     # OKR 섹션 전용 스타일
│   ├── task-section.css    # TASK 섹션 전용 스타일
│   └── components.css      # 공통 컴포넌트 스타일
├── js/
│   ├── app.js              # 애플리케이션 진입점
│   ├── models/
│   │   ├── OKR.js          # OKR 데이터 모델
│   │   ├── Task.js         # Task 데이터 모델
│   │   └── SubTask.js      # SubTask 데이터 모델
│   ├── views/
│   │   ├── OKRView.js      # OKR 섹션 렌더링
│   │   ├── TaskView.js     # Task 섹션 렌더링
│   │   └── MatrixView.js   # 매트릭스 렌더링
│   ├── controllers/
│   │   ├── OKRController.js
│   │   ├── TaskController.js
│   │   └── SyncController.js
│   └── utils/
│       ├── storage.js      # Local Storage 유틸리티
│       ├── dom.js          # DOM 조작 헬퍼
│       └── date.js         # 날짜 처리 유틸리티
├── assets/
│   ├── icons/              # SVG 아이콘
│   └── images/             # 이미지 리소스
└── README.md
```

### 3.3 아키텍처 패턴

**MVC (Model-View-Controller) 패턴 적용**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Model     │◄────│ Controller  │◄────│    View     │
│  (데이터)   │────►│  (로직)     │────►│   (UI)      │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                   ┌───────────────┐
                   │ Local Storage │
                   └───────────────┘
```

---

## 4. 데이터 모델 설계

### 4.1 계층 구조

```
OKR (최상위)
 └── Objective (목표)
      └── Key Results (핵심 결과) [1:N 관계, 수동 추가 가능]
           └── Tasks (태스크) [1:N 관계]
                └── Sub-Tasks (하위 태스크) [1:N 관계, 최소 단위]
```

### 4.2 스키마 정의

#### 4.2.1 OKR 스키마
```javascript
{
  id: "okr_001",
  objective: "세계인이 매일 10억 시간 동안 유튜브를 시청하게 만든다",
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-04-09T00:00:00Z",
  status: "active", // active | completed | on-hold
  period: {
    type: "quarterly", // quarterly | monthly | custom
    startDate: "2026-01-01",
    endDate: "2026-03-31"
  },
  keyResults: ["kr_001", "kr_002", "kr_003"]
}
```

#### 4.2.2 Key Result 스키마
```javascript
{
  id: "kr_001",
  okrId: "okr_001",
  krNo: 1,
  title: "사용자의 하루 평균 시청 시간을 20% 늘린다",
  progress: 0,  // 0-100%, 하위 Task 달성도에 따라 자동 계산
  targetValue: 20,
  currentValue: 0,
  unit: "%",
  tasks: ["task_001", "task_002"]
}
```

#### 4.2.3 Task 스키마
```javascript
{
  id: "task_001",
  krId: "kr_001",
  order: 1,
  title: "영상 추천 알고리즘 개선",
  description: "사용자 맞춤형 추천 정확도 향상",
  status: "in-progress", // pending | in-progress | completed
  priority: "high", // high | medium | low
  matrixQuadrant: "Q1", // Q1 | Q2 | Q3 | Q4
  startDate: "2026-02-08",
  dueDate: "2026-02-22",
  memo: "자유롭게 메모 사항 기재 가능",
  subTasks: ["subtask_001", "subtask_002", "subtask_003"]
}
```

#### 4.2.4 Sub-Task 스키마
```javascript
{
  id: "subtask_001",
  taskId: "task_001",
  order: 1,
  title: "'다음 영상 자동 재생' UI/UX 개선 및 로딩 속도 최적화",
  completed: true,
  startDate: "2026-02-08",
  dueDate: "2026-02-22"
}
```

### 4.3 연동 다이어그램

```
┌─── OKR ─────────────────────────────────────────────────────┐
│      └─── Objective (목표) ─────────────────┐               │
│             │                               │               │
│             ├── KR 1 ◄────────────────────┐ │               │
│             │     │                       │ │               │
│             │     ├── TASK A              │ │               │
│             │     │     ├── Sub-Task A-1  │ │               │
│             │     │     ├── Sub-Task A-2  │ │  연동         │
│             │     │     └── Sub-Task A-3  │ │               │
│             │     │                       │ │               │
│             │     └── TASK B              │ │               │
│             │           └── Sub-Task B-1  │ │               │
│             │                             │ │               │
│             ├── KR 2 ◄────────────────────┤ │               │
│             │     └── TASK C              │ │               │
│             │                             │ │               │
│             └── KR 3 ◄────────────────────┘ │               │
│                                             │               │
└─────────────────────────────────────────────┴───────────────┘
```

---

## 5. UI/UX 컴포넌트 설계

### 5.1 레이아웃 구조

```
┌────────────────────────────────────────────────────────────┐
│                      HEADER / NAV                          │
├──────────────────────────┬─────────────────────────────────┤
│                          │                                 │
│     OKR SECTION          │       TASK SECTION              │
│     (왼쪽 패널)          │       (오른쪽 패널)             │
│                          │                                 │
│  ┌────────────────────┐  │  ┌───────────┬───────────┐     │
│  │ Objective          │  │  │    Q1     │    Q2     │     │
│  │  ├── KR 1          │  │  │   (DO)    │(SCHEDULE) │     │
│  │  │    ├── Task A   │  │  │           │           │     │
│  │  │    └── Task B   │  │  ├───────────┼───────────┤     │
│  │  ├── KR 2          │  │  │    Q3     │    Q4     │     │
│  │  └── KR 3          │  │  │(DELEGATE) │(ELIMINATE)│     │
│  └────────────────────┘  │  └───────────┴───────────┘     │
│                          │                                 │
├──────────────────────────┴─────────────────────────────────┤
│                      FOOTER / STATUS                       │
└────────────────────────────────────────────────────────────┘
```

### 5.2 주요 컴포넌트

| 컴포넌트 | 파일 | 기능 |
|----------|------|------|
| `OKRCard` | okr-section.css | OKR 목표 카드 표시 |
| `KRItem` | okr-section.css | Key Result 아이템 |
| `TaskCard` | task-section.css | 태스크 카드 (드래그 가능) |
| `SubTaskList` | task-section.css | 하위 태스크 목록 |
| `MatrixGrid` | task-section.css | 4사분면 그리드 |
| `ProgressBar` | components.css | 진행률 표시 바 |
| `DatePicker` | components.css | 날짜 선택기 |
| `Modal` | components.css | 모달 다이얼로그 |
| `Toast` | components.css | 알림 토스트 |

### 5.3 반응형 브레이크포인트

```css
/* 모바일 */
@media (max-width: 767px) {
  /* 단일 컬럼 레이아웃 */
}

/* 태블릿 */
@media (min-width: 768px) and (max-width: 1023px) {
  /* 탭 전환 레이아웃 */
}

/* 데스크톱 */
@media (min-width: 1024px) {
  /* 2컬럼 분할 레이아웃 */
}

/* 대형 모니터 */
@media (min-width: 1440px) {
  /* 최대 너비 제한 */
}
```

---

## 6. 개발 단계별 계획

### 6.1 Phase 1: 기반 구축 (2주)

**Week 1: 프로젝트 셋업 & 기본 구조**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | 프로젝트 구조 생성, HTML 스캐폴딩 | index.html, 디렉토리 구조 |
| Day 3-4 | CSS 기본 스타일 및 변수 정의 | styles.css, CSS 변수 |
| Day 5 | 데이터 모델 클래스 구현 | OKR.js, Task.js, SubTask.js |

**Week 2: 저장소 & 기본 렌더링**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | Local Storage 유틸리티 구현 | storage.js |
| Day 3-4 | 기본 뷰 렌더링 함수 구현 | OKRView.js, TaskView.js |
| Day 5 | 초기 데이터 로드/저장 테스트 | 통합 테스트 |

### 6.2 Phase 2: 핵심 기능 개발 (3주)

**Week 3: OKR 섹션 완성**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | Objective CRUD 구현 | OKRController.js |
| Day 3-4 | Key Result CRUD 구현 | KR 관리 기능 |
| Day 5 | Task/Sub-Task CRUD 구현 | Task 관리 기능 |

**Week 4: 매트릭스 섹션 개발**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | 4사분면 그리드 레이아웃 | MatrixView.js |
| Day 3-4 | 드래그 앤 드롭 구현 | DnD 기능 |
| Day 5 | 사분면 ↔ Task 연동 | 양방향 동기화 |

**Week 5: 동기화 & 진행률**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | OKR ↔ Task 실시간 동기화 | SyncController.js |
| Day 3-4 | 진행률 자동 계산 로직 | Progress 계산 |
| Day 5 | 진행률 시각화 (ProgressBar) | UI 컴포넌트 |

### 6.3 Phase 3: UI/UX 고도화 (2주)

**Week 6: 컴포넌트 & 인터랙션**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | 모달 & 폼 컴포넌트 | Modal, Form 컴포넌트 |
| Day 3-4 | 날짜 선택기 구현 | DatePicker |
| Day 5 | 토스트 알림 시스템 | Toast 컴포넌트 |

**Week 7: 반응형 & 접근성**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | 반응형 레이아웃 적용 | 미디어 쿼리 |
| Day 3-4 | 키보드 네비게이션 | 접근성 개선 |
| Day 5 | ARIA 레이블 & 스크린리더 | 접근성 완료 |

### 6.4 Phase 4: 최적화 & 배포 (1주)

**Week 8: 최종 마무리**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | 성능 최적화 적용 | 최적화된 코드 |
| Day 3 | 버그 수정 & QA | 안정화 |
| Day 4 | 문서화 | README, 사용 가이드 |
| Day 5 | 배포 | 프로덕션 릴리즈 |

### 6.5 전체 타임라인

```
Week 1  Week 2  Week 3  Week 4  Week 5  Week 6  Week 7  Week 8
  │       │       │       │       │       │       │       │
  ├───────┤       │       │       │       │       │       │
  │Phase 1│       │       │       │       │       │       │
  │ 기반  │       │       │       │       │       │       │
  └───────┴───────┼───────┼───────┤       │       │       │
                  │    Phase 2     │       │       │       │
                  │   핵심 기능    │       │       │       │
                  └───────┴───────┴───────┼───────┤       │
                                          │Phase 3│       │
                                          │ UI/UX │       │
                                          └───────┴───────┤
                                                          │P4│
                                                          │배포│
                                                          └──┘
```

---

## 7. 성능 최적화 전략

### 7.1 최적화 영역별 전략

| 영역 | 전략 | 구현 방법 | 효과 |
|------|------|----------|------|
| **DOM 조작** | Batch Update | `DocumentFragment` 사용 | 리플로우 최소화 |
| **이벤트** | 이벤트 위임 | 컨테이너에 단일 리스너 | 메모리 절약 |
| **검색** | 디바운스 | 300ms 지연 처리 | API 호출 감소 |
| **저장** | 스로틀링 | 1초당 최대 1회 저장 | Storage 부하 감소 |
| **렌더링** | 가상화 | 화면 영역만 렌더 | 대용량 처리 |

### 7.2 구현 예시

```javascript
// 디바운스 구현
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 스로틀링 구현
function throttle(func, limit = 1000) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Batch DOM Update
function batchRender(items, container) {
  const fragment = document.createDocumentFragment();
  items.forEach(item => {
    const el = createItemElement(item);
    fragment.appendChild(el);
  });
  container.innerHTML = '';
  container.appendChild(fragment);
}
```

### 7.3 성능 목표

| 지표 | 목표값 | 측정 방법 |
|------|--------|----------|
| First Contentful Paint | < 1.5s | Lighthouse |
| Time to Interactive | < 3s | Lighthouse |
| DOM 노드 수 | < 1500 | DevTools |
| JS 번들 크기 | < 100KB | 파일 사이즈 |
| 메모리 사용량 | < 50MB | DevTools Memory |

---

## 8. 테스트 및 품질 보증

### 8.1 테스트 전략

```
┌─────────────────────────────────────────────────────────┐
│                    테스트 피라미드                       │
│                                                         │
│                        /\                              │
│                       /  \    E2E 테스트 (10%)         │
│                      /────\   - 주요 사용자 흐름       │
│                     /      \                           │
│                    /────────\  통합 테스트 (30%)       │
│                   /          \  - 모듈 간 상호작용     │
│                  /────────────\                        │
│                 /              \  단위 테스트 (60%)    │
│                /────────────────\  - 개별 함수/모듈    │
│               /──────────────────\                     │
└─────────────────────────────────────────────────────────┘
```

### 8.2 테스트 케이스 (주요)

#### 단위 테스트
- [x] OKR 모델 CRUD 동작 검증 (TypeScript strict 모드로 정적 검증 완료)
- [x] Task 모델 CRUD 동작 검증
- [x] 진행률 계산 로직 검증
- [x] 날짜 유틸리티 함수 검증
- [x] Storage 저장/불러오기 검증

#### 통합 테스트
- [x] OKR 생성 → KR 추가 → Task 연결 흐름
- [x] Task 완료 → 진행률 자동 업데이트 (SyncController)
- [x] 매트릭스 드래그 → 사분면 변경 반영
- [x] 데이터 동기화 정합성

#### E2E 테스트
- [ ] 신규 사용자 온보딩 시나리오
- [ ] OKR 전체 생명주기 (생성 → 진행 → 완료)
- [ ] 대용량 데이터 처리 (100+ Tasks)

### 8.3 품질 체크리스트

- [ ] 코드 린팅 (ESLint)
- [ ] 코드 포매팅 (Prettier)
- [x] 브라우저 호환성 (Chrome, Firefox, Safari, Edge) — ES2020 + native modules
- [x] 모바일 반응형 테스트 — 미디어 쿼리 구현 완료
- [x] 접근성 검증 (WCAG 2.1 AA) — ARIA 레이블, role, aria-live 구현
- [ ] 성능 벤치마크 (Lighthouse 90+)

---

## 9. 배포 및 유지보수

### 9.1 배포 옵션

| 옵션 | 장점 | 단점 | 비용 |
|------|------|------|------|
| **GitHub Pages** | 무료, 간편 | 정적 파일만 | 무료 |
| **Netlify** | 자동 배포, CDN | - | 무료 티어 |
| **Vercel** | 빠른 배포 | - | 무료 티어 |
| **자체 서버** | 완전 제어 | 관리 부담 | 유료 |

### 9.2 배포 체크리스트

```
배포 전 체크리스트:
□ 모든 테스트 통과
□ 프로덕션 빌드 생성
□ 환경 변수 설정
□ 성능 최종 점검
□ SEO 메타 태그 확인
□ 파비콘 및 PWA 매니페스트
□ 에러 모니터링 설정
□ 백업 전략 수립
```

### 9.3 유지보수 계획

| 주기 | 활동 | 담당 |
|------|------|------|
| **일간** | 에러 로그 모니터링 | 자동화 |
| **주간** | 사용자 피드백 검토 | 개발팀 |
| **월간** | 보안 업데이트, 의존성 점검 | 개발팀 |
| **분기** | 기능 개선, 성능 최적화 | 전체 팀 |

---

## 10. 리스크 관리

### 10.1 리스크 식별 및 대응

| 리스크 | 확률 | 영향 | 대응 전략 |
|--------|------|------|----------|
| Local Storage 용량 초과 | 중 | 높 | IndexedDB 마이그레이션 계획 |
| 브라우저 호환성 이슈 | 중 | 중 | Polyfill, 기능 탐지 |
| 성능 저하 (대용량) | 중 | 높 | 가상화, 페이지네이션 |
| 데이터 유실 | 저 | 높 | 내보내기/가져오기 기능 |
| 일정 지연 | 중 | 중 | 버퍼 기간, MVP 우선 |

### 10.2 마일스톤 체크포인트

```
Week 2 ──► 기반 구축 완료 리뷰
Week 5 ──► 핵심 기능 완료 리뷰 (MVP)
Week 7 ──► UI/UX 완료 리뷰
Week 8 ──► 최종 릴리즈 승인
```

---

## 부록

### A. 참고 자료

#### OKR 관련
- [Quantive OKR Guide](https://quantive.com/resources/articles/okr-guide)
- [Google re:Work OKR Guide](https://rework.withgoogle.com/guides/set-goals-with-okrs)
- [Perdoo OKR Resources](https://www.perdoo.com/)

#### 아이젠하워 매트릭스
- Eisenhower Decision Matrix 원리
- 시간 관리 프레임워크

### B. 용어 정의

| 용어 | 정의 |
|------|------|
| OKR | Objectives and Key Results - 목표 및 핵심 결과 |
| KR | Key Result - 핵심 결과 |
| Objective | 달성하고자 하는 정성적 목표 |
| Task | 구체적인 실행 항목 |
| Sub-Task | Task의 하위 실행 단위 |
| Quadrant | 아이젠하워 매트릭스의 4개 사분면 |

### C. 버전 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| 1.0 | 2026-04-09 | 초기 계획서 작성 |
| 1.1 | 2026-04-09 | 전체 구현 완료 — TypeScript MVC 앱, 타입 체크 통과 |

---

**문서 끝**
