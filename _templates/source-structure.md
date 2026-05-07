---
type: source-structure
domain: <domain>
source: <source-type>
date: <% tp.date.now("YYYY-MM-DD") %>
status: stable
---

# <Source Name> 구조 가이드

## 목적
LLM이 이 source 파일 read 전 좌표(연도 × Item/섹션)를 정하기 위한 참조. Raw Reading Discipline 운영 전제.

## 파일 형태
- 포맷: <HTML|JSON|PDF|MD>
- 일반 위치: `10_RAW/...`
- 평균 토큰 규모: 

## 섹션·Item 구조
| Item/섹션 | 1줄 요약 | 우리 분석 활용 |
|---|---|---|

## 좌표 통보 형식 예시
- "<source> <year/version> <Item/section> only"

## 관련 Concept/Theme 백링크
<!-- [[../concepts/...]] -->
