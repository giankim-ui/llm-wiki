# Plan — KM v2.2.1 Phase 0 + Phase 1 실행

## Context

사용자가 통합 지식 관리 체계 PLAN v2.2.1 (Pilot-first)을 승인했음. v2.2.1 plan 본문 + Appendix A skeleton 외부 분리 완료 (이번 세션):

- `c:\Users\nayut\!claudeProject\archive\PLAN_통합지식관리체계_v2.2.1_260505.md`
- `c:\Users\nayut\!claudeProject\archive\REF_CLAUDE-md_skeleton_260505.md`

**다음 단계**: v2.2.1 §12 권장에 따라 **세션 1 = Phase 0 (안전망) + Phase 1 (vault 골격)** 실행. 약 3~3.5h. 본 plan은 v2.2.1 §8 Phase 0~1 내용을 실행 체크리스트로 압축.

**왜 지금**: v2.2.1 까지 4번 plan 반복하면서 설계가 충분히 정련됨. 더 이상 plan 만 다듬는 단계가 아니라, pilot 으로 실측 데이터를 모아야 v2.3 가 나옴. 일단 Phase 0+1 까지만 실행해서 골격을 깔고, 사용자 승인 받은 뒤 Phase 2-pilot 으로 진행.

## Repo 사전 상태 확인 (verified)

- **Repo 루트**: `C:\Users\nayut\!claudeProject\` — vault 루트와 일치 (단일 repo)
- **원격**: `https://github.com/giankim-ui/git-remote-origin.git` (push 가능)
- **기존 KB 브랜치/태그**: 없음 (clean slate)
- **`.obsidian/`**: 없음 — Obsidian 첫 vault open 시 자동 생성
- **Phase 1 신규 폴더**: 모두 존재하지 않음 — 충돌 없음
- **uncommitted**: 19 M + 41 untracked → Phase 0에서 정리 대상
- **유의**: vault 루트에 기존 폴더 `asset-rpa/`, `blueprint/`, `debug-archive/`, `my-app/`, `studies/`, `자료실/` 존재. v2.2.1 에서 다루지 않은 것들 — Phase 1에서는 그대로 두고 향후 Phase 2-full / Phase 5 lint 에서 분류 결정

## Phase 0 — 안전망 (예상 5~10분)

`kb-v2.2` 작업 진입 전 안전책. git 정리(uncommitted/untracked)는 **사용자가 직접 처리** — LLM 관여 없음.

> **이유**: plan*.md, handoff*.md 같은 frozen 문서는 commit 후 diff 없음 → git 추적 실익 없음. agent configs/GOTCHAS/CLAUDE.md 같이 편집되는 "기능성 .md"만 git 추적 의미 있음. 사용자가 직접 판단해 필요한 것만 commit.

### 0.1 uncommitted 정리 — 사용자 직접 처리 (LLM 스킵)

