# 구현 계획: Meeting Dashboard × OKR Matrix 통합 (P1~P5)

> **계획 기반**: research-v2.2.md  
> **범위**: P1~P5 (프론트엔드 단계)  
> **대상 파일**: `meeting_dashboard.html`  
> **예상 라인**: 450~550줄  
> **위험도**: 중간  

---

## 1. 통합 전략

### 아키텍처 결정
- **iframe 분리형**: OKR 앱과 Meeting Dashboard 완전 독립
  - 기술 스택 충돌 없음 (TS vs Vanilla JS)
  - localStorage 독립 유지
  - CSS 스코프 분리
  
### 데이터 흐름
```
localStorage (front) ─→ P6~P9: Supabase 마이그레이션 (추후)
├─ hr_todos
├─ hr_current_user (신규)
├─ hr_team_members (신규)
├─ hr_comments (신규)
└─ hr_task_assignments (신규)
```

---

## 2. 단계별 구현 계획

### Step 1-4: P1 — OKR 탭 통합
| Step | 작업 | 파일 | 라인 | 의존성 |
|------|------|------|------|--------|
| 1 | okr_matrix.html 복사 배치 | (외부 작업) | — | 빌드 완료 후 |
| 2 | 탭 버튼 추가 (#btn-okr) | HTML | 5 | Step 1 완료 |
| 3 | 탭 콘텐츠 추가 (#tab-okr iframe) | HTML | 10 | Step 2 완료 |
| 4 | switchTab() 함수 'okr' 케이스 추가 | JS | 8 | Step 3 완료 |

**핵심 구현:**
```html
<!-- Step 2: <button> 추가 위치 = #btn-analysis 바로 다음 (라인 ~420) -->
<button class="tab-btn" id="btn-okr" onclick="switchTab('okr')">
  📊 OKR Matrix
</button>

<!-- Step 3: <div> 추가 위치 = #tab-analysis 바로 다음 (라인 ~740) -->
<div id="tab-okr" class="tab-content">
  <iframe
    id="okr-frame"
    src="about:blank"
    style="width:100%; height:calc(100vh - 120px); border:none; display:block;"
    loading="lazy"
  ></iframe>
</div>

<!-- Step 4: switchTab() 함수 내부 (라인 ~1683) -->
case 'okr':
  const frame = document.getElementById('okr-frame');
  if (!frame.src || frame.src === 'about:blank') {
    frame.src = 'okr_matrix.html';
  }
  break;
```

**테스트**: 탭 클릭 → iframe 로드 확인

---

### Step 5-8: P2 — 퍼스펙티브 스위처

#### Step 5: localStorage 초기값 설정
```javascript
// 앱 초기 로드 시 실행
function initTeamContext() {
  if (!localStorage.getItem('hr_team_members')) {
    // 초기 설정 모달 표시 (Step 6)
    showTeamSetupModal();
  }
  
  if (!localStorage.getItem('hr_current_user')) {
    const members = JSON.parse(localStorage.getItem('hr_team_members') || '[]');
    if (members.length > 0) {
      localStorage.setItem('hr_current_user', members[0]); // 첫 팀장 기본값
    }
  }
}
```

#### Step 6-7: 초기 설정 모달 & 제어 (CSS + HTML + JS)

**CSS (50줄)**: 모달 스타일, 입력 폼, 버튼
**HTML (25줄)**: 모달 마크업
  ```html
  <div id="team-setup-modal" class="modal">
    <div class="modal-content">
      <h2>👥 팀 구성원 설정</h2>
      <label>팀장: <input type="text" id="team-lead-input" /></label>
      <div id="team-members-list"></div>
      <button onclick="addTeamMember()">+ 팀원 추가</button>
      <button onclick="saveTeamSetup()">시작하기</button>
    </div>
  </div>
  ```

**JS (35줄)**:
  ```javascript
  function showTeamSetupModal() { /* 모달 표시 */ }
  function addTeamMember() { /* 팀원 입력 필드 추가 */ }
  function saveTeamSetup() {
    const lead = document.getElementById('team-lead-input').value;
    const members = [lead, ...getAdditionalMembers()];
    localStorage.setItem('hr_team_members', JSON.stringify(members));
    localStorage.setItem('hr_current_user', lead);
    document.getElementById('team-setup-modal').style.display = 'none';
    renderTeamSwitcher();
  }
  ```

#### Step 8: 헤더 우측 사용자 선택 드롭다운

**HTML (15줄)**: 헤더 우측에 추가
  ```html
  <div id="user-switcher" class="user-switcher">
    <span>현재: </span>
    <select id="current-user-select" onchange="switchUser(this.value)">
      <!-- options 동적 생성 -->
    </select>
  </div>
  ```

**CSS (20줄)**: 스타일 (우측 정렬, 좌상향 드롭다운)

**JS (20줄)**:
  ```javascript
  function renderTeamSwitcher() {
    const members = JSON.parse(localStorage.getItem('hr_team_members') || '[]');
    const current = localStorage.getItem('hr_current_user');
    const select = document.getElementById('current-user-select');
    select.innerHTML = members
      .map(m => `<option value="${m}" ${m === current ? 'selected' : ''}>${m}</option>`)
      .join('');
  }
  
  function switchUser(name) {
    localStorage.setItem('hr_current_user', name);
    // TODO/분석 탭 UI 새로고침 (Step 10)
    renderTodos();
  }
  ```

---

### Step 9-11: P3 — 팀원별 Task 뷰 + 필터

#### Step 9: TODO 탭 필터 버튼 추가
**위치**: `.todo-controls` 내부 (라인 ~428)  
**HTML (15줄)**:
```html
<div class="filter-group" id="team-filter-group">
  <button class="filter-btn active" onclick="filterByAssignee('all')">전체</button>
  <!-- 팀원별 버튼 동적 생성 -->
</div>
```

#### Step 10: renderTodos() 필터 로직 추가
**위치**: 기존 `renderTodos()` 함수 수정 (라인 ~1000)  
**JS (40줄)**:
```javascript
let currentAssigneeFilter = 'all';

function filterByAssignee(assignee) {
  currentAssigneeFilter = assignee;
  document.querySelectorAll('#team-filter-group .filter-btn').forEach(b => 
    b.classList.remove('active')
  );
  event.currentTarget.classList.add('active');
  renderTodos(); // 재렌더
}

// renderTodos() 내부에 필터 로직 추가:
// if (currentAssigneeFilter !== 'all') {
//   todos = todos.filter(t => {
//     const assignees = (t.assignments || []).map(a => a.assignee);
//     return assignees.includes(currentAssigneeFilter) || t.owner === currentAssigneeFilter;
//   });
// }
```

#### Step 11: Task 카드에 담당자 표시
**위치**: Task 카드 렌더링 (라인 ~1200)  
**HTML (5줄)** — Task 카드 내부:
```html
<div class="task-assignees">
  담당: 
  <span class="assignee-badges">
    <!-- assignments 배열 렌더 -->
  </span>
</div>
```

**CSS (15줄)**: `.task-assignees`, `.assignee-badges` 스타일  
**JS (5줄)**: Task 렌더링 시 할당자 표시

---

### Step 12-14: P4 — 팀장 배분 UI

#### Step 12: Task 카드에 [배분] 버튼 추가
**위치**: Task 카드 우측 상단  
**HTML (3줄)**:
```html
<button class="btn-distribute" onclick="openDistributeModal(taskId)">
  배분
</button>
```

#### Step 13: 배분 모달 UI
**CSS (50줄)**: 모달, 체크박스 목록  
**HTML (30줄)**:
```html
<div id="distribute-modal" class="modal">
  <div class="modal-content">
    <h3>담당자 선택</h3>
    <div id="assignee-checkboxes">
      <!-- 팀원 체크박스 동적 생성 -->
    </div>
    <label>
      <input type="radio" name="distribute-unit" value="task" checked /> Task 개별
      <input type="radio" name="distribute-unit" value="group" /> 묶음 (P5 이후)
    </label>
    <button onclick="saveDistribution()">배분 저장</button>
  </div>
</div>
```

#### Step 14: 배분 저장 로직
**JS (60줄)**:
```javascript
function openDistributeModal(taskId) {
  currentDistributeTaskId = taskId;
  // 모달 팝업
  const members = JSON.parse(localStorage.getItem('hr_team_members') || '[]');
  const checkboxes = members
    .map(m => `<label><input type="checkbox" value="${m}" /> ${m}</label>`)
    .join('');
  document.getElementById('assignee-checkboxes').innerHTML = checkboxes;
}

function saveDistribution() {
  const selected = Array.from(
    document.querySelectorAll('#assignee-checkboxes input:checked')
  ).map(el => el.value);
  
  const task = todos.find(t => t.id === currentDistributeTaskId);
  if (task) {
    task.assignments = selected.map(name => ({
      assignee: name,
      assignedAt: new Date().toISOString(),
      assignedBy: localStorage.getItem('hr_current_user')
    }));
    autoSave(); // 기존 저장 함수
  }
  document.getElementById('distribute-modal').style.display = 'none';
}
```

**새 localStorage 키**: `hr_task_assignments`는 `hr_todos` 내부 `assignments[]` 배열로 통합  
→ hr_todos 구조 확장:
```javascript
{
  id: "...",
  subject: "...",
  assignments: [  // 신규
    { assignee: "팀원A", assignedAt: "...", assignedBy: "팀장" }
  ]
}
```

---

### Step 15-18: P5 — Task 코멘트 (슬라이드-오버)

#### Step 15: localStorage 'hr_comments' 키 초기화
```javascript
// hr_comments 구조 (Supabase 동일):
[
  {
    id: "uuid",
    taskId: "task-uuid",
    author: "팀원명",
    content: "코멘트 텍스트",
    createdAt: "2026-04-21T10:30:00Z"
  }
]

function initCommentsStorage() {
  if (!localStorage.getItem('hr_comments')) {
    localStorage.setItem('hr_comments', JSON.stringify([]));
  }
}
```

#### Step 16: Task 카드에 💬 아이콘 + 뱃지 추가
**HTML (3줄)** — Task 카드 내부:
```html
<div class="comment-badge" onclick="openCommentPanel(taskId)">
  💬 <span class="comment-count">3</span>
</div>
```

**JS (10줄)**: 주어진 taskId의 댓글 수 계산 & 표시

#### Step 17: 슬라이드-오버 패널 UI
**CSS (50줄)**:
```css
.comment-panel {
  position: fixed; right: 0; top: 0;
  width: 350px; height: 100vh;
  background: white; box-shadow: -2px 0 8px rgba(0,0,0,0.15);
  display: none; z-index: 1000;
  flex-direction: column;
  animation: slideIn 0.3s ease-out;
}
.comment-panel.open { display: flex; }
.comment-list { flex: 1; overflow-y: auto; padding: 16px; }
.comment-item { margin-bottom: 16px; border-bottom: 1px solid #eee; }
```

**HTML (30줄)**:
```html
<div id="comment-panel" class="comment-panel">
  <div class="panel-header">
    <h3>💬 코멘트</h3>
    <button class="close-btn" onclick="closeCommentPanel()">×</button>
  </div>
  <div class="comment-list" id="comment-list">
    <!-- 동적 렌더 -->
  </div>
  <div class="comment-input">
    <select id="comment-author">
      <!-- 현재 사용자 고정 (수정 불가) -->
    </select>
    <textarea id="comment-text" placeholder="코멘트를 입력하세요..."></textarea>
    <button onclick="postComment()">전송</button>
  </div>
</div>
```

#### Step 18: 코멘트 저장/로드 JavaScript
**JS (70줄)**:
```javascript
let currentCommentTaskId = null;

function openCommentPanel(taskId) {
  currentCommentTaskId = taskId;
  const panel = document.getElementById('comment-panel');
  panel.classList.add('open');
  
  // 작성자 고정 (현재 사용자)
  document.getElementById('comment-author').innerHTML = 
    `<option>${localStorage.getItem('hr_current_user')}</option>`;
  
  // 기존 댓글 로드
  renderComments();
}

function renderComments() {
  const comments = JSON.parse(localStorage.getItem('hr_comments') || '[]');
  const taskComments = comments.filter(c => c.taskId === currentCommentTaskId);
  
  const html = taskComments
    .map(c => `
      <div class="comment-item">
        <strong>${c.author}</strong> 
        <span class="comment-time">${new Date(c.createdAt).toLocaleString('ko-KR')}</span>
        <p>${escapeHtml(c.content)}</p>
      </div>
    `)
    .join('');
  
  document.getElementById('comment-list').innerHTML = html;
}

function postComment() {
  const text = document.getElementById('comment-text').value.trim();
  if (!text) return;
  
  const comments = JSON.parse(localStorage.getItem('hr_comments') || '[]');
  comments.push({
    id: generateUUID(),
    taskId: currentCommentTaskId,
    author: localStorage.getItem('hr_current_user'),
    content: text,
    createdAt: new Date().toISOString()
  });
  
  localStorage.setItem('hr_comments', JSON.stringify(comments));
  document.getElementById('comment-text').value = '';
  renderComments();
}

function closeCommentPanel() {
  document.getElementById('comment-panel').classList.remove('open');
  currentCommentTaskId = null;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16 | 0), v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
```

---

## 3. 의존성 그래프 & 병렬 실행 그룹

### 의존성 (Dependency Chain)
```
Step 1
  ↓
Step 2 → Step 3 → Step 4 (P1 완료)
          ↓
        Step 5 → Step 6 → Step 7 → Step 8 (P2 완료)
                ↓
          Step 9 → Step 10 → Step 11 (P3)
          Step 12 → Step 13 → Step 14 (P4)  ← P3/P4는 병렬 가능 (P2 완료 후)
                ↓
          Step 15 → Step 16 → Step 17 → Step 18 (P5)
```

### 병렬 실행 그룹
| 그룹 | 단계 | 조건 |
|------|------|------|
| **Group 1** | Step 1-4 (P1) | 독립적 |
| **Group 2** | Step 5-8 (P2) | P1 완료 후 |
| **Group 3** | Step 9-11, Step 12-14 (P3+P4) | P2 완료 후, 병렬 가능 (파일 영역 분리) |
| **Group 4** | Step 15-18 (P5) | P3, P4 완료 후 |

---

## 4. 예상 라인 수 & 변경 범위

| 단계 | CSS | HTML | JS | 소계 |
|------|-----|------|-----|------|
| P1 (Step 1-4) | 0 | 15 | 8 | **23** |
| P2 (Step 5-8) | 70 | 40 | 55 | **165** |
| P3 (Step 9-11) | 20 | 20 | 50 | **90** |
| P4 (Step 12-14) | 50 | 35 | 60 | **145** |
| P5 (Step 15-18) | 50 | 35 | 70 | **155** |
| **합계** | **190** | **145** | **243** | **578** |

**예상 최종 라인**: ~1900 + 578 = **2478줄** (현재 대비 +30%)

---

## 5. 위험 평가 및 완화

| 위험 | 가능성 | 영향 | 완화 방안 |
|-----|--------|------|---------|
| iframe 로드 실패 (file://) | 높음 | 높음 | okr_matrix.html 동일 폴더 배치 검증 필수 |
| 팀 구성원 미설정 (초기 실행) | 중간 | 중간 | 초기 설정 모달 필수 & 유효성 체크 |
| Task 배분과 기존 owner 충돌 | 중간 | 중간 | assignments[] 배열 + 기존 owner 필드 보존 |
| 댓글 XSS 취약점 | 낮음 | 높음 | escapeHtml() 필수, innerHTML 대신 textContent |
| localStorage 용량 초과 (댓글 많음) | 낮음 | 중간 | P6 Supabase 이전 시 자동 해소 |

---

## 6. 로드맵 요약

```
[Phase 2 완료] ──→ [Phase 3 계획 검토] ──→ [Phase 4 실행] 
                                            ├─ Split 1: okr_matrix.html 배치
                                            ├─ Split 2: P1 구현
                                            ├─ Split 3: P2 구현
                                            ├─ Split 4: P3/P4 구현 (병렬)
                                            └─ Split 5: P5 구현
                                            ↓
                                    [Phase 5 검증]
                                    ├─ 정적 검증 (HTML/CSS)
                                    ├─ 기능 검증 (5개 탭)
                                    ├─ 회귀 검증 (기존 기능)
                                    └─ 보안 검증 (XSS/입력)
                                            ↓
                                    [Phase 6 배포]
                                    └─ 파일 저장 (OneDrive 동기화)
```

---

## 참고: 현재 코드 위치

| 항목 | 라인 범위 |
|------|---------|
| 탭 버튼 영역 (Step 2 삽입점) | 413-425 |
| 탭 콘텐츠 영역 (Step 3 삽입점) | 562-740 |
| switchTab() 함수 (Step 4 수정점) | 1683-1688 |
| TODO 컨트롤 (Step 9 삽입점) | 427-432 |
| renderTodos() 함수 (Step 10 수정점) | 1000-1300 (예상) |
| app-header (Step 8 삽입점) | 28-36 |
