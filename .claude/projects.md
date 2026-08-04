---
description: cwd/archive 및 3국 ~/archive 의 .md 파일을 10_RAW/projects/{슬러그}/{타입}/ 으로 일괄 이관 (git mv) + wikilink cascade 자동 갱신
---

# /projects — Project raw 일괄 이관

Vault 의 분산된 archive .md 파일을 `10_RAW/projects/<slug>/{plans,results,handoffs,clippings}/` 로 일괄 이관하고, `20_WIKI/` 의 wikilink·`mirrors_raw` 를 cascade 갱신한다.

## 1. 소스 폴더 (4곳, cwd 기준)

- `<cwd>/archive/` (재귀)
- `<cwd>/S-anlyz/archive/` (재귀)
- `<cwd>/S-anlyz-kr/archive/` (재귀)
- `<cwd>/S-anlyz-jp/archive/` (재귀)

## 2. 자동 분류 규칙 (PLAN v2.2.1 부록 F 기준)

| 파일명 패턴 | slug | 타입 폴더 |
|---|---|---|
| `PLAN_통합지식관리*`, `PLAN_km-*`, `PLAN_raw-data-preservation*`, `PLAN_phase-model*`, `PLAN-phase-model*`, `REF_CLAUDE-md_skeleton*`, `lim-wiki*` | `knowledge-management` | `plans/` |
| `PLAN_cross-country-pipeline-sync*`, `PLAN_pipeline-sync-agent*`, `PLAN_investing-scraper*`, `PLAN_sec-scraper*`, `PLAN_us-sync-screening-cyclical*`, `PLAN_data-collector*`, `PLAN_S-anlyz-jp*`, `plan*.md`, `plan-*.md`, `plan-jp-*`, `plan-sonnet*`, `plan-industry*` | `multi-agent-stock-analysis` | `plans/` |
| `PLAN_jp-sync-screening*`, `PLAN_edinet-api-integration*` | `screening-mode` | `plans/` |
| `RESULT_*`, `result-*`, `result.md`, `result-2026*` | (PLAN과 동일 매핑 적용) | `results/` |
| `HANDOFF*` (cwd/archive) | `knowledge-management` | `handoffs/` |
| `HANDOFF*` (S-anlyz*/archive) | `multi-agent-stock-analysis` | `handoffs/` |
| `research*.md` (cwd/archive) | `knowledge-management` | `clippings/` |
| `research*.md`, `research.v*.md`, `research-v*.md` (S-anlyz/archive) | `multi-agent-stock-analysis` | `clippings/` |
| `CLAUDE_KR*`, `jp-stock-analysis-framework*`, `jSX-HTML-변환규칙*`, `investing-scriper*`, `supervisor-v1*`, `result.md`, `result-2026*` (S-anlyz*/archive) | `multi-agent-stock-analysis` | `clippings/` |

> **소스 폴더 우선 규칙**: `plan-*.md` 패턴은 소스 폴더로 구분한다 — **cwd/archive** 는 `knowledge-management` 우선, **S-anlyz\*/archive** 는 `multi-agent-stock-analysis` 우선.

## 3. 모호 파일 (AskUserQuestion 런타임)

다음 패턴은 자동 분류 불가 → 사용자에게 슬러그 묻기:
- `security-guide-*`, `excel-py-*`, `task.md`, `lim-wiki-ko.md`, 기타 위 표에 매핑되지 않는 파일

옵션: `knowledge-management` / `multi-agent-stock-analysis` / `screening-mode` / skip

여러 파일 묶어 한 번에 묻지 말 것 — 파일별 1 질문 (사용자 컨텍스트 손실 방지). 단 4개 초과 시 묶어 multiSelect 사용.

## 4. 중복 충돌 처리

동일 basename 이 여러 폴더에 존재 시:
- 첫 번째는 그대로 mv
- 두 번째부터는 `<base>_<src-folder-name>.md` 로 rename mv
  - 예: `S-anlyz-jp/archive/jp-stock-analysis-framework.md` → `jp-stock-analysis-framework_S-anlyz-jp.md`

## 5. 실행 절차

> Pre-flight 스캔은 `scripts/projects_classify.py` (ThreadPoolExecutor 병렬)를 사용한다.

### 5.1 Pre-flight: 변환 맵 수집
1. `python scripts/projects_classify.py` 실행 → stdout JSON 수신
   - 출력 스키마: `{files: [{src_path, ctime_iso, slug, type, confidence, reason}], summary}`
   - 4개 소스 폴더를 `ThreadPoolExecutor(max_workers=5)` 병렬 스캔
2. `confidence=L3` (모호) 파일 → **Agent(haiku) 병렬 읽기**: 파일당 독립 Agent(model=haiku) 1개씩 단일 메시지에서 동시 호출
   - 프롬프트: `"다음 파일의 앞 20줄을 Read하고, slug를 knowledge-management / multi-agent-stock-analysis / screening-mode / unknown 중 하나로만 답하라: {src_path}"`
   - Agent 결과(slug 문자열만)를 분류 맵에 반영
   - **읽기 전용** — Agent가 파일을 수정하거나 INDEX/LOG를 건드리면 안 됨
3. AskUserQuestion: `confidence=L3` 이고 Agent도 `unknown` 판정한 파일만 사용자에게 묻기
4. 중복 basename 충돌 검출 → rename 적용
5. 최종 변환 맵 = `[(src, dst, basename_changed: bool), ...]`

