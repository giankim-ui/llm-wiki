---
type: concept
scope: bottleneck
category: infra
status: stable
tags:
  - bottleneck
  - infra
---

# Infra — 환경·인프라 함정

권한 부족, 의존성 미설치, 경로 오류, OS 환경 차이 등 환경 문제로 발생.

## 대응 원칙
- 파이프라인 시작 전 의존성(openpyxl, duckdb 등) 버전 확인
- 경로 공백 포함 시 항상 따옴표 처리
- 권한 이슈는 taskkill / 관리자 실행으로 사전 해소

## 관련 bottleneck

```dataview
TABLE project, time_lost_min, root_cause
FROM "10_RAW/projects"
WHERE type = "bottleneck" AND category = "infra"
SORT time_lost_min DESC
```
