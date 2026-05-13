# 이슈 3: OKR 아코디언 토글 기능

> 🎯 **목표**: OKR 헤더 클릭 시 KR 목록 접기/펼치기
> ⏱️ **예상 시간**: 10분
> 📁 **수정 파일**: `src/views/OKRSection.ts`, `css/okr-section.css`

---

## 📋 구현 사양

- 토글 버튼: 헤더 행 오른쪽에 배치
- 버튼 텍스트: 펼침 `▽` / 접힘 `△`
- 버튼 색상: `#FF6600` (주황색)
- 헤더는 항상 고정 (sticky 유지)

---

## ✅ 수정 방법

### 1단계: OKRSection.ts 수정

**클래스 상단에 상태 변수 추가**:
```typescript
export class OKRSection {
  private container: HTMLElement;
  // 🆕 추가: OKR별 접힘 상태 관리
  private collapsedState: Map<string, boolean> = new Map();
```

**render 메서드 내 헤더 블록에 버튼 추가** (titleRow 생성 부분):
```typescript
// 기존 titleRow 코드 찾기
const titleRow = document.createElement('div');
titleRow.className = 'okr-title-row';

// 🆕 토글 버튼 추가
const toggleBtn = document.createElement('button');
toggleBtn.className = 'okr-collapse-btn';
const isCollapsed = this.collapsedState.get(okr.id) ?? false;
toggleBtn.textContent = isCollapsed ? '△' : '▽';
toggleBtn.addEventListener('click', () => {
  this.collapsedState.set(okr.id, !isCollapsed);
  this.render(state);  // 리렌더링
});
titleRow.appendChild(toggleBtn);
```

**KR 테이블 조건부 렌더링**:
```typescript
// KR 테이블 렌더링 코드를 조건문으로 감싸기
const isCollapsed = this.collapsedState.get(okr.id) ?? false;

if (!isCollapsed) {
  // 기존 KR 테이블 렌더링 코드 전체
  const krTable = document.createElement('table');
  // ... (기존 코드 유지)
}
```

---

### 2단계: okr-section.css 수정

**파일 끝에 추가**:
```css
/* 토글 버튼 스타일 */
.okr-collapse-btn {
  background: none;
  border: none;
  color: #FF6600;
  font-size: 1rem;
  cursor: pointer;
  margin-left: auto;
  padding: 4px 8px;
  transition: opacity 0.2s;
}

.okr-collapse-btn:hover {
  opacity: 0.7;
}

/* 헤더 행 flex 정렬 (버튼을 오른쪽으로) */
.okr-title-row {
  display: flex;
  align-items: center;
}
```

---

## 🧪 테스트 체크리스트

- [ ] 토글 버튼이 OKR 헤더 오른쪽에 표시됨
- [ ] 버튼 클릭 시 KR 목록이 접힘/펼쳐짐
- [ ] 버튼 아이콘이 상태에 따라 변경 (▽ ↔ △)
- [ ] 여러 OKR이 있을 때 각각 독립적으로 동작
- [ ] 페이지 스크롤 시 헤더 sticky 유지됨

---

## ✅ 완료 확인

이 이슈 완료 후 → `issue-2-dnd.md`로 진행
