---
type: concept
scope: bottleneck
status: stable
tags:
  - bottleneck
  - dataview
  - queries
---

# Dataview 쿼리 템플릿

## 프로젝트별 전체 병목

```dataview
TABLE category, severity, time_lost_min, root_cause
FROM "10_RAW/projects"
WHERE type = "bottleneck" AND project = "anlyz-hrIndexData"
SORT date DESC
```

## 카테고리 = tool-trap 만

```dataview
TABLE project, time_lost_min, root_cause, prevention
FROM "10_RAW/projects"
WHERE type = "bottleneck" AND category = "tool-trap"
SORT time_lost_min DESC
```

## 총 손실 시간 (프로젝트별 합계)

```dataview
TABLE sum(rows.time_lost_min) AS "총 손실(분)"
FROM "10_RAW/projects"
WHERE type = "bottleneck"
GROUP BY project
```
