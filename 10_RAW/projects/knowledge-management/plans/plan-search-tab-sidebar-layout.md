# Plan: 검색 탭 사이드바 이식 소급 plan 문서 작성

## Context

pipeline 실행 중 Research/Plan 단계가 Plan mode 없이 대화 인라인으로 처리되어
`~/.claude/plans/`에 plan 파일이 생성되지 않았다.

이후 `/T.S` 실행 시 `merry-baking-candle.md`(실제 내용: ax-interview-app 관련 타 프로젝트)를
검색 탭 작업의 plan으로 오이동·오명명함.

→ `archive/plan-search-tab-sidebar-layout.md` 내용이 완전히 잘못된 상태.

## 조치 내용

### Step 1: 잘못된 파일 교체

`archive/plan-search-tab-sidebar-layout.md`를 올바른 소급 plan 내용으로 덮어씀.

### Step 2: 소급 plan 내용 (Write 대상)

```markdown
# Plan: 검색 탭 사이드바 레이아웃 이식 (v6 → meeting_dashboard.html)

## Context

meeting_dashboard.html의 검색 탭이 단순 검색박스 + 필터버튼 flat 구조로
회의록 목록을 탐색하기 불편했다. meeting_dashboard_v6.html에 구현된
월별 폴더 사이드바 + 카드 그리드 2열 레이아웃을 이식해 UX를 개선한다.
다른 탭(TODO·분석·OKR) 및 sync.py 마커는 변경하지 않는다.

## 대상 파일

| 파일 | 조치 |
|------|------|
| `10_HR_IN_Meeting_DB/meeting_dashboard.html` | CSS 추가 + HTML #tab-search 교체 + JS 교체/추가 |

## 변경 범위

### CSS (추가, ~155줄)
- `.search-layout` (flex 2열), `.meeting-sidebar` (sticky 280px), `.sidebar-header`
- `.month-group`, `.month-header`, `.month-toggle`, `.month-count`
- `.meeting-item`, `.search-main`
- `.title-list-intro`, `.title-list-section`, `.title-list-grid`, `.title-card`
- 반응형: `@media (max-width: 900px)`, `@media (max-width: 1200px/760px)`
- 삽입 위치: `.no-results .icon` 규칙 이후, `/* Detail modal */` 전

### HTML #tab-search (교체, ~50줄)
- 기존: 검색박스 → 필터버튼(visible) → 결과 div
- 변경: 히든 필터(sync.py 마커 보존) + `.search-layout` 2열
  - 좌측: `.meeting-sidebar#meetingSidebar > #sidebarList`
  - 우측: `.search-main` > 검색박스 + hint + count + results

### JS SEARCH 섹션 (교체+추가, ~220줄)
| 함수 | 변경 |
|------|------|
| `showSearchPlaceholder()` | 교체 → `renderTitleList()` 위임 |
| `doSearch()` | 교체 → 사이드바 연동 + 기본화면 분기 |
| `renderMeetingSidebar()` | 신규 — 월별 폴더 트리 렌더 |
| `selectMonth(headerEl)` | 신규 — 월 클릭 → 카드 그리드 |
| `selectSidebarMeeting(id)` | 신규 — 개별 회의 → 요약 전문 |
| `clearSidebarSelection()` | 신규 — 사이드바 active 초기화 |
| `renderTitleList(monthFilter?)` | 신규 — 카드 그리드 렌더 |
| `showFullMeeting(id)` | 신규 — 요약 전문 우측 패널 표시 |
| `toggleMonth(el)` | 신규 — 월 접기/펼치기 |

### init() 수정
- `renderMeetingSidebar()` 추가 (showSearchPlaceholder 전)

## 핵심 설계 결정

1. 히든 필터 보존: `#searchFilters style="display:none;"` → sync.py 마커 손상 방지
2. 사이드바 sticky: `position: sticky; top: 16px` — 스크롤 시 좌측 고정
3. 기본 화면: 검색어/선택 없을 때 renderTitleList()로 전체 카드 그리드 표시
4. 검색어 입력 시 사이드바 선택 자동 해제 (clearSidebarSelection)

## 검증 항목

- 사이드바 월 클릭 → 해당 월 카드 그리드 표시
- 개별 회의 클릭 → 요약 전문 인라인 표시
- 검색어 입력 → 전체 키워드 검색 실행
- sync.py 마커(@@AUTO_FILTER_START@@) 유지 확인
- 다른 탭(TODO·분석·OKR) 정상 동작

## 배포 결과

- RP-ID: RP-20260428-093659
- 백업: `.claude/backups/meeting_dashboard_20260428-093659.html`
- 3018줄 → 3357줄 (+339줄)
```

## 실행 단계

1. `Write` — `archive/plan-search-tab-sidebar-layout.md` 위 내용으로 덮어쓰기
```
