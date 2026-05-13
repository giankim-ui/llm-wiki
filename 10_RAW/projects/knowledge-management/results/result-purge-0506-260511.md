# Result: 5/6 회의록 2건 완전 제거

- 날짜: 2026-05-11
- 상태: 완료
- 참조 plan: 없음

## 요약

사용자가 10_Raw의 5/6 원본 파일 2개를 직접 삭제한 뒤 요청. 이번 pipeline-mt에서 생성된 요약 파일과 DB 레코드를 함께 제거해 일관성을 맞췄다. meetings 삭제 시 ON DELETE CASCADE로 action_items 자동 삭제, file_ingestion_log는 별도 DELETE. 이후 sync.py 재실행으로 meeting_dashboard.html 필터·데이터를 22개 기준으로 재생성 완료.

## 수정 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `20_Summary/20260506_1642_인사혁신팀_정기미팅_요약.md` | 삭제 |
| `20_Summary/20260506_1643_인사혁신팀_정기미팅_요약.md` | 삭제 |
| `30_DB/hr_meetings.db` | meetings 2건 + action_items(cascade) + ingestion_log 2건 삭제 |
| `meeting_dashboard.html` | sync.py 재실행으로 필터·meetings·todos·label 재생성 |

## 핵심 설계 결정 및 이유

- **ingestion_log 별도 삭제 필수**: sync.py는 `file_ingestion_log`를 기준으로 변경 감지를 하므로 로그를 남기면 이후 파일 재추가 시 hash 충돌로 skip될 수 있음. 함께 제거.
- **sync.py 재실행으로 HTML 재생성**: DB DELETE 후 대시보드 HTML의 `@@AUTO_*@@` 마커 구간을 sync.py가 자동 갱신 — 별도 Edit 불필요.

## 빌드/타입체크 결과

해당 없음. sync.py exit 0, files_failed: 0 확인.

## 테스트 체크리스트

- [x] 20_Summary에 20260506_* 파일 없음 확인
- [x] DB meetings 테이블에 `20260506%` id 없음 확인
- [x] sync.py 재실행 files_skipped: 22, files_failed: 0
- [ ] 대시보드 브라우저 열기 — 5/6 필터 버튼 미표시 확인 (수동)
