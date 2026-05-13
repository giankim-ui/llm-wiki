# OKR-Matrix 웹 애플리케이션 개발 계획서

> **문서 버전**: 1.1  
> **작성일**: 2026-04-09  
> **수정일**: 2026-04-09  
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

OKR(Objectives and Key Results)과 아이젠하워 매트릭스(Eisenhower Matrix)를 **하나의 통합된 화면**에서 유기적으로 관리할 수 있는 경량 웹 애플리케이션 개발.

### 1.2 핵심 가치

- **통합성**: OKR과 EM이 분리되지 않고 하나의 대시보드에서 연동
- **유기적 연결**: OKR의 KR(Key Results)과 Task/Sub-Task가 실시간 연동
- **직관성**: 시각적으로 명확한 우선순위 파악
- **경량성**: 바닐라 JavaScript 기반, 외부 의존성 최소화

---

## 2. 핵심 기능 정의

### 2.1 OKR 관리

- Objective(목표) 생성/수정/삭제
- Key Results(핵심 결과) 관리 (최대 5개 권장)
- KR 달성도 자동 계산 (연결된 Task 진행률 기반)
- KR 수동 추가 버튼 ([+])

### 2.2 Task/Sub-Task 관리

- Task 생성 시 KR 연결 필수
- Sub-Task 세분화
- 시작일/기한 설정
- 달성도 추적

### 2.3 Eisenhower Matrix 통합

- 4사분면 우선순위 분류 (긴급/중요 기준)
- 드래그 앤 드롭으로 우선순위 변경
- 순서(order) 관리

### 2.4 OKR-EM 연동

- KR과 Task의 양방향 연결
- Task 완료 시 KR 진행률 자동 업데이트
- 통합 대시보드에서 전체 현황 파악

---

## 3. 기술 스택 및 아키텍처

### 3.1 기술 스택

| 구분 | 기술 | 선정 이유 |
|------|------|-----------|
| 언어 | Vanilla JavaScript (ES6+) | 경량성, 의존성 최소화 |
| 스타일 | CSS3 + CSS Variables | 테마 지원, 유지보수 용이 |
| 스토리지 | Local Storage | 서버 불필요, 오프라인 지원 |
| 빌드 | 없음 (직접 실행) | 단순성 유지 |

### 3.2 아키텍처 패턴

```
┌─────────────────────────────────────────────────┐
│                    View Layer                    │
│  ┌─────────────────┐  ┌──────────────────────┐  │
│  │   OKR Section   │  │    Task Section      │  │
│  │   (상단 고정)    │  │    (하단 스크롤)      │  │
│  └────────┬────────┘  └──────────┬───────────┘  │
│           │         연동          │              │
│           └──────────┬───────────┘              │
├─────────────────────────────────────────────────┤
│                 Controller Layer                 │
│         (이벤트 핸들링, 상태 관리)                │
├─────────────────────────────────────────────────┤
│                   Model Layer                    │
│    ┌─────┐  ┌──────┐  ┌────────┐  ┌─────────┐  │
│    │ OKR │──│  KR  │──│  Task  │──│SubTask  │  │
│    └─────┘  └──────┘  └────────┘  └─────────┘  │
├─────────────────────────────────────────────────┤
│                  Storage Layer                   │
│               (Local Storage)                    │
└─────────────────────────────────────────────────┘
```

---

## 4. 데이터 모델 설계

### 4.1 OKR 모델

```javascript
// OKR.js
class OKR {
  constructor(data) {
    this.id = data.id || generateUUID();
    this.objective = data.objective;  // 목표 텍스트
    this.keyResults = data.keyResults || [];  // KR 배열
    this.createdAt = data.createdAt || new Date().toISOString();
    this.updatedAt = data.updatedAt || new Date().toISOString();
  }
}

// KeyResult.js
class KeyResult {
  constructor(data) {
    this.id = data.id || generateUUID();
    this.krNo = data.krNo;           // KR 번호 (1, 2, 3...)
    this.description = data.description;  // KR 설명
    this.progress = data.progress || 0;   // 달성도 (0-100)
    this.linkedTasks = data.linkedTasks || [];  // 연결된 Task ID 배열
  }
}
```

