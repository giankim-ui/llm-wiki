# 이슈 2: Drag & Drop 기능 구현

> 🎯 **목표**: KR, Task, SubTask 행 순서를 드래그로 변경
> ⏱️ **예상 시간**: 30분
> 📁 **수정 파일**: 5개 (아래 참조)

---

## 📋 동작 규칙

| 대상 | 이동 범위 | 드래그 핸들 |
|------|----------|------------|
| KR 행 | 같은 OKR 내 | ⠿ 아이콘 |
| Task 행 | 같은 KR 내 | ⠿ 아이콘 |
| SubTask 행 | 같은 Task 내 | ⠿ 아이콘 |

⚠️ **제약**: OKR ↔ Task 섹션 간 이동 불가

---

## ✅ 수정 순서

### Step 1: 타입 정의 수정

**파일: `src/types/index.ts`**

```typescript
// TaskData 인터페이스에 order 필드 확인/추가
export interface TaskData {
  id: string;
  title: string;
  order: number;  // 🆕 없으면 추가
  // ... 기타 필드
}

// KeyResultData 인터페이스에 order 필드 확인/추가  
export interface KeyResultData {
  id: string;
  title: string;
  order: number;  // 🆕 없으면 추가
  // ... 기타 필드
}

// SubTaskData 인터페이스에 order 필드 확인/추가
export interface SubTaskData {
  id: string;
  title: string;
  order: number;  // 🆕 없으면 추가
  // ... 기타 필드
}
```

---

### Step 2: Store 메서드 추가

**파일: `src/models/store.ts`**

```typescript
// 클래스 내에 아래 메서드들 추가

/**
 * KR 순서 변경
 */
reorderKRs(okrId: string, fromIndex: number, toIndex: number): void {
  const okr = this.state.okrs.find(o => o.id === okrId);
  if (!okr) return;

  const [moved] = okr.keyResults.splice(fromIndex, 1);
  okr.keyResults.splice(toIndex, 0, moved);

  // order 값 재할당
  okr.keyResults.forEach((kr, idx) => {
    kr.order = idx;
  });

  this.save();
  this.notify();
}

/**
 * Task 순서 변경
 */
reorderTasks(krId: string, fromIndex: number, toIndex: number): void {
  const tasks = this.state.tasks.filter(t => t.krId === krId);
  const allTasks = this.state.tasks;

  // 해당 KR의 task만 재정렬
  const [moved] = tasks.splice(fromIndex, 1);
  tasks.splice(toIndex, 0, moved);

  tasks.forEach((task, idx) => {
    task.order = idx;
  });

  this.save();
  this.notify();
}

/**
 * SubTask 순서 변경
 */
reorderSubTasks(taskId: string, fromIndex: number, toIndex: number): void {
  const task = this.state.tasks.find(t => t.id === taskId);
  if (!task || !task.subTasks) return;

  const [moved] = task.subTasks.splice(fromIndex, 1);
  task.subTasks.splice(toIndex, 0, moved);

  task.subTasks.forEach((st, idx) => {
    st.order = idx;
  });

  this.save();
  this.notify();
}
```

---

### Step 3: TaskSection D&D 구현

**파일: `src/views/TaskSection.ts`**

```typescript
// 클래스 상단에 D&D 상태 변수 추가
private draggedElement: HTMLElement | null = null;
private draggedIndex: number = -1;
private dragContext: { type: string; parentId: string } | null = null;

// 행 렌더링 시 드래그 핸들 추가 (각 <tr> 생성 부분)
private createDragHandle(): HTMLTableCellElement {
  const td = document.createElement('td');
  td.className = 'drag-handle';
  td.textContent = '⠿';
  td.draggable = true;
  return td;
}

// Task 행에 D&D 이벤트 연결
private setupTaskDragEvents(
  row: HTMLTableRowElement, 
  index: number, 
  krId: string
): void {
  const handle = row.querySelector('.drag-handle');
  if (!handle) return;

  handle.addEventListener('dragstart', (e) => {
    this.draggedElement = row;
    this.draggedIndex = index;
    this.dragContext = { type: 'task', parentId: krId };
    row.classList.add('dragging');
    (e as DragEvent).dataTransfer?.setData('text/plain', '');
  });

  handle.addEventListener('dragend', () => {
    row.classList.remove('dragging');
    this.draggedElement = null;
    this.draggedIndex = -1;
    this.dragContext = null;
  });

  row.addEventListener('dragover', (e) => {
    e.preventDefault();
    if (this.dragContext?.type !== 'task') return;
    if (this.dragContext?.parentId !== krId) return;
    row.classList.add('drag-over');
  });

  row.addEventListener('dragleave', () => {
    row.classList.remove('drag-over');
  });

  row.addEventListener('drop', (e) => {
    e.preventDefault();
    row.classList.remove('drag-over');

    if (this.dragContext?.type !== 'task') return;
    if (this.dragContext?.parentId !== krId) return;
    if (this.draggedIndex === index) return;

    // Store 호출하여 순서 변경
    this.store.reorderTasks(krId, this.draggedIndex, index);
  });
}

// SubTask도 동일한 패턴으로 구현 (parentId를 taskId로 변경)
```

---

### Step 4: OKRSection D&D 구현

**파일: `src/views/OKRSection.ts`**

```typescript
// TaskSection과 동일한 패턴
// dragContext.type = 'kr', parentId = okrId 사용
// store.reorderKRs() 호출
```

---

### Step 5: CSS 스타일 추가

**파일: `css/task-section.css`**

```css
/* 드래그 핸들 */
.drag-handle {
  cursor: grab;
  color: #999;
  width: 24px;
  text-align: center;
  user-select: none;
}

.drag-handle:hover {
  color: #FF6600;
}

/* 드래그 중인 행 */
.dragging {
  opacity: 0.5;
  background: #fff3e0 !important;
}

/* 드롭 대상 행 */
.drag-over {
  border-top: 2px solid #FF6600;
}
```

---

## 🧪 테스트 체크리스트

### KR 드래그
- [ ] ⠿ 핸들을 잡아야만 드래그 시작
- [ ] 같은 OKR 내 KR만 이동 가능
- [ ] 다른 OKR의 KR 위에 드롭 불가
- [ ] 순서 변경 후 새로고침해도 유지

### Task 드래그
- [ ] 같은 KR 내 Task만 이동 가능
- [ ] 다른 KR의 Task 위에 드롭 불가

### SubTask 드래그
- [ ] 같은 Task 내 SubTask만 이동 가능

---

## ✅ 완료 확인

모든 이슈 완료! 🎉
전체 기능 통합 테스트 진행.
