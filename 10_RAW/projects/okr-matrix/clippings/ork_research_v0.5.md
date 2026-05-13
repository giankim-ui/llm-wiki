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
- **투명성(Transparency)**: 조직 전체가 목표를 공유하고 진행 상황을 확인
- **정렬(Alignment)**: 개인-팀-조직 목표의 수직적 연결
- **집중(Focus)**: 제한된 수의 핵심 목표에 집중
- **책임(Accountability)**: 측정 가능한 결과를 통한 명확한 책임

### 1.2 OKR의 구성 요소

#### A. Objectives (목표)
| 특성 | 설명 | 예시 |
|------|------|------|
| **영감적(Inspirational)** | 동기 부여가 되는 언어 사용 | "고객이 사랑하는 제품 만들기" |
| **정성적(Qualitative)** | 숫자가 아닌 방향성 제시 | "시장 리더십 확보" |
| **행동 지향적(Action-oriented)** | 동사로 시작하는 짧은 문장 | "개발 프로세스 혁신하기" |
| **시간 제한적(Time-bound)** | 분기/연간 단위 설정 | "Q1 내 달성" |

#### B. Key Results (핵심결과)
| 특성 | 설명 | 예시 |
|------|------|------|
| **측정 가능(Measurable)** | 구체적 수치로 표현 | "NPS 50 → 70 향상" |
| **결과 중심(Outcome-focused)** | 산출물이 아닌 결과 측정 | "기능 출시" ❌ → "사용률 30% 달성" ✅ |
| **도전적(Stretch)** | 60-70% 달성이 적정 | 100% 달성 = 목표가 낮았음 |
| **3-5개 제한** | 집중력 유지를 위한 제한 | 목표당 최대 5개 |

### 1.3 OKR 계층 구조

```
┌─────────────────────────────────────────┐
│           Company OKRs                  │
│   (연간/반기 - CEO 및 경영진 설정)        │
└─────────────────┬───────────────────────┘
                  │ 정렬(Alignment)
                  ▼
┌─────────────────────────────────────────┐
│           Department OKRs               │
│   (분기별 - 부서장 설정)                  │
└─────────────────┬───────────────────────┘
                  │ 정렬(Alignment)
                  ▼
┌─────────────────────────────────────────┐
│           Team OKRs                     │
│   (분기별 - 팀 리더 설정)                 │
└─────────────────┬───────────────────────┘
                  │ 정렬(Alignment)
                  ▼
┌─────────────────────────────────────────┐
│           Individual OKRs               │
│   (분기/월별 - 개인 설정)                 │
└─────────────────────────────────────────┘
```

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

#### 점수 체계
- **0.0 - 0.3**: 실패 (원인 분석 필요)
- **0.4 - 0.6**: 부분 달성 (개선점 파악)
- **0.7 - 0.8**: 성공적 달성 (이상적 범위)
- **0.9 - 1.0**: 완전 달성 (목표가 너무 쉬웠을 가능성)

---

## 2. 아이젠하워 매트릭스 핵심 개념

### 2.1 정의와 기원

드와이트 D. 아이젠하워 대통령의 시간 관리 원칙에서 유래한 **우선순위 결정 프레임워크**입니다.

> "What is important is seldom urgent and what is urgent is seldom important."
> — Dwight D. Eisenhower

### 2.2 4사분면 상세 분석

```
                    긴급함 (Urgent)
            ┌──────────────┬──────────────┐
            │              │              │
            │  Q1: DO      │  Q2: DECIDE  │
            │  (즉시 실행)  │  (계획 수립)  │
     중      │              │              │
     요      │  위기 관리    │  전략적 성장  │
     함      │  마감 임박    │  장기 목표    │
  (Important)│              │              │
            ├──────────────┼──────────────┤
            │              │              │
            │  Q3: DELEGATE│  Q4: DELETE  │
            │  (위임)       │  (제거)       │
            │              │              │
            │  방해 요소    │  시간 낭비    │
            │  일부 회의    │  불필요 활동  │
            │              │              │
            └──────────────┴──────────────┘
                    긴급하지 않음 (Not Urgent)
```

### 2.3 각 사분면 심층 분석

