---
type: concept
scope: bottleneck
category: domain-knowledge
status: stable
tags:
  - bottleneck
  - domain-knowledge
---

# Domain-Knowledge — 비즈니스·스키마 이해 부족 함정

도메인 규칙(컬럼 의미, BU 계층, 집계 기준 등)을 코드 작성 전에 확인하지 않을 때 발생.

## 대응 원칙
- 컬럼 한국어 레이블 + 실제 데이터 샘플 먼저 확인
- BU 계층 구조(lv1/lv2/lv3)와 scope 명확히 파악 후 PK 설계
- 집계 기준(합계 vs 소계) 사전 협의

## 관련 bottleneck

```dataview
TABLE project, time_lost_min, root_cause
FROM "10_RAW/projects"
WHERE type = "bottleneck" AND category = "domain-knowledge"
SORT time_lost_min DESC
```
