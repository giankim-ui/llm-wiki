# Plan — Fix: TO-DO 배분 후 OKR Matrix TASK 섹션 미표시 버그

> **선행 plan**: v2.2 통합 (`Smartmeeting - 문서/archive/260422-interg-m-o/plan/`) 은 완료됨. 이 plan 은 v2.2 후 발견된 회로 단절 버그를 수정.

---

## 1. Context (왜)

### 시뮬레이션 결과 (사용자 보고)
1. TO-DO 탭 → '인사기록카드 개발 착수' 배분 버튼 클릭
2. 안수민 체크박스 선택 → KR 드롭다운 선택 → 배분 저장
3. OKR Matrix 탭 이동 → TASK 섹션 확인
4. **결과: 해당 task 가 TASK 섹션에 보이지 않음**

### 의도 일치 여부
- **사용자 의도**: TO-DO 과제가 OKR 의 KR 과 매칭되어 OKR Matrix TASK 섹션에 자동 등장
- **v2.2 구현 의도**: 동일 (Plan v2.2 §5, §6 — `hr_shared_tasks` 기록 + OKR `kr.tasks` 업데이트 + postMessage)
- **결론**: 의도는 같았으나 양쪽 구현 모두 **task 객체 자체 생성 누락** 으로 회로 단절

---

## 2. 근본 원인 (코드 추적 결과)

| # | 위치 | 현 코드 동작 | 문제 |
|---|------|------------|------|
| R1 | `meeting_dashboard.html` saveDistribution lines 2561~2578 | `okr-matrix-v2:{user}.state.keyResults[krId].tasks[]` 에 taskId 만 push | OKR state 의 `state.tasks[taskId]` 객체는 생성 안 함 — TaskSection 이 참조할 본체 없음 |
| R2 | `OKR/okr-matrix-app/src/models/store.ts` syncSharedTask lines 50~62 | `if (!task) return;` — 기존 task 없으면 즉시 종료. title 외 미갱신 | 신규 task 절대 생성 못 함. krId 도 설정 안 함 |
| R3 | `OKR/okr-matrix-app/src/views/task-section/TaskSection.ts` line 245 | `task.krId !== null ? state.keyResults[task.krId] : undefined` 로 매칭 | task 자체가 없거나 krId 미설정이면 화면에서 누락 |

### 데이터 흐름 단절 지점
```
saveDistribution → hr_shared_tasks ✓
                → okr-matrix-v2:{user}.keyResults[kr].tasks[] ID push ✓
                → state.tasks[taskId] 객체 ✗ (NEVER CREATED)
                → postMessage OKR_TASK_UPDATED ✓
                                    ↓
            syncSharedTask → state.tasks[taskId] 조회 → undefined → return ✗
```

---

## 3. 수정 계획

### 3.1 변경 파일 (총 2개 + 빌드 1개)

| # | 파일 | 변경 |
|---|------|------|
| F1 | `Smartmeeting - 문서/10_HR_IN_Meeting_DB/meeting_dashboard.html` lines 2561~2578 | task 객체 생성·갱신 로직 추가 |
| F2 | `OKR/okr-matrix-app/src/models/store.ts` lines 50~62 | syncSharedTask 완전 재작성 — task 신규 생성 + KR 연결 + 화면 즉시 반영 |
| F3 | (빌드) `npm run build` + `python build_bundle_html.py` | bundle.html → okr_matrix.html 자동 동기화 |

### 3.2 F1 — saveDistribution 강화

**현재 (lines 2561~2578)**: KR.tasks 배열에 ID 만 push
**변경**: 각 팀원 `okr-matrix-v2:{user}` 안에 완전한 task 객체 작성