#### Q1: DO (긴급 & 중요) - 🔴 빨간색
| 항목 | 내용 |
|------|------|
| **정의** | 즉각적인 행동이 필요한 핵심 업무 |
| **특징** | 마감이 임박하고, 미처리 시 큰 영향 발생 |
| **예시** | 클라이언트 위기 대응, 마감일 당일 프로젝트, 긴급 버그 수정 |
| **전략** | 즉시 실행, 반복 방지를 위한 시스템 개선 |
| **주의** | Q1이 많으면 계획 부재 → Q2 투자 필요 |

#### Q2: DECIDE/SCHEDULE (중요 & 긴급하지 않음) - 🟢 녹색
| 항목 | 내용 |
|------|------|
| **정의** | 장기적 성공의 핵심인 전략적 업무 |
| **특징** | 마감 압박은 없지만 미래 가치 창출 |
| **예시** | 역량 개발, 관계 구축, 장기 프로젝트 기획, 건강 관리 |
| **전략** | 캘린더에 시간 블록 확보, 우선 처리 |
| **핵심** | **생산성의 핵심!** 여기에 시간 투자 극대화 |

#### Q3: DELEGATE (긴급 & 중요하지 않음) - 🟡 노란색
| 항목 | 내용 |
|------|------|
| **정의** | 다른 사람이 처리할 수 있는 업무 |
| **특징** | 시간 압박은 있지만 본인이 할 필요 없음 |
| **예시** | 일부 이메일, 일반 미팅, 단순 데이터 입력 |
| **전략** | 명확한 지침과 마감일을 주고 위임 |
| **팁** | 위임 불가 시 자동화 또는 최소화 |

#### Q4: DELETE (긴급하지 않음 & 중요하지 않음) - ⚫ 회색
| 항목 | 내용 |
|------|------|
| **정의** | 제거해야 할 시간 낭비 활동 |
| **특징** | 목표 달성에 기여하지 않음 |
| **예시** | 무목적 SNS, 불필요한 웹서핑, 과도한 휴식 |
| **전략** | 목록에서 삭제, 의식적 제한 |
| **주의** | 완전한 휴식과 구분 (휴식은 Q2!) |

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
┌─────────────────────────────────────────────────────────────┐
│                      OKR Framework                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Objective: "Q1 제품 출시 성공"                      │   │
│  │  ├─ KR1: 베타 사용자 1000명 확보                    │   │
│  │  ├─ KR2: 버그 발생률 0.1% 미만                      │   │
│  │  └─ KR3: NPS 점수 50 이상                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼ 태스크 분해                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Eisenhower Matrix (일일 실행)              │   │
│  │  ┌─────────────┬─────────────┐                      │   │
│  │  │ Q1: 버그 수정│ Q2: 기능개발 │                      │   │
│  │  │ (KR2 직결)  │ (KR1,3 기여)│                      │   │
│  │  ├─────────────┼─────────────┤                      │   │
│  │  │ Q3: 미팅응답│ Q4: 관련없는 │                      │   │
│  │  │ (위임가능)  │ 활동 제거   │                      │   │
│  │  └─────────────┴─────────────┘                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 통합의 핵심 원리

| OKR 요소 | 아이젠하워 매핑 | 설명 |
|----------|----------------|------|
| **Objective** | Q2 기반 | 장기 목표는 본질적으로 "중요하지만 긴급하지 않음" |
| **Key Results** | Q1/Q2 측정 | 마감이 다가올수록 Q2→Q1 이동 |
| **일일 태스크** | 4사분면 분류 | KR 달성을 위한 태스크를 매일 분류 |

### 3.3 통합 사용 워크플로우

```
[주간 시작]
    │
    ▼
┌───────────────────────┐
│ OKR 진행 상황 점검     │
│ - KR 달성률 확인       │
│ - 이번 주 집중 KR 선정 │
└───────────┬───────────┘
            │
            ▼
[일일 시작]
    │
    ▼
┌───────────────────────┐
│ 태스크 수집           │
│ - 새로운 업무 추가     │
│ - 기존 업무 검토       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 아이젠하워 분류       │
│ - 각 태스크 사분면 배치│
│ - KR과 연결 확인      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ 실행                  │
│ - Q1 즉시 처리        │
│ - Q2 시간 블록 확보   │
│ - Q3 위임/자동화      │
│ - Q4 제거             │
└───────────┬───────────┘
            │
            ▼
[일일 종료]
    │
    ▼
┌───────────────────────┐
│ 회고                  │
│ - 완료 태스크 체크    │
│ - KR 진행률 업데이트  │
│ - 내일 계획 수립      │
└───────────────────────┘
```

