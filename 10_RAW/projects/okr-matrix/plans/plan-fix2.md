# plan-fix.md 수정 계획

## Context

`okr-matrix-app`에 세 가지 수정이 필요합니다:
1. **[버그]** SUB-TASK EM 값 변경 시 부모 TASK 계층구조 붕괴
2. **[신기능]** KEY RESULTS 및 TASK/SUB-TASK 목록 Drag & Drop 정렬
3. **[신기능]** OKR 섹션 아코디언(접기/펼치기) UI

---

## 이슈 1: SUB-TASK 계층구조 버그 (우선 수정)

### 원인 분석

`TaskSection.ts:82-87`의 **전역 정렬** 로직이 문제:

```typescript
// 현재 버그 코드
rows.sort((a, b) =>
  a.st.emQuadrant !== b.st.emQuadrant
    ? a.st.emQuadrant - b.st.emQuadrant
    : a.st.order - b.st.order,
);
```

이 정렬은 모든 TASK의 SUB-TASK를 뒤섞으므로,
TASK A(EM=1)→TASK B(EM=2)→TASK A(EM=3) 순으로 배열됩니다.
`renderedTasks` Set이 최초 등장 시에만 헤더를 삽입하므로
TASK A의 EM=3 행이 TASK B 헤더 아래에 표시됩니다.

### 수정 방법

**파일:** `src/views/TaskSection.ts:82-87`

```typescript
// 수정 후 — TASK 단위 그룹화 유지 + 그룹 내 EM → order 정렬
rows.sort((a, b) => {
  if (a.task.id !== b.task.id) {
    // TASK 간 순서는 task.order 필드 기준 (없으면 title 알파벳순)
    return (a.task.order ?? 0) - (b.task.order ?? 0) || a.task.title.localeCompare(b.task.title);
  }
  if (a.st.emQuadrant !== b.st.emQuadrant) return a.st.emQuadrant - b.st.emQuadrant;
  return a.st.order - b.st.order;
});
```

> **주의:** `TaskData` 타입에 `order` 필드가 없으면 `title` 알파벳순으로 대체.
> `src/types/index.ts`에서 TaskData 확인 후 필드 유무에 따라 분기.

---

## 이슈 2: Drag & Drop 기능 추가

### 구현 범위

| 대상 | 파일 |
|------|------|
| KEY RESULTS 행 순서 변경 | `src/views/OKRSection.ts` |
| TASK 간 D&D (같은 KR 내) | `src/views/TaskSection.ts` |
| SUB-TASK 간 D&D (같은 TASK 내) | `src/views/TaskSection.ts` |
| 정렬 상태 저장 | `src/models/store.ts` (이미 구현됨) |

### 동작 규칙
- OKR 섹션 ↔ TASK 섹션 간 이동 **불가**
- TASK 행은 **같은 KR** 내에서만 이동 가능
- SUB-TASK 행은 **같은 TASK** 내에서만 이동 가능
- 드래그 핸들(⠿)을 잡아야만 드래그 시작

### 구현 단계

#### A. SUB-TASK D&D (`TaskSection.ts`)

1. **핸들 셀 추가** — 각 SUB-TASK 행 맨 왼쪽에 `⠿` 아이콘 `<td>` 추가
   - `cols` 배열(Line 104)에 `''` 컬럼 맨 앞에 추가
   - colspan 11 → 12로 변경

2. **드래그 이벤트 연결** — 각 `<tr>` 에 아래 이벤트 부착:
   ```
   dragstart, dragend, dragover, dragenter, dragleave, drop
   ```
   - `draggable="true"` 속성은 핸들 아이콘에만 설정 (handle 패턴)
   - `dragstart` 시 `dataTransfer.setData('stId', st.id)` 저장
   - `dragover` 시 드롭 인디케이터 표시 (행 위/아래 파란 선)
   - `drop` 시 같은 `taskId` 검증 후 `this.events.onReorder(taskId, newOrder)` 호출

