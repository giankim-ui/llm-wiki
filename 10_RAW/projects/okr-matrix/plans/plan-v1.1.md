# OKR Matrix App v1.1 — 울트라 구현 계획서

## 📋 문서 개요

| 항목 | 내용 |
|------|------|
| 버전 | v1.1 |
| 기준 문서 | app.summary.md, research-v1.1.md |
| 작성 목적 | 신규 기능 2개의 전문가 수준 구현 가이드 |
| 예상 복잡도 | ★★★★☆ (고급) |

---

# Part 1: 기존 앱 아키텍처 심층 분석

## 1.1 기술 스택 및 빌드 환경

```
┌─────────────────────────────────────────────────────────┐
│  OKR Matrix App — 바닐라 TypeScript 웹앱               │
├─────────────────────────────────────────────────────────┤
│  언어: TypeScript (ES Module)                          │
│  번들러: esbuild                                        │
│  프레임워크: 없음 (Vanilla DOM 조작)                    │
│  저장소: localStorage (키: okr-matrix-v2)              │
│  빌드물: bundle.js, bundle.html (단일파일 배포용)      │
└─────────────────────────────────────────────────────────┘
```

## 1.2 데이터 모델 계층 구조

```
OKR (Objective)
 └── KR (Key Result) [1:N]
      └── Task [1:N]
           └── SubTask [1:N]
                ├── 시작일 (startDate)
                ├── 기한 (dueDate)
                └── 완료여부 (completed: boolean)
```

### EMQuadrant (아이젠하워 매트릭스)
| 값 | 분류 | 색상 | 의미 |
|----|------|------|------|
| 1 | Q1 | 빨강 | 긴급 + 중요 |
| 2 | Q2 | 남색 | 중요 + 비긴급 |
| 3 | Q3 | 주황 | 긴급 + 비중요 |
| 4 | Q4 | 회색 | 제거 대상 |

## 1.3 MVC 아키텍처 상세

```
                    ┌─────────────┐
                    │   App.ts    │  ← 진입점 (이벤트 조정자)
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │   Store    │  │   Views    │  │  ModalView │
    │ (상태관리) │  │ (렌더링)   │  │  (폼 처리) │
    └────────────┘  └────────────┘  └────────────┘
           │               │               │
           │    subscribe()│               │
           ◀───────────────┘               │
           │                               │
           │         events 콜백           │
           ◀───────────────────────────────┘
           │
           ▼
    ┌────────────┐
    │localStorage│  ← 800ms 디바운스 자동저장
    └────────────┘
```

### 컴포넌트별 역할

| 컴포넌트 | 역할 | 주요 메서드 |
|----------|------|-------------|
| **Store** | 상태 관리, 영속화 | `subscribe()`, `save()`, `load()` |
| **OKRSection** | OKR/KR 테이블 렌더링 | `render()`, KR 드래그앤드롭 |
| **TaskSection** | Task/SubTask 테이블 렌더링 | `render()`, Task/SubTask D&D |
| **ModalView** | 7종 모달 폼 | `open()`, `close()`, 데이터 바인딩 |
| **ToastView** | 알림 토스트 | `show()`, 자동 dismiss |

## 1.4 현재 기능 매트릭스

### OKR 섹션
- ✅ Objective 텍스트 CRUD
- ✅ KR 추가/편집/삭제 (연쇄 삭제 포함)
- ✅ KR 드래그앤드롭 순서 변경
- ✅ KR 클릭 → Task 섹션 하이라이트 연동
- ✅ KR 진행률 바 (SubTask 완료율 자동 계산)
- ✅ KR 목록 접기/펴기

### Task 섹션
- ✅ Task CRUD (연쇄 삭제 포함)
- ✅ Task 그룹 헤더 행 표시
- ✅ Task 드래그앤드롭 (동일 KR 내)
- ✅ SubTask CRUD
- ✅ SubTask 드래그앤드롭 (동일 Task 내)
- ✅ SubTask 완료 체크박스
- ✅ 기한 초과 강조 표시

### 테이블 컬럼 구조
```
| EM | 순서 | SUB-TASK | 시작일 | 기한 | TASK | 달성도 | KR no. | KR 내용 |
```

---

# Part 2: 신규 기능 요구사항 심층 분석