### 4.2 Task 모델

```javascript
// Task.js
class Task {
  constructor(data) {
    this.id = data.id || generateUUID();
    this.title = data.title;           // 태스크명
    this.krId = data.krId;             // 연결된 KR ID
    this.krNo = data.krNo;             // 연결된 KR 번호 (표시용)
    this.subTasks = data.subTasks || [];
    this.memo = data.memo || '';
    this.createdAt = data.createdAt || new Date().toISOString();
  }

  // 달성도 계산 (SubTask 기반)
  get progress() {
    if (this.subTasks.length === 0) return 0;
    const completed = this.subTasks.filter(st => st.isCompleted).length;
    return Math.round((completed / this.subTasks.length) * 100);
  }
}

// SubTask.js
class SubTask {
  constructor(data) {
    this.id = data.id || generateUUID();
    this.title = data.title;           // 하위 태스크명
    this.emQuadrant = data.emQuadrant; // EM 사분면 (1-4)
    this.order = data.order || 0;      // 순서
    this.startDate = data.startDate;   // 시작일
    this.dueDate = data.dueDate;       // 기한
    this.isCompleted = data.isCompleted || false;
    this.taskId = data.taskId;         // 상위 Task ID
  }
}
```

### 4.3 데이터 관계도

```
OKR (1) ─────┬───── (N) KeyResult
             │
             │ krId 참조
             ▼
KeyResult (1) ───── (N) Task
             │
             │ taskId 참조
             ▼
Task (1) ─────────── (N) SubTask
                         │
                         ├── emQuadrant (EM 사분면)
                         ├── order (순서)
                         ├── startDate (시작일)
                         └── dueDate (기한)
```

---

## 5. UI/UX 컴포넌트 설계

### 5.1 통합 화면 구성 원칙

> **핵심 원칙**: OKR과 아이젠하워 매트릭스(EM)는 **하나의 화면에서 통합적이고 유기적으로** 구성되어야 합니다.

### 5.2 통합 OKR-EM 대시보드 레이아웃

