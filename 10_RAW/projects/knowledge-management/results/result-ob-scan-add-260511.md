# Result: organize.py — 20-Obsidian 폴더 스캔 추가

- 날짜: 2026-05-11
- 상태: 완료
- 참조 plan: 없음

## 요약

`!Claude/organize.py`가 `!Claude` 폴더만 스캔하던 것을 `20-Obsidian` 폴더까지 통합 인덱싱하도록 확장.
초기엔 Obsidian vault 방식(frontmatter)으로 구현했으나, 사용자 요청에 따라 `!Claude`와 동일하게
`plan*`, `result*`, `research*.md` 파일만 추적하는 방식으로 변경.
`rglob("*")` 전체 스캔을 Obsidian 폴더에서 제거해 OneDrive 느린 I/O 개선.

## 수정 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `!Claude/organize.py` | `OBSIDIAN_DIR` 상수 추가, `get_obsidian_project_info` 신규, `get_project_info`에 `mtime_scan` 파라미터 추가, `TRACKED_PATTERNS` + `iter_tracked_files` 추가, `build_recent` 소스별 필터링, `main()` Obsidian 스캔 루프 추가 |

## 핵심 설계 결정 및 이유

- **`mtime_scan=False`** : Obsidian 폴더는 수천 개 노트가 있을 수 있어 `rglob("*")` 대신 tracked 파일만으로 mtime 재계산
- **`[Ob]` 접두사** : index/tags/recent에서 Claude 프로젝트와 시각적으로 구분
- **`iter_tracked_files`** : `build_recent`가 소스(claude/obsidian)에 따라 다른 파일 집합을 순회하도록 분리
- **출력 위치는 `!Claude`로 통합** : index.md/tags.md/recent.md 하나씩만 유지

## 빌드/타입체크 결과

해당 없음 (Python 스크립트, exit code 0 확인)

## 테스트 체크리스트

- [x] `organize.py` 실행 성공 (exit code 0)
- [x] `11개 Claude + 3개 Obsidian 폴더` 감지 확인
- [x] `recent.md`에 `[Ob] 10_RAW`, `[Ob] 20_WIKI` plan/result 파일 포착 확인
- [x] `[Ob] 90_ARCHIVE` — tracked 파일 없으면 recent에 미등장 확인