## 2.1 기능 1: TASK 이동 기능 개선

### 현재 제약사항
```
[AS-IS]
KR1 ─┬─ Task A
     └─ Task B
KR2 ─┬─ Task C
     └─ Task D
KR3 ─── Task E

※ Task는 동일 KR 내에서만 이동 가능
※ KR 순서(KR.NO)에 종속된 구조
```

### 요구사항
```
[TO-BE]
- KR 순서(NO)와 무관하게 KR 자체를 자유롭게 재배치
- 예: KR3를 KR1 위로 이동 가능
- D&D로 KR 순서 변경 시 하위 Task/SubTask도 함께 이동
```

### 영향 범위 분석
| 영역 | 영향도 | 변경 내용 |
|------|--------|-----------|
| Store | 🔴 높음 | KR 배열 순서 변경 로직 |
| OKRSection | 🔴 높음 | D&D 핸들러 개선, 시각적 피드백 |
| TaskSection | 🟡 중간 | KR 순서 변경 시 Task 그룹 재정렬 |
| types/index.ts | 🟢 낮음 | 기존 타입 유지 (order 필드 활용) |

---

## 2.2 기능 2: TASK 완료 내역 별도 탭 신설

### 탭 구조 설계
```
┌──────────────────────────────────────────────────────┐
│  TASK SECTION                                        │
├──────────┬───────────┐                               │
│ 🔵 작업중 │ ✅ 완료   │  ← 신규 탭 UI                │
├──────────┴───────────┴───────────────────────────────┤
│                                                      │
│  [Task 테이블 영역]                                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 완료 판정 로직 (핵심)

```typescript
// 완료 조건 (모두 충족해야 함)
interface CompletionCriteria {
  allSubTasksCompleted: boolean;  // Task 내 모든 SubTask의 completed === true
  allStartDatesSet: boolean;      // 모든 SubTask에 시작일 입력됨
  allDueDatesSet: boolean;        // 모든 SubTask에 기한 입력됨
}

function isTaskCompleted(task: Task): boolean {
  if (task.subTasks.length === 0) return false;

  return task.subTasks.every(st => 
    st.completed === true &&
    st.startDate !== null && st.startDate !== '' &&
    st.dueDate !== null && st.dueDate !== ''
  );
}
```

### 명시적 제외 규칙 (Don't do it)

| # | 제외 규칙 | 근거 |
|---|-----------|------|
| 1 | Task 내 일부 SubTask만 완료 시 이동 금지 | 부분 완료는 작업중 상태 |
| 2 | 완료되어도 OKR 진행률 계산 로직 변경 금지 | 기존 로직 유지 |

### 영향 범위 분석
| 영역 | 영향도 | 변경 내용 |
|------|--------|-----------|
| types/index.ts | 🟡 중간 | 탭 상태 타입 추가 |
| Store | 🔴 높음 | 탭 필터링 로직, 완료 판정 로직 |
| TaskSection | 🔴 높음 | 탭 UI, 탭 전환, 필터 렌더링 |
| OKRSection | 🟢 낮음 | 진행률 계산 로직 유지 (변경 없음) |
| ModalView | 🟢 낮음 | 기존 유지 |

---

## 2.3 기능 3: 운영 업무 연결 기능 (Task 추가 팝업 개선)

### 요구사항
```
기존 KR-Task-SubTask 계층에 포함되지 않는 
"운영 업무"를 연결할 수 있는 기능 추가
```

### UI 변경사항
```
┌─────────────────────────────────────────┐
│         Task 추가 팝업                  │
├─────────────────────────────────────────┤
│ Task 이름: [________________]           │
│                                         │
│ KR 연결:   [KR 선택 드롭다운 ▼]        │
│                                         │
│ ☐ 운영 업무로 등록 (KR 미연결)  ← 신규 │
│                                         │
│        [취소]  [저장]                   │
└─────────────────────────────────────────┘
```

### 영향 범위 분석
| 영역 | 영향도 | 변경 내용 |
|------|--------|-----------|
| types/index.ts | 🔴 높음 | Task에 isOperational 필드 추가 또는 krId nullable |
| Store | 🟡 중간 | 운영 업무 필터링/관리 로직 |
| ModalView | 🔴 높음 | 체크박스 UI, 조건부 KR 선택 |
| TaskSection | 🟡 중간 | 운영 업무 표시 (KR 미연결 그룹) |

---

# Part 3: 울트라 구현 계획

## 3.1 구현 순서 (의존성 기반)

```
Phase 1: 기반 작업
    │
    ├─► [1-1] 타입 정의 확장
    │
    └─► [1-2] Store 리팩토링 (완료 판정 로직)
            │
            ▼
