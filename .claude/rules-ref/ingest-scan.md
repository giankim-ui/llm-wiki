---
trigger: /ingest, /projects 백로그 스캔, 미반영 파일, stage 모드 프로젝트, synthesis grep, 슬러그 분류, 수동 이관 manifest, stage_ingest_gate
---
# Ingest/Projects — 백로그 스캔 규칙

경로 범위: `10_RAW/projects/**`, `.claude/commands/ingest-project-modes.json`, `scripts/stage_ingest_gate.py`

## stage 모드 프로젝트는 synthesis grep으로 backlog 판정 금지

**트리거**: `/ingest` 또는 `/projects` 자동 스캔에서 "미반영 파일" 후보를 뽑을 때.

**가드레일**: `.claude/commands/ingest-project-modes.json`에서 `mode: "stage"`로 등록된 프로젝트(예: `anlyz-hrIndexData`)는 raw 파일명이 `20_WIKI/projects/<slug>/synthesis.md`에 텍스트로 안 보인다고 "미반영"으로 판정하면 안 된다. stage 프로젝트는 `$env:TEMP\claude-projects-state\moved.json`의 `completed`/`consumed_at` 플래그로만 신규 여부를 가린다 — synthesis는 stage 단위로 요약돼 개별 파일명이 그대로 안 남을 수 있다.

**검증 방법**: 백로그를 보고하기 전 반드시
```
python scripts/stage_ingest_gate.py inspect
```
를 실행하고, `pending Stage files: 0`이면 grep 결과가 몇 건이든 오탐으로 간주하고 폐기한다. legacy 프로젝트는 `git diff`/`git ls-files --others` 기반 스캔이 원칙이지만, `10_RAW/projects/<slug>/`가 `.gitignore`에 완전히 걸려 있으면(허용된 하위 경로 외) git 기반 스캔도 무음 실패하므로 실제 폴더 존재 여부와 `synthesis.md`를 함께 대조해야 한다.

**사고 기록 (2026-08-18)**: 전체 `10_RAW/projects/**` 파일명 대 각 slug `synthesis.md` 텍스트 포함 여부만으로 "anlyz-hrIndexData 34건 미반영"을 보고했다가, `stage_ingest_gate.py inspect`가 `pending: 0`을 반환하고 synthesis에 실제로 27회 언급됨을 확인해 전량 오탐으로 정정. 동일 실수가 이전 세션에서도 있었다는 사용자 지적으로 재발 확인.

## `/projects` 슬러그 분류: 키워드 테이블 매칭보다 관련 plan/Stage 문서 우선 확인

**트리거**: `/projects` §2 Level 2 키워드 테이블로 `result-*`/`handoff-*` 파일의 슬러그를 자동 판정할 때, 특히 stage 모드 프로젝트(`anlyz-hrIndexData` 등)와 소재 겹치는 키워드(`hcroi`, `headcount`, `salary`, `duckdb` 등은 `hr-pipeline` 우선순위 7에 등록)가 걸리는 경우.

**가드레일**: 파일명에 `duckdb`/`hcroi`/`headcount`/`salary` 같은 hr-pipeline 키워드가 포함돼도, raw 본문이 특정 plan(`§6 게이트`, `plan-lc-dashboard-260824-v1_0` 등)을 명시적으로 참조하면 그 plan이 속한 프로젝트(Stage 문서 유무로 판별)를 슬러그로 우선 채택한다. Level 2 키워드 테이블은 파일명만 보는 fallback이라 stage 프로젝트의 후속 result가 다른 슬러그로 새는 것을 못 막는다 — Level 3(내용 분석) 단계에서 본문 1~20줄에 언급된 참조 plan/파일명을 `20_WIKI/projects/*/stage-*.md` 전수 grep해 어느 Stage 흐름에 속하는지 먼저 확인한 뒤에만 키워드 테이블 결과를 채택한다.

**검증 방법**: raw 본문에 `참조 plan:` 또는 유사 표기로 다른 파일명이 나오면, 그 파일명을 `grep -rl "<참조파일명>" 20_WIKI/projects/*/stage-*.md 20_WIKI/projects/*/synthesis.md` 로 먼저 찾는다. 매치되는 Stage 문서가 있으면 그 프로젝트 슬러그를 쓰고, 없으면 키워드 테이블 결과를 그대로 쓴다.

**사고 기록 (2026-08-27)**: `result-lc-data-check-260825-v1.0.md`/`result-lc-data-issues-260825-v1.0.md`가 본문에 `hcroi`/`headcount`/`salary` 관련 테이블 언급을 포함해 키워드 테이블(우선순위 7 hr-pipeline)로 분류·이관됐으나, 실제로는 `참조 plan: plan-lc-dashboard-260824-v1_0.md`를 명시하고 있었고 그 plan은 `anlyz-hrIndexData`의 `stage-6-p03-cost-dashboard.md` 흐름 #1로 이미 등록돼 있었다. 사용자가 직접 지적해 `10_RAW/projects/hr-pipeline/results/` → `10_RAW/projects/anlyz-hrIndexData/results/`로 재이관하고 stage-6 흐름에 재편입.

## /projects 수동 이관 후 manifest 기록 필수 (stage 프로젝트)

**트리거**: `/projects` 실행 중 `collect_map.ps1`이 `unknowns`로 분류한 파일을 Level 3/4에서 슬러그 확정한 뒤 직접 `Move-ProjectFile`로 옮기는 경우. 특히 frontmatter `project:`가 있는데 스크립트 canonical 목록에 없는 신규 slug(예: `infra-guide`)일 때 `classified=0, unknowns=N`이 나온다.

**가드레일**: unknowns를 수동으로 옮겨도 §5.1 절차대로 `classified.json`에 merge하고 §5.4의 `classified.json` 로드 → 이동 흐름을 따른다. 어떤 경로로 옮기든 이동 직후 `$env:TEMP\claude-projects-state\moved.json`에 `{source, destination, slug, type}` 항목을 추가하고 `completed: true`, `consumed_at: null`, 새 `run_id`로 기록한다. `moved.json`에 없는 stage 프로젝트 파일은 `stage_ingest_gate.py inspect`가 `pending: 0`을 내 `/ingest`가 조용히 0건으로 끝난다.

**검증 방법**: `/projects` 종료 보고 전에 `python scripts/stage_ingest_gate.py inspect`로 이동한 파일 수와 `pending Stage files`가 일치하는지 확인한다. 불일치하면 `/ingest`로 넘어가지 말고 manifest부터 보정한다. `/ingest`가 `pending: 0`이어도 이번 런에서 이동한 파일이 있으면 오탐으로 보고 즉시 중단·보정한다.

**사고 기록 (2026-09-30)**: `handoff-infra-guide-260929(-2).md` 두 건을 수동 이관하고 manifest를 남기지 않아 `/ingest`가 "반영할 파일 없음"으로 종료했다. 사용자 지적 후 Stage 1 흐름에 수동 편입.