```
┌─────────────────────────────────────────────────────────────────┐
│                    통합 OKR-EM 대시보드                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              ★ OKR 섹션 (상단 고정) ★                      │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │ Objective: 세계인이 매일 1억 시간 동안 유튜브를       │  │  │
│  │  │            시청하게 만든다                           │  │  │
│  │  ├──────────┬──────────────────────────────────────────┤  │  │
│  │  │  KR no.  │              Key Results                 │  │  │
│  │  ├──────────┼──────────────────────────────────────────┤  │  │
│  │  │    1     │ 사용자의 하루 평균 시청 시간을 20% 늘린다.  │  │  │
│  │  │    2     │ 추천 알고리즘 정확도를 높여 시청 지속       │  │  │
│  │  │          │ 시간을 15분 이상 유지                     │  │  │
│  │  │    3     │ 모바일 기기에서의 유입량을 전 분기 대비     │  │  │
│  │  │          │ 2배 확대한다.                            │  │  │
│  │  │   [+]    │ (KR 수동 추가 버튼)                       │  │  │
│  │  └──────────┴──────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            ▼ 연동                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              ★ TASK 섹션 (하단 스크롤) ★                   │  │
│  │  ┌────┬────┬──────────┬───────┬───────┬────────────────┐  │  │
│  │  │ EM │순서│ SUB-TASK │ 시작일 │  기한  │     TASK      │  │  │
│  │  ├────┼────┼──────────┼───────┼───────┼────────────────┤  │  │
│  │  │ 1  │ 1  │ 분석작업  │04-10  │04-15  │ 데이터 분석    │  │  │
│  │  │ 1  │ 2  │ 보고서    │04-12  │04-18  │ 데이터 분석    │  │  │
│  │  │ 2  │ 1  │ UI 개선   │04-11  │04-20  │ 앱 개선       │  │  │
│  │  │... │... │   ...    │ ...   │ ...   │    ...        │  │  │
│  │  ├────┴────┴──────────┼───────┴───────┼────────────────┤  │  │
│  │  │      달성도        │    KR no.     │    KR          │  │  │
│  │  ├────────────────────┼───────────────┼────────────────┤  │  │
│  │  │        60%         │      1        │ 시청시간 20%↑  │  │  │
│  │  │        30%         │      2        │ 알고리즘 개선   │  │  │
│  │  └────────────────────┴───────────────┴────────────────┤  │  │
│  │                          메모                          │  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 주요 컴포넌트 명세

| 컴포넌트 | 파일 | 기능 | 위치 |
|----------|------|------|------|
| `OKRSection` | okr-section.css | OKR 전체 섹션 (상단 고정) | 대시보드 상단 |
| `ObjectiveCard` | okr-section.css | Objective 표시 카드 | OKR 섹션 내 |
| `KRTable` | okr-section.css | Key Results 테이블 | OKR 섹션 내 |
| `KRAddButton` | okr-section.css | KR 수동 추가 버튼 [+] | KR 테이블 하단 |
| `TaskSection` | task-section.css | Task 전체 섹션 (스크롤) | 대시보드 하단 |
| `TaskTable` | task-section.css | Task/Sub-Task 테이블 | Task 섹션 내 |
| `EMIndicator` | task-section.css | EM 사분면 표시 (1-4) | Task 테이블 셀 |
| `OrderIndicator` | task-section.css | 순서 표시 | Task 테이블 셀 |
| `ProgressBar` | components.css | 달성도 표시 바 | Task 테이블 |
| `KRLinkBadge` | components.css | 연결된 KR 표시 배지 | Task 테이블 |
| `ConnectionLine` | components.css | OKR-Task 연동 시각화 | 섹션 사이 |
| `Modal` | components.css | 모달 다이얼로그 | 오버레이 |
| `Toast` | components.css | 알림 토스트 | 화면 하단 |

### 5.4 EM(Eisenhower Matrix) 사분면 정의

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   1: 긴급 & 중요     │   2: 긴급하지 않음   │
│   (Do First)        │      & 중요         │
│   즉시 실행          │   (Schedule)        │
│                     │   일정 계획          │
├─────────────────────┼─────────────────────┤
│                     │                     │
│   3: 긴급 &         │   4: 긴급하지 않음   │
│   중요하지 않음      │   & 중요하지 않음    │
│   (Delegate)        │   (Eliminate)       │
│   위임              │   제거              │
│                     │                     │
└─────────────────────┴─────────────────────┘
```

### 5.5 Task 테이블 컬럼 상세

| 컬럼 | 설명 | 데이터 타입 | 비고 |
|------|------|------------|------|
| EM | 아이젠하워 사분면 | Number (1-4) | 드래그로 변경 가능 |
| 순서 | 같은 EM 내 우선순위 | Number | 드래그로 변경 가능 |
| SUB-TASK | 하위 태스크명 | String | 체크박스 포함 |
| 시작일 | 작업 시작 예정일 | Date | DatePicker |
| 기한 | 작업 완료 기한 | Date | DatePicker |
| TASK | 상위 태스크명 | String | 그룹핑 기준 |
| 달성도 | SubTask 완료율 | Percentage | 자동 계산 |
| KR no. | 연결된 KR 번호 | Number | 필수 연결 |
| KR | 연결된 KR 내용 | String | 읽기 전용 |
| 메모 | 추가 메모 | String | 선택 사항 |

### 5.6 반응형 브레이크포인트

```css
/* 모바일 (기본) */
@media (max-width: 767px) {
  /* OKR 섹션: 축소 표시, 터치 확장 */
  /* Task 테이블: 카드 형태로 변환 */
  /* EM 컬럼 아이콘으로 표시 */
}

/* 태블릿 */
@media (min-width: 768px) and (max-width: 1023px) {
  /* OKR 섹션: 고정 높이 제한 */
  /* Task 테이블: 일부 컬럼 숨김 처리 */
}

/* 데스크톱 */
@media (min-width: 1024px) {
  /* OKR 섹션: 상단 고정 (sticky) */
  /* Task 섹션: 전체 컬럼 표시, 스크롤 */
}

/* 대형 모니터 */
@media (min-width: 1440px) {
  /* 최대 너비 1400px 제한 */
  /* 중앙 정렬 */
}
```

### 5.7 OKR-Task 연동 인터랙션

