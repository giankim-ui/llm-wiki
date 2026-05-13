---
type: index
scope: bottleneck
maintained_by: claude-code
tags:
  - bottleneck
  - dataview
---

# Bottleneck Index

병목 현상 분석 통합 허브. 모든 프로젝트의 `type: bottleneck` raw 문서를 Dataview로 집계한다.

## 전체 병목 현황

```dataview
TABLE project, category, severity, time_lost_min, root_cause, date
FROM "10_RAW/projects"
WHERE type = "bottleneck"
SORT time_lost_min DESC
```

## 카테고리별

```dataview
TABLE rows.file.link AS "문서", rows.project AS "프로젝트", rows.time_lost_min AS "손실(분)"
FROM "10_RAW/projects"
WHERE type = "bottleneck"
GROUP BY category
```

## 관련 페이지
- [[playbook]] — 새 프로젝트 시작 시 통합 체크리스트
- [[top-traps]] — 자주 발생한 함정 Top N
- [[queries]] — Dataview 쿼리 템플릿
- [[tool-trap]] / [[domain-knowledge]] / [[data-quality]] / [[process]] / [[infra]]
