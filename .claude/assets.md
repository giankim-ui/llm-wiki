---
description: 3국 !Report 의 .html/.jsx + raw 의 SOURCE_PACKAGE.json 을 10_RAW/assets/{국가-티커}/reports/ 로 이관. 스크리닝은 10_RAW/screening/<날짜>/ 로 분리. (!Report 는 git mv, raw 는 cp 캐시 유지) + wikilink cascade 자동 갱신
---

# /assets — Asset 파이프라인 산출물 일괄 이관

3국 분석 파이프라인 (`S-anlyz/`, `S-anlyz-kr/`, `S-anlyz-jp/`) 의 산출물을 `10_RAW/assets/<COUNTRY-TICKER>/reports/` 로 이관하고, 스크리닝 파일은 `10_RAW/screening/<날짜>/` 로 분리한다. `20_WIKI/` wikilink·`mirrors_raw` cascade 갱신 포함 (현재 깨진 가짜 `[[dashboard_260503]]` 등 자동 보정).

## 1. 소스 → 국가 prefix 매핑

| 소스 폴더 | 국가 |
|---|---|
| `<cwd>/S-anlyz/` | `US` |
| `<cwd>/S-anlyz-kr/` | `KR` |
| `<cwd>/S-anlyz-jp/` | `JP` |

## 2. 파일 분류 + 이관 규칙

### 2.1 분석 대시보드 (`!Report/<TICKER>_분석대시보드.{html,jsx}`)

- 한글 변형: `_분석대시보드`, 일본어 간체 변형: `_分析대시보드`, 한국어 회사명 포함: `_현대자동차_분석대시보드`
- **티커 추출**: 첫 `_` 앞부분 (`MOS_분석대시보드.html` → `MOS`, `088980_분석대시보드.html` → `088980`, `HMC_현대자동차_분석대시보드.html` → `HMC`)
- **날짜**: 파일 mtime → `YYMMDD` (예: 2026-05-03 → `260503`)
- **이관**: `git mv <src> 10_RAW/assets/<COUNTRY>-<TICKER>/reports/dashboard_<YYMMDD>.{html,jsx}`
- 같은 티커의 .html/.jsx 쌍 → 같은 폴더에 둘 다 이관

### 2.2 스크리닝 파일 (`!Report/{US|KR|JP}_{스크리닝|スクリーニング}_<YYYYMMDD>.html`)

- 파일명에서 YYYYMMDD 추출
- **이관**: `git mv <src> 10_RAW/screening/<YYYYMMDD>/<COUNTRY>_screening.html`

### 2.3 SOURCE_PACKAGE (`raw/<TICKER>/SOURCE_PACKAGE.json`)

- **티커**: 폴더명 그대로
- **날짜**: mtime → YYMMDD
- **이관**: **`cp`** (원본 유지 — 파이프 캐시 재사용 보존). 대상 = `10_RAW/assets/<COUNTRY>-<TICKER>/reports/SOURCE_PACKAGE_<YYMMDD>.json`

### 2.4 Skip 대상

- `raw/<TICKER>/sources/` 하위 (10-K/10-Q HTML 본문) — 파이프 캐시. vault 미러링 불필요
- `Source_Packages/` (S-anlyz/ 한정) — 레거시 구조. 사용자 명시 요청 시만 처리

### 2.5 Dup 감지 (사전 부트스트랩 손상 정리)

이관 직전 dst 폴더에 **이미 존재하는 파일**이 있으면:
1. size + mtime + (가능하면) md5 비교
2. 새 mv 대상과 동일 → "사전 부트스트랩 손상 사본" 추정
3. **AskUserQuestion** 으로 사용자 확인 → "삭제 / 보존 / 이름 변경"
4. 동일하지 않으면 dst basename 에 `-v2` suffix 부여하여 충돌 회피

## 3. 충돌 처리