```js
selected.forEach(s => {
  if (!s.kr_id) return;
  try {
    const key = `okr-matrix-v2:${s.assignee}`;
    const raw = localStorage.getItem(key);
    if (!raw) return;
    const data = JSON.parse(raw);
    const stateObj = data?.state;
    if (!stateObj) return;
    const kr = stateObj.keyResults?.[s.kr_id];
    if (!kr) return;

    // (a) task 객체 생성/갱신 — store.ts TaskData schema 준수 (camelCase)
    if (!stateObj.tasks) stateObj.tasks = {};
    const existing = stateObj.tasks[currentDistributeTaskId];
    if (!existing) {
      stateObj.tasks[currentDistributeTaskId] = {
        id: currentDistributeTaskId,
        krId: s.kr_id,
        krNo: kr.krNo || 0,
        title: task.subject,
        memo: task.detail || '',
        subTasks: [],
        isOperational: false,
        createdAt: now,
        updatedAt: now
      };
    } else {
      // 재배분: 다른 KR 로 이동하는 경우 기존 KR.tasks 에서 제거
      if (existing.krId && existing.krId !== s.kr_id) {
        const oldKR = stateObj.keyResults[existing.krId];
        if (oldKR && Array.isArray(oldKR.tasks)) {
          oldKR.tasks = oldKR.tasks.filter(id => id !== currentDistributeTaskId);
        }
      }
      existing.krId = s.kr_id;
      existing.krNo = kr.krNo || 0;
      existing.title = task.subject;
      existing.memo = task.detail || '';
      existing.updatedAt = now;
    }

    // (b) KR.tasks 에 push (중복 방지)
    if (!Array.isArray(kr.tasks)) kr.tasks = [];
    if (!kr.tasks.includes(currentDistributeTaskId)) {
      kr.tasks.push(currentDistributeTaskId);
    }

    // (c) okr.taskDisplayOrder 에 push (있는 경우만)
    if (stateObj.okr && Array.isArray(stateObj.okr.taskDisplayOrder)) {
      if (!stateObj.okr.taskDisplayOrder.includes(currentDistributeTaskId)) {
        stateObj.okr.taskDisplayOrder.push(currentDistributeTaskId);
      }
    }

    data.savedAt = now;
    localStorage.setItem(key, JSON.stringify(data));
  } catch(e) { console.warn('OKR state update failed for', s.assignee, e); }
});
```

### 3.3 F2 — syncSharedTask 완전 재작성

**목표**: postMessage 수신 시 in-memory state 도 동일하게 갱신 → 사용자가 OKR 탭으로 전환하지 않아도 즉시 반영

```ts
syncSharedTask(taskId: string): void {
  const raw = localStorage.getItem('hr_shared_tasks');
  if (!raw) return;
  try {
    const shared = JSON.parse(raw);
    const entry = shared[taskId];
    if (!entry) return;

    // 현재 user 가 assignees 안에 있는지 + 그 user 의 kr_id 추출
    const currentUser = getCurrentUser(); // utils/storage 에서 import
    const myAssign = entry.assignees?.find((a: any) => a.assignee === currentUser);
    if (!myAssign?.kr_id) return; // 나에게 배분 안 됨

    const krId = myAssign.kr_id;
    const kr = this.state.keyResults[krId];
    if (!kr) return; // 내 OKR 에 해당 KR 없음 (예외 케이스)

    const now = nowISO();
    const existing = this.state.tasks[taskId];

    const task: TaskData = existing
      ? { ...existing, krId, krNo: kr.krNo, title: entry.title || existing.title,
          memo: entry.memo ?? existing.memo, updatedAt: now }
      : { id: taskId, krId, krNo: kr.krNo, title: entry.title || '',
          memo: entry.memo || '', subTasks: [], isOperational: !!entry.is_operational,
          createdAt: entry.created_at || now, updatedAt: now };

    // KR 이동 처리: 기존 KR.tasks 에서 제거
    const newKRs = { ...this.state.keyResults };
    if (existing && existing.krId !== null && existing.krId !== krId) {
      const oldKR = newKRs[existing.krId];
      if (oldKR) newKRs[existing.krId] = { ...oldKR, tasks: oldKR.tasks.filter(id => id !== taskId) };
    }
    // 새 KR.tasks 에 push
    if (!kr.tasks.includes(taskId)) {
      newKRs[krId] = { ...kr, tasks: [...kr.tasks, taskId] };
    }

    // taskDisplayOrder 에 push
    let newOKR = this.state.okr;
    if (newOKR) {
      const order = newOKR.taskDisplayOrder ?? [];
      if (!order.includes(taskId)) {
        newOKR = { ...newOKR, taskDisplayOrder: [...order, taskId] };
      }
    }

    this.commit({
      ...this.state,
      tasks: { ...this.state.tasks, [taskId]: task },
      keyResults: newKRs,
      okr: newOKR
    });
  } catch { /* ignore */ }
}
```