---

## 4. 최적의 코드베이스 설계안

### 4.1 아키텍처 패턴: MVC (Model-View-Controller)

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
├───────────────┬───────────────┬─────────────────────────────┤
│    MODEL      │    VIEW       │    CONTROLLER               │
├───────────────┼───────────────┼─────────────────────────────┤
│ • OKRModel    │ • OKRView     │ • AppController             │
│ • TaskModel   │ • MatrixView  │ • OKRController             │
│ • StorageAPI  │ • DashboardV  │ • MatrixController          │
└───────┬───────┴───────┬───────┴──────────────┬──────────────┘
        │               │                      │
        ▼               ▼                      ▼
┌───────────────┐ ┌───────────────┐  ┌────────────────────────┐
│  localStorage │ │    DOM API    │  │    Event Delegation    │
└───────────────┘ └───────────────┘  └────────────────────────┘
```

### 4.2 프로젝트 구조

```
okr-eisenhower-app/
│
├── index.html              # 메인 HTML 구조
├── css/
│   ├── main.css            # 전역 스타일
│   ├── components/
│   │   ├── okr-card.css    # OKR 카드 스타일
│   │   ├── matrix.css      # 4사분면 매트릭스 스타일
│   │   ├── task.css        # 태스크 아이템 스타일
│   │   └── modal.css       # 모달/팝업 스타일
│   └── utilities/
│       ├── variables.css   # CSS 변수 (색상, 폰트 등)
│       └── animations.css  # 애니메이션 정의
│
├── js/
│   ├── app.js              # 앱 초기화 및 부트스트랩
│   ├── models/
│   │   ├── OKR.js          # OKR 데이터 모델
│   │   ├── Task.js         # Task 데이터 모델
│   │   └── Storage.js      # localStorage 래퍼
│   ├── views/
│   │   ├── OKRView.js      # OKR 렌더링
│   │   ├── MatrixView.js   # 아이젠하워 매트릭스 렌더링
│   │   └── DashboardView.js# 대시보드/통계 렌더링
│   ├── controllers/
│   │   ├── AppController.js    # 전역 컨트롤러
│   │   ├── OKRController.js    # OKR CRUD 로직
│   │   └── MatrixController.js # 매트릭스 상호작용
│   └── utils/
│       ├── helpers.js      # 유틸리티 함수
│       ├── constants.js    # 상수 정의
│       └── validators.js   # 입력 검증
│
├── assets/
│   └── icons/              # SVG 아이콘
│
└── README.md
```

### 4.3 데이터 모델 설계

#### OKR 데이터 구조
```javascript
{
  "okrs": [
    {
      "id": "okr_uuid_001",
      "objective": "Q1 제품 출시 성공",
      "description": "시장 경쟁력 있는 MVP 출시",
      "period": {
        "type": "quarterly",
        "year": 2024,
        "quarter": 1,
        "startDate": "2024-01-01",
        "endDate": "2024-03-31"
      },
      "keyResults": [
        {
          "id": "kr_001",
          "description": "베타 사용자 확보",
          "metric": {
            "type": "number",
            "target": 1000,
            "current": 450,
            "unit": "명"
          },
          "confidence": 0.7,
          "status": "on-track"
        },
        {
          "id": "kr_002",
          "description": "버그 발생률 감소",
          "metric": {
            "type": "percentage",
            "target": 0.1,
            "current": 0.3,
            "unit": "%"
          },
          "confidence": 0.5,
          "status": "at-risk"
        }
      ],
      "progress": 45,
      "status": "active",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-02-15T10:30:00Z"
    }
  ]
}
```

#### Task 데이터 구조
```javascript
{
  "tasks": [
    {
      "id": "task_uuid_001",
      "title": "버그 #1234 수정",
      "description": "로그인 시 발생하는 500 에러 해결",
      "quadrant": 1,  // 1: Do, 2: Schedule, 3: Delegate, 4: Delete
      "priority": {
        "urgent": true,
        "important": true
      },
      "linkedOKR": {
        "okrId": "okr_uuid_001",
        "keyResultId": "kr_002"
      },
      "dueDate": "2024-02-16",
      "estimatedTime": 120,  // 분 단위
      "status": "in-progress",
      "delegatedTo": null,
      "tags": ["버그", "긴급"],
      "createdAt": "2024-02-15T09:00:00Z",
      "completedAt": null
    }
  ]
}
```

### 4.4 핵심 클래스 설계

#### Storage 클래스
```javascript
class Storage {
  static KEYS = {
    OKRS: 'okr_app_okrs',
    TASKS: 'okr_app_tasks',
    SETTINGS: 'okr_app_settings'
  };

