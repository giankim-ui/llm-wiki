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

### 5.1 Pre-flight: 변환 맵 수집
1. 4개 소스 폴더에서 `.md` 파일 전수 enumerate (Glob + Bash ls)
2. 각 파일에 분류 규칙 적용 → `(src_path, slug, type, dst_basename)` 4-tuple 리스트 생성
3. 모호 파일은 AskUserQuestion 으로 slug 결정
4. 중복 basename 충돌 검출 → rename 적용
5. 최종 변환 맵 = `[(src, dst, basename_changed: bool), ...]`

### 5.2 Pre-flight: wikilink 영향 스캔
변환 맵에서 `basename_changed = True` 인 파일들의 old basename 만 추출.

다음 패턴을 `20_WIKI/**/*.md` 에서 Grep:
- `\[\[<old_basename>\]\]`
- `\[\[<old_basename>\.md\]\]`
- `mirrors_raw: "\[\[<old_basename>\]\]"`

영향받는 wiki 파일 목록 + 위치(line) 수집.

### 5.3 사용자 보고 (실행 전)
다음 형식으로 보고:
```
[/projects] 이관 계획
- 총 N개 파일 → 슬러그별 분포: km=X, multi=Y, screening=Z
- AskUserQuestion 처리 필요: 모호 파일 M개
- 중복 충돌 rename: P개
- Wikilink cascade 영향 wiki 파일: Q개

진행할까?
```

여기서 사용자 확인 받기 (단순 yes/no 자연어).

### 5.4 실행
1. 타겟 디렉토리 일괄 생성:
   ```bash
   mkdir -p 10_RAW/projects/{knowledge-management,multi-agent-stock-analysis,screening-mode}/{plans,results,handoffs,clippings}
   ```
2. `git mv <src> <dst>` 순차 실행 (각 파일 개별)
3. 빈 파일도 그대로 이관
4. nested 폴더(예: `S-anlyz/archive/debug-archive/excel-py-260419.md`) → flatten
5. **wiki 폴더 자동 git add** (사용자 승인 정책, 260505): `20_WIKI/projects/<slug>/` 가 untracked 이면 `git add 20_WIKI/projects/<slug>/` 자동 실행

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
`20_WIKI/projects/projects-LOG.md` 에 append:
```
## [YYYY-MM-DD HH:MM] ingest | bulk raw migration via /projects (N files, M wikilinks cascaded)
- raw read 좌표: none (이관만, 본문 read 없음)
- 슬러그별: km=X, multi=Y, screening=Z
- cascade 갱신 wiki: Q개
```

루트 `LOG.md` 에도 highlight append (Schema Rule #4).

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
