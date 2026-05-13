# Plan: OKR Matrix — OBJECTIVE 팀 동기화 + KR 가져오기 기능

## Context

`okr_matrix.html` 의 OBJECTIVE/KR 은 현재 user별로 독립 저장되어 팀 내 일관성이 없다.
두 가지 변경을 적용한다:

1. **OBJECTIVE 팀 동기화**: 같은 팀의 모든 member 는 동일 OBJECTIVE 를 공유.
   - 아무도 입력 안 했으면 제한 없이 저장
   - 한 명이라도 입력했으면 수정 시 confirm 팝업 → 확인 시 전원 동기화, 취소 시 원상복구
2. **KR 가져오기**: 헤더에 "OKR 가져오기" 버튼 추가 → 팀원 선택 → 해당 팀원의 KR을 체크박스로 다중 선택 → 복사 (Task·서브태스크 포함, 새 ID 발급)

---

## 변경 대상 파일

| 파일 | 변경 내용 |
|------|---------|
| `10_HR_IN_Meeting_DB/okr_matrix.html` | CSS + header HTML + Store 메서드 + ModalView + App events + button 바인딩 |

---

## 현재 진행 상태 (이미 수정 완료)

| # | 변경 | 위치 | 상태 |
|---|------|-----|------|
| 1 | 헤더 버튼 CSS (`#btn-import-okr`, `.import-kr-list`, `.import-kr-row`) | line 88-97 | ✅ |
| 2 | 헤더 HTML (`<div class="header-actions">` + 버튼) | line 757-759 | ✅ |
| 3 | Store: `_getTeamMembers`, `listOtherTeamMembers`, `loadUserState`, `hasAnyTeamObjective`, `setObjectiveForAll`, `importKRsFromUser` | line 1375-1458 | ✅ |
| 4 | ModalView switch case `"import-okr"` | line 2111-2113 | ✅ |
| 5 | ModalView `_buildImportOKRForm(state)` | line 2323-2410 | ✅ |
| 6 | App `onSetObjective` 에 팀 동기화 confirm 로직 | line 2514-2521 | ✅ |

---

## 남은 작업

### 잔여 A. ModalView 생성자 events 에 3개 핸들러 추가

`this.modal = new ModalView({...})` 블록 내, `onSetObjective` 블록 직후에 삽입:

```javascript
onListOtherMembers: () => this.store.listOtherTeamMembers(),
onListUserKRs: (user) => {
  const st = this.store.loadUserState(user);
  if (!st.okr) return [];
  return Object.values(st.keyResults)
    .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
    .map((kr) => ({ id: kr.id, krNo: kr.krNo, title: kr.title, progress: kr.progress ?? 0, taskCount: (kr.tasks || []).length }));
},
onImportKRs: (fromUser, krIds) => {
  try {
    const result = this.store.importKRsFromUser(fromUser, krIds);
    if (result.added > 0) this.toast.success(result.added + "개 KR을 가져왔습니다.");
    else this.toast.error("가져올 KR이 없습니다.");
  } catch (err) {
    console.error("importKRs failed", err);
    this.toast.error("KR 가져오기 실패");
  }
},
```

### 잔여 B. 헤더 버튼 클릭 바인딩

App 생성자 `this.setupMessageListener();` 이후에 추가:

```javascript
const importBtn = document.getElementById("btn-import-okr");
if (importBtn) {
  importBtn.addEventListener("click", () => this.openModal({ type: "import-okr" }));
}
```

### Edit 도구 제약 해결 전략

`okr_matrix.html` 은 번들러 (esbuild) 출력으로 모든 Korean string 이 `\uXXXX` literal escape sequence 로 저장됨 (예: `"저장되었습니다"` → `"저장되었습니다"`).

Edit 의 old_string 에 실제 Korean character 를 포함하면 파일 bytes 와 매칭 실패 → 이번 세션에서 반복된 "String to replace not found in file" 에러의 근본 원인.

**금지 패턴 (매칭 실패):**
```
old_string: this.toast.success("Objective가 저장되었습니다.");
```

**올바른 패턴 (택 1):**
1. **ASCII-only anchor 분리**: Korean 이 없는 인접 ASCII 라인만으로 old_string 구성
   ```
   old_string:
     this.store.setObjectiveForAll(text);
   new_string:
     this.store.setObjectiveForAll(text);
     // 새 코드
   ```
2. **Escape sequence 그대로 작성**: `저장...` 를 literal backslash 로 입력 (shell/JSON 이스케이프 충돌 주의)

**이번 잔여 작업 적용:**
- 잔여 A: `this.store.setObjectiveForAll(text);` + 다음 `},` + `onAddKR: (p) => {` ASCII 3줄 anchor 로 한 번에 삽입
- 잔여 B: `this.render(this.store.getState());\n    this.setupMessageListener();\n  }` ASCII anchor

### 반복 실수 방지 규칙 (향후)

esbuild/번들러 출력 HTML·JS 파일 수정 시:
1. 먼저 `grep -n "ASCII-keyword"` 로 정확한 라인 내용 확인
2. `Read` 로 원문 bytes 확인 (Korean 은 `\uXXXX` 로 표시됨)
3. Edit old_string 은 ASCII-only 영역으로 한정

---

## 검증 (Phase 5)

| 항목 | 방법 |
|------|------|
| JS 문법 | 브라우저 DevTools 콘솔 에러 없음 확인 |
| 버튼 표시 | OKR 탭 오른쪽 상단에 "📥 OKR 가져오기" 버튼 표시 |
| OBJECTIVE sync (최초) | 빈 상태에서 OBJECTIVE 입력 → 팝업 없이 저장, 팀 전원에게 전파 |
| OBJECTIVE sync (수정) | 기존 OBJECTIVE 있을 때 수정 → confirm 팝업 → 확인 시 전원 동기화, 취소 시 저장 안 됨 |
| KR 복사 모달 | 버튼 클릭 → 팀원 드롭다운 → 팀원 선택 → 해당 팀원 KR 목록 표시 |
| KR 복사 실행 | 체크박스 다중 선택 → 복사 → 새 KR 추가됨 (Task·서브태스크 포함), ID 충돌 없음 |
| 회귀 | 기존 KR/Task/서브태스크 CRUD 정상 동작 |

---

## 백업

`okr_matrix_20260422-141827.html` (`.claude/backups/`) — 이미 생성됨

---

## 배포 (Phase 6)

파일 저장 = OneDrive 자동 동기화 배포. 사용자 확인 필수.