  static get(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : null;
  }

  static set(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
  }

  static remove(key) {
    localStorage.removeItem(key);
  }

  static exportAll() {
    return {
      okrs: this.get(this.KEYS.OKRS),
      tasks: this.get(this.KEYS.TASKS),
      settings: this.get(this.KEYS.SETTINGS),
      exportedAt: new Date().toISOString()
    };
  }

  static importAll(data) {
    if (data.okrs) this.set(this.KEYS.OKRS, data.okrs);
    if (data.tasks) this.set(this.KEYS.TASKS, data.tasks);
    if (data.settings) this.set(this.KEYS.SETTINGS, data.settings);
  }
}
```

#### OKR Model 클래스
```javascript
class OKRModel {
  constructor() {
    this.okrs = Storage.get(Storage.KEYS.OKRS) || [];
  }

  // CRUD Operations
  add(okrData) {
    const okr = {
      id: this.generateId(),
      ...okrData,
      progress: 0,
      status: 'active',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    this.okrs.push(okr);
    this.save();
    return okr;
  }

  update(id, updates) {
    const index = this.okrs.findIndex(o => o.id === id);
    if (index !== -1) {
      this.okrs[index] = {
        ...this.okrs[index],
        ...updates,
        updatedAt: new Date().toISOString()
      };
      this.recalculateProgress(id);
      this.save();
      return this.okrs[index];
    }
    return null;
  }

  delete(id) {
    this.okrs = this.okrs.filter(o => o.id !== id);
    this.save();
  }

  // Key Result Operations
  updateKeyResult(okrId, krId, updates) {
    const okr = this.findById(okrId);
    if (okr) {
      const krIndex = okr.keyResults.findIndex(kr => kr.id === krId);
      if (krIndex !== -1) {
        okr.keyResults[krIndex] = { ...okr.keyResults[krIndex], ...updates };
        this.recalculateProgress(okrId);
        this.save();
      }
    }
  }

  // Progress Calculation
  recalculateProgress(okrId) {
    const okr = this.findById(okrId);
    if (okr && okr.keyResults.length > 0) {
      const totalProgress = okr.keyResults.reduce((sum, kr) => {
        const progress = (kr.metric.current / kr.metric.target) * 100;
        return sum + Math.min(progress, 100);
      }, 0);
      okr.progress = Math.round(totalProgress / okr.keyResults.length);
    }
  }

  // Query Methods
  findById(id) {
    return this.okrs.find(o => o.id === id);
  }

  filterByStatus(status) {
    return this.okrs.filter(o => o.status === status);
  }

  getActive() {
    return this.filterByStatus('active');
  }

  // Persistence
  save() {
    Storage.set(Storage.KEYS.OKRS, this.okrs);
  }

  generateId() {
    return 'okr_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }
}
```

#### Task Model 클래스
```javascript
class TaskModel {
  constructor() {
    this.tasks = Storage.get(Storage.KEYS.TASKS) || [];
  }

  add(taskData) {
    const task = {
      id: this.generateId(),
      ...taskData,
      quadrant: this.calculateQuadrant(taskData.priority),
      status: 'pending',
      createdAt: new Date().toISOString(),
      completedAt: null
    };
    this.tasks.push(task);
    this.save();
    return task;
  }

  calculateQuadrant(priority) {
    if (priority.urgent && priority.important) return 1;
    if (!priority.urgent && priority.important) return 2;
    if (priority.urgent && !priority.important) return 3;
    return 4;
  }

  moveToQuadrant(taskId, newQuadrant) {
    const task = this.findById(taskId);
    if (task) {
      task.quadrant = newQuadrant;
      task.priority = {
        urgent: newQuadrant === 1 || newQuadrant === 3,
        important: newQuadrant === 1 || newQuadrant === 2
      };
      this.save();
    }
  }

  getByQuadrant(quadrant) {
    return this.tasks.filter(t => t.quadrant === quadrant && t.status !== 'completed');
  }

  getByOKR(okrId) {
    return this.tasks.filter(t => t.linkedOKR?.okrId === okrId);
  }

  getByKeyResult(krId) {
    return this.tasks.filter(t => t.linkedOKR?.keyResultId === krId);
  }

  complete(taskId) {
    const task = this.findById(taskId);
    if (task) {
      task.status = 'completed';
      task.completedAt = new Date().toISOString();
      this.save();
    }
  }

  // ... 기타 CRUD 메서드
}
```

---

## 5. 권장 기술 스택 및 아키텍처

### 5.1 기술 스택

| 영역 | 기술 | 이유 |
|------|------|------|
| **마크업** | HTML5 (Semantic) | 접근성, SEO, 구조화 |
| **스타일링** | CSS3 (CSS Variables, Grid, Flexbox) | 프레임워크 없이 반응형 구현 |
| **스크립팅** | Vanilla JavaScript (ES6+) | 의존성 없음, 빠른 로딩 |
| **저장소** | localStorage API | 서버 없이 데이터 영속성 |
| **드래그앤드롭** | HTML5 Drag and Drop API | 네이티브 지원, 라이브러리 불필요 |
| **아이콘** | SVG (인라인 또는 sprite) | 확장성, 스타일링 용이 |

### 5.2 UI/UX 설계 원칙

#### 레이아웃 구조
```
┌─────────────────────────────────────────────────────────────┐
│  HEADER: 앱 타이틀 | 뷰 전환 (OKR / Matrix / Dashboard)      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─── OKR 패널 (좌측 30%) ───┐ ┌─── Matrix (우측 70%) ───┐ │
│  │                           │ │  ┌────────┬────────┐    │ │
│  │  [Objective 1]            │ │  │   Q1   │   Q2   │    │ │
│  │    ├─ KR1 ████░░ 60%     │ │  │   DO   │ DECIDE │    │ │
│  │    ├─ KR2 ██░░░░ 30%     │ │  │        │        │    │ │
│  │    └─ KR3 ███░░░ 45%     │ │  ├────────┼────────┤    │ │
│  │                           │ │  │   Q3   │   Q4   │    │ │
│  │  [+ 새 OKR 추가]          │ │  │DELEGATE│ DELETE │    │ │
│  │                           │ │  │        │        │    │ │
│  │                           │ │  └────────┴────────┘    │ │
│  └───────────────────────────┘ └─────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  FOOTER: 통계 요약 | 내보내기/가져오기 | 설정                 │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 핵심 기능 명세

#### 필수 기능 (MVP)
1. **OKR 관리**
   - OKR 생성/수정/삭제
   - Key Result 추가/수정/삭제
   - 진행률 자동 계산
   - 기간별 필터링 (분기/월)

2. **아이젠하워 매트릭스**
   - 4사분면 시각화
   - 드래그앤드롭으로 태스크 이동
   - 사분면별 태스크 카운트
   - 색상 코딩 (긴급도/중요도)

3. **태스크 관리**
   - 태스크 CRUD
   - OKR/KR 연결
   - 완료 체크
   - 마감일 설정

4. **데이터 관리**
   - localStorage 저장
   - JSON 내보내기/가져오기

#### 확장 기능 (향후)
- 주간/일간 리포트
- 알림/리마인더
- 다크 모드
- 협업 (Firebase 연동)
- PWA 지원

---

## 6. 상세 구현 가이드

### 6.1 HTML 구조 (index.html)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OKR & Eisenhower Matrix</title>
  <link rel="stylesheet" href="css/main.css">
</head>
<body>
  <div id="app">
    <!-- Header -->
    <header class="app-header">
      <h1>🎯 OKR Matrix</h1>
      <nav class="view-switcher">
        <button data-view="combined" class="active">통합 뷰</button>
        <button data-view="okr">OKR 목록</button>
        <button data-view="matrix">매트릭스</button>
        <button data-view="dashboard">대시보드</button>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <!-- OKR Panel -->
      <aside class="okr-panel" id="okr-panel">
        <div class="panel-header">
          <h2>목표 (Objectives)</h2>
          <button id="add-okr-btn" class="btn-primary">+ 새 OKR</button>
        </div>
        <div class="okr-list" id="okr-list">
          <!-- OKR cards rendered here -->
        </div>
      </aside>

      <!-- Eisenhower Matrix -->
      <section class="matrix-container" id="matrix-container">
        <div class="matrix-header">
          <h2>아이젠하워 매트릭스</h2>
          <button id="add-task-btn" class="btn-secondary">+ 태스크</button>
        </div>
        <div class="matrix-grid">
          <div class="quadrant q1" data-quadrant="1" 
               ondragover="event.preventDefault()" ondrop="handleDrop(event)">
            <div class="quadrant-header">
              <span class="quadrant-icon">🔥</span>
              <h3>DO (즉시 실행)</h3>
              <span class="task-count" id="q1-count">0</span>
            </div>
            <div class="quadrant-label">긴급 & 중요</div>
            <div class="task-list" id="q1-tasks"></div>
          </div>
          <div class="quadrant q2" data-quadrant="2"
               ondragover="event.preventDefault()" ondrop="handleDrop(event)">
            <div class="quadrant-header">
              <span class="quadrant-icon">📅</span>
              <h3>SCHEDULE (계획)</h3>
              <span class="task-count" id="q2-count">0</span>
            </div>
            <div class="quadrant-label">중요 & 긴급하지 않음</div>
            <div class="task-list" id="q2-tasks"></div>
          </div>
          <div class="quadrant q3" data-quadrant="3"
               ondragover="event.preventDefault()" ondrop="handleDrop(event)">
            <div class="quadrant-header">
              <span class="quadrant-icon">👥</span>
              <h3>DELEGATE (위임)</h3>
              <span class="task-count" id="q3-count">0</span>
            </div>
            <div class="quadrant-label">긴급 & 중요하지 않음</div>
            <div class="task-list" id="q3-tasks"></div>
          </div>
          <div class="quadrant q4" data-quadrant="4"
               ondragover="event.preventDefault()" ondrop="handleDrop(event)">
            <div class="quadrant-header">
              <span class="quadrant-icon">🗑️</span>
              <h3>ELIMINATE (제거)</h3>
              <span class="task-count" id="q4-count">0</span>
            </div>
            <div class="quadrant-label">긴급하지 않음 & 중요하지 않음</div>
            <div class="task-list" id="q4-tasks"></div>
          </div>
        </div>
      </section>
    </main>

    <!-- Modals -->
    <div class="modal" id="okr-modal">
      <!-- OKR 생성/수정 폼 -->
    </div>
    <div class="modal" id="task-modal">
      <!-- Task 생성/수정 폼 -->
    </div>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="stats-summary">
        <span>활성 OKR: <strong id="active-okr-count">0</strong></span>
        <span>오늘 할 일: <strong id="today-task-count">0</strong></span>
      </div>
      <div class="actions">
        <button id="export-btn">📤 내보내기</button>
        <button id="import-btn">📥 가져오기</button>
      </div>
    </footer>
  </div>

  <script type="module" src="js/app.js"></script>
</body>
</html>
```

### 6.2 CSS 핵심 스타일 (주요 부분)

```css
/* css/utilities/variables.css */
:root {
  /* Colors - Quadrant */
  --q1-color: #ef4444;  /* Red - Do */
  --q2-color: #22c55e;  /* Green - Schedule */
  --q3-color: #f59e0b;  /* Yellow - Delegate */
  --q4-color: #6b7280;  /* Gray - Delete */

  /* Colors - Status */
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --info: #3b82f6;

  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;

  /* Layout */
  --okr-panel-width: 320px;
  --header-height: 60px;
  --footer-height: 50px;
}

/* css/components/matrix.css */
.matrix-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: var(--space-md);
  height: calc(100vh - var(--header-height) - var(--footer-height) - 100px);
}

.quadrant {
  border-radius: 12px;
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.quadrant.q1 { background: linear-gradient(135deg, #fef2f2, #fee2e2); border-left: 4px solid var(--q1-color); }
.quadrant.q2 { background: linear-gradient(135deg, #f0fdf4, #dcfce7); border-left: 4px solid var(--q2-color); }
.quadrant.q3 { background: linear-gradient(135deg, #fffbeb, #fef3c7); border-left: 4px solid var(--q3-color); }
.quadrant.q4 { background: linear-gradient(135deg, #f9fafb, #f3f4f6); border-left: 4px solid var(--q4-color); }

.quadrant.drag-over {
  transform: scale(1.02);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.task-item {
  background: white;
  border-radius: 8px;
  padding: var(--space-sm) var(--space-md);
  margin-bottom: var(--space-sm);
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.2s ease;
}

.task-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.task-item.dragging {
  opacity: 0.5;
  cursor: grabbing;
}
```

### 6.3 이벤트 처리 및 드래그앤드롭

```javascript
// js/controllers/MatrixController.js
class MatrixController {
  constructor(taskModel, matrixView) {
    this.taskModel = taskModel;
    this.matrixView = matrixView;
    this.draggedTask = null;
  }

  init() {
    this.setupEventDelegation();
    this.render();
  }

  setupEventDelegation() {
    const container = document.getElementById('matrix-container');

    // Drag events
    container.addEventListener('dragstart', (e) => this.handleDragStart(e));
    container.addEventListener('dragend', (e) => this.handleDragEnd(e));
    container.addEventListener('dragover', (e) => this.handleDragOver(e));
    container.addEventListener('dragleave', (e) => this.handleDragLeave(e));
    container.addEventListener('drop', (e) => this.handleDrop(e));

    // Click events (delegation)
    container.addEventListener('click', (e) => {
      if (e.target.matches('.task-complete-btn')) {
        this.completeTask(e.target.closest('.task-item').dataset.id);
      }
      if (e.target.matches('.task-delete-btn')) {
        this.deleteTask(e.target.closest('.task-item').dataset.id);
      }
      if (e.target.matches('.task-edit-btn')) {
        this.editTask(e.target.closest('.task-item').dataset.id);
      }
    });
  }

  handleDragStart(e) {
    if (!e.target.classList.contains('task-item')) return;

    this.draggedTask = e.target;
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', e.target.dataset.id);
  }

  handleDragEnd(e) {
    if (this.draggedTask) {
      this.draggedTask.classList.remove('dragging');
      this.draggedTask = null;
    }
    document.querySelectorAll('.quadrant').forEach(q => q.classList.remove('drag-over'));
  }

  handleDragOver(e) {
    e.preventDefault();
    const quadrant = e.target.closest('.quadrant');
    if (quadrant) {
      quadrant.classList.add('drag-over');
    }
  }

  handleDragLeave(e) {
    const quadrant = e.target.closest('.quadrant');
    if (quadrant && !quadrant.contains(e.relatedTarget)) {
      quadrant.classList.remove('drag-over');
    }
  }

  handleDrop(e) {
    e.preventDefault();
    const quadrant = e.target.closest('.quadrant');
    if (!quadrant) return;

    const taskId = e.dataTransfer.getData('text/plain');
    const newQuadrant = parseInt(quadrant.dataset.quadrant);

    this.taskModel.moveToQuadrant(taskId, newQuadrant);
    this.render();

    // Feedback
    quadrant.classList.remove('drag-over');
    this.showNotification(`태스크가 ${this.getQuadrantName(newQuadrant)}(으)로 이동되었습니다.`);
  }

  getQuadrantName(q) {
    const names = { 1: 'DO', 2: 'SCHEDULE', 3: 'DELEGATE', 4: 'ELIMINATE' };
    return names[q];
  }

  render() {
    [1, 2, 3, 4].forEach(q => {
      const tasks = this.taskModel.getByQuadrant(q);
      const container = document.getElementById(`q${q}-tasks`);
      const count = document.getElementById(`q${q}-count`);

      container.innerHTML = tasks.map(task => this.matrixView.renderTask(task)).join('');
      count.textContent = tasks.length;
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
- Perdoo OKR Resources: https://www.perdoo.com/resources

### 아이젠하워 매트릭스 관련
- Monday.com Eisenhower Template: https://monday.com/blog/ko/eisenhower-matrix-template
- Asana Eisenhower Guide: https://asana.com/ko/resources/eisenhower-matrix
- Eisenhower.me Apps: https://www.eisenhower.me/eisenhower-matrix-apps

### 기술 구현 관련
- HTML5 Drag and Drop API: MDN Web Docs
- localStorage API: MDN Web Docs
- GitHub Open Source: https://github.com/antoinechampion/eisenhower-matrix

---

*문서 작성일: 2024년*
*버전: 1.0*