Phase 2: 기능 1 — KR 이동 개선
    │
    ├─► [2-1] OKRSection D&D 개선
    │
    └─► [2-2] TaskSection 연동 업데이트
            │
            ▼
Phase 3: 기능 2 — 완료 탭
    │
    ├─► [3-1] 탭 UI 컴포넌트 구현
    │
    ├─► [3-2] 필터링 로직 구현
    │
    └─► [3-3] 자동 이동 로직 구현
            │
            ▼
Phase 4: 기능 3 — 운영 업무
    │
    ├─► [4-1] Modal 체크박스 추가
    │
    └─► [4-2] 운영 업무 그룹 렌더링
            │
            ▼
Phase 5: 통합 테스트 및 마무리
```

---

## 3.2 Phase 1: 기반 작업

### [1-1] 타입 정의 확장 (`src/types/index.ts`)

```typescript
// 기존 타입 유지하며 확장

// 탭 상태 타입 추가
export type TaskTabType = 'working' | 'completed';

// Task 타입 확장
export interface Task {
  id: string;
  krId: string | null;       // ✨ nullable로 변경 (운영업무 지원)
  title: string;
  order: number;
  subTasks: SubTask[];
  isOperational?: boolean;   // ✨ 신규: 운영 업무 플래그
}

// 앱 상태 타입 확장
export interface AppState {
  // ... 기존 필드
  activeTaskTab: TaskTabType;  // ✨ 신규: 현재 활성 탭
}
```

### [1-2] Store 리팩토링

```typescript
// src/store.ts

class Store {
  // ✨ 신규: 완료 판정 헬퍼
  isTaskCompleted(task: Task): boolean {
    if (task.subTasks.length === 0) return false;

    return task.subTasks.every(st => 
      st.completed === true &&
      this.isValidDate(st.startDate) &&
      this.isValidDate(st.dueDate)
    );
  }

  private isValidDate(date: string | null | undefined): boolean {
    return date !== null && date !== undefined && date.trim() !== '';
  }

  // ✨ 신규: 탭별 Task 필터링
  getTasksByTab(tab: TaskTabType): Task[] {
    const allTasks = this.getAllTasks();

    if (tab === 'completed') {
      return allTasks.filter(t => this.isTaskCompleted(t));
    }
    return allTasks.filter(t => !this.isTaskCompleted(t));
  }

  // ✨ 신규: 탭 전환
  setActiveTab(tab: TaskTabType): void {
    this.state.activeTaskTab = tab;
    this.notify();
  }
}
```

---

## 3.3 Phase 2: KR 이동 기능 개선

### [2-1] OKRSection D&D 개선 (`src/views/OKRSection.ts`)

```typescript
// 핵심 변경사항

class OKRSection {
  private draggedKRId: string | null = null;

  render() {
    // KR 행에 드래그 속성 추가
    krRows.forEach(kr => {
      const row = this.createKRRow(kr);
      row.draggable = true;
      row.dataset.krId = kr.id;

      // ✨ 개선된 D&D 이벤트
      row.addEventListener('dragstart', this.handleDragStart.bind(this));
      row.addEventListener('dragover', this.handleDragOver.bind(this));
      row.addEventListener('drop', this.handleDrop.bind(this));
      row.addEventListener('dragend', this.handleDragEnd.bind(this));
    });
  }

  private handleDragStart(e: DragEvent) {
    const target = e.target as HTMLElement;
    this.draggedKRId = target.dataset.krId!;
    target.classList.add('dragging');

    // ✨ 시각적 피드백: 드롭 가능 영역 표시
    this.showDropZones();
  }

