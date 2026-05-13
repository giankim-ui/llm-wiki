---
type: project-index
project: interview-stt
date: 2026-05-13
status: active
last_activity: 2026-05-06
current_phase: implementation
current_version: v1.0
done_criteria: "인터뷰 STT txt → bundle.html 호환 JSON 자동 변환 에이전트 구현 완료 + 골든 샘플 검증"
tags:
  - interview
  - stt
  - automation
  - json
  - claude-agent
themes: []
concepts: []
data_points: 2
last_lint: 2026-05-13
mirrors_raw: "[[plan-interview-stt-260428]]"
---

# interview-stt — Project Index

## Overview
인터뷰 STT(Speech-to-Text) txt 원문을 bundle.html 호환 JSON(Q0~Q4 × 기본/심화/꼬리 = 최대 15 answers)으로 자동 변환하는 에이전트 신설 프로젝트. 기존 `hr-meeting-processor` 골격을 fork해 `30_interview/` 폴더 안에 격리된 새 에이전트를 구축한다. 사번 lookup, 동명이인 disambiguation, 5질문 의미 기반 매핑, 스키마 검증 포함.

## Status & Progress
| Phase | Status | Started | Completed | Notes |
|---|---|---|---|---|
| 설계 | done | 2026-04-28 | 2026-04-28 | 에이전트 구조·파이프라인 6 STEP 확정 |
| 2-part 분할 계획 | done | 2026-05-06 | 2026-05-06 | Part B(ROI 관리자 이동) + Part A(업무 요약 재설계) 분리 |
| 에이전트 구현 | active | — | — | 7개 신설 파일 작성 |

## Key Plans
| Version | Date | Key Changes | Raw |
|---|---|---|---|
| plan-interview-stt v1.0 | 2026-04-28 | 에이전트 설계 (6 STEP 파이프라인, 슬래시 커맨드 /stt) | [[plan-interview-stt-260428]] |
| plan-2part-split | 2026-05-06 | ROI 관리자 이동(Part B) + 업무요약 재설계(Part A) 분리 | [[plan-2part-split-260506]] |

## Architecture
- **STEP 0**: SKILL.md + question-spec.md + format-spec.md 로딩, directory.csv 캐싱
- **STEP 1**: interview_STT/*.txt 글로빙 + 미처리 파일 식별
- **STEP 2**: 파일명 파싱 → directory.csv 사번 lookup (동명이인 시 사용자 disambiguation)
- **STEP 3**: STT 원문 Read + ISO8601 시각 추출
- **STEP 4**: 5질문 × 최대 3탭(기본/심화/꼬리) 의미 기반 매핑
- **STEP 5**: JSON 직렬화 → 파일명 결정 → Write
- **STEP 6**: 스키마 검증 + 원본 보존 확인 + 완료 보고
