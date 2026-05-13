# Result: TO-DO → OKR Task 동기화 버그 수정

버전: v1.0 | 날짜: 2026-04-22 | 상태: 코드 완료, 브라우저 검증 대기
참조 Plan: `archive/260422-interg-m-o/plan-okr-task-sync-fix-v1.0.md`
선행 통합: `result-okr-integration-v2.2.md`

---

## 요약

**문제**: TO-DO 탭에서 task 를 팀원에게 배분 → OKR Matrix 탭 TASK 섹션에 안 나타남.
사용자 의도(KR 매칭 후 TASK 섹션 자동 등장) 와 v2.2 구현 의도는 일치했으나, 양쪽 모두 **task 객체 자체 생성을 누락**.

**해결**:
1. `saveDistribution` (대시보드): 각 팀원 `okr-matrix-v2:{user}` localStorage 에 task 객체·KR 연결·taskDisplayOrder 까지 완전 작성.
2. `syncSharedTask` (OKR store): 현재 user 의 in-memory state 도 동일 갱신 → postMessage 수신 시 즉시 화면 반영.

---

## 수정 파일 목록

| 파일 | 변경 |
|------|------|
| `OKR/okr-matrix-app/src/utils/storage.ts` | (변경 없음 — `getCurrentUser` 이미 export) |
| `OKR/okr-matrix-app/src/models/store.ts` | `getCurrentUser` import 추가, `syncSharedTask` 완전 재작성 (title only → 신규 생성·KR 연결·재배분 KR 이동) |
| `Smartmeeting/10_HR_IN_Meeting_DB/meeting_dashboard.html` saveDistribution lines 2561~2620 | KR.tasks ID push 만 → task 객체 생성/갱신 + KR 이동 처리 + taskDisplayOrder 갱신 |
| `okr_matrix.html` | 빌드 자동 동기화 |

---

## 핵심 설계 결정 및 이유

| 결정 | 이유 |
|------|------|
| task schema = camelCase (krId, createdAt) | OKR 내부는 v2.2 에서도 camelCase 유지. snake_case 는 hr_shared_tasks 경계에서만 |
| saveDistribution 이 OKR schema 직접 갱신 | 이미 keyResults[krId].tasks 건드리고 있어 사실상 알고 있음. 누락 필드만 추가 |
| subTasks: [] (빈 배열) 신규 생성 | isTaskCompleted=false → "활성" 탭 표시 (사용자 의도 부합) |
| syncSharedTask in-memory 갱신 책임 | 다른 팀원 OKR iframe 미열림 → localStorage 사전 작성 + 본인 화면 즉시 반영 둘 다 필요 |
| 재배분 KR 이동 처리 | 기존 KR.tasks 에서 제거 후 새 KR 에 push — store.ts updateTask 패턴 모방 |

---

## 빌드/타입체크 결과

```
tsc --noEmit: 오류 없음
esbuild: bundle.js 62.6KB (이전 61.2KB → +1.4KB)
build_bundle_html.py: bundle.html 85.9KB → okr_matrix.html 동기화 완료
```

---

## 검증 체크리스트

| # | 항목 | 확인방법 | 결과 |
|---|------|---------|------|
| V_FIX_6 | TS 빌드·sync | 명령 실행 | ✅ tsc 무오류, sync 완료 |
| V_FIX_1 | 본인 배분 즉시 반영 | TO-DO 배분 → OKR 탭 → TASK 섹션 | 🔲 브라우저 확인 필요 |
| V_FIX_2 | 타 팀원 배분 + 사용자 전환 | switcher 로 안수민 선택 → OKR 탭 | 🔲 브라우저 확인 필요 |
| V_FIX_3 | 새로고침 후 유지 | 배분 후 reload → OKR 탭 | 🔲 브라우저 확인 필요 |
| V_FIX_4 | 재배분 KR 이동 | 같은 task 다른 KR 로 재배분 → 양쪽 표시 금지 | 🔲 브라우저 확인 필요 |
| V_FIX_5 | OKR 직접 추가 task 회귀 | 기존 OKR task 정상 동작 | 🔲 브라우저 확인 필요 |

---

## 백업

- ID: `RP-FIX-20260422-112427`
- `10_HR_IN_Meeting_DB/.claude/backups/meeting_dashboard_20260422-112427.html`
- `10_HR_IN_Meeting_DB/.claude/backups/okr_matrix_20260422-112427.html`