동일 dst 경로 (예: `dashboard_260503.html` 이미 존재) 시 → `dashboard_260503-v2.html` 식 suffix 부여.

## 4. 실행 절차

### 4.1 Pre-flight: 변환 맵 수집
1. 3국 `!Report/` Glob → 대시보드 파일 + 스크리닝 파일 분리
2. 3국 `raw/<TICKER>/SOURCE_PACKAGE.json` Glob
3. 각 파일에 분류 규칙 적용 → 변환 맵:
   ```
   [(src_path, dst_path, op: "mv"|"cp", old_basename, new_basename), ...]
   ```
4. mtime 추출 (Bash `stat` 또는 `ls -la`)

### 4.2 Pre-flight: wikilink 영향 스캔

다음 패턴을 `20_WIKI/**/*.md` 에서 Grep (각 자산별):
- `\[\[<TICKER>_분석대시보드\]\]`, `\[\[<TICKER>_분석대시보드\.html\]\]`, `\[\[<TICKER>_분석대시보드\.jsx\]\]`
- `\[\[<TICKER>_分析대시보드\.html\]\]` 등 변형 (JP 간체)
- `\[\[<HMC>_현대자동차_분석대시보드\]\]` (KR 한글 포함)
- **현재 가짜 mirrors_raw 패턴** (자동 보정 대상):
  - `\[\[dashboard_260503\]\]`, `\[\[dashboard_260503\.html\]\]`, `\[\[dashboard_20260503_v2\.html\]\]`
- **folder link 위반 (자동 수정 대상)**: `\[\[10_RAW/.+/\]\]` 또는 `\[\[10_RAW/assets/.+\]\]` 형태로 폴더 가리키는 케이스

각 wiki 파일 + line + 매칭 패턴 수집.

### 4.3 사용자 보고 (실행 전)
```
[/assets] 이관 계획
- !Report 대시보드: N개 (mv) — US=X, KR=Y, JP=Z
- 스크리닝 파일: M개 (mv) → 10_RAW/screening/
- SOURCE_PACKAGE.json: P개 (cp, 원본 보존)
- skip: sources/ 폴더 + Source_Packages/

Wikilink cascade 영향:
- 자산별 raw 파일명 변경: <TICKER>_분석대시보드.* → dashboard_<YYMMDD>.*
- 영향 wiki 파일: Q개 (US-MOS/, US-MO/, ..., comparisons/raw-materials-druckenmiller-260505.md)
- 자동 보정 대상 (현재 가짜 mirrors_raw): R개
- folder link 위반 수정: S개

진행할까?
```

사용자 확인 받기.

### 4.4 실행
1. 타겟 디렉토리 일괄 생성:
   ```bash
   mkdir -p 10_RAW/assets/<COUNTRY>-<TICKER>/reports
   mkdir -p 10_RAW/screening/<YYYYMMDD>
   ```
2. **dup 감지** (§2.5): dst 폴더에 이미 존재하는 파일 size+mtime 비교 → 동일 시 AskUserQuestion 으로 삭제/보존 결정
3. 대시보드: `git mv` 순차
4. 스크리닝: `git mv` 순차
5. SOURCE_PACKAGE: `cp` 순차 (원본 보존) → cp 직후 자동 `git add 10_RAW/assets/<COUNTRY>-<TICKER>/reports/SOURCE_PACKAGE_<YYMMDD>.json`
6. **wiki 폴더 자동 git add** (사용자 승인 정책, 260505): `20_WIKI/assets/<COUNTRY-TICKER>/` 가 untracked 이면 `git add 20_WIKI/assets/<COUNTRY-TICKER>/` 자동 실행

### 4.5 Post-flight: Wikilink Cascade
영향 wiki 파일 일괄 갱신 (Edit tool, replace_all: true 가능 케이스 위주):

