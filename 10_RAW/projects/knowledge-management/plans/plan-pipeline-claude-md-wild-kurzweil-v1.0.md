# Plan: /pipeline 및 CLAUDE.md 현재 폴더 기준 업데이트

## Context

세 가지 불일치 해소:
1. WORKSPACE 경로에서 `!Claude\` 누락 (루트 CLAUDE.md + 10_HR_IN_Meeting_DB/CLAUDE.md)
2. `meeting_dashboard.html`에 OKR Matrix 탭(Tab 4) 및 User Switcher가 추가되었으나 CLAUDE.md들에 미반영
3. `/pipeline` description에 Split Phase 누락 + 신규 폴더 `20_인사실AX_개인별PJT/` 미문서화

---

## 변경 대상 파일 (4개)

| 파일 | 변경 내용 |
|------|---------|
| `CLAUDE.md` (루트) | ① WORKSPACE 경로, ② 폴더 구조 섹션, ③ HTML 탭 구조(4탭), ④ pipeline 명령어 설명 |
| `10_HR_IN_Meeting_DB/CLAUDE.md` | ① BASE 경로, ② 폴더 구조(okr_matrix.html), ③ 대시보드 구조 섹션 추가 |
| `.claude/commands/pipeline.md` | frontmatter description에 Split 단계 추가 |

---

## 수정 상세

### A. 루트 CLAUDE.md

**A-1. WORKSPACE 경로 수정 (line 15)**
```diff
- WORKSPACE = C:\Users\Pulmuone\OneDrive - 풀무원\Smartmeeting - 문서
+ WORKSPACE = C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\Smartmeeting - 문서
```

**A-2. 워크스페이스 목적 섹션 아래 폴더 구조 섹션 삽입**
```markdown
## 워크스페이스 폴더 구조

├── 10_HR_IN_Meeting_DB/      ← 메인 대시보드 (meeting_dashboard.html + okr_matrix.html)
├── 20_인사실AX_개인별PJT/    ← HR 워크플로우 POC (hr_workflow_dashboard_poc_v4.html)
├── archive/                   ← Plan·Result 파일 버전 보관
└── record/                    ← 기타 기록
```

**A-3. HTML 구조 섹션 탭 4개로 업데이트 (현재 3탭 → 4탭)**
```diff
-│   ├── .tabs    ← 탭 네비게이션 (TODO / 검색 / 분석)
+│   ├── .tabs    ← 탭 네비게이션 (TODO / 검색 / AX혁신 제언 / OKR Matrix)
 │   ├── #tab-todo     ← TAB 1: 할일 목록, 인라인 편집 가능 테이블
 │   ├── #tab-search   ← TAB 2: 전문 검색, 결과 카드, 모달
 │   └── #tab-analysis ← TAB 3: 인사이트 카드, 리스크, 로드맵
+│   └── #tab-okr      ← TAB 4: OKR Matrix (okr_matrix.html iframe, lazy load)
```

기능 검증 항목도 "3개 탭 전환" → "4개 탭 전환"으로 수정.

**A-4. 에이전트 명령어 표 pipeline 설명 수정**
```diff
- Research→Plan→Execute→Validate→Deploy
+ Research→Plan→Split→Execute→Validate→Deploy
```

---

### B. 10_HR_IN_Meeting_DB/CLAUDE.md

**B-1. BASE 경로 수정 (line 9)**
```diff
- BASE  = C:\Users\Pulmuone\OneDrive - 풀무원\Smartmeeting - 문서\10_HR_IN_Meeting_DB
+ BASE  = C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\Smartmeeting - 문서\10_HR_IN_Meeting_DB
```

**B-2. 폴더 구조에 okr_matrix.html 추가 (line 23)**
```diff
 ├── meeting_dashboard.html ← 회의 데이터 시각화 대시보드
+├── okr_matrix.html        ← OKR Matrix 뷰 (Tab 4 iframe 타깃, 독립 실행 가능)
```

**B-3. 대시보드 구조 섹션 추가** (경로 설정 섹션 뒤, 에이전트 실행 방법 앞)

```markdown
## meeting_dashboard.html 탭 구조

| 탭 | ID | 주요 기능 |
|----|-----|---------|
| ✅ TO-DO 리스트 | `#tab-todo` | Epic 아코디언·평면 뷰, 인라인 편집, 담당자 배분 모달 |
| 🔍 전문 검색   | `#tab-search` | 키워드 검색, 결과 카드, 상세 모달 |
| 📈 AX혁신 제언 | `#tab-analysis` | 인사이트·리스크·로드맵·전략, 버전 배지 |
| 📊 OKR Matrix  | `#tab-okr` | `okr_matrix.html` iframe lazy load, User Switcher 연동 |

**OKR Matrix 연동 핵심:**
- localStorage `hr_current_user` — 현재 사용자 (User Switcher가 설정)
- localStorage `okr-matrix-v2:{userName}` — 사용자별 OKR 상태
- User Switcher: 헤더 `#user-switcher-container` 위치, OKR 탭 활성화 시에만 활성
- 담당자 배분 저장 시 → `okr-matrix-v2:{assignee}` 업데이트 + iframe postMessage
- 탭 전환 시 iframe src 최초 1회 로드 (lazy); 사용자 변경 시 재로드
```

---

### C. `.claude/commands/pipeline.md`

```diff
- description: 통합 파이프라인 — Research → Plan → Execute → Validate → Deploy 연속 진행
+ description: 통합 파이프라인 — Research → Plan → Split → Execute → Validate → Deploy 연속 진행
```

---

## 검증

- 두 CLAUDE.md의 경로를 실제 작업 디렉토리와 대조
- `meeting_dashboard.html` 탭 수(4개) 및 OKR 연동 설명이 코드와 일치하는지 확인
- `/pipeline` description이 AGENT_ORCHESTRATOR.md 핵심 흐름과 일치하는지 확인
