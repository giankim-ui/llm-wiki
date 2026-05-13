# OKR Matrix App 오류 개선 - 마스터 가이드

> ⚠️ **중요**: 이 작업은 3개의 독립된 이슈 파일로 분리되어 있습니다.
> 각 이슈를 **순서대로 하나씩** 완료 후 다음으로 진행하세요.

---

## 🎯 전체 이슈 개요

| 순서 | 파일 | 이슈 | 난이도 | 예상 시간 |
|------|------|------|--------|----------|
| 1️⃣ | `issue-1-sort-fix.md` | Task 정렬 버그 수정 | ⭐ 쉬움 | 5분 |
| 2️⃣ | `issue-3-accordion.md` | OKR 아코디언 토글 | ⭐⭐ 중간 | 10분 |
| 3️⃣ | `issue-2-dnd.md` | Drag & Drop 기능 | ⭐⭐⭐ 어려움 | 30분 |

---

## 📁 수정 대상 파일 매트릭스

```
src/
├── views/
│   ├── TaskSection.ts    ← 이슈 1, 2
│   └── OKRSection.ts     ← 이슈 2, 3
├── models/
│   └── store.ts          ← 이슈 2
└── types/
    └── index.ts          ← 이슈 2

css/
├── task-section.css      ← 이슈 2
└── okr-section.css       ← 이슈 3
```

---

## ✅ 실행 방법

```bash
# 1단계: 정렬 버그 수정 (가장 간단)
# issue-1-sort-fix.md 파일 읽고 작업 수행

# 2단계: 아코디언 토글 (독립적 UI 기능)
# issue-3-accordion.md 파일 읽고 작업 수행

# 3단계: D&D 기능 (가장 복잡, 마지막)
# issue-2-dnd.md 파일 읽고 작업 수행
```

---

## 🔍 각 이슈 완료 체크

- [ ] 이슈 1: Task 정렬이 order 우선, title 차순으로 동작
- [ ] 이슈 3: OKR 헤더 클릭 시 KR 목록 접기/펼치기 동작
- [ ] 이슈 2: 드래그 핸들로 KR/Task/SubTask 순서 변경 가능
