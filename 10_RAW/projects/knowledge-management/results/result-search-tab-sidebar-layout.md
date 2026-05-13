# Result: 검색 탭 사이드바 레이아웃 이식

- 버전: v1.0
- 날짜: 2026-04-28
- 상태: 배포 완료 (RP-20260428-093659)
- 참조 Plan: archive/plan-search-tab-sidebar-layout.md

## 요약

**문제**: `meeting_dashboard.html`의 검색 탭이 단순 검색박스 + 필터버튼 flat 구조로, 회의록 목록을 탐색하기 어려웠음.

**해결**: `meeting_dashboard_v6.html`의 검색 탭 구현(월별 폴더 사이드바 + 카드 그리드 우측 패널 2열 레이아웃)을 현재 대시보드에 이식. 다른 탭(TODO·분석·OKR) 및 sync.py 마커는 그대로 유지.

## 수정 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `10_HR_IN_Meeting_DB/meeting_dashboard.html` | CSS 추가(~155줄), HTML #tab-search 교체(~45줄), JS SEARCH 섹션 교체+신규 함수 추가(~220줄), init() 수정(+1줄) |

## 핵심 설계 결정

1. **히든 필터 행 보존**: `#searchFilters`에 `style="display:none;"` 적용해 sync.py `@@AUTO_FILTER_START@@`/`@@AUTO_FILTER_END@@` 마커 손상 없이 유지
2. **2열 레이아웃**: `.search-layout`(flex) → 좌측 `.meeting-sidebar`(sticky, 280px) + 우측 `.search-main`(flex:1)
3. **기본 화면**: 검색어/선택 없을 때 `renderTitleList()` 로 전체 회의록을 월별 카드 그리드로 표시
4. **사이드바 → 우측 패널 연동**: 월 클릭 → 해당 월 카드 그리드, 개별 회의 클릭 → 요약 전문 인라인 표시
5. **검색어 입력 시**: 사이드바 선택 자동 해제 후 전체 키워드 검색 실행

## 신규 JS 함수

| 함수 | 역할 |
|------|------|
| `renderMeetingSidebar()` | 월별 폴더 트리 렌더 (init에서 1회 호출) |
| `selectMonth(headerEl)` | 월 헤더 클릭 → 해당 월 카드 그리드 |
| `selectSidebarMeeting(id)` | 개별 회의 클릭 → 요약 전문 표시 |
| `clearSidebarSelection()` | 사이드바 active 초기화 |
| `renderTitleList(monthFilter?)` | 카드 그리드 렌더 (월 필터 옵션) |
| `showFullMeeting(id)` | 특정 회의 요약 전문 우측 패널에 표시 |
| `toggleMonth(el)` | 월 접기/펼치기 (호환용) |

## 변경 규모

- 3018줄 → 3357줄 (+339줄)
- CSS: +155줄, HTML: +45줄, JS: +139줄

## 검증 결과

| 항목 | 결과 |
|------|------|
| 신규 HTML 구조 (sidebar · search-layout · search-main) | ✅ |
| 히든 필터 + sync.py 마커 보존 | ✅ |
| 신규 CSS 클래스 (meeting-sidebar · month-group · title-card 등) | ✅ |
| 신규 JS 함수 7개 모두 존재 | ✅ |
| init()에 renderMeetingSidebar() 추가 | ✅ |
| 다른 탭(todo · analysis · okr) 무결성 | ✅ |

## 백업

`.claude/backups/meeting_dashboard_20260428-*.html`
