---
title: S-anlyz SEC API 통합 작업 인계
date: 2026-05-01
tags: [handoff, sec-api, integration]
---

# HANDOFF — S-anlyz SEC API 통합 작업 인계

**작성일**: 2026-05-01  
**작업 디렉토리**: `C:\Users\nayut\!claudeProject\S-anlyz`  
**참고 모델**: `C:\Users\nayut\!claudeProject\S-anlyz-jp\archive\PLAN_edinet-api-integration.md`

---

## 시도한 것

- `S-anlyz-jp\archive\PLAN_edinet-api-integration.md` 파일 내용 확인 (JP 파이프라인의 EDINET API 통합 계획서)
- `S-anlyz` 디렉토리 구조 탐색 시도 → 사용자 중단으로 미완료
- 세션 종료 전 실제 파일 변경 없음

---

## 성공한 것

- JP 플랜 문서 (`PLAN_edinet-api-integration.md`) 내용 파악 완료
  - EDINET API 1순위 사용, WebFetch 2순위, Chrome 최후 구조 확인
  - `data-collector-agent.md`, `CLAUDE.md`, `GOTCHAS.md` 3개 파일 수정 패턴 확인
  - SOURCE_PACKAGE `financials_api` 블록 스키마 확인
- SEC API 키 발급 확인: `c4bee0d5ceba586113c5efd5834595365762dbdc18e79948b66be763034b9941`

---

## 실패한 것 / 막힌 것

- `S-anlyz` 디렉토리 구조 탐색 미완료 (Agent 실행이 사용자에 의해 차단됨)
- `S-anlyz/.claude/agents/` 하위 에이전트 파일 목록 미확인
- `S-anlyz/CLAUDE.md` 현재 내용 미확인
- 실제 파일 수정 작업 미착수

---

## 다음 단계

### 0. 사전 준비 — SEC API 키 등록

`S-anlyz/.claude/settings.local.json` 에 아래 항목 추가:
```json
{
  "env": {
    "SEC_API_KEY": "c4bee0d5ceba586113c5efd5834595365762dbdc18e79948b66be763034b9941"
  },
  "permissions": {
    "allow": [
      "Bash(curl *data.sec.gov*)",
      "Bash(curl *efts.sec.gov*)"
    ]
  }
}
```

> SEC EDGAR API 엔드포인트:
> - `https://data.sec.gov/submissions/CIK{cik}.json` — 기업 제출 목록
> - `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` — 재무 데이터 (XBRL)
> - `https://efts.sec.gov/LATEST/search-index?q=...` — 전문 검색

---

### 1. S-anlyz 구조 파악

아래 경로를 먼저 확인:
```
S-anlyz/CLAUDE.md
S-anlyz/.claude/agents/          ← 기존 에이전트 파일 목록 확인
S-anlyz/Source_Packages/         ← 기존 SOURCE_PACKAGE 샘플 확인
S-anlyz/src/                     ← 파이프라인 소스 확인
```

---

### 2. `data-collector-agent.md` 신설 (핵심)

JP 패턴 (`S-anlyz-jp/.claude/agents/data-collector-agent.md`) 을 fork 하여  
`S-anlyz/.claude/agents/data-collector-agent.md` 생성.

**Source Allowlist 우선순위**:
```
1순위: SEC EDGAR API (data.sec.gov) — Bash curl (SEC_API_KEY, User-Agent 헤더 필수)
2순위: WebFetch (finance.yahoo.com · macrotrends.net · 기업 IR · SEC.gov 직접)
최후:  Chrome (SEC 전자공시 UI · 기업 IR 동적 페이지)
```

**Step I-1: CIK 조회**
```bash
# ticker → CIK 매핑
curl -s "https://efts.sec.gov/LATEST/search-index?q=%22TICKER%22&dateRange=custom&startdt=2020-01-01&enddt=2025-12-31&forms=10-K" \
  -H "User-Agent: YourName yourname@email.com"

# 또는 company_tickers.json (전체 매핑 파일)
curl -s "https://www.sec.gov/files/company_tickers.json" \
  -H "User-Agent: YourName yourname@email.com"
```

