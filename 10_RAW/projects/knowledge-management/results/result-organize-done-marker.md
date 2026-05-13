# Result: organize.py 수동 완료 마킹(.done) 지원 추가

- 날짜: 2026-04-27
- 상태: 완료
- 참조 plan: 없음

## 요약

`organize.py` 는 프로젝트 폴더에 `result*.md` 가 있어야만 완료로 판정했지만, 일부 프로젝트는 result 문서 없이 완료된 상태였다. `.done` 빈 파일을 마커로 인식하도록 `get_project_info` 의 분기 조건과 `is_done` 판정을 확장했고, mtime 계산에서는 `.done` 을 제외해 마커 생성일이 프로젝트의 "마지막 활동일" 표시를 덮지 않도록 했다.

## 수정 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `organize.py` | `done_marker = (folder / ".done").exists()` 추가, `result_f or done_marker` 분기로 완료 판정 확장 |
| `organize.py` | mtime 집계에서 `f.name != ".done"` 필터 추가 — 마커가 활동일을 가리지 않도록 |
| `organize.py` | 반환 dict 의 `is_done` 을 `bool(result_f) or done_marker` 로 변경 |
| `OKR/.done` 외 6개 | 완료 처리할 7개 프로젝트(OKR, notepad db, mailing-agent, agents, #Studies, skills, HR database building) 루트에 빈 마커 파일 생성 |
| `index.md` | 사전 수동 편집으로 7개 항목을 진행 중 → 최근 완료 섹션으로 이동 (organize.py 재실행 결과와 동일 상태로 수렴) |

## 핵심 설계 결정 및 이유

- **`.done` 빈 파일 방식 선택**: CLAUDE.md/README 등 기존 메타파일을 건드리지 않고, 폴더당 1바이트 파일 하나로 토글 가능. `touch <project>/.done` 로 마킹, `rm` 로 해제. 직관적이고 git 에 자연스럽게 추적된다.
- **mtime 집계에서 `.done` 제외**: 마커를 오늘 만들면 프로젝트 mtime 이 "오늘"로 갱신되어 정렬·표시가 왜곡됨. 활동 종료 후 늦게 완료 처리하는 케이스를 위해 마커는 정렬에 영향을 주지 않도록 분리.
- **result*.md 와 동급 처리**: 둘 중 하나만 있어도 완료. 향후 result 가 추가되면 자동으로 둘 다 있는 상태가 되며 동작 변화 없음.

## 빌드/타입체크 결과

`python organize.py` 실행 성공 (exit code 0). 진행 중에는 `Smartmeeting - 문서/30_interview` 만 남고 7개 마커 프로젝트는 모두 최근 완료로 이동 확인 (index.md 16:22 갱신).

## 테스트 체크리스트

- [x] `.done` 마커 있는 프로젝트가 진행 중에서 최근 완료로 이동
- [x] `Smartmeeting - 문서/30_interview` 가 진행 중에 그대로 유지
- [x] 마커 프로젝트의 표시 날짜가 "마지막 활동일" 기준 (오늘로 덮이지 않음)
- [ ] `.done` 삭제 후 재실행 시 다시 진행 중으로 복귀 (역동작 검증)
- [ ] 새 프로젝트에 `.done` 추가 시 즉시 완료로 분류
