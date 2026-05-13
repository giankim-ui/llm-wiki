---
type: concept
scope: bottleneck
category: data-quality
status: stable
tags:
  - bottleneck
  - data-quality
---

# Data-Quality — 데이터 품질 함정

결측·인코딩 오류·형식 불일치·중복 등 입력 데이터 자체의 문제.

## 대응 원칙
- Pre-flight 스캔으로 결측·null·형식 이상 먼저 파악
- 인코딩: UTF-8 / CP949 확인 후 처리
- tolerance 범위 설정 (±15 등) — 엄격 동등 비교 금지

## 관련 bottleneck

```dataview
TABLE project, time_lost_min, root_cause
FROM "10_RAW/projects"
WHERE type = "bottleneck" AND category = "data-quality"
SORT time_lost_min DESC
```