### 5.2 Pre-flight: wikilink 영향 스캔
변환 맵에서 `basename_changed = True` 인 파일들의 old basename 만 추출.

다음 패턴을 `20_WIKI/**/*.md` 에서 Grep:
- `\[\[<old_basename>\]\]`
- `\[\[<old_basename>\.md\]\]`
- `mirrors_raw: "\[\[<old_basename>\]\]"`

영향받는 wiki 파일 목록 + 위치(line) 수집.

### 5.3 사용자 통지 (실행 전, 확인 대기 없음)
다음 형식으로 통지 후 **별도 확인 없이 바로 §5.4 진행**:
```
[/projects] 이관 계획
- 총 N개 파일 → 슬러그별 분포: km=X, multi=Y, screening=Z
- AskUserQuestion 처리 필요: 모호 파일 M개
- 중복 충돌 rename: P개
- Wikilink cascade 영향 wiki 파일: Q개
```

이 보고는 "지금부터 이렇게 실행합니다" 통지이며 진행 여부를 묻는 게이트가 아니다 — yes/no 확인 대기 금지. (단, §5.0 D3 신규 발견 소스 폴더 및 §3 Level 4 모호 슬러그 AskUserQuestion 은 그대로 유지되며 이 규칙과 무관하게 별도 정지점이다.)

### 5.4 실행
0. 실행 시작 시 `$env:TEMP\claude-projects-state\moved.json` 을 새로 만든다.
   - `schema_version: 1`, 새 `run_id`, `completed: false`, `consumed_at: null`, `entries: []`를 기록한다.
   - 이전 manifest가 있어도 재사용하거나 이어 쓰지 않는다.
1. 타겟 디렉토리 일괄 생성:
   ```bash
   mkdir -p 10_RAW/projects/{knowledge-management,multi-agent-stock-analysis,screening-mode}/{plans,results,handoffs,clippings}
   ```
2. `git mv <src> <dst>` 순차 실행 (각 파일 개별)
3. 빈 파일도 그대로 이관
4. nested 폴더(예: `S-anlyz/archive/debug-archive/excel-py-260419.md`) → flatten
5. **wiki 폴더 자동 git add** (사용자 승인 정책, 260505): `20_WIKI/projects/<slug>/` 가 untracked 이면 `git add 20_WIKI/projects/<slug>/` 자동 실행

### 5.4.1 이동 manifest 기록 (Phase 3)

- 각 파일은 `git mv` 성공 직후 목적지 파일이 실제로 존재하는지 확인한다.
- 확인된 파일만 `entries`에 `source`, `destination`, `slug`, `type`을 기록한다. 예정 목록(`classified.json`)은 Stage 신규 판정에 사용하지 않는다.
- 모든 이동과 목적지 확인이 끝난 경우에만 `completed: true`로 바꾼다. 중단·부분 실패 시 `false`로 남겨 `/ingest`가 Stage를 변경하지 않게 한다.
- `/ingest`가 해당 실행을 성공적으로 처리한 뒤에만 `consumed_at`을 기록한다. `/projects`가 선제 소비하지 않는다.
- `destination`은 현재 Vault의 `10_RAW/projects/` 안에 있는 파일이어야 하며, 다른 Vault의 manifest나 목적지 누락 항목은 Stage 라우팅에서 무시한다.

### 5.5 Post-flight: Wikilink Cascade
basename 이 변경된 파일에 한해 영향 wiki 일괄 치환:
- Edit tool 사용, 각 파일별 `replace_all: true`:
  - `[[<old>]]` → `[[<new>]]`
  - `[[<old>.md]]` → `[[<new>.md]]`
- frontmatter `mirrors_raw: "[[<old>]]"` → `"[[<new>]]"` (동일 패턴이라 자동 포함)

### 5.6 Post-flight 검증
1. 모든 `mirrors_raw` 추출 → 실제 `10_RAW/projects/.../` 내 파일 존재 확인 (Bash test -f 또는 Glob)
2. folder link 위반 (`[[10_RAW/.../]]`) 잔존 검사
3. 미해결 wikilink 0건이어야 함. 있으면 보고 + 사용자 확인

### 5.7 LOG 갱신
`/projects`는 raw 이관과 manifest 기록만 담당한다. `LOG.md`·`synthesis.md`에는 행을 쓰지 않는다. 파일별 LOG 기록은 `/ingest`가 실제 내용을 처리한 뒤 허용된 이벤트 어휘로 추가한다.

### 5.8 종료 보고
```
[/projects] 완료
- 이관 N개 (km=X, multi=Y, screening=Z)
- AskUserQuestion 처리 M개: <목록>
- skip P개: <이유>
- Wikilink cascade Q개 wiki 파일 갱신
- 검증: 미해결 0건
- LOG 항목 추가
```

## 6. 주의사항

- `.md` 만 대상. `.json/.html/.jsx` 는 /assets 명령 영역
- HANDOFF.md (root, archive 외부) 는 대상 아님 — archive/ 안의 HANDOFF*만
- git mv 실패 (예: 충돌, 권한) 시 즉시 중단 + 부분 진행 상태 보고. 사용자 결정 대기
- 새 세션에서도 동일 동작하도록 본 명령 본문에 절차 self-contained