```
[OKR 섹션에서의 동작]
1. KR 클릭 → 해당 KR에 연결된 Task들 하이라이트
2. KR 추가 [+] → 새 KR 입력 모달
3. KR 진행률 → 연결된 Task 완료율 자동 반영

[Task 섹션에서의 동작]
1. Task 추가 → KR 선택 필수
2. SubTask 완료 체크 → Task 달성도 업데이트 → KR 진행률 업데이트
3. EM 값 변경 → 드래그 또는 드롭다운 선택
4. 순서 변경 → 드래그로 재정렬

[연동 시각화]
- OKR 섹션과 Task 섹션 사이 "▼ 연동" 표시
- KR 선택 시 연결선 하이라이트 (선택적 기능)
```

---

## 6. 개발 단계별 계획

### 6.1 Phase 1: 기반 구축 (2주)

**Week 1: 프로젝트 셋업 & 기본 구조**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | 프로젝트 구조 생성, HTML 스캐폴딩 | index.html, 디렉토리 구조 |
| Day 3-4 | CSS 기본 스타일 및 변수 정의, **통합 대시보드 레이아웃** | styles.css, layout.css |
| Day 5 | 데이터 모델 클래스 구현 | OKR.js, KeyResult.js, Task.js, SubTask.js |

**Week 2: 저장소 & 기본 렌더링**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | Local Storage 유틸리티 구현 | storage.js |
| Day 3-4 | **OKR 섹션 렌더링 (상단 고정)** | okr-section.js, okr-section.css |
| Day 5 | **Task 테이블 기본 렌더링** | task-section.js, task-section.css |

### 6.2 Phase 2: 핵심 기능 (3주)

**Week 3: OKR 기능 완성**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | Objective CRUD | objective-controller.js |
| Day 3-4 | Key Results CRUD, **[+] 버튼 기능** | kr-controller.js |
| Day 5 | KR 진행률 계산 로직 | progress-calculator.js |

**Week 4: Task/SubTask 기능**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | Task CRUD, **KR 연결 필수화** | task-controller.js |
| Day 3-4 | SubTask CRUD, 체크박스 상태 관리 | subtask-controller.js |
| Day 5 | **EM 사분면 할당 기능** | em-controller.js |

**Week 5: 연동 & 인터랙션**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | **OKR-Task 연동 로직** | linkage-manager.js |
| Day 3-4 | 드래그 앤 드롭 (순서, EM 변경) | drag-drop.js |
| Day 5 | DatePicker 컴포넌트 | date-picker.js |

### 6.3 Phase 3: UI/UX 고도화 (2주)

**Week 6: 시각적 완성**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | **통합 대시보드 스타일링** | dashboard.css |
| Day 3-4 | **연동 시각화 (하이라이트, 연결선)** | connection-visualizer.js |
| Day 5 | ProgressBar, Badge 컴포넌트 | components.css |

**Week 7: 반응형 & 접근성**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | **모바일 레이아웃 (카드 변환)** | responsive.css |
| Day 3-4 | 태블릿/데스크톱 레이아웃 | responsive.css |
| Day 5 | 접근성 (키보드, ARIA) | accessibility.js |

### 6.4 Phase 4: 테스트 & 배포 (1주)

**Week 8: QA & 배포**

| 일차 | 태스크 | 산출물 |
|------|--------|--------|
| Day 1-2 | 단위 테스트, 통합 테스트 | tests/ |
| Day 3-4 | E2E 시나리오 테스트 | e2e-tests/ |
| Day 5 | 배포 (GitHub Pages / Vercel) | 프로덕션 URL |

---

## 7. 성능 최적화 전략

### 7.1 렌더링 최적화

- **가상 스크롤**: Task 테이블 대량 데이터 시 적용
- **디바운싱**: 검색/필터 입력 시 300ms 디바운스
- **배치 업데이트**: DOM 변경 최소화

### 7.2 데이터 최적화

- **인덱싱**: KR ID 기준 Task 인덱스 구축
- **캐싱**: 계산된 진행률 캐시
- **Lazy 계산**: 필요 시점에만 달성도 계산

### 7.3 로딩 최적화

- **Critical CSS**: 인라인 처리
- **지연 로딩**: 모달, Toast 등 온디맨드 로드

