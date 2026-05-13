# 이슈 1: Task 정렬 버그 수정

> 🎯 **목표**: Task가 order 필드 기준으로 정렬되도록 수정
> ⏱️ **예상 시간**: 5분
> 📁 **수정 파일**: `src/views/TaskSection.ts` (1곳)

---

## 📋 현재 문제

Task 목록이 `title` 알파벳순으로만 정렬됨.
`order` 필드가 있어도 무시되는 버그.

---

## ✅ 수정 방법

### 파일: `src/views/TaskSection.ts`

**찾을 코드** (약 Line 45~50 근처):
```typescript
// 기존 (잘못된 코드)
const sortedTasks = tasks.sort((a, b) => a.title.localeCompare(b.title));
```

**변경할 코드**:
```typescript
// 수정된 코드
const sortedTasks = tasks.sort((a, b) => {
  // order 필드가 있으면 order 기준, 없으면 title 기준
  if (a.order !== undefined && b.order !== undefined) {
    return a.order - b.order;
  }
  return a.title.localeCompare(b.title);
});
```

---

## 🧪 테스트 체크리스트

- [ ] order 값이 있는 Task들이 order 순서로 표시됨
- [ ] order 값이 없는 Task들은 title 알파벳순 정렬
- [ ] order 값이 일부만 있을 때 혼합 정렬 정상 동작

---

## ✅ 완료 확인

이 이슈 완료 후 → `issue-3-accordion.md`로 진행
