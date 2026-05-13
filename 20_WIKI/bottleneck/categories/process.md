---
type: concept
scope: bottleneck
category: process
status: stable
tags:
  - bottleneck
  - process
---

# Process — 작업 절차 함정

검증 없는 일괄 처리, 반복 수정 사이클, 단계 건너뜀 등 프로세스 미준수로 발생.

## 대응 원칙
- LIMIT=1 → LIMIT=5 → 전체 순서 단계 검증 필수
- 각 단계 검증 앵커(요약 시트 SUM 등) 확인 후 다음 단계 진입
- 임시 스크립트(_explore*, _verify*) 실행 후 반드시 삭제

## 관련 bottleneck

```dataview
TABLE project, time_lost_min, root_cause
FROM "10_RAW/projects"
WHERE type = "bottleneck" AND category = "process"
SORT time_lost_min DESC
```