  private handleDragOver(e: DragEvent) {
    e.preventDefault();
    const target = e.target as HTMLElement;
    const krRow = target.closest('[data-kr-id]');

    if (krRow && krRow.dataset.krId !== this.draggedKRId) {
      // ✨ 삽입 위치 미리보기
      this.showInsertionIndicator(krRow, e.clientY);
    }
  }

  private handleDrop(e: DragEvent) {
    e.preventDefault();
    const target = e.target as HTMLElement;
    const dropTarget = target.closest('[data-kr-id]');

    if (dropTarget && this.draggedKRId) {
      const targetKRId = dropTarget.dataset.krId!;

      // ✨ Store에 순서 변경 요청
      this.events.onReorderKR(this.draggedKRId, targetKRId, this.insertPosition);
    }

    this.clearDragState();
  }

  // ✨ 신규: 드롭존 시각화
  private showDropZones() {
    document.querySelectorAll('[data-kr-id]').forEach(row => {
      if (row.dataset.krId !== this.draggedKRId) {
        row.classList.add('drop-zone');
      }
    });
  }
}
```

### [2-2] Store KR 순서 변경 로직

```typescript
// src/store.ts

reorderKR(draggedId: string, targetId: string, position: 'before' | 'after'): void {
  const krs = [...this.state.okr.keyResults];

  const draggedIndex = krs.findIndex(kr => kr.id === draggedId);
  const targetIndex = krs.findIndex(kr => kr.id === targetId);

  if (draggedIndex === -1 || targetIndex === -1) return;

  // 드래그된 KR 추출
  const [draggedKR] = krs.splice(draggedIndex, 1);

  // 새 위치에 삽입
  const newIndex = position === 'before' 
    ? targetIndex 
    : targetIndex + 1;

  krs.splice(draggedIndex < targetIndex ? newIndex - 1 : newIndex, 0, draggedKR);

  // order 필드 재계산
  krs.forEach((kr, idx) => kr.order = idx + 1);

  this.state.okr.keyResults = krs;
  this.notify();
  this.scheduleSave();
}
```

---

## 3.4 Phase 3: 완료 탭 구현

### [3-1] 탭 UI 컴포넌트 (`src/views/TaskSection.ts`)

```typescript
// 탭 UI 렌더링

private renderTabs(): HTMLElement {
  const tabContainer = document.createElement('div');
  tabContainer.className = 'task-tabs';
  tabContainer.innerHTML = `
    <button class="tab-btn ${this.activeTab === 'working' ? 'active' : ''}" 
            data-tab="working">
      🔵 작업중
      <span class="badge">${this.getWorkingCount()}</span>
    </button>
    <button class="tab-btn ${this.activeTab === 'completed' ? 'active' : ''}" 
            data-tab="completed">
      ✅ 완료
      <span class="badge">${this.getCompletedCount()}</span>
    </button>
  `;

  // 탭 클릭 이벤트
  tabContainer.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const tab = (e.target as HTMLElement).dataset.tab as TaskTabType;
      this.events.onTabChange(tab);
    });
  });

  return tabContainer;
}
```

### [3-2] 필터링 로직 구현

```typescript
// TaskSection 렌더링 로직 수정

render() {
  const container = this.getContainer();
  container.innerHTML = '';

  // ✨ 탭 UI 삽입
  container.appendChild(this.renderTabs());

  // ✨ 현재 탭에 맞는 Task만 필터링
  const tasks = this.store.getTasksByTab(this.activeTab);

  // 테이블 렌더링
  const table = this.renderTaskTable(tasks);
  container.appendChild(table);
}
```

### [3-3] 자동 이동 로직

```typescript
// Store에서 SubTask 상태 변경 감지

updateSubTask(taskId: string, subTaskId: string, updates: Partial<SubTask>): void {
  // ... 기존 업데이트 로직

  // ✨ 완료 상태 변경 시 탭 이동 체크
  const task = this.getTaskById(taskId);
  if (task) {
    const wasCompleted = this.isTaskCompleted(task);

    // 업데이트 적용
    Object.assign(subTask, updates);

    const isNowCompleted = this.isTaskCompleted(task);

    // 상태 변경 감지 → 토스트 알림
    if (!wasCompleted && isNowCompleted) {
      this.showToast('✅ Task가 완료되어 [완료] 탭으로 이동합니다.', 'success');
    } else if (wasCompleted && !isNowCompleted) {
      this.showToast('🔄 Task가 [작업중] 탭으로 복원되었습니다.', 'info');
    }
  }

  this.notify();
  this.scheduleSave();
}
```

### CSS 스타일 추가

```css
/* 탭 스타일 */
.task-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 16px;
  border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
  padding: 12px 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  position: relative;
  transition: all 0.2s ease;
}