**필요 import 추가**: `import { loadState, debouncedSave, saveState, getCurrentUser } from '../utils/storage.js';`
(getCurrentUser 가 export 안 되어 있으면 storage.ts 에 export 추가)

---

## 4. 설계 결정

| # | 결정 | 이유 |
|---|------|------|
| D1 | task 객체 schema 는 camelCase (krId, createdAt 등) | OKR 내부 schema 는 v2.2 에서도 camelCase 유지. snake_case 는 hr_shared_tasks 경계에서만 |
| D2 | saveDistribution 이 OKR schema 를 알게 됨 | 이미 keyResults[krId].tasks 를 건드리고 있어 사실상 알고 있음. 누락 필드만 추가 |
| D3 | subTasks: [] (빈 배열) | isTaskCompleted=false 로 계산 → "활성" 탭에 표시 (사용자 의도 부합) |
| D4 | syncSharedTask 가 in-memory 갱신 책임 | 다른 팀원의 OKR iframe 은 안 떠있음 → localStorage 사전 작성 + 본인 화면 즉시 반영 둘 다 필요 |
| D5 | 재배분(KR 이동) 처리 | 기존 KR.tasks 에서 제거 후 새 KR 에 push — store.ts updateTask 패턴 모방 |

---

## 5. 검증 체크리스트

| # | 항목 | 합격 기준 |
|---|-----|---------|
| V_FIX_1 | 본인 배분 즉시 반영 | TO-DO 배분 → OKR 탭 전환 → TASK 섹션에 해당 task 표시 (페이지 새로고침 불필요) |
| V_FIX_2 | 타 팀원 배분 + 사용자 전환 | 안수민에게 배분 → 사용자 switcher 로 안수민 선택 → OKR 탭에서 표시 |
| V_FIX_3 | 새로고침 후에도 유지 | 배분 후 페이지 reload → OKR 탭 → 여전히 표시 (localStorage 영속성 확인) |
| V_FIX_4 | 재배분 시 KR 이동 | 같은 task 를 다른 KR 로 재배분 → 기존 KR 에서 제거, 새 KR 에 등장 (양쪽 표시 금지) |
| V_FIX_5 | OKR 직접 추가 task 회귀 | OKR 화면에서 직접 추가한 task 는 변경 없음 |
| V_FIX_6 | TS 빌드·sync | `npm run build` → tsc 무오류, esbuild 성공, `python build_bundle_html.py` → okr_matrix.html 갱신 시각 방금 |

---

## 6. 실행 순서

1. F2 (store.ts) 수정 — getCurrentUser import 추가 + syncSharedTask 재작성
2. `npm run build` (OKR 폴더) — TypeScript 컴파일·번들 확인
3. F1 (meeting_dashboard.html saveDistribution) 수정
4. `python build_bundle_html.py` 실행 — okr_matrix.html 자동 동기화
5. 백업: `RP-FIX-{시각}` 으로 meeting_dashboard.html 과 okr_matrix.html 보관
6. V_FIX_1 ~ V_FIX_6 브라우저 검증 (사용자 확인 필요 항목)
7. result-okr-task-sync-fix.md 작성 (archive/260422-interg-m-o/)

---

## 7. 위험·주의

- **getCurrentUser 가 export 되어 있는지 확인 필요** — 안 되어 있으면 storage.ts 에 export 추가
- **TaskData 타입의 startDate/dueDate 는 optional** — 신규 생성 시 미설정 OK (기존 코드도 동일)
- **OKR 빈 상태(KR 0개)** 인 팀원에게 배분 시 — kr 조회 실패 → 조용히 skip (현재 동작과 동일, 안전)
- **race condition**: 배분 직후 사용자가 OKR 탭으로 전환하면 reload(user) 가 호출됨 — 그 시점에 localStorage 는 이미 업데이트되어 있으므로 정상 표시. postMessage 와 reload 둘 다 같은 결과 도달.