3. **스타일 추가** (`css/task-section.css`)
   ```css
   .drag-handle { cursor: grab; color: #aaa; user-select: none; }
   tr.dragging { opacity: 0.4; }
   tr.drop-above { border-top: 2px solid #3b82f6; }
   tr.drop-below { border-bottom: 2px solid #3b82f6; }
   ```

#### B. KR D&D (`OKRSection.ts`)

1. KR 테이블 각 행에 `⠿` 핸들 셀 추가 (맨 왼쪽)
2. 동일한 drag 이벤트 패턴 적용
3. `store.reorderKRs(orderedIds)` 메서드 추가 필요 (`store.ts`)
4. `OKRSectionEvents`에 `onReorderKRs` 이벤트 추가

#### C. Store 확장 (`store.ts`)

```typescript
// KR 정렬 저장 (신규 추가)
reorderKRs(orderedIds: string[]): void {
  // KeyResultData에 order 필드 추가 필요 (types/index.ts)
  const newKRs = { ...this.state.keyResults };
  orderedIds.forEach((id, i) => {
    if (newKRs[id]) newKRs[id] = { ...newKRs[id], order: i };
  });
  this.setState({ keyResults: newKRs });
}
```

> `reorderSubTasks`는 `store.ts:209-220`에 이미 구현됨 — 재사용

---

## 이슈 3: OKR 섹션 아코디언 UI

### 구현 대상

**파일:** `src/views/OKRSection.ts`, `css/okr-section.css`

### 구현 방법

#### OKRSection.ts 변경

1. **상태 추가** (클래스 멤버):
   ```typescript
   private isKRCollapsed: boolean = false;
   ```

2. **헤더 토글 버튼 추가** (`render` 메서드, Line 31~41 헤더 블록):
   - `titleRow` 맨 오른쪽에 버튼 추가
   - 버튼 텍스트: 펼쳐짐 → `▽`, 접힘 → `△`
   - 색상: `#FF6600` (주황)
   - 클릭 시 `this.isKRCollapsed = !this.isKRCollapsed; this.render(state);`

3. **KR 테이블 조건부 렌더링** (현재 Line 62~139):
   ```typescript
   if (!this.isKRCollapsed) {
     // KR 테이블 렌더링 (기존 코드 유지)
   }
   ```

#### okr-section.css 변경

```css
/* 토글 버튼 */
.okr-collapse-btn {
  background: none;
  border: none;
  color: #FF6600;
  font-size: 1rem;
  cursor: pointer;
  margin-left: auto;
  padding: 4px 8px;
}
.okr-collapse-btn:hover { opacity: 0.7; }
```

> sticky 고정(`position: sticky`)은 **그대로 유지** — 헤더 행만 고정, KR 목록만 토글

---

## 수정 파일 목록

| 파일 | 이슈 | 변경 내용 |
|------|------|---------|
| `src/views/TaskSection.ts` | 1, 2 | 정렬 로직 수정, D&D 이벤트/핸들 추가 |
| `src/views/OKRSection.ts` | 2, 3 | KR D&D 핸들/이벤트, 아코디언 토글 |
| `src/models/store.ts` | 2 | `reorderKRs()` 메서드 추가 |
| `src/types/index.ts` | 2 | `KeyResultData`에 `order` 필드 추가 |
| `css/task-section.css` | 2 | 드래그 스타일 추가 |
| `css/okr-section.css` | 3 | 토글 버튼 스타일 추가 |

---

## 실행 순서 (우선순위)

1. **이슈 1 먼저** — 버그 수정이므로 즉시 반영 (단 1줄 로직 변경)
2. **이슈 3** — UI 변경이 작고 독립적
3. **이슈 2** — 가장 큰 신기능, SUB-TASK → KR 순으로 구현

## 검증 방법

1. **이슈 1:** SUB-TASK의 EM을 1→3으로 변경 후 같은 TASK 아래에 표시되는지 확인
2. **이슈 2:** D&D로 SUB-TASK 순서 변경 후 새로고침해도 순서 유지되는지 확인
3. **이슈 3:** OKR 섹션 토글 버튼 클릭 시 KR 목록 접힘/펼침 동작 확인, sticky 헤더 유지 확인