사용자가 직접 커밋. 단, 다음 구분만 참고:
- **추적 가치 있음**: 계속 편집되는 .md (agents/*.md, GOTCHAS.md, CLAUDE.md, skills/*.md)
- **추적 불필요**: plan*.md, handoff*.md, archive/* (frozen 문서 — 첫 commit 후 diff 없음)

### 0.2 태그 (local only — push는 사용자 명시 트리거 시)

```
git tag v-pre-kb-v2.2
```

> push 는 본 plan 자동 단계에 포함하지 않음. 사용자가 "push" 명시 요청 시 별도 진행: `git push origin master --tags`

### 0.3 새 브랜치

```
git checkout -b kb-v2.2/phase1-skeleton
```

## Phase 1 — Vault 골격 (예상 2.5h)

`kb-v2.2/phase1-skeleton` 브랜치에서 진행. vault 루트는 `C:\Users\nayut\!claudeProject\`.

### 1.1 빈 폴더 생성 (PowerShell `New-Item` 또는 `mkdir`)

```
10_RAW/
  assets/, projects/, screening/, chats/, clippings/, docs/, attachments/, inbox/
20_WIKI/
  assets/, projects/, concepts/, themes/, comparisons/,
  industry/, macro/, frameworks/, methodology/, screening/,
  concepts/sources/
90_ARCHIVE/
  handoffs/, lint-reports/
_templates/
```

### 1.2 루트 메타파일 작성 (Write)

| 파일 | 내용 출처 |
|---|---|
| `CLAUDE.md` | `archive/REF_CLAUDE-md_skeleton_260505.md` 본문 markdown 블록 그대로 복사 (헤더/메모 제외) |
| `INDEX.md` | Tier 1 dashboard 골격 (v2.2.1 §4.1 그대로). 빈 표 + Deep Navigation 표 |
| `LOG.md` | "# Vault Recent Activity" 헤더만, 첫 항목 비워둠 |
| `MAP.md` | 사람용 5분 가이드 — Phase 5에서 보강 예정. 일단 stub |

### 1.3 axis Tier 2 INDEX/LOG stub (v2.2.1 §4.3~4.6)

| 파일 | 비고 |
|---|---|
| `20_WIKI/projects/INDEX.md` | Active/Blocked/Paused/Done/Archived 빈 표 + Concept Reverse Index 빈 표 |
| `20_WIKI/projects/LOG.md` | 헤더만 |
| `20_WIKI/assets/INDEX.md` | Watchlist/Recently Analyzed/Holdings 빈 표 + Theme Reverse Index 빈 표 |
| `20_WIKI/assets/LOG.md` | 헤더만 |
| `20_WIKI/concepts/INDEX.md` | reverse index 빈 표 |
| `20_WIKI/themes/INDEX.md` | 빈 목록 |
| `20_WIKI/comparisons/INDEX.md` | 빈 목록 |

### 1.4 Templater 템플릿 9종 (v2.2.1 부록 E + §3 _templates)

`_templates/` 에 9개 .md:
- `asset-INDEX.md`, `asset-synthesis.md`
- `project-INDEX.md`, `project-synthesis.md`
- `concept.md`, `theme.md`, `comparison.md`
- `source-structure.md`
- `plan.md`, `chat-extract.md`

각 템플릿 frontmatter 표준 (v2.2.1 §5.1) + 섹션 골격만. Templater 플러그인 미설치 시 일반 .md로도 작동하도록 작성.

### 1.5 .gitignore 보강

기존 `.gitignore` Read 후 다음 라인 추가:
```
# KM v2.2 — chat raw exports (개인정보)
10_RAW/chats/**/raw.json
10_RAW/chats/**/raw/
10_RAW/chats/claude/**/raw.json
10_RAW/chats/gemini/**/raw.json
```

### 1.6 검증

다음 모두 합격 시 머지:
- [ ] Obsidian으로 `!claudeProject/` vault open → 좌측 트리에 10_/20_/90_ 폴더 표시
- [ ] 루트 `CLAUDE.md` 열기 → §6.0 Raw Reading Discipline + Mirror Principle + Status Vocabulary 모두 포함
- [ ] `_templates/` 9개 .md 모두 존재, 각 frontmatter 의 `type` 필드 정확
- [ ] `20_WIKI/projects/INDEX.md` 와 `20_WIKI/assets/INDEX.md` 열림
- [ ] `.gitignore` 에 raw.json 패턴 추가 확인
- [ ] (Optional) Obsidian Templater 플러그인 설치 후 템플릿 작동 → 새 노트 생성 시 frontmatter 자동 채움

### 1.7 머지 + 태그 (local only)

```
git checkout master
git merge --ff-only kb-v2.2/phase1-skeleton
git tag v-kb-v2.2-phase1
```

> push 는 사용자 명시 트리거 시 별도 진행. 본 plan 자동 단계 외.

## Critical Files

**참조 (read-only)**:
- `c:\Users\nayut\!claudeProject\archive\PLAN_통합지식관리체계_v2.2.1_260505.md` — canonical spec (§8 Phase 0~1, §11 검증)
- `c:\Users\nayut\!claudeProject\archive\REF_CLAUDE-md_skeleton_260505.md` — 루트 CLAUDE.md baseline

**생성 (Phase 1)**:
- `c:\Users\nayut\!claudeProject\CLAUDE.md`
- `c:\Users\nayut\!claudeProject\INDEX.md`
- `c:\Users\nayut\!claudeProject\LOG.md`
- `c:\Users\nayut\!claudeProject\MAP.md`
- `c:\Users\nayut\!claudeProject\_templates\*.md` (9종)
- `c:\Users\nayut\!claudeProject\20_WIKI\{projects,assets,concepts,themes,comparisons}\INDEX.md`
- `c:\Users\nayut\!claudeProject\20_WIKI\{projects,assets}\LOG.md`
- 빈 폴더 다수

**수정 (Phase 1)**:
- `c:\Users\nayut\!claudeProject\.gitignore` (Read → Edit)

## 리스크 / 확인 필요

| 리스크 | 대응 |
|---|---|
| uncommitted 정리 | 사용자 직접 처리 — LLM 스킵. plan*.md/handoff*.md 등 frozen 문서는 git 추적 불필요 |
| Obsidian 미설치 또는 첫 vault open 시 .obsidian/ 자동 생성 | 사용자가 직접 Obsidian 으로 vault open 해야 함. plan 실행 종료 후 검증 단계 |
| Templater 플러그인 미설치 | 검증 1.6 의 Optional 항목. 설치는 사용자 결정 |
| 기존 vault 루트 폴더 (`asset-rpa`, `studies`, `자료실` 등) 분류 | Phase 1 범위 외. Phase 2-full 또는 Phase 5 lint에서 처리 |
| Write protection hook | 새로 만드는 파일은 충돌 없음. `.gitignore` 만 Read → Edit |
| 원격 백업 부재 | push 가 본 plan 외이므로 PC 사고 시 마지막 원격 동기화 시점까지만 복구 가능. 사용자가 phase 종료 후 "push" 명시하면 그때 동기화 |

## 실행 순서 요약

1. Phase 0.1 — 사용자가 직접 git 정리 (LLM 스킵)
2. Phase 0.2~0.3 자동 (local 태그·브랜치, push 제외)
3. Phase 1.1~1.5 자동 (폴더·파일 생성)
4. **사용자 confirm**: 1.6 검증 결과 + Obsidian으로 직접 vault 확인
5. Phase 1.7 자동 (local 머지·태그, push 제외)
6. 종료 → 사용자가 "push" 명시 시 원격 동기화. Phase 2-pilot은 다음 세션에서

## End-to-End 검증

세션 1 종료 시 다음 모두 합격해야 다음 세션 (Phase 2-pilot) 진입 가능:

```bash
# 1. 태그 확인 (local)
git tag | grep v-kb-v2.2
# 출력: v-pre-kb-v2.2, v-kb-v2.2-phase1

# 2. 원격 동기화는 본 plan 외 — 사용자가 "push" 요청 시 별도 진행

# 3. 볼트 골격 확인 (PowerShell)
Get-ChildItem -Path "C:\Users\nayut\!claudeProject" -Directory | Select-Object Name
# 10_RAW, 20_WIKI, 90_ARCHIVE, _templates 포함

# 4. CLAUDE.md key 항목 확인
Select-String -Path "C:\Users\nayut\!claudeProject\CLAUDE.md" -Pattern "Raw Reading Discipline|Mirror Principle|Status Vocabulary"
# 3개 항목 모두 매치

# 5. Obsidian 직접 검증 (사용자 작업)
# - Obsidian Open Folder as Vault → !claudeProject/
# - 좌측 트리에 10_RAW/, 20_WIKI/, 90_ARCHIVE/, _templates/ 폴더 표시
# - 루트 CLAUDE.md, INDEX.md 클릭 → 정상 렌더링
```

다음 세션 (Phase 2-pilot) 시작 트리거: 사용자가 "phase 2-pilot 시작" 명시.
