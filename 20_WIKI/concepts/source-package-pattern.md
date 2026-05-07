---
type: concept
date: 2026-05-05
status: draft
tags:
  - raw-preservation
  - source-package
  - token-economy
related:
  - raw-reading-discipline
  - mirror-principle
---

# Source Package Pattern

## Definition
SOURCE_PACKAGE.json은 PHASE 2에서 supervisor가 생성하는 SEC 파일링 URL 레지스트리다. 실제 데이터를 담지 않고 "어디서 가져올지"의 좌표(CIK, 10-K/10-Q URL, transcript URL)만 기록한다. 실제 fetch된 데이터는 `sources/` 하위에 별도 보존된다.

## Two-Layer Preservation

| 레이어 | 파일 | 역할 |
|---|---|---|
| 수집 지도 | `SOURCE_PACKAGE.json` | URL 인덱스. "다음에 어디서 가져오나" |
| 수집 내용 | `sources/sec_10k/*.html`, `sources/investing/*.json` | 실제 fetch된 원천 데이터 |

investing.com 데이터(consensus/dividends/technical)는 SOURCE_PACKAGE 계약 외부 경로 — `sources/investing/`에 별도 보존된다.

## Why It Matters (In This Vault)
재분析 시 PHASE 2(URL 탐색)를 생략할 수 있다. SOURCE_PACKAGE가 있으면 supervisor는 바로 PHASE 4(에이전트 실행)로 진입 가능. 토큰 절감 + URL 탐색 오류 방지.

PHASE 2 완료 직후 SOURCE_PACKAGE.json 저장이 누락되면 PHASE 4 진입 불가 — 파이프라인 게이트 역할도 겸한다.

## What Does NOT Belong in raw/
에이전트 출력 JSON(performance/governance/strategy-risk/auditor)은 sources에서 재생성 가능하므로 raw/ 저장 불필요. MOS 폴더에 정책 위반으로 에이전트 JSON이 혼재 중(미정리).

## Data Points
| Date | Context | Observation |
|---|---|---|
| 2026-05-02 | raw-data-preservation v1.0 | SOURCE_PACKAGE 패턴 최초 설계 |
| 2026-05-05 | S-anlyz US/JP 운영 | `raw/MSFT`, `raw/5411` 적용 확인. KR는 미적용 |
| 2026-05-05 | query | URL 레지스트리 vs 실제 데이터 층위 구분 명문화. MOS 정책 위반 발견 |

## Related Concepts
- `[[raw-reading-discipline]]`
- `[[mirror-principle]]`

## Sources
- `[[PLAN_raw-data-preservation]]`