.tab-btn.active {
  color: #1a73e8;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #1a73e8;
}

.tab-btn .badge {
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #e8f0fe;
  color: #1a73e8;
  font-size: 12px;
}

.tab-btn.active .badge {
  background: #1a73e8;
  color: white;
}
```

---

## 3.5 Phase 4: 운영 업무 기능

### [4-1] Modal 체크박스 추가 (`src/views/ModalView.ts`)

```typescript
// add-task 모달 렌더링 수정

private renderAddTaskForm(): string {
  return `
    <div class="modal-content">
      <h3>Task 추가</h3>

      <div class="form-group">
        <label for="task-title">Task 이름</label>
        <input type="text" id="task-title" required>
      </div>

      <div class="form-group">
        <label for="kr-select">KR 연결</label>
        <select id="kr-select" ${this.isOperational ? 'disabled' : ''}>
          <option value="">KR 선택...</option>
          ${this.renderKROptions()}
        </select>
      </div>

      <!-- ✨ 신규: 운영 업무 체크박스 -->
      <div class="form-group checkbox-group">
        <label>
          <input type="checkbox" id="is-operational" 
                 ${this.isOperational ? 'checked' : ''}>
          운영 업무로 등록 (KR 미연결)
        </label>
        <p class="hint">체크 시 KR과 연결되지 않는 독립 업무로 관리됩니다.</p>
      </div>

      <div class="modal-actions">
        <button type="button" class="btn-cancel">취소</button>
        <button type="submit" class="btn-submit">저장</button>
      </div>
    </div>
  `;
}

private setupOperationalCheckbox() {
  const checkbox = document.getElementById('is-operational') as HTMLInputElement;
  const krSelect = document.getElementById('kr-select') as HTMLSelectElement;

  checkbox.addEventListener('change', () => {
    this.isOperational = checkbox.checked;
    krSelect.disabled = this.isOperational;

    if (this.isOperational) {
      krSelect.value = '';
    }
  });
}
```

### [4-2] 운영 업무 그룹 렌더링

```typescript
// TaskSection 렌더링에 운영 업무 그룹 추가

private renderTaskGroups(): HTMLElement[] {
  const groups: HTMLElement[] = [];

  // KR별 Task 그룹
  this.store.state.okr.keyResults.forEach(kr => {
    const krTasks = this.getTasksByKR(kr.id);
    if (krTasks.length > 0) {
      groups.push(this.renderKRGroup(kr, krTasks));
    }
  });

  // ✨ 운영 업무 그룹 (KR 미연결)
  const operationalTasks = this.getOperationalTasks();
  if (operationalTasks.length > 0) {
    groups.push(this.renderOperationalGroup(operationalTasks));
  }

  return groups;
}

