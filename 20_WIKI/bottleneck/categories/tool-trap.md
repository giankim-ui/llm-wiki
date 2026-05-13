---
type: concept
scope: bottleneck
category: tool-trap
status: stable
tags:
  - bottleneck
  - tool-trap
---

# Tool-Trap — 도구 특성 미숙지 함정

도구(DuckDB, pandas, regex 등)의 기본 동작·한계를 모르고 사용할 때 발생.

## 대응 원칙
- `auto_detect` / 자동 추론 → 명시적 설정으로 대체
- 헤더 row 직접 읽어 컬럼 1:1 확인 후 코딩
- 도구 문서에서 기본값 사전 확인

## 관련 bottleneck

```dataview
TABLE project, time_lost_min, root_cause
FROM "10_RAW/projects"
WHERE type = "bottleneck" AND category = "tool-trap"
SORT time_lost_min DESC
```
