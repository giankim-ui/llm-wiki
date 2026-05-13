---
type: concept
scope: bottleneck
status: draft
tags:
  - bottleneck
  - top-traps
---

# 자주 발생한 함정 Top N

```dataview
TABLE project, time_lost_min, root_cause, prevention
FROM "10_RAW/projects"
WHERE type = "bottleneck" AND severity = "high"
SORT time_lost_min DESC
LIMIT 10
```

> 이 페이지는 Dataview 자동 집계 — 수동 편집 불필요.