private renderOperationalGroup(tasks: Task[]): HTMLElement {
  const group = document.createElement('div');
  group.className = 'task-group operational-group';
  group.innerHTML = `
    <div class="group-header operational">
      <span class="group-icon">⚙️</span>
      <span class="group-title">운영 업무</span>
      <span class="group-count">${tasks.length}개</span>
    </div>
  `;

  tasks.forEach(task => {
    group.appendChild(this.renderTaskRow(task));
  });

  return group;
}
```

---

## 3.6 Phase 5: 통합 테스트 체크리스트

### 기능 1: KR 이동
| # | 테스트 케이스 | 예상 결과 |
|---|---------------|-----------|
| 1 | KR3를 KR1 위로 드래그 | KR3 → KR1 → KR2 순서로 변경 |
| 2 | KR 이동 후 새로고침 | 변경된 순서 유지 |
| 3 | KR 이동 시 하위 Task | 함께 이동, 연결 유지 |
| 4 | 드래그 중 시각적 피드백 | 드롭존 하이라이트, 삽입선 표시 |

### 기능 2: 완료 탭
| # | 테스트 케이스 | 예상 결과 |
|---|---------------|-----------|
| 1 | 모든 SubTask 완료 체크 | Task가 완료 탭으로 자동 이동 |
| 2 | 완료 탭에서 체크 해제 | Task가 작업중 탭으로 복귀 |
| 3 | 일부 SubTask만 완료 | 작업중 탭에 유지 |
| 4 | 시작일/기한 미입력 상태로 완료 체크 | 작업중 탭에 유지 |
| 5 | 완료된 Task의 OKR 진행률 | 기존 계산 방식 그대로 반영 |
| 6 | 탭 전환 시 테이블 렌더링 | 해당 탭의 Task만 표시 |

### 기능 3: 운영 업무
| # | 테스트 케이스 | 예상 결과 |
|---|---------------|-----------|
| 1 | 운영 업무 체크 후 저장 | KR 선택 비활성화, 독립 Task 생성 |
| 2 | 운영 업무 Task 표시 | 별도 그룹으로 하단 렌더링 |
| 3 | 운영 업무 편집 | KR 연결 가능하게 전환 |

---

## 3.7 성능 최적화 포인트

### 렌더링 최적화
```typescript
// 가상 스크롤링 또는 증분 렌더링 고려
// (Task 수가 100개 이상일 경우)

private renderIncrementally(tasks: Task[], batchSize = 20): void {
  let index = 0;

  const renderBatch = () => {
    const batch = tasks.slice(index, index + batchSize);
    batch.forEach(task => this.appendTaskRow(task));
    index += batchSize;

    if (index < tasks.length) {
      requestAnimationFrame(renderBatch);
    }
  };

  renderBatch();
}
```

### 메모이제이션
```typescript
// 완료 판정 결과 캐싱
private completionCache = new Map<string, boolean>();

isTaskCompleted(task: Task): boolean {
  const cacheKey = this.getTaskCacheKey(task);

  if (this.completionCache.has(cacheKey)) {
    return this.completionCache.get(cacheKey)!;
  }

  const result = /* 계산 로직 */;
  this.completionCache.set(cacheKey, result);
  return result;
}

// SubTask 변경 시 캐시 무효화
invalidateTaskCache(taskId: string): void {
  // taskId로 시작하는 모든 캐시 키 삭제
}
```

---

## 3.8 파일 변경 요약

| 파일 | 변경 유형 | 변경 내용 |
|------|-----------|-----------|
| `src/types/index.ts` | 수정 | TaskTabType, Task.krId nullable, isOperational |
| `src/store.ts` | 수정 | 탭 필터링, 완료 판정, KR 재정렬 |
| `src/views/OKRSection.ts` | 수정 | 개선된 D&D, 드롭존 시각화 |
| `src/views/TaskSection.ts` | 수정 | 탭 UI, 필터 렌더링, 운영업무 그룹 |
| `src/views/ModalView.ts` | 수정 | 운영업무 체크박스 |
| `src/styles.css` | 수정 | 탭 스타일, D&D 스타일 |
| `src/app.ts` | 수정 | 탭 이벤트 연결 |

---

## 3.9 예상 개발 일정

| Phase | 작업 | 예상 시간 | 담당 |
|-------|------|-----------|------|
| 1 | 타입 정의 및 Store 기반 | 2시간 | - |
| 2 | KR 이동 기능 | 4시간 | - |
| 3 | 완료 탭 기능 | 6시간 | - |
| 4 | 운영 업무 기능 | 3시간 | - |
| 5 | 통합 테스트 및 버그 수정 | 3시간 | - |
| **총계** | | **18시간** | |

---

## 📌 핵심 주의사항

### ⚠️ Don't Do It (명시적 금지)
1. **Task 내 일부 SubTask만 완료 시 완료 탭 이동 금지**
2. **완료되어도 OKR 진행률 계산 로직 변경 금지**
3. **기존 localStorage 키 변경 금지** (마이그레이션 필요 시 별도 처리)

### ✅ Must Do (필수 구현)
1. 모든 SubTask가 완료 + 시작일/기한 입력 = 완료 탭 이동
2. KR 순서 변경 시 하위 데이터 연결 유지
3. 운영 업무는 KR과 독립적으로 관리

---

*문서 버전: v1.1*  
*최종 업데이트: 2026-04-13*
