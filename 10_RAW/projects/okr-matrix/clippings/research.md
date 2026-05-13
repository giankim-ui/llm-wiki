# OKR & 아이젠하워 매트릭스 통합 웹 애플리케이션 리서치 보고서

---

## 목차
1. [OKR (Objectives and Key Results) 핵심 개념](#1-okr-objectives-and-key-results-핵심-개념)
2. [아이젠하워 매트릭스 핵심 개념](#2-아이젠하워-매트릭스-핵심-개념)
3. [두 프레임워크의 시너지 분석](#3-두-프레임워크의-시너지-분석)
4. [최적의 코드베이스 설계안](#4-최적의-코드베이스-설계안)
5. [권장 기술 스택 및 아키텍처](#5-권장-기술-스택-및-아키텍처)
6. [상세 구현 가이드](#6-상세-구현-가이드)

---

## 1. OKR (Objectives and Key Results) 핵심 개념

### 1.1 OKR의 정의와 철학

OKR은 **목표(Objectives)와 핵심결과(Key Results)**를 결합하여 조직의 전략과 실행을 연결하는 목표 설정 방법론입니다.

#### 핵심 철학
- **투명성(Transparency)**: 모든 구성원이 서로의 OKR을 볼 수 있음
- **정렬(Alignment)**: 개인-팀-조직 목표가 유기적으로 연결
- **집중(Focus)**: 3-5개의 핵심 목표에 역량 집중
- **추적 가능성(Trackability)**: 정량적 측정을 통한 진행률 확인

### 1.2 Objective (목표) 특성

| 특성 | 설명 | 예시 |
|------|------|------|
| **영감을 주는** | 팀에 동기부여 제공 | "고객이 사랑하는 제품 만들기" |
| **질적(Qualitative)** | 측정 가능한 숫자가 아닌 방향성 | "시장 1위 달성" (X) → "시장을 선도하는 브랜드 되기" (O) |
| **시간 제한적** | 분기/반기 단위로 설정 | Q1 2026 목표 |
| **실행 가능한** | 팀이 통제할 수 있는 범위 | 외부 요인에 의존하지 않음 |

### 1.3 Key Results (핵심 결과) 특성

| 특성 | 설명 | 좋은 예시 | 나쁜 예시 |
|------|------|----------|----------|
| **측정 가능** | 숫자로 표현 | "NPS 50점 달성" | "고객 만족도 향상" |
| **구체적** | 모호함 없음 | "신규 가입자 1만명" | "많은 사용자 확보" |
| **도전적** | 70% 달성이 성공 | "매출 200% 성장" | "매출 5% 성장" |
| **결과 중심** | Output이 아닌 Outcome | "전환율 15% 달성" | "광고 10개 집행" |

### 1.4 OKR 설정 방식

| 방식 | 특징 | 장점 | 단점 |
|------|------|------|------|
| **Top-down** | 경영진 → 팀 → 개인 | 빠른 정렬, 전략 일관성 | 참여도 낮음 |
| **Bottom-up** | 개인 → 팀 → 조직 | 높은 동기부여, 현실적 | 조정 시간 필요 |
| **Bidirectional** | 양방향 협의 | 균형잡힌 접근 | 가장 권장됨 |

### 1.5 OKR 운영 사이클

```
Quarter -2주: 팀별 목표 초안 공개
        ↓
Quarter -1주: 팀 간 협업 및 정렬 검토
        ↓
Quarter 시작: 최종 OKR 확정 및 커밋
        ↓
Weekly: 진행 상황 체크인 (10-15분)
        ↓
Monthly: 중간 점검 및 조정
        ↓
Quarter 종료: 회고 및 평가 (0.0-1.0 스코어)
```

### 1.6 OKR 측정 및 평가

#### 스코어링 시스템 (0.0 ~ 1.0)

| 점수 범위 | 의미 | 해석 |
|-----------|------|------|
| 0.0 - 0.3 | 실패 | 목표 설정 또는 실행에 문제 |
| 0.4 - 0.6 | 진행 중 | 부분적 달성, 개선 필요 |
| 0.7 - 0.8 | **Sweet Spot** | 도전적 목표의 성공적 달성 |
| 0.9 - 1.0 | 과달성 | 목표가 충분히 도전적이지 않았을 가능성 |

---

## 2. 아이젠하워 매트릭스 핵심 개념

### 2.1 매트릭스 구조

```
                    긴급함 (Urgent)
                    ↑
        ┌───────────┬───────────┐
        │    Q1     │    Q2     │
        │  DO FIRST │  SCHEDULE │
        │ 즉시 실행  │  일정 수립  │
중요함 ←├───────────┼───────────┤→ 중요하지 않음
        │    Q3     │    Q4     │
        │ DELEGATE  │ ELIMINATE │
        │   위임    │   제거    │
        └───────────┴───────────┘
                    ↓
              긴급하지 않음
```

### 2.2 사분면별 상세 설명

| 사분면 | 특성 | 행동 전략 | 예시 |
|--------|------|----------|------|
| **Q1** | 긴급 + 중요 | 즉시 직접 처리 | 마감 임박 프로젝트, 위기 대응 |
| **Q2** | 중요 + 비긴급 | 계획 수립 후 실행 | 전략 수립, 역량 개발, 관계 구축 |
| **Q3** | 긴급 + 비중요 | 위임 또는 최소화 | 일부 회의, 전화, 이메일 |
| **Q4** | 비긴급 + 비중요 | 제거 또는 줄이기 | SNS, 의미 없는 웹서핑 |

### 2.3 효과적인 시간 배분 권장 비율

```
이상적인 시간 배분:
┌────────────────────────────────────────┐
│ Q2 (계획/전략): 65-80%  ████████████░░ │
│ Q1 (긴급/중요): 15-20%  ███░░░░░░░░░░░ │
│ Q3 (위임):       5-10%  █░░░░░░░░░░░░░ │
│ Q4 (제거):       0-5%   ░░░░░░░░░░░░░░ │
└────────────────────────────────────────┘
```

### 2.4 긴급성 vs 중요성 판별 기준

#### 긴급성 판별 질문
- [ ] 마감일이 24시간 이내인가?
- [ ] 누군가가 즉각적인 응답을 기다리는가?
- [ ] 미루면 금전적/물리적 손실이 발생하는가?
- [ ] 외부 요인에 의해 시간이 제한되어 있는가?

#### 중요성 판별 질문
- [ ] 장기 목표 달성에 기여하는가?
- [ ] 핵심 가치나 미션과 연결되는가?
- [ ] 이것을 하지 않으면 심각한 결과가 있는가?
- [ ] 나만이 할 수 있는 일인가?

### 2.5 "내일 테스트" (Tomorrow Test)

> 이 일을 내일로 미뤄도 큰 문제가 없다면, **긴급하지 않은 것**입니다.

---

## 3. 두 프레임워크의 시너지 분석

### 3.1 OKR과 아이젠하워 매트릭스의 통합 모델

```
┌─────────────────────────────────────────────────────────┐
│                    OBJECTIVE                            │
│        "세계인이 매일 10억 시간 동안 유튜브를 시청하게 만든다"      │
└─────────────────────┬───────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    ▼                 ▼                 ▼
┌────────┐      ┌────────┐       ┌────────┐
│  KR 1  │      │  KR 2  │       │  KR 3  │
│시청시간 │      │알고리즘 │       │모바일   │
│ 20%↑  │      │정확도↑ │       │유입2배 │
└───┬────┘      └───┬────┘       └───┬────┘
    │               │                │
    ▼               ▼                ▼
┌────────────────────────────────────────┐
│         아이젠하워 매트릭스               │
│  ┌─────────┬─────────┐                │
│  │ Q1(DO)  │Q2(PLAN) │                │
│  │ 긴급KR  │ 전략KR   │                │
│  ├─────────┼─────────┤                │
│  │Q3(위임) │Q4(제거) │                │
│  └─────────┴─────────┘                │
└────────────────────────────────────────┘
```

### 3.2 통합의 핵심 원리

| OKR 요소 | 아이젠하워 매핑 | 설명 |
|----------|----------------|------|
| **Objective** | Q2 기반 | 장기 목표는 본질적으로 "중요하지만 긴급하지 않음" |
| **Key Results** | Q1/Q2 측정 | 마감이 다가올수록 Q2→Q1 이동 |
| **일일 태스크** | 4사분면 분류 | KR 달성을 위한 태스크를 매일 분류 |

### 3.3 통합 사용 워크플로우

```
1. 분기 시작: Objective 설정 (Q2 영역에서 시작)
        ↓
2. KR 정의: 측정 가능한 Key Results 3-5개 설정
        ↓
3. 태스크 분해: 각 KR을 달성하기 위한 TASK 도출
        ↓
4. 일일 분류: TASK를 아이젠하워 매트릭스로 분류
        ↓
5. 실행 & 추적: Q1→Q2 순으로 처리, 진척률 업데이트
        ↓
6. 주간 리뷰: KR 진행률 확인 및 TASK 재분류
```

---

## 4. 최적의 코드베이스 설계안

### 4.1 프로젝트 구조

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
│   │   └── TreeView.js     # 트리 구조 시각화
│   ├── controllers/
│   │   ├── OKRController.js    # OKR 비즈니스 로직
│   │   ├── TaskController.js   # Task 비즈니스 로직
│   │   └── SyncController.js   # 데이터 동기화 컨트롤러
│   └── utils/
│       ├── storage.js      # localStorage 관리
│       ├── dragdrop.js     # 드래그 앤 드롭 유틸리티
│       └── sync.js         # 실시간 동기화 유틸리티
└── assets/
    └── icons/              # 아이콘 리소스
```

### 4.2 데이터 계층 구조

```
OKR (최상위)
 └── Objective (목표)
      └── Key Results (핵심 결과) [1:N 관계, 수동 추가 가능]
           └── Tasks (태스크) [1:N 관계]
                └── Sub-Tasks (하위 태스크) [1:N 관계, 최소 단위]
```

### 4.3 데이터 모델 스키마

```javascript
// OKR 스키마
{
  id: "okr_001",
  objective: "세계인이 매일 10억 시간 동안 유튜브를 시청하게 만든다",
  keyResults: [
    {
      id: "kr_001",
      krNo: 1,
      title: "사용자의 하루 평균 시청 시간을 20% 늘린다",
      progress: 0,  // 0-100%, 하위 Task 달성도에 따라 자동 계산
      tasks: ["task_001", "task_002"]  // 연결된 Task ID 배열
    },
    {
      id: "kr_002",
      krNo: 2,
      title: "추천 알고리즘 정확도를 높여 시청 지속 시간을 15분 이상으로 유지한다",
      progress: 0,
      tasks: []
    }
  ],
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-04-08T00:00:00Z"
}

// Task 스키마
{
  id: "task_001",
  krId: "kr_001",           // 연결된 KR ID (동기화 키)
  krNo: 1,                  // KR 번호 (자동 연동)
  krTitle: "사용자의 하루 평균 시청 시간을 20% 늘린다",  // KR 제목 (자동 연동)
  title: "연속 시청을 유도하는 'Binge-watching' 기능 강화",
  quadrant: "Q1",           // EM 사분면 (Q1/Q2/Q3/Q4)
  order: 1,                 // 순서 (드래그&드롭으로 변경 가능)
  progress: 66,             // 달성도 (서브태스크 완료율 자동 계산)
  startDate: "2026-02-08",
  dueDate: "2026-02-22",
  memo: "자유롭게 메모 사항 기재 가능",
  subTasks: [
    {
      id: "subtask_001",
      order: 1,
      title: "다음 영상 자동 재생' UI/UX 개선 및 로딩 속도 최적화",
      completed: true,
      startDate: "2026-02-08",
      dueDate: "2026-02-22"
    },
    {
      id: "subtask_002",
      order: 2,
      title: "영상 중간에 관련 있는 다른 영상을 추천하는 '카드/엔드 스크린' 노출 로직 최적화",
      completed: true,
      startDate: "2026-03-08",
      dueDate: "2026-03-22"
    },
    {
      id: "subtask_003",
      order: 3,
      title: "시청 중인 영상과 유사한 주제의 '재생 목록' 자동 생성 기능 도입",
      completed: false,
      startDate: "2026-04-08",
      dueDate: "2026-04-22"
    }
  ]
}
```

---

## 5. 권장 기술 스택 및 아키텍처

### 5.1 기술 스택 선정

| 영역 | 기술 | 선정 이유 |
|------|------|----------|
| **프론트엔드** | Vanilla JS (ES6+) | 의존성 최소화, 빠른 로딩 |
| **스타일링** | CSS3 + CSS Grid/Flexbox | 반응형 레이아웃, 모던 UI |
| **데이터 저장** | localStorage + IndexedDB | 오프라인 지원, 빠른 접근 |
| **상태 관리** | Pub/Sub 패턴 | 컴포넌트 간 느슨한 결합, 실시간 동기화 |
| **드래그앤드롭** | HTML5 Drag and Drop API | 네이티브 지원, 추가 라이브러리 불필요 |

### 5.2 UI/UX 설계 원칙

#### 5.2.1 통합 화면 구성 원칙

> **핵심 원칙**: OKR과 아이젠하워 매트릭스(EM)는 **하나의 화면에서 통합적이고 유기적으로** 구성되어야 합니다.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         통합 OKR-EM 대시보드                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    ★ OKR 섹션 (상단 고정) ★                         │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │ Objective: 세계인이 매일 10억 시간 동안 유튜브를 시청하게 만든다   │  │  │
│  │  ├─────────────────────────────────────────────────────────────┤  │  │
│  │  │ KR no. │              Key Results                          │  │  │
│  │  ├────────┼────────────────────────────────────────────────────┤  │  │
│  │  │   1    │ 사용자의 하루 평균 시청 시간을 20% 늘린다.              │  │  │
│  │  │   2    │ 추천 알고리즘 정확도를 높여 시청 지속 시간을 15분 이상 유지 │  │  │
│  │  │   3    │ 모바일 기기에서의 유입량을 전 분기 대비 2배 확대한다.     │  │  │
│  │  │  [+]   │ (KR 수동 추가 버튼)                                  │  │  │
│  │  └─────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                    ▼ 연동                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    ★ TASK 섹션 (하단 스크롤) ★                       │  │
│  │  ┌────┬────┬─────────────────┬───────┬───────┬───────────────────┐  │
│  │  │ EM │순서│   SUB-TASK      │ 시작일 │ 기한  │      TASK         │  │
│  │  ├────┼────┼─────────────────┼───────┼───────┼───────────────────┤  │
│  │  │... │... │                 │       │       │                   │  │
│  │  ├────┴────┴─────────────────┴───────┴───────┼───────────────────┤  │
│  │  │ 달성도 │ KR no. │           KR            │       메모        │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 5.2.2 OKR 섹션 상세 설계 (상단 고정)

| 요소 | 설명 | 인터랙션 |
|------|------|----------|
| **Objective** | 하나의 핵심 목표 표시 | 클릭하여 인라인 편집 |
| **KR no.** | Key Result 순번 (자동 부여) | 자동 증가, 삭제 시 재정렬 |
| **KR** | Key Result 내용 | 클릭하여 인라인 편집 |
| **[+] 버튼** | KR 수동 추가 | 클릭 시 새 KR 행 추가 |
| **[-] 버튼** | KR 삭제 (행별) | 삭제 시 연결된 TASK의 KR 연결 해제 확인 |

**OKR 섹션 특징:**
- 📌 **상단 고정(Sticky Header)**: 스크롤해도 항상 화면 상단에 표시
- ➕ **KR 수동 추가**: 사용자가 필요에 따라 KR을 추가 가능 (제한 없음)
- 🔗 **TASK 섹션과 실시간 연동**: KR 변경 시 하단 TASK 섹션에 자동 반영

#### 5.2.3 TASK 섹션 상세 설계 (하단)

| 컬럼 | 설명 | 데이터 타입 | 인터랙션 |
|------|------|------------|----------|
| **EM** | 아이젠하워 매트릭스 사분면 | 목록 박스 (Q1/Q2/Q3/Q4) | 드롭다운 선택 |
| **순서** | 태스크 우선순위 | 숫자 (자동) | 드래그&드롭으로 변경 |
| **SUB-TASK** | 세부 작업 항목 | 텍스트 | 인라인 편집 |
| **시작일** | 작업 시작 날짜 | Date | 데이트피커 |
| **기한** | 작업 완료 기한 | Date | 데이트피커 |
| **TASK** | 상위 태스크명 | 텍스트 | 인라인 편집 |
| **달성도** | 진행률 | % (자동계산) | 서브태스크 완료율 기반 |
| **KR no.** | 연결된 KR 번호 | 숫자 (연동) | OKR 섹션에서 자동 동기화 |
| **KR** | 연결된 KR 내용 | 텍스트 (연동) | OKR 섹션에서 자동 동기화 |
| **메모** | 자유 메모 | 텍스트 | 인라인 편집 |

**TASK 섹션 특징:**
- 📊 **ROW 무제한 추가**: 행을 계속 추가하여 태스크 관리
- 🔄 **순서 변경**: 드래그&드롭으로 우선순위 자유롭게 조정
- 🧮 **달성도 자동 계산**: 서브태스크 완료 개수에 따라 % 자동 갱신

#### 5.2.4 계층 구조 및 데이터 연동 규칙

```
┌─────────────────────────────────────────────────────────────┐
│                    데이터 계층 구조                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    OKR (최상위)                                              │
│      │                                                      │
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
│             ├── KR 2 ◄────────────────────┘ │               │
│             │     └── TASK C                │               │
│             │           └── Sub-Task C-1    │               │
│             │                               │               │
│             └── KR 3 (수동 추가 가능)         │               │
│                   └── ...                   │               │
│                                             │               │
└─────────────────────────────────────────────────────────────┘
```

**연동 규칙:**

| 규칙 | 설명 | 동작 |
|------|------|------|
| **KR ↔ TASK 연동** | OKR 섹션의 KR과 TASK 섹션의 KR 컬럼은 동일 데이터 | KR 수정 시 TASK 섹션에 자동 반영 |
| **트리 구조 동기화** | OKR > KR > TASK > SUB-TASK 계층 유지 | 상위 항목 변경 시 하위 항목 자동 업데이트 |
| **달성도 자동 계산** | SUB-TASK 완료율 → TASK 달성도 | (완료된 SUB-TASK / 전체 SUB-TASK) × 100% |
| **SUB-TASK 독립성** | SUB-TASK는 최소 단위로 값 연동 불필요 | 트리 구조 내 위치만 유지 |

#### 5.2.5 실시간 동기화 메커니즘

```javascript
// 동기화 이벤트 흐름
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  OKR 섹션     │────▶│  SyncEngine  │────▶│  TASK 섹션   │
│  KR 수정      │     │  (이벤트버스) │     │  KR 자동갱신 │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ localStorage │
                     │  영속화 저장  │
                     └──────────────┘
```

**동기화 트리거 이벤트:**
- `kr:created` - 새 KR 추가 시
- `kr:updated` - KR 내용 수정 시
- `kr:deleted` - KR 삭제 시
- `task:linked` - TASK에 KR 연결 시
- `subtask:completed` - SUB-TASK 완료 상태 변경 시
- `tree:reordered` - 트리 구조 순서 변경 시

### 5.3 반응형 레이아웃 전략

| 화면 크기 | OKR 섹션 | TASK 섹션 | 인터랙션 |
|-----------|----------|-----------|----------|
| **Desktop (>1200px)** | 상단 고정, 전체 너비 | 수평 스크롤 테이블 | 드래그&드롭 완전 지원 |
| **Tablet (768-1200px)** | 상단 고정, 축소 | 카드형 변환 | 터치 드래그 지원 |
| **Mobile (<768px)** | 접이식 아코디언 | 수직 카드 리스트 | 스와이프 액션 |

---

## 6. 상세 구현 가이드

### 6.1 핵심 컴포넌트 구현

#### OKR 섹션 컴포넌트

```javascript
class OKRSection {
  constructor(container, syncEngine) {
    this.container = container;
    this.syncEngine = syncEngine;
    this.okrData = null;
  }

  render(okr) {
    this.okrData = okr;
    this.container.innerHTML = `
      <div class="okr-section sticky-top">
        <div class="objective-row">
          <label>Objective</label>
          <input type="text" 
                 class="objective-input" 
                 value="${okr.objective}"
                 data-field="objective">
        </div>
        <div class="kr-table">
          <div class="kr-header">
            <span class="kr-no-col">KR no.</span>
            <span class="kr-content-col">Key Results</span>
            <span class="kr-action-col"></span>
          </div>
          ${okr.keyResults.map(kr => this.renderKRRow(kr)).join('')}
          <button class="add-kr-btn" onclick="this.addKR()">+ KR 추가</button>
        </div>
      </div>
    `;
    this.bindEvents();
  }

  renderKRRow(kr) {
    return `
      <div class="kr-row" data-kr-id="${kr.id}">
        <span class="kr-no">${kr.krNo}</span>
        <input type="text" 
               class="kr-input" 
               value="${kr.title}"
               data-kr-id="${kr.id}">
        <button class="delete-kr-btn" data-kr-id="${kr.id}">×</button>
      </div>
    `;
  }

  addKR() {
    const newKR = {
      id: `kr_${Date.now()}`,
      krNo: this.okrData.keyResults.length + 1,
      title: '',
      progress: 0,
      tasks: []
    };
    this.okrData.keyResults.push(newKR);
    this.syncEngine.emit('kr:created', newKR);
    this.render(this.okrData);
  }

  bindEvents() {
    // KR 입력 변경 시 동기화 트리거
    this.container.querySelectorAll('.kr-input').forEach(input => {
      input.addEventListener('change', (e) => {
        const krId = e.target.dataset.krId;
        const kr = this.okrData.keyResults.find(k => k.id === krId);
        kr.title = e.target.value;
        this.syncEngine.emit('kr:updated', kr);
      });
    });
  }
}
```

#### TASK 섹션 컴포넌트

```javascript
class TaskSection {
  constructor(container, syncEngine) {
    this.container = container;
    this.syncEngine = syncEngine;
    this.tasks = [];

    // 동기화 이벤트 구독
    this.syncEngine.on('kr:updated', (kr) => this.onKRUpdated(kr));
    this.syncEngine.on('kr:deleted', (kr) => this.onKRDeleted(kr));
  }

  onKRUpdated(kr) {
    // 연결된 모든 TASK의 KR 정보 자동 갱신
    this.tasks
      .filter(task => task.krId === kr.id)
      .forEach(task => {
        task.krNo = kr.krNo;
        task.krTitle = kr.title;
      });
    this.render();
  }

  calculateProgress(task) {
    if (!task.subTasks || task.subTasks.length === 0) return 0;
    const completed = task.subTasks.filter(st => st.completed).length;
    return Math.round((completed / task.subTasks.length) * 100);
  }

  render() {
    this.container.innerHTML = `
      <div class="task-section">
        <table class="task-table">
          <thead>
            <tr>
              <th>EM</th>
              <th>순서</th>
              <th>SUB-TASK</th>
              <th>시작일</th>
              <th>기한</th>
              <th>TASK</th>
              <th>달성도</th>
              <th>KR no.</th>
              <th>KR</th>
              <th>메모</th>
            </tr>
          </thead>
          <tbody>
            ${this.tasks.map(task => this.renderTaskRows(task)).join('')}
          </tbody>
        </table>
        <button class="add-row-btn" onclick="this.addTask()">+ 행 추가</button>
      </div>
    `;
    this.initDragDrop();
  }

  renderTaskRows(task) {
    const progress = this.calculateProgress(task);
    return task.subTasks.map((subTask, idx) => `
      <tr class="task-row" 
          draggable="true" 
          data-task-id="${task.id}" 
          data-subtask-id="${subTask.id}">
        <td>
          <select class="em-select" data-task-id="${task.id}">
            <option value="Q1" ${task.quadrant === 'Q1' ? 'selected' : ''}>Q1</option>
            <option value="Q2" ${task.quadrant === 'Q2' ? 'selected' : ''}>Q2</option>
            <option value="Q3" ${task.quadrant === 'Q3' ? 'selected' : ''}>Q3</option>
            <option value="Q4" ${task.quadrant === 'Q4' ? 'selected' : ''}>Q4</option>
          </select>
        </td>
        <td class="order-cell">${subTask.order}</td>
        <td><input type="text" value="${subTask.title}" class="subtask-input"></td>
        <td><input type="date" value="${subTask.startDate}"></td>
        <td><input type="date" value="${subTask.dueDate}"></td>
        ${idx === 0 ? `
          <td rowspan="${task.subTasks.length}">${task.title}</td>
          <td rowspan="${task.subTasks.length}" class="progress-cell">${progress}%</td>
          <td rowspan="${task.subTasks.length}" class="synced-kr-no">${task.krNo}</td>
          <td rowspan="${task.subTasks.length}" class="synced-kr-title">${task.krTitle}</td>
          <td rowspan="${task.subTasks.length}"><textarea>${task.memo || ''}</textarea></td>
        ` : ''}
      </tr>
    `).join('');
  }

  initDragDrop() {
    // 드래그&드롭으로 순서 변경
    const rows = this.container.querySelectorAll('.task-row');
    rows.forEach(row => {
      row.addEventListener('dragstart', this.handleDragStart.bind(this));
      row.addEventListener('dragover', this.handleDragOver.bind(this));
      row.addEventListener('drop', this.handleDrop.bind(this));
    });
  }
}
```

#### 동기화 엔진

```javascript
class SyncEngine {
  constructor() {
    this.listeners = {};
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }

  emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data));
    }
    // 모든 변경사항 자동 저장
    this.persistToStorage();
  }

  persistToStorage() {
    // localStorage에 현재 상태 저장
    const state = {
      okr: window.app.okrSection.okrData,
      tasks: window.app.taskSection.tasks,
      lastUpdated: new Date().toISOString()
    };
    localStorage.setItem('okr-em-state', JSON.stringify(state));
  }

  loadFromStorage() {
    const saved = localStorage.getItem('okr-em-state');
    return saved ? JSON.parse(saved) : null;
  }
}
```

### 6.2 UI 컴포넌트 스타일

```css
/* OKR 섹션 - 상단 고정 */
.okr-section {
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  margin-bottom: 20px;
}

.okr-section .objective-row {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.okr-section .objective-input {
  flex: 1;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  padding: 12px 16px;
  border-radius: 8px;
}

.kr-table {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  overflow: hidden;
}

.kr-row {
  display: grid;
  grid-template-columns: 80px 1fr 40px;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.add-kr-btn {
  width: 100%;
  padding: 12px;
  background: #f0f4ff;
  border: 2px dashed #667eea;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-kr-btn:hover {
  background: #667eea;
  color: white;
}

/* TASK 섹션 */
.task-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow-x: auto;
}

.task-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1200px;
}

.task-table th {
  background: #f8fafc;
  padding: 14px 12px;
  text-align: left;
  font-weight: 600;
  color: #374151;
  border-bottom: 2px solid #e5e7eb;
}

.task-table td {
  padding: 12px;
  border-bottom: 1px solid #f3f4f6;
  vertical-align: middle;
}

.task-row {
  transition: background 0.2s;
  cursor: grab;
}

.task-row:hover {
  background: #f8fafc;
}

.task-row.dragging {
  opacity: 0.5;
  cursor: grabbing;
}

/* EM 사분면 선택 스타일 */
.em-select {
  padding: 6px 10px;
  border-radius: 6px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.em-select[data-value="Q1"] { background: #fee2e2; color: #dc2626; }
.em-select[data-value="Q2"] { background: #dbeafe; color: #2563eb; }
.em-select[data-value="Q3"] { background: #fef3c7; color: #d97706; }
.em-select[data-value="Q4"] { background: #f3f4f6; color: #6b7280; }

/* 연동 컬럼 표시 (KR) */
.synced-kr-no,
.synced-kr-title {
  background: #f0f9ff;
  color: #0369a1;
  font-style: italic;
}

/* 달성도 프로그레스 바 */
.progress-cell {
  position: relative;
  min-width: 80px;
}

.progress-cell::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: #10b981;
  width: var(--progress, 0%);
  transition: width 0.3s;
}

/* 행 추가 버튼 */
.add-row-btn {
  width: 100%;
  padding: 16px;
  background: #f8fafc;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-row-btn:hover {
  background: #667eea;
  color: white;
}
```

### 6.3 드래그 앤 드롭 기능 구현

```javascript
class DragDropManager {
  constructor(taskSection) {
    this.taskSection = taskSection;
    this.draggedElement = null;
  }

  handleDragStart(e) {
    this.draggedElement = e.target.closest('.task-row');
    this.draggedElement.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
  }

  handleDragOver(e) {
    e.preventDefault();
    const targetRow = e.target.closest('.task-row');
    if (targetRow && targetRow !== this.draggedElement) {
      const rect = targetRow.getBoundingClientRect();
      const midpoint = rect.top + rect.height / 2;

      if (e.clientY < midpoint) {
        targetRow.parentNode.insertBefore(this.draggedElement, targetRow);
      } else {
        targetRow.parentNode.insertBefore(this.draggedElement, targetRow.nextSibling);
      }
    }
  }

  handleDrop(e) {
    e.preventDefault();
    this.draggedElement.classList.remove('dragging');
    this.updateOrder();
    this.taskSection.syncEngine.emit('tree:reordered', this.taskSection.tasks);
  }

  updateOrder() {
    const rows = this.taskSection.container.querySelectorAll('.task-row');
    rows.forEach((row, index) => {
      const subtaskId = row.dataset.subtaskId;
      const task = this.taskSection.tasks.find(t => 
        t.subTasks.some(st => st.id === subtaskId)
      );
      if (task) {
        const subtask = task.subTasks.find(st => st.id === subtaskId);
        subtask.order = index + 1;
      }
    });
  }
}
```

### 6.4 성능 최적화 전략

| 영역 | 전략 | 구현 방법 |
|------|------|----------|
| **DOM 조작** | Batch Update | `DocumentFragment` 사용 |
| **이벤트** | 이벤트 위임 | 컨테이너에 단일 리스너 |
| **검색** | 디바운스 | 300ms 지연 처리 |
| **저장** | 스로틀링 | 1초당 최대 1회 저장 |
| **렌더링** | 가상화 | 많은 태스크 시 화면 영역만 렌더 |

---

## 부록: 참고 자료 및 출처

### OKR 관련
- Quantive OKR Guide: https://quantive.com/resources/articles/okr-guide
- Google re:Work OKR Guide: https://rework.withgoogle.com/guides/set-goals-with-okrs
- Perdoo OKR Resources: https://www.perdoo.com/

### 아이젠하워 매트릭스 관련
- Eisenhower.me Official: https://www.eisenhower.me/
- Todoist Eisenhower Guide: https://todoist.com/productivity-methods/eisenhower-matrix