---

## 8. 테스트 및 품질 보증

### 8.1 단위 테스트

| 대상 | 테스트 케이스 |
|------|--------------|
| OKR 모델 | 생성, 수정, KR 추가/삭제 |
| Task 모델 | 생성, KR 연결, 달성도 계산 |
| SubTask 모델 | EM 할당, 순서 변경, 완료 처리 |
| Storage | 저장, 불러오기, 동기화 |

### 8.2 통합 테스트

| 시나리오 | 검증 항목 |
|----------|----------|
| OKR-Task 연동 | KR 선택 시 Task 연결, 진행률 자동 계산 |
| EM 변경 | 드래그로 사분면 이동, 순서 유지 |
| 달성도 업데이트 | SubTask 완료 → Task → KR 전파 |

### 8.3 E2E 테스트

```
시나리오 1: 신규 OKR 생성 플로우
1. Objective 입력
2. KR 3개 추가
3. 각 KR에 Task 연결
4. SubTask 추가 및 EM 할당
5. 통합 대시보드 확인

시나리오 2: 달성도 추적 플로우
1. SubTask 체크 완료
2. Task 달성도 업데이트 확인
3. KR 진행률 업데이트 확인
4. OKR 섹션 반영 확인
```

---

## 9. 배포 및 유지보수

### 9.1 배포 옵션

| 플랫폼 | 장점 | 설정 난이도 |
|--------|------|------------|
| GitHub Pages | 무료, Git 연동 | 낮음 |
| Vercel | 자동 배포, 프리뷰 | 낮음 |
| Netlify | 무료 SSL, 폼 지원 | 낮음 |

### 9.2 버전 관리

- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **변경 로그**: CHANGELOG.md 유지
- **브랜치 전략**: main, develop, feature/*

### 9.3 유지보수 체크리스트

- [ ] 주간 의존성 보안 점검
- [ ] 월간 성능 모니터링
- [ ] 분기별 UX 피드백 반영

---

## 10. 리스크 관리

### 10.1 기술적 리스크

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|----------|
| Local Storage 용량 초과 | 중 | 데이터 압축, IndexedDB 대체 |
| 브라우저 호환성 | 중 | Polyfill 적용, 기능 감지 |
| 성능 저하 (대량 데이터) | 중 | 가상 스크롤, 페이지네이션 |

### 10.2 UX 리스크

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|----------|
| 통합 화면 복잡성 | 고 | 섹션 접기/펼치기, 가이드 투어 |
| 연동 관계 혼란 | 중 | 시각적 연결선, 하이라이트 |
| 모바일 사용성 | 중 | 단순화된 카드 뷰 |

### 10.3 일정 리스크

| 리스크 | 확률 | 대응 방안 |
|--------|------|----------|
| 기능 범위 초과 | 중 | MVP 우선, 기능 우선순위화 |
| 예상치 못한 버그 | 중 | 버퍼 시간 확보 (10%) |

---

## 부록: 파일 구조

```
okr-matrix/
├── index.html
├── css/
│   ├── styles.css          # 전역 스타일, 변수
│   ├── layout.css          # 통합 대시보드 레이아웃
│   ├── okr-section.css     # OKR 섹션 스타일
│   ├── task-section.css    # Task 섹션 스타일
│   ├── components.css      # 공통 컴포넌트
│   └── responsive.css      # 반응형 스타일
├── js/
│   ├── models/
│   │   ├── OKR.js
│   │   ├── KeyResult.js
│   │   ├── Task.js
│   │   └── SubTask.js
│   ├── controllers/
│   │   ├── objective-controller.js
│   │   ├── kr-controller.js
│   │   ├── task-controller.js
│   │   ├── subtask-controller.js
│   │   └── em-controller.js
│   ├── views/
│   │   ├── okr-section.js
│   │   ├── task-section.js
│   │   └── connection-visualizer.js
│   ├── utils/
│   │   ├── storage.js
│   │   ├── linkage-manager.js
│   │   ├── progress-calculator.js
│   │   ├── drag-drop.js
│   │   └── date-picker.js
│   └── app.js              # 애플리케이션 진입점
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── README.md
```

---

> **문서 끝**