**a) 본문/표 wikilink**:
- `[[<TICKER>_분석대시보드]]` → `[[dashboard_<YYMMDD>]]`
- `[[<TICKER>_分析대시보드.html]]` → `[[dashboard_<YYMMDD>.html]]`
- 자산별로 mtime 다르므로 정확한 매핑 필요

**b) frontmatter mirrors_raw 자동 보정** (현재 가짜 통일 날짜):
- `US-MOS/US-MOS.md`, `synthesis.md`: 현재 `[[dashboard_260503]]` → MOS 실제 mtime 기반 새 값
- `US-MO/`, `US-OXY/`, `US-RIO/`, `US-TGT/`, `US-PFE/`, `US-PLTR/`, `JP-5401/`, `JP-5411/`, `KR-HMC/` 동일 처리
- `US-MSFT/`: `[[dashboard_20260503_v2.html]]` → 실제 mtime 기반 (MSFT 는 raw에 SOURCE_PACKAGE.json만 있고 .html dashboard 없음 → 이 케이스는 사용자에게 확인 필요할 수 있음. 변환 맵 단계에서 검토)

**c) folder link 위반 수정**:
- `concepts/mirror-principle.md:24` 의 `[[10_RAW/assets/US-MSFT/]]` → 실제 raw 파일 wikilink로. 모호하면 가장 최근 mtime 파일 또는 AskUserQuestion

### 4.6 Post-flight 검증
1. 모든 자산 wiki (`20_WIKI/assets/<COUNTRY-TICKER>/*.md`) 의 `mirrors_raw` 추출 → 실제 `10_RAW/assets/<COUNTRY-TICKER>/reports/` 내 파일 존재 확인
2. `comparisons/raw-materials-druckenmiller-260505.md` 의 모든 raw wikilink 검증
3. `concepts/mirror-principle.md` folder link 0건 확인
4. 미해결 wikilink 보고 — 0건이어야 함

### 4.7 LOG 갱신
`20_WIKI/assets/assets-LOG.md` append:
```
## [YYYY-MM-DD HH:MM] ingest | bulk raw migration via /assets (N files mv + P files cp, M wikilinks cascaded, R fake mirrors_raw corrected)
- raw read 좌표: none (이관만)
- 국가별: US=X, KR=Y, JP=Z
- 스크리닝: <YYYYMMDD> 파일 K개
- cascade 갱신 wiki: Q개
- folder link 위반 수정: S개
```

루트 `LOG.md` 에도 highlight append.

### 4.8 종료 보고
```
[/assets] 완료
- 대시보드 mv N개 (US=X, KR=Y, JP=Z)
- 스크리닝 mv M개 → 10_RAW/screening/
- SOURCE_PACKAGE cp P개 (원본 보존됨, 파이프 캐시 무영향)
- skip: sources/ 폴더 (파이프 캐시), Source_Packages/ (레거시)
- Wikilink cascade Q개 wiki 파일 갱신
- 자동 보정 가짜 mirrors_raw R개
- folder link 위반 수정 S개
- 검증: 미해결 0건
- LOG 항목 추가
```

## 5. 주의사항

- 파이프라인 영향: `!Report/*.{html,jsx}` mv 무영향 (다음 분석 시 새로 작성). `raw/<TICKER>/SOURCE_PACKAGE.json` 원본 유지로 캐시 보존
- US-MSFT 특이 케이스: `S-anlyz/!Report/` 에 MSFT 대시보드 부재 (현재 wiki 의 `[[dashboard_20260503_v2.html]]` 는 출처 불명) → cascade 단계에서 사용자 확인 필요
- KR `088980` ticker: 파일명 그대로 신뢰 (사용자가 `005380` 으로도 언급 가능 — 보고에 명시)
- KR `HMC_현대자동차_*`: 폴더명 `KR-HMC` 로 통일 (한글 부분 무시)
- git mv 실패 시 즉시 중단 + 부분 진행 상태 보고
- 새 세션에서도 동일 동작하도록 본 명령 본문 self-contained
