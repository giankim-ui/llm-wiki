---
type: project-index
project: mailing-agent
date: 2026-05-13
status: active
last_activity: 2026-04-15
current_phase: feature-add
current_version: v1.1
done_criteria: "Outlook 임시보관함 저장 + 표 자동 변환 테스트 완료"
tags:
  - mailing
  - email-automation
  - claude-agent
  - tone-matching
  - sqlite
themes: []
concepts: []
data_points: 2
last_lint: 2026-05-13
mirrors_raw: "[[plan-emailing]]"
---

# mailing-agent — Project Index

## Overview
업무 메일 초안 자동 생성 에이전트. SQLite DB(email_drafts / sent_emails / reference_emails / tone_profiles) 기반으로 발송본 대비 변경률을 분석해 톤앤매너를 누적 학습한다. `/draft` `/analyze` `/optimize` 슬래시 커맨드로 초안 생성·톤 분석·패턴 고도화를 제공.

## Status & Progress
| Phase | Status | Started | Completed | Notes |
|---|---|---|---|---|
| Phase 1~3 (골격·DB·에이전트) | done | 2026-04-15 | 2026-04-15 | CLAUDE.md, 4 에이전트, 2 스킬, DB 스키마 |
| Phase 4 (슬래시 커맨드) | done | 2026-04-15 | 2026-04-15 | /draft /analyze /optimize |
| Phase 5 (Python 로직) | done | 2026-04-15 | 2026-04-15 | analyzer.py, generator.py, optimizer.py |
| Cold start 시드 적재 | done | 2026-04-15 | 2026-04-15 | consulted.txt + draft.md + 결재메일 1건 매칭 |
| feature: /draft 단순화 | done | 2026-04-15 | 2026-04-15 | 입력 필드 6→3개 간소화 |
| feature: 아웃룩 임시보관함 저장 | active | 2026-04-15 | — | 구현 완료, 테스트 보류 |

## Key Plans & Results
| 유형 | Date | Summary | Raw |
|---|---|---|---|
| plan (초기) | 2026-04-15 | 전체 6 Phase 구현 계획 | [[plan-emailing]] |
| plan (v0.5 신기능) | 2026-04-15 | /draft 단순화 + 아웃룩 저장 + 최초사용자등록 | [[plan-new-feature-v0.5]] |
| result (신기능) | 2026-04-15 | /draft 단순화 완료, 아웃룩 저장 구현 완료(테스트 보류) | [[result-new-feature]] |

## Architecture
- **tone-analyzer**: .eml 분석 → 문체·어조·인사말 패턴 추출 → data/templates/ JSON
- **draft-writer**: 키워드 + DB 참조 → 초안 생성 → data/drafts/ 자동 저장 + 피드백 수집
- **optimizer**: data/sent/ 신규 파일 감지 → 초안 매칭 → diff 분석 → edit_ratio → 패턴 제안
- **db-manager**: SQLite CRUD (SELECT 자동, INSERT/UPDATE는 사용자 확인)