**Step I-2: 10-K 제출 목록 조회**
```bash
CIK_PADDED=$(printf "%010d" $CIK)
curl -s "https://data.sec.gov/submissions/CIK${CIK_PADDED}.json" \
  -H "User-Agent: gian.kim.pmo@gmail.com"
```

**Step I-3: XBRL 재무 데이터**
```bash
curl -s "https://data.sec.gov/api/xbrl/companyfacts/CIK${CIK_PADDED}.json" \
  -H "User-Agent: gian.kim.pmo@gmail.com"
# us-gaap.Revenues, us-gaap.NetIncomeLoss, us-gaap.OperatingIncomeLoss 등 추출
```

**SOURCE_PACKAGE `financials_api` 블록 추가**:
```json
"financials_api": {
  "source": "data.sec.gov",
  "fetch_method": "api",
  "cik": "",
  "annual_by_fy": {
    "2024": {
      "revenue_usd": null,
      "op_income_usd": null,
      "net_income_usd": null,
      "op_cf_usd": null,
      "eps_diluted": null,
      "form_type": "10-K",
      "accession_number": ""
    }
  }
}
```

---

### 3. `CLAUDE.md` 수정

**Source Allowlist 테이블 업데이트** (§7.2 또는 동등 섹션):
```
| 순위 | 도메인 | 방법 |
| 1 | data.sec.gov · efts.sec.gov | Bash curl (SEC_API_KEY + User-Agent) |
| 2 | finance.yahoo.com · macrotrends.net · 기업IR | WebFetch → Chrome |
| 최후 | sec.gov 전자공시 UI | Chrome 전용 |
```

**환경변수 섹션 추가**:
- `SEC_API_KEY`: `.claude/settings.local.json`에 설정됨
- User-Agent 헤더 필수: `gian.kim.pmo@gmail.com`

**절대 준수 원칙 추가**:
- `API First`: SEC EDGAR API 가용 항목은 반드시 API 먼저. WebFetch/Chrome 우선 시도 금지.

---

### 4. `GOTCHAS.md` 수정 또는 신설

신규 GOTCHA 항목:
```
G-US-001: SEC EDGAR API User-Agent 헤더 필수
  User-Agent 없으면 403 반환. 반드시 "Name email" 형식으로 포함.

G-US-002: CIK 10자리 zero-padding 필수
  data.sec.gov/submissions/CIK0000012345.json — 10자리 패딩 필수.

G-US-003: ticker → CIK 매핑
  company_tickers.json 캐싱 권장. 직접 ticker로 API 조회 불가.

G-US-004: XBRL 태그명 변동
  us-gaap 태그는 기업마다 다를 수 있음 (Revenues vs RevenueFromContractWithCustomerExcludingAssessedTax).
  복수 태그 시도 후 null 처리.
```

---

### 수정 파일 목록 요약

| 파일 | 작업 |
|------|------|
| `S-anlyz/.claude/settings.local.json` | SEC_API_KEY 추가 + Bash curl 권한 |
| `S-anlyz/.claude/agents/data-collector-agent.md` | **신설** (JP fork + SEC API 로직) |
| `S-anlyz/CLAUDE.md` | Allowlist 테이블 + env 문서화 + SOURCE_PACKAGE 스키마 |
| `S-anlyz/.claude/GOTCHAS/GOTCHAS.md` (또는 동등 파일) | G-US-001~004 신규 |

---

## 참고 문서

- JP 플랜 원본: `S-anlyz-jp/archive/PLAN_edinet-api-integration.md`
- JP collector 참고: `S-anlyz-jp/.claude/agents/data-collector-agent.md`
- KR collector 참고: `S-anlyz-kr/archive/RESULT_data-collector-kr.md`
- SEC EDGAR API 공식: https://www.sec.gov/developer
