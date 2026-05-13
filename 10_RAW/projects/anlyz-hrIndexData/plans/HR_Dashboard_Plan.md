# HR Data Dashboard 재설계 Plan
## (그룹 총수·사장단 보고용 / 인사기획실 작성)

> 분석 대상: `10-RAW/DB-Report-F` 내 2023~2026년 인사위원회 PPTX 13개  
> 핵심 챕터: **「조직/인력 운영 계획 ▸ 인력 운영 계획 ▸ HR 주요 데이터 지표 리뷰」**  
> 보고 대상: 그룹 총수 및 사장단 (Top Executives / Board)  
> 보고 주체: 인사기획실 (CHO Office)  
> 작성일: 2026-05-08

---

## 0. Executive Summary (한 장 요약)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| AS-IS  현행 「HR 주요 데이터 지표 리뷰」                                    |
|   - 4~5장의 정적 표 (전사 인원·관계 인력·지원조직·인건비·NNR 대비 인건비율) |
|   - "직전연도 vs 현시점" 단순 YoY 비교                                       |
|   - 후행지표(Lagging) 100%, 선행지표(Leading) 0%                             |
|   - ISO 30414 11개 영역 중 3~4개 영역만 커버                                 | <ISO 30414 11개 영역이 뭐지?>
|   - 인사이트(So-What·권고)·예측·시나리오 부재                               |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| TO-BE  Executive HR Dashboard (12장 구성)                                    |
|   1) Hero KPI 6대 + BU Heatmap     2) 전사 Workforce Composition            |
|   3) Productivity & Cost Linkage   4) BU 5축 신호등(Heatmap)                |
|   5)~7) 핵심 BU 3개 Drill-down     8) Talent Risk (Regrettable Attrition)   |
|   9) Engagement → Profit Linkage   10) Span of Control 최적화                |
|   11) 외부인력(도급·파견·특고) 효율 12) Action Watchlist + KPI Glossary      |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| 핵심 변화 3가지 (Bersin · Deloitte · McKinsey · ISO 30414 기반)              |
|  ① YoY 단순 비교 → "Plan vs Actual vs Industry Best-in-Class" 3-way 비교    |
|  ② Headcount/Cost 위주 → Productivity·Risk·Engagement·Capability 6대 축    |
|  ③ "현황만" → "현황 + 원인 + 재무영향(EBIT) + 권고 액션" 4-단 구조           |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

**기대 효과(글로벌 권위 출처 근거)**
- McKinsey OHI: 조직 건강도 상위 25% 기업, 3배 높은 TSR (Total Shareholder Return)
- Gallup Q12 메타: 몰입 상위 25% BU, 23% 더 높은 수익성
- Deloitte/Visier: 인력 분석 도입 시 비즈니스 생산성 +20%
- ISO 30414 (2018→2025 개정): 11개 영역·69개 표준 지표 — 글로벌 자본시장 공시 표준

---

## 1. 현행 보고(As-Is) 심층 진단

### 1-1. 추출 결과 — 13개 PPTX 챕터 구성 패턴

| 보고 회차 | 챕터 슬라이드 수 | 주요 KPI 페이지 구성 |
|---|---|---|
| 2023.02 | 6 | 도입기 (인원·관계인력 위주) |
| 2023.05 | 13 | 확장기 (생산성·인건비율 추가) |
| 2023.08 | 10 | (동일 패턴) |
| 2023.12 | 5 | 연말 결산형 |
| 2024.01 | 4 | 압축형 |
| 2024.05 | 14 | **HCROI 도입 시점** |
| 2024.09 | 11 | (HCROI 동종사 비교 강화) |
| 2024.12 | 6 | (재정착) |
| 2025.02 | 11 | 장애인고용·인건비 결산 추가 |
| 2025.05 | 9 | (정기 패턴 안착) |
| 2025.09 | 7 | 본문 4장으로 압축 |
| 2025.12 | 8 | 본문 4장 + NNR/CEBIT 표 |
| 2026.02 | 4 | 본문이 차트·이미지화되어 텍스트 추출 한계 |

### 1-2. 현행에서 일관 사용 중인 KPI

| # | KPI | 사용 빈도 | 비교 방식 | 분류 |
|---|---|---|---|---|
| 1 | 전사 정규직 인원 (TO 대비) | 13/13 | YoY + Plan 대비 | Lagging |
| 2 | 계약직 / 도급·파견 / 특수고용 인원 | 12/13 | YoY | Lagging |
| 3 | 지원조직 비중 (전사 대비 %) | 12/13 | YoY (목표 10% 이내) | Lagging |
| 4 | 예산 대비 인건비 사용률 | 13/13 | Plan 대비 | Lagging |
| 5 | NNR 대비 인건비율 (Labor Cost % of Revenue) | 9/13 | 산업 평균 대비 | **Mixed** |
| 6 | 인당 평균 인건비 | 5/13 | YoY | Lagging |
| 7 | HCROI (Human Capital ROI) | **2/13** | 동종사·법인별 | **Strategic** |
| 8 | 장애인 고용 부담금 | 4/13 | 의무 대비 | Compliance |

### 1-3. 한계점 (개선 포인트 8가지)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
①  Lagging 일변도   |  Headcount/Cost는 결과치 — "왜 그런가, 어디로 갈 것인가" 부재
②  YoY만 비교       |  Plan·Industry·Best-in-class 3-way 비교 부재
③  단편 KPI         |  ISO 30414 11개 영역 중 3~4개만 — 7개 영역(다양성·승계·역량
                     |  ·안전·이직질·조직문화·외부인력 효율) 사실상 공백
④  재무 연결 약함   |  HCROI는 12·연말에만, 분기 운영 의사결정에는 미연결
⑤  So-What 부재     |  표만 있고 "그래서 어떤 의사결정이 필요한가" 권고 없음
⑥  예측 부재        |  현재까지 치적만 — 향후 분기·연말 forecast 미제시
⑦  내부 사일로      |  부문/SBU/MBU 표만 — Cross-BU 비교 신호등 없음
⑧  외부인력 가시성  |  도급·파견·특고·로하미 4,257명+3,345명, 정규직(6,846)에 육박
                     |  하나 효율·리스크 KPI 없음
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

---

## 2. 글로벌 선도 다국적 기업 벤치마크

### 2-1. 표준 / Framework

| 출처 | 핵심 메시지 | 풀무원 적용 시사점 |
|---|---|---|
| **ISO 30414:2018 / 2025 개정** | 11개 인적자본 영역, 69개 표준 지표. 내·외부 보고 글로벌 기준. | 현행 3~4개 영역 → 11개 영역 단계적 확장 |
| **Deloitte CHRO Key Metrics** | CHRO 보고 4계층: ① 기본 인력 인지 ② 인재 영입 ③ 몰입·생산성 ④ 리더십·문화 | 분기 보고를 4계층 구조로 재편 |
| **McKinsey HR Monitor 2025** (1,925개사 조사) | "Strategic Workforce Planning이 가장 미흡한 영역" — 5대 트렌드 1순위 | 분기 단순 현황 → 시나리오 기반 SWP 도입 |
| **McKinsey OHI** (2,500+개사, 8M 응답자) | 조직 건강도 상위 25%, **TSR 3배·재무성과 3배** | OHI 또는 동등한 조직건강 지수 도입 |
| **Gallup Q12 Meta-Analysis** (347개사, 736 연구) | 몰입 상위 25% BU, **수익성 +23%, 매출과 가장 강한 상관** | 몰입 ↔ NNR/CEBIT 연결 모델링 |
| **Bersin / Deloitte People Analytics** | 분석 기반 의사결정 문화 도입 시 **생산성 +20%** | 대시보드 + decision rights 동시 설계 |
| **Visier × Gartner Magic Quadrant** | 머신러닝(25~40개 변수) 이직 예측 정확도 87% | Phase 3에서 Predictive Attrition 도입 |

### 2-2. Best-in-Class 기업 사례

| 기업 | 실천 | 출처 |
|---|---|---|
| **Google (People Operations)** | 데이터 기반 의사결정 문화. 연 인당 매출 ≈ $1M, 인당 영업이익 ≈ $200K. 예측·What-if 분석 일상화 | peopleHum / Excellence in People Analytics |
| **IBM Workforce Mgmt Initiative (2003~)** | "Talent Supply Chain" 개념 — 인재 모빌리티·벤더·학습·자원 통합 DB | HR Tech Central / scribd |
| **Microsoft** | 예측 분석으로 Disengagement 패턴 식별 → 개인화 멘토링 | Microsoft Internal People Analytics |
| **Unilever** | 웰빙 투자 $1당 ROI $2.50 입증. 게이미피케이션 기반 채용 평가 | Effectory / People Analytics 사례 |
| **Nestlé "4B Strategy"** | Buy / Build / Borrow / Bot — 스킬 기반 SWP, 270K 인원 글로벌 운영 | myHRfuture · Nestlé Head of People Analytics |
| **Siemens** | "160년 만에 전 직원 성과 데이터 단일 통합" — 인재검색·승계 분석 고도화 | Siemens HR Strategy Case |

### 2-3. 글로벌 표준 KPI 벤치마크 (출처별 임계치)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| KPI                        |  벤치마크 / Best-in-Class                          |
|----------------------------|----------------------------------------------------|
| Revenue per Employee       |  Cross-industry $350K / 제조 $200~500K / Google $1M |
| Labor Cost % of Revenue    |  제조 14% / 서비스 25% / SaaS 20~30% / 의료 40~50% |
| Voluntary Turnover (전체)  |  글로벌 제조 8~12% / 자발 best-in-class <8%        |
| First-Year Attrition       |  Best-in-class < 10~15%                            |
| Internal Mobility Rate     |  20~30% (강한 조직 기준)                          |
| Span of Control (관리폭)    |  표준 6~10 / 단순업무 10~15 / 복잡업무 3~6        |
| Successor Coverage Ratio   |  Critical Position당 Ready Successor ≥ 3명        |
| Bench Strength (Net)       |  Gross 87% vs Net 27% 사례 — Net 기준 점검 필요   |
| Quality of Hire (QoH)      |  Internal Mobility 92 / Referral 88 / Job board 75|
| Replacement Cost           |  연봉의 50~200% (C-Suite 213%, 신입 30~50%)       |
| 몰입 상위 25% 효과          |  수익 +23%, 안전사고↓, 결근↓ (Gallup Q12)         |
| 조직건강 상위 25% 효과      |  TSR 3배, 재무성과 3배 (McKinsey OHI)             |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

---

## 3. KPI 체계 재설계 — 6대 축, 24개 핵심 KPI

### 3-1. 설계 원칙

1. **CEO Test (5초 룰)**: 사장단이 5초 안에 핵심 메시지를 읽을 수 있어야 함 (Qlik / Bersin)
2. **재무 연결**: 모든 KPI 옆 "EBIT 영향도" 또는 "재무 신호"를 병기
3. **3-way 비교**: Plan / Actual / Industry Best-in-Class — YoY는 보조 표시
4. **선행+후행 균형**: 6대 축 각각 선행지표 1개 이상 의무 포함
5. **ISO 30414 정합성**: 각 KPI를 ISO 11개 영역과 매핑

### 3-2. 6대 KPI 축 (24개 KPI)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  A. Workforce & Cost (인력·비용 / Lagging)                                  |
|     ┃ A1 Total Workforce (정·계·도급·파견·특고 통합)                         |
|     ┃ A2 Labor Cost % of Revenue (NNR 대비 인건비율)        ← 현행 사용     |
|     ┃ A3 Total Cost of Workforce (TCOW)  ← 외부인력 포함 신규               |
|     ┃ A4 Cost per Hire (CPH)                                                |
|----------------------------------------------------------------------------|
|  B. Productivity & Financial Linkage (생산성·재무연결 / Mixed)              |
|     ┃ B1 Revenue per FTE (NNR/FTE)                                         |
|     ┃ B2 Profit per FTE (CEBIT/FTE)                                        |
|     ┃ B3 Human Capital ROI (HCROI)        ← 현행 4분기에만 → 분기 상시화   |
|     ┃ B4 Human Capital Value Added (HCVA)                                  |
|----------------------------------------------------------------------------|
|  C. Talent Risk (인재 리스크 / Leading)                                     |
|     ┃ C1 Voluntary Turnover Rate                                           |
|     ┃ C2 Regrettable Attrition (핵심인재 자발 이직률)  ← Spring Health/AIHR|
|     ┃ C3 First-Year Attrition (신규입사자 1년 이탈률)                       |
|     ┃ C4 Internal Mobility Rate                                            |
|----------------------------------------------------------------------------|
|  D. Engagement & Culture (몰입·문화 / Leading)                              |
|     ┃ D1 Engagement Index (Q12 / OHI / eNPS 중 1택)                         |
|     ┃ D2 Manager Effectiveness (Span × 부하 만족도)                         |
|     ┃ D3 Absenteeism Rate                                                  |
|     ┃ D4 Safety - LTIFR (Lost Time Injury Frequency Rate)                  |
|----------------------------------------------------------------------------|
|  E. Capability & Future Readiness (역량·미래 준비 / Leading)                |
|     ┃ E1 Critical Skills Coverage (AI/Digital/글로벌 등)                    |
|     ┃ E2 Training Hours / Spend per FTE                                    |
|     ┃ E3 Quality of Hire (QoH)                                             |
|     ┃ E4 Successor Coverage Ratio (Net Bench Strength)                     |
|----------------------------------------------------------------------------|
|  F. Diversity & Compliance (다양성·컴플라이언스 / Compliance)               |
|     ┃ F1 Female / Diverse Leadership %                                     |
|     ┃ F2 Disability Employment Rate                  ← 현행 사용           |
|     ┃ F3 외부인력 의존도 (도급·파견 비중)                                    |
|     ┃ F4 Generational Mix & Pay Equity Index                               |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### 3-3. 도입 단계 (Phasing)

| Phase | 시점 | KPI 추가 | Source |
|---|---|---|---|
| Phase 0 (현행) | 2026.Q1 | A1·A2·F2 (3개) | 운영 중 |
| Phase 1 (Quick Win) | 2026.Q2~Q3 | A3·A4·B1·B2·B3·B4·C1·C3 (8개 추가, 누적 11개) | ERP+급여+채용DB 즉시 산출 가능 |
| Phase 2 (분석) | 2026.Q4~2027.Q1 | C2·C4·D1·D2·D3·D4·F1·F3·F4 (9개 추가, 누적 20개) | 몰입조사/안전DB/조직개편 정합 |
| Phase 3 (예측) | 2027.Q2~ | E1·E2·E3·E4 (4개 추가, 24개 완성) + Predictive Attrition | HCM AX 2단계 연계 |

---

## 4. Executive HR Dashboard 구조 — 12장 구성

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Section 1. WHAT (전사 현황 — 인원·인건비)                  P.1~P.3      │
├─────────────────────────────────────────────────────────────────────────┤
│ Section 2. WHERE (사업단위별 현황·특이사항)                P.4~P.7      │
├─────────────────────────────────────────────────────────────────────────┤
│ Section 3. SO-WHAT (재무 개선 인사이트)                    P.8~P.11     │
├─────────────────────────────────────────────────────────────────────────┤
│ Section 4. NEXT (액션 워치리스트 + 정의 사전)              P.12          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. 페이지별 ASCII 목업 (총 12장)

### P.1 — Executive Cover (Hero KPI 6대 + BU Heatmap)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| 풀무원 그룹 HR Dashboard ─ 2026.Q1                          (인사기획실) |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| HERO KPI (Plan vs Actual vs Industry Best-in-Class)                     |
|                                                                         |
|  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────┐  |
|  | Total     | | Labor     | | NNR       | | HCROI     | | Volunt.  |  |
|  | Workforce | | Cost %    | | / FTE     | | (HC ROI)  | | Turnover |  |
|  |  8,366    | |  15.6%    | | ₩410M     | | 1.18×     | |  9.4%    |  |
|  | ▲ 적정    | | ▼ 양호    | | ▲ 개선    | | ▼ 동종    | | ▲ 주의   |  |
|  | (TO99.3%) | | (제조14%) | | (PL+3%)   | | 1.73 미달 | | ↑ vs Q4  |  |
|  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └──────────┘  |
|  ┌──────────┐                                                            |
|  | Engage.  |    범례  ●양호  ◐주의  ▲경고                              |
|  | Index    |    배경 색 — Plan 대비 Δ%                                  |
|  | 측정전 - |                                                            |
|  | Phase2 → |                                                            |
|  └──────────┘                                                            |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| BU Heatmap (5축 신호등)   ●양호 ◐주의 ▲경고                            |
|              | A.인력 | B.생산성 | C.리스크 | D.몰입 | F.컴플 | 종합 |  |
|  식품통합MBU |   ●    |    ●     |    ◐     |    ◐    |   ●   |  ●   |  |
|  샘물 SBU    |   ●    |    ●     |    ●     |    ◐    |   ●   |  ●   |  |
|  다논 SBU    |   ●    |    ●     |    ●     |    ◐    |   ●   |  ●   |  |
|  NA MBU      |   ◐    |    ▲     |    ▲     |   N/A   |   ●   |  ▲   |  |
|  중국 MBU    |   ●    |    ●     |    ◐     |   N/A   |   ●   |  ●   |  |
|  일본 SBU    |   ▲    |    ▲     |    ▲     |   N/A   |   ●   |  ▲   |  |
|  건강케어혁신|   ●    |    ▲     |    ◐     |    ◐    |   ●   |  ◐   |  |
|  FNC MBU     |   ●    |    ●     |    ◐     |    ◐    |   ●   |  ●   |  |
|  올가 SBU    |   ●    |    ◐     |    ●     |    ◐    |   ●   |  ◐   |  |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| 핵심 메시지 (총 3줄, 사장단 5초 가독)                                    |
|  · NA·일본은 인건비율·HCROI 모두 산업평균 미달 — 재무 회복 옵션 필요    |
|  · 자발 이직률 9.4%로 분기 상승 (Q4 8.1%) — 핵심인재 이탈 점검 필요     |
|  · FNC 사업장 확장으로 외부인력(도급) +250 — 적정성 후속 검토 권고      |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.2 — 전사 Workforce Composition (인력 구성 풀뷰)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.2  전사 인력 구성 (Workforce Composition)               2026.Q1       |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  내부인력  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8,366명          |
|   정규직  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6,846  (TO99.3%)               |
|   계약직  ━━━━━━━━━━━ 1,520                                            |
|                                                                         |
|  외부인력  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 7,602명     |
|   도급    ━━━━━━━━━━ 1,263                                              |
|   파견    ━━━━━━━━━━━━━━━━━━━━━━ 2,994                                  |
|   특수고용 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3,345                       |
|                                                                         |
|  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ |
|   총 노출 인력 15,968명  (내부 52% : 외부 48%)                          |
|   외부인력 의존도가 1:1에 근접 — 사업장 확장(FNC)·녹즙 채널이 주 동인  |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  부문별 정규직 (Stacked) ─ 경영간부 / 운영직 / 현장직                   |
|                          0    1k    2k    3k    4k                      |
|  국내식품제조유통       ┃ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░ 2,442                  |
|  해외식품제조유통       ┃ ▓▓▓▓▓▓░░░░░░░░░░░░░░░  882                    |
|  건강케어               ┃ ▓░░░░░░░░░░░░░░░░░░░░  155                    |
|  식품서비스(FNC)        ┃ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░ 2,424                  |
|  Corporate              ┃ ▓▓▓▓▓░░░░░░░░░░░░░░░░  708                    |
|  올가 SBU               ┃ ▓░░░░░░░░░░░░░░░░░░░░  235                    |
|                                                                         |
|  Insight: FNC가 식품제조와 인원 규모 동급 — 인력 운영 정책의 분리 검토  |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.3 — Productivity & Cost Linkage (생산성·재무 연결)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.3  생산성·재무 연결 (Productivity & Cost Linkage)        2026.Q1      |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  Plan vs Actual vs Industry Best-in-Class (3-Way)                       |
|                                                                         |
|  KPI                  | Plan   | Actual | YoY   | Industry | Δ vs IND |
|  ─────────────────────┼────────┼────────┼───────┼──────────┼────────── |
|  NNR / FTE            | ₩400M  | ₩410M  | +3%   | ₩520M*   | -21%     |
|  CEBIT / FTE          | ₩12M   | ₩7.2M  | -8%   | ₩18M*    | -60%     |
|  HCROI (B3)           | 1.30   | 1.18   | +0.03 | 1.73**   | -32%     |
|  Labor Cost % (A2)    | 14.5%  | 15.6%  | -0.2p | 14% 제조 | +1.6p    |
|  TCOW % (A3 신규)     | 18.0%  | 19.2%  |  N/A  | N/A       | -        |
|  Cost per Hire (A4)   | ₩6.0M  | ₩7.4M  | +12%  | $4,700***| 환산 비교|
|                                                                         |
|  *  damodaran 산업평균(식품가공) / **24년 4분기 동종사 평균             |
|  *** SHRM Benchmark (글로벌 평균)                                        |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  HCROI 추세 (4년)                          ▲동종평균  ●풀무원          |
|     2.0 ┤                                                                |
|     1.8 ┤              ▲────▲────▲────▲                                 |
|     1.6 ┤                                                                |
|     1.4 ┤                                                                |
|     1.2 ┤    ●────●────●────●                                            |
|     1.0 ┤                                                                |
|         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                     |
|         2023        2024        2025        2026.Q1                      |
|                                                                         |
|  Insight: HCROI gap -0.55 = 약 ₩1,500억 잠재 EBIT 손실 (Phase 1 모델)   |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.4 — BU 5축 신호등 + 분기 변동

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.4  사업단위별 5축 Heatmap & 특이사항                     2026.Q1      |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|                  | A      | B      | C      | D      | F      | 특이 |  |
|                  | 인력   | 생산성 | 리스크 | 몰입   | 컴플   | 사항 |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  식품통합 MBU    | TO-44  | 14.6→  | 자발↑  | -      | 100%   |  ◐   |  |
|                  |        | 14.0%  | 8.9%   |        | 장애인 |      |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  샘물 SBU        | TO+0   | 14.3%  | 7.2%   | -      | 미달2  |  ●   |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  다논 SBU        | TO-5   | 11.5→  | 6.5%   | -      | -      |  ●   |  |
|                  |        | 9.6%↓  |        |        |        |      |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  NA MBU          | TO-23  | 16.1→  | 11.5%  | N/A    | -      |  ▲   |  |
|                  |        | 18.3%↑ | (해외) |        |        | 적자 |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  중국 MBU        | TO-5   | 11.7→  | 6.0%   | N/A    | -      |  ●   |  |
|                  |        |  9.1%  |        |        |        |      |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  일본 SBU        | TO-72  | 19.5→  | 12.8%  | N/A    | -      |  ▲   |  |
|                  |        | 20.6%↑ | 계약↓  |        |        | 부진 |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  건강케어혁신MBU | TO-7   | 20.3→  | 8.5%   | -      | 미달2  |  ◐   |  |
|                  |        | 20.4%  |        |        |        | 적자 |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  FNC MBU         | TO+72  | 안정    | 13.0%  | -      | 100%+α |  ◐   |  |
|                  | 확장   |        | 외부↑  |        |        |      |  |
|  ────────────────┼────────┼────────┼────────┼────────┼────────┼──────|  |
|  올가 SBU        | TO-12  |  -     | 7.0%   | -      | -      |  ●   |  |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| ▲ 즉시 조치(NA·일본) — Drill-down P.6, P.7 / ◐ 모니터링 / ● 양호       |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.5 — Drill-down: 식품통합 MBU (국내 본진)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.5  Drill-down ─ 식품통합 MBU (국내 본진)                              |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  WHAT (현황)                                                            |
|   · 정규직 1,376 (TO 1,420 / -44)  · 계약직 662 (+83)                    |
|   · NNR 누계 ₩14,954억 (PL 98.4%)  · CEBIT ₩604억 (PL -143)              |
|   · NNR/FTE 환산 ₩1,087백만 (제조평균 ₩520M 상회)                         |
|   · Labor Cost % (배분 후) 9.7~10.5% (산업 14% 하회 — 양호)              |
|                                                                         |
|  WHY (원인 가설 — 데이터 기반)                                          |
|   · 계약직 +83 = 아이엔 단시간 판촉직 일시 증가 (시즌 영향)              |
|   · CEBIT PL 미달 -143억 ─ 매출 대비 비용 효율 저하 가설                |
|       └─ 인건비 외 원자재·물류 영향 추정 (재무팀 협업 점검 필요)        |
|   · 자발 이직 8.9% — 식품제조 동종 best-in-class 8% 근접                |
|                                                                         |
|  EBIT IMPACT (재무영향 추정)                                            |
|   · TO 차이 -44 × 인당 EBIT기여 ₩7M ≒ ₩3억 운영 LOSS                    |
|   · 자발 이직 +0.9p (vs 8%) × 평균 연봉 60M × 50% 대체비 = 약 ₩6.4억    |
|                                                                         |
|  NEXT (권고 액션)                                                       |
|   ① 아이엔 판촉직 정·계 비중 1년 추세 시각화 → P.11에서 외부인력 확장  |
|   ② 자발 이직 사유 분석 (Exit 인터뷰 텍스트 분석 — Phase 2)             |
|   ③ NNR/FTE 우수 → Compensation Stretch 정책 재검토 가능                |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.6 — Drill-down: NA MBU (해외 적자 단위 1)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.6  Drill-down ─ NA MBU (해외 적자 단위 ①)        ▲ 즉시 조치          |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  WHAT                                                                   |
|   · 정규직 486 (TO 521 / -35)                                            |
|   · NNR 누계 ₩3,681억 (PL 88.7%)  · CEBIT ₩-96억 (PL +29 → -125)         |
|   · Labor Cost % 18.3% (산업 14% +4.3p 초과)                            |
|   · 도급/파견 448명 — 정규직 대비 92%                                    |
|                                                                         |
|  WHY                                                                    |
|   · 매출 미달 -₩468억 + 외부인력 비용 leverage 부재                     |
|   · Ayer 공장 일시 인력 ↑ 후 정상화 지연                                 |
|                                                                         |
|  EBIT IMPACT                                                            |
|   · Labor Cost % gap +4.3p × NNR 4,149억 = 약 ₩178억 비용 과중           |
|   · HCROI 모델: NA를 동종(1.73)으로 회복 시 + ₩90~120억 EBIT 회복 가능  |
|                                                                         |
|  NEXT                                                                   |
|   ① 매출 정상화 시나리오 + 인력 우선순위 매트릭스 (재무·법인 합동)       |
|   ② 외부인력→내재화 ROI 분석 (현지 노동시장 임금 곡선 비교)             |
|   ③ Successor Coverage (해외 법인장 후보) Net 기준 점검                  |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.7 — Drill-down: 일본 SBU (해외 적자 단위 2) + FNC

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.7-A  Drill-down ─ 일본 SBU (해외 적자 단위 ②)    ▲ 즉시 조치          |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  · 정규직 118 (TO -22)  계약직 279 (TO -50)                             |
|  · NNR 누계 ₩685억 (PL 77.5%)  CEBIT -₩79억                            |
|  · Labor Cost % 20.6% — 동종 일본식품 평균(15~17%) 상회                  |
|  · 분기 자발 이직률 12.8% — best-in-class 8% 대비 4.8p 위험             |
|                                                                         |
|  EBIT IMPACT                                                            |
|   · 인건비율 갭 +5.6p × NNR 884억 = 약 ₩50억 비용 과중                   |
|                                                                         |
|  NEXT  ① 이직 사유 일본 노동시장 동향 매핑 (후행→선행 전환)             |
|         ② 가격 전가 어려움 시 인력 재구성 (계약직→정규직 vs 반대 검토)  |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.7-B  Drill-down ─ FNC MBU (서비스·확장)                ◐ 모니터링      |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  · 정규직 2,424 (TO +102) — 그룹 내 유일한 확장 BU                       |
|  · NNR 누계 ₩8,255억 (PL 102.1%)  CEBIT ₩290억 (PL +14)                  |
|  · 외부인력 도급/파견 2,722 — Q3 대비 +250 (사업장 오픈)                 |
|                                                                         |
|  WHY                                                                    |
|   · 신규 사업장 오픈 → 외부 인력 우선 충원 (정규직 전환은 시차 발생)   |
|                                                                         |
|  NEXT  ① 사업장 단위 외부→정규 전환 ROI 모델                            |
|         ② 서비스업 평균 25% 인건비율 대비 14.4% — 효율 우수, 전사 학습 |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.8 — Insight 1: Talent Risk (Regrettable Attrition)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.8  Insight ① ─ Talent Risk (Regrettable Attrition)                    |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|                                                                         |
|  핵심 메시지: "전체 이직률이 낮아도 핵심인재 이직률이 높다면 위험"     |
|              (Spring Health · AIHR · Visier 공통 메시지)                |
|                                                                         |
|  지표 정의 (ISO 30414 / Visier 표준)                                    |
|   ┃ Voluntary Turnover    = (자발 퇴사 ÷ 평균 인원) ×100               |
|   ┃ Regrettable Attrition = (의도하지 않은 자발퇴사 ÷ 자발퇴사) ×100   |
|   ┃ High-Performer Att.   = (상위 성과자 자발퇴사 ÷ 평균 상위인원)      |
|                                                                         |
|  Benchmark                                                              |
|   ┃ 자발 이직 best-in-class : <8% (글로벌 제조)                          |
|   ┃ Regrettable share       : 10~20% (top quartile)                      |
|   ┃ High-Performer Volun.   : <5% (red flag >10%)                        |
|                                                                         |
|  As-Is (예시 모형 — 데이터 산출 후 채움)                                |
|   ┃ 풀무원 자발 이직 9.4% (Q4 8.1% → Q1 9.4%, +1.3p)                    |
|   ┃ Regrettable share 추정 N/A (Phase 1 산출 가능)                       |
|   ┃ High-Performer Vol. 추정 N/A (HRIS 평가 데이터 연결 필요)            |
|                                                                         |
|  EBIT IMPACT (Center for American Progress / Forma 출처)                |
|   ┃ 일반직 대체비용  = 연봉 50~80% (사무 50~80%, 숙련 75~125%)          |
|   ┃ 임원/핵심인재   = 연봉 100~213%                                      |
|   ┃ 자발 +1p × 6,846 × 평균 70M × 평균 60% = 약 ₩28.7억 / 분기          |
|                                                                         |
|  NEXT                                                                   |
|   ① Stay 인터뷰 + Exit 인터뷰 정형화 → 분기 입력                        |
|   ② Visier-style 머신러닝 이직 예측(25~40 변수, 정확도 87%) Phase 3     |
|   ③ 핵심인재 정의(Top 10% 평가자) → Regrettable·HP 분리 trend          |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.9 — Insight 2: Engagement → Profit Linkage

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.9  Insight ② ─ Engagement → Profit Linkage                            |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  글로벌 evidence                                                        |
|   ┃ Gallup Q12 메타(347사·736연구): 몰입 상위 25% BU = 수익 +23%        |
|   ┃ McKinsey OHI(2,500사·8M인): 조직건강 상위 25% = TSR 3배              |
|   ┃ Bersin/Deloitte: 분석 기반 의사결정 도입 → 생산성 +20%               |
|   ┃ Unilever 사례: 웰빙 $1 투자 → ROI $2.50                              |
|                                                                         |
|  도입 옵션 비교                                                          |
|                                                                         |
|   옵션  | 도구          | 빈도  | 비용    | 재무연결 강도 | 권장        |
|   ──────┼───────────────┼───────┼─────────┼───────────────┼──────────── |
|   A     | Gallup Q12    | 분기  | ₩₩₩    | ★★★★★         | ▲ 의사결정용|
|   B     | McKinsey OHI  | 연1   | ₩₩₩₩  | ★★★★★         | ▲ 진단용    |
|   C     | eNPS (단문항) | 월/분 | ₩      | ★★★           | ● Quick win |
|   D     | 자체 설계     | 분기  | ₩₩     | ★★★           | ◐ 비교 어려움|
|                                                                         |
|  권고: Phase 2에서 옵션 A or B 도입 → 재무지표 회귀분석 모델 구축       |
|                                                                         |
|  ASCII 회귀 모형 시각화 (예시 — 도입 후 채움)                           |
|     EBIT/FTE                                                             |
|     ┃                       *  *                                         |
|     ┃                  *  *                  R² = 0.6X (예상)            |
|     ┃             *  *                                                   |
|     ┃          *                              y = 4.2x + 1.1             |
|     ┃     *                                                              |
|     ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Engagement Index               |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.10 — Insight 3: Span of Control 최적화

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.10  Insight ③ ─ Span of Control 최적화                                 |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  배경 (McKinsey · Visier · Gallup)                                       |
|   ┃ 표준 6~10명 / 단순업무 10~15 / 복잡업무 3~6                          |
|   ┃ 너무 좁으면(<5) 관리자 비용 과다·승진정체                            |
|   ┃ 너무 넓으면(>15) 코칭 부재·번아웃·이직률 ↑                          |
|                                                                         |
|  As-Is (예시 — 조직도 정합 후 채움)                                     |
|     6.0 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Best 7명 (글로벌)   |
|     ●식품통합 5.4   ●다논 4.8   ●건강케어 4.1                           |
|     ●FNC 11.2 (서비스 정상)    ●Corporate 3.2 (좁음)                    |
|     ●NA 12.1 (해외 — 유의)                                              |
|                                                                         |
|  EBIT IMPACT 추정                                                       |
|   ┃ Corporate Span 3.2 → 6.0 정상화 시                                   |
|   ┃ 관리자 직급 약 X명 절감 → 인건비 ₩A억 + 의사결정 속도 +30~50%       |
|                                                                         |
|  NEXT  ① 조직도 표준 분류(단순/복잡) 후 BU별 적정 Span 정의              |
|         ② 부하 만족도(D2)와 Span 상관 분석 (Manager Effectiveness)       |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.11 — Insight 4: 외부인력(도급·파견·특고) 효율

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.11  Insight ④ ─ External Workforce Efficiency                         |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  현황 — 외부인력 7,602명, 정규직 6,846명 대비 111% (1.1×)               |
|                                                                         |
|  사업단위별 외부인력 의존도 (External / Internal)                        |
|     0%      50%      100%     150%     200%     250%                    |
|  FNC      ┃ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 224%                              |
|  COO      ┃ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 90%                                     |
|  NA       ┃ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 92%                                       |
|  건강케어 ┃ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 85% (특고+SM/HS+로하미)                    |
|  식품통합 ┃ ▓▓▓▓▓ 33% (가맹점주)                                        |
|  다논     ┃ ▓▓▓▓▓ 67%                                                  |
|                                                                         |
|  Risk Lens (글로벌 트렌드 — Deloitte Human Capital 2025)                |
|   ┃ 외부인력 의존도 증가는 단기 비용 ↓ vs 장기 역량 ↓ trade-off           |
|   ┃ "Workforce Ecosystem" — 정규/계약/도급/특고 통합 가시성 ESG 공시 흐름|
|   ┃ ISO 30414도 "Workforce Availability"에 외부인력 포함                |
|                                                                         |
|  KPI 신설 (Phase 1)                                                     |
|   ┃ External Dependency Ratio = 외부인력 ÷ 내부인력                      |
|   ┃ TCOW (Total Cost of Workforce) = 인건비 + 도급비 + 위탁수수료        |
|   ┃ TCOW % of NNR — 진정한 노동비용 비율                                |
|                                                                         |
|  NEXT                                                                   |
|   ① TCOW 분기 산출 → 현재 Labor Cost%를 보완·대체                        |
|   ② BU별 외부인력 효율(매출/외부인력 1인) 산출                          |
|   ③ 노동시장 리스크(노란봉투법 등) 시나리오 분석 — 25.Q3 보고와 연계   |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

### P.12 — Action Watchlist + KPI Glossary

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| P.12  Action Watchlist + KPI Glossary                                   |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  Action Watchlist — 다음 분기 사장단 의사결정 필요사항                  |
|                                                                         |
|  # | Action                                | Owner   | Due     | EBIT  |
|  ──┼───────────────────────────────────────┼─────────┼─────────┼────── |
|  1 | NA·일본 인건비율 회복 시나리오 수립    | CFO/CHO | 26.Q2  | +90억 |
|  2 | TCOW % 분기 산출 모델 가동             | 인사기획| 26.Q2  | -    |
|  3 | Stay/Exit 인터뷰 정형 시작             | 인사기획| 26.Q2  | +28억|
|  4 | Engagement Index 도구 선정 (Q12/OHI)   | CHO     | 26.Q3  | -    |
|  5 | Successor Coverage(Net) 점검           | 경영기획| 26.Q3  | -    |
|  6 | Span 표준 정의(BU·직무유형별)           | 조직개발| 26.Q3  | -    |
|  7 | Critical Skills Coverage 분류 정의     | 인사기획| 26.Q4  | -    |
|  8 | HCM AX Phase 2: 시각화·분석 자동화      | DT/CHO  | 26.Q4  | -    |
|                                                                         |
|  KPI Glossary (요약 — Appendix에 산식·출처 전체 정의)                    |
|   A1 Total Workforce | 정규+계약+도급+파견+특수고용                    |
|   A2 Labor Cost %    | 인건비성비용 ÷ NNR                              |
|   A3 TCOW            | 인건비+도급비+위탁수수료                        |
|   A4 CPH             | 채용 총비용 ÷ 채용자수 (SHRM)                   |
|   B1 NNR/FTE         | NNR ÷ 평균 FTE (ISO 30414)                       |
|   B3 HCROI           | (NNR-(비용-인건비)) ÷ 인건비 (Saratoga)         |
|   C1 Vol Turnover    | 자발 퇴사 ÷ 평균 인원 (ISO 30414)                |
|   C2 Regrettable     | 의도치 않은 자발 퇴사 ÷ 자발 퇴사 (Spring Health)|
|   C3 First-Year Att. | 1년내 이탈 ÷ 신규입사 (AIHR)                    |
|   D1 Engagement      | Q12 / OHI / eNPS (Gallup / McKinsey)            |
|   E4 Successor Cov.  | Ready 후계자 ÷ Critical Position (One Model)     |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

---

## 6. 데이터 소스 매핑 (Phase 1 Quick Win 우선)

| KPI | 1차 데이터 소스 | 2차 (조인 키) | 산출 주체 |
|---|---|---|---|
| A1·A2·A3·F2·F3 | ERP (인사기준정보), 급여원장 | NNR/CEBIT (재무) | 인사기획 |
| B1·B2·B3·B4 | 급여원장, 손익원장 | FTE 환산 룰 | 경영기획+인사 |
| C1·C3·C4 | ERP 입퇴사·인사이동 | 평가데이터 (HiPo Tag) | 인사기획 |
| C2·E3 | 평가시스템 + Exit 인터뷰 | 채용DB (Source) | 인사기획+조직개발 |
| D1·D2 | 외부 몰입조사(Q12/OHI) | 조직도 Manager Map | CHO |
| D3·D4 | 근태시스템·ESH | 안전사고 DB | COO/ESH |
| E1·E4 | 스킬 인벤토리(미구축)·승계계획 | 평가·교육이력 | 인사기획 |
| E2 | 교육관리시스템 | 급여원장 | HRD |
| F1·F4 | 인사기준정보 | 급여원장 (Pay Equity) | 인사기획 |

---

## 7. 직접 참고할 만한 HR Dashboard 사례 모음 (Live & Visual)

> 본 절은 위 리서치 과정에서 검증된 권위 있는 출처(Tableau, Qlik, Visier, AIHR, Deloitte 등)에서 **풀무원 대시보드 설계 시 직접 클릭해 시각·구조를 참고할 수 있는 사례**만 선별. 각 항목 옆에 우리 12장 구성 중 어느 페이지(P.x) 설계에 활용 가능한지 매핑.

### 7-1. 인터랙티브 라이브 대시보드 (직접 클릭·드릴다운 가능)

| # | 사례 | 출처 / 링크 | 우리 설계 매핑 | 참고 포인트 |
|---|---|---|---|---|
| 1 | **Tableau Public ─ HR Dashboard #RWFD** (Gandes Goldestan) | [public.tableau.com/.../HRDashboard_16284874251120](https://public.tableau.com/app/profile/gandes.goldestan/viz/HRDashboard_16284874251120/Overview) | **P.1 Hero KPI / P.2 인력 구성** | Hero KPI 6개 가로 배치 + 부서·근속별 드릴다운 패턴이 매우 깔끔. 풀무원 BU Heatmap 베이스 디자인으로 활용 |
| 2 | **Tableau Public ─ Headcount Dashboard** (Lintao) | [public.tableau.com/.../HumanResources-HeadcountDashboard](https://public.tableau.com/app/profile/lintao/viz/HumanResources-HeadcountDashboard/Home) | **P.2 Workforce Composition** | 정규/계약/현장직 stacked bar + 부문별 비중 — 풀무원 부문 구조와 거의 동일. 색상 팔레트 차분해 임원보고에 적합 |
| 3 | **Tableau Public ─ HR Analytics Dashboard** (Shuvashis Das) | [public.tableau.com/.../HRANALYTICSDASHBOARD_17055462626630](https://public.tableau.com/app/profile/shuvashisdasbd/viz/HRANALYTICSDASHBOARD_17055462626630/HRANALYTICSDASHBOARD) | **P.4 BU Heatmap / P.8 Talent Risk** | Attrition Risk 색상 신호등이 잘 표현. 자발/비자발 분리 시각화 — P.8에서 그대로 활용 가능 |
| 4 | **Tableau Public ─ Starbucks Workforce Diversity** (공개 실제 기업 사례) | [tableau.com/solutions/human-resources-analytics/dashboards](https://www.tableau.com/solutions/human-resources-analytics/dashboards) | **P.12 Diversity & Compliance** | 글로벌 상장사가 외부 공시 수준으로 만든 다양성 대시보드. ESG 공시 흐름 참고 |
| 5 | **Tableau People Analytics Dashboard** (Tableau 자체 운영) | [tableau.com/solutions/human-resources-analytics/dashboards](https://www.tableau.com/solutions/human-resources-analytics/dashboards) | **P.9 Engagement** | 직원 서베이 + WFH 영향 분석 — 풀무원 Phase 2 Engagement 도입 시 모범 사례 |

### 7-2. 검증된 디자인 가이드 + 시각 갤러리

| # | 사례 | 출처 / 링크 | 우리 설계 매핑 | 참고 포인트 |
|---|---|---|---|---|
| 6 | **Qlik ─ HR Dashboard: 7 Key Examples and Best Practices** | [qlik.com/us/dashboard-examples/hr-dashboard](https://www.qlik.com/us/dashboard-examples/hr-dashboard) | **전체 12장** | 7가지 HR 대시보드 유형(전사/채용/이직/몰입/보상/D&I/생산성)과 각 유형별 KPI·시각화 권고. 풀무원 12장 Section 분류와 1:1 매핑 가능 |
| 7 | **Qlik ─ Executive Dashboards: 5 Examples for Data-Driven Leaders** | [qlik.com/us/dashboard-examples/executive-dashboards](https://www.qlik.com/us/dashboard-examples/executive-dashboards) | **P.1 Cover** | "5초 룰" Hero KPI 배치 원칙. 사장단 보고 첫 페이지의 Anchor 디자인 |
| 8 | **Qlik ─ Dashboard Design 7 Best Practices** | [qlik.com/us/dashboard-examples/dashboard-design](https://www.qlik.com/us/dashboard-examples/dashboard-design) | **전체** | 색·레이아웃·계층 디자인 7원칙. 풀무원 사내 표준 작성에 그대로 인용 가능 |
| 9 | **AIHR ─ People Analytics Dashboard: How To Build One That Works for You** | [aihr.com/blog/people-analytics-dashboard](https://www.aihr.com/blog/people-analytics-dashboard/) | **전체 (방법론)** | Workforce Structure / Recruitment / Turnover 3대 대시보드 step-by-step. Phase 1 Quick Win 구축 매뉴얼로 활용 |
| 10 | **AIHR ─ HR Dashboard: 5 Examples, Metrics and a How-To** | [aihr.com/blog/hr-dashboard](https://www.aihr.com/blog/hr-dashboard/) | **P.2~P.4** | 5가지 HR 대시보드 사례 + 각 사례별 KPI 리스트. 우리 6대 KPI 축과 교차검증용 |

### 7-3. 임원·CHRO 시점의 운영형 사례

| # | 사례 | 출처 / 링크 | 우리 설계 매핑 | 참고 포인트 |
|---|---|---|---|---|
| 11 | **Visier ─ 7 People Analytics Dashboards You Need to Track** | [visier.com/blog/people-analytics-dashboard-examples](https://www.visier.com/blog/people-analytics-dashboard-examples/) | **P.1, P.8, P.9** | 7개 대시보드(People Cost / Movement / Diversity / Talent Acquisition / Manager / Engagement / Strategic Workforce Planning) 각각 CHRO·CFO 활용 시나리오 명시 |
| 12 | **Visier ─ Vee Boards: AI Executive Dashboards** (Talent Density Board) | [visier.com/blog/ai-executive-dashboard](https://www.visier.com/blog/ai-executive-dashboard/) | **P.1 Cover (확장 버전)** | CHRO+CEO 공동 보드. AI가 outlier 자동 탐지·권고. Phase 3 예측 단계의 모델 |
| 13 | **Visier ─ People Analytics Case Studies** | [visier.com/blog/case-studies-how-companies-use-analytics-to-achieve-results](https://www.visier.com/blog/case-studies-how-companies-use-analytics-to-achieve-results/) | **전체 (의사결정 연계)** | 실제 기업이 분석을 통해 EBIT를 회복한 케이스. P.5~P.7 Drill-down "EBIT IMPACT" 산정에 활용 |
| 14 | **Vena ─ Free HR Executive Dashboard for Power BI** | [venasolutions.com/templates/reporting/hr-executive-dashboard](https://www.venasolutions.com/templates/reporting/hr-executive-dashboard) | **P.1 Cover** | Power BI 즉시 사용 가능한 Executive HR 템플릿. 풀무원 HCM AX Phase 2 도구 선정 시 baseline |
| 15 | **Improvado ─ Executive Dashboards: 13+ Examples & Best Practices** | [improvado.io/blog/executive-dashboards](https://improvado.io/blog/executive-dashboards) | **P.1, P.4** | 임원 대시보드 13개 영역별 best practice. Hero KPI + Heatmap + Anomaly 알림 구조 |

### 7-4. 운영형 KPI 템플릿 (Phase 1 즉시 활용)

| # | 사례 | 출처 / 링크 | 우리 설계 매핑 | 참고 포인트 |
|---|---|---|---|---|
| 16 | **Klipfolio ─ HR Dashboard: Examples, Templates, and Best Practices** | [klipfolio.com/resources/dashboard-examples/hr](https://www.klipfolio.com/resources/dashboard-examples/hr) | **P.8, P.9, P.11** | 4종 템플릿(Turnover / Engagement / Development / Recruitment). 각 KPI에 산식·임계치까지 명시 |
| 17 | **Klipfolio ─ Recruitment Dashboard Examples** | [klipfolio.com/resources/dashboard-examples/hr/recruitment-dashboard](https://www.klipfolio.com/resources/dashboard-examples/hr/recruitment-dashboard) | **P.12 Watchlist (Phase 2)** | Time-to-Fill, Quality of Hire, Source Effectiveness 등 채용 funnel 시각화 |
| 18 | **Databox ─ 100+ KPI Dashboard Examples** | [databox.com/dashboard-examples/kpi](https://databox.com/dashboard-examples/kpi) | **전체** | 산업별·역할별 100+ 템플릿 갤러리. 풀무원 KPI 6대 축 각각 매핑 가능 |
| 19 | **Coupler.io ─ 32 Best Power BI Dashboard Examples & Templates 2026** | [blog.coupler.io/power-bi-dashboard-examples](https://blog.coupler.io/power-bi-dashboard-examples/) | **도구 선정** | Phase 2 Power BI 채택 시 즉시 fork 가능한 32종 |
| 20 | **Quantize Analytics ─ Best 8 Tableau HR Dashboard Examples** | [quantizeanalytics.co.uk/tableau-human-resources-examples](https://www.quantizeanalytics.co.uk/tableau-human-resources-examples/) | **시각 사양 협의용** | 8개 사례별 화면 + 인사이트 도출 방식 — 사장단 시안 회의 자료로 활용 |

### 7-5. 외부 데이터 소스 (벤치마크 자동 갱신용)

| # | 사례 | 출처 / 링크 | 활용 방법 |
|---|---|---|---|
| 21 | **Damodaran (NYU Stern) ─ Employee Metrics by Sector (US)** | [pages.stern.nyu.edu/~adamodar/.../Employee.html](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Employee.html) | NNR/FTE·인건비율 산업 평균 자동 갱신 (연 1회) |
| 22 | **CSI Market ─ Food Processing Industry Efficiency** | [csimarket.com/Industry/industry_Efficiency.php?ind=505](https://csimarket.com/Industry/industry_Efficiency.php?ind=505) | 식품가공 동종 업계 분기별 효율 지표 |
| 23 | **Conference Board ─ ISO 30414 Overview** | [conference-board.org/.../Overview-of-ISO-30414-Human-Capita-Reporting-Standards-Conference-Board.pdf](https://www.conference-board.org/pdf_free/Overview-of-ISO-30414-Human-Capita-Reporting-Standards-Conference-Board.pdf) | 11개 영역·69개 KPI 정의 표준 |
| 24 | **Gartner ─ CHRO Top Priorities 2026** | [gartner.com/en/human-resources/trends/top-priorities-for-hr-leaders](https://www.gartner.com/en/human-resources/trends/top-priorities-for-hr-leaders) | 매년 1월 업데이트 — 분기 보고에 글로벌 트렌드 반영 |

### 7-6. 매핑 요약 (어느 사례를 어느 페이지에 — 한눈에)

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
| Page              | 1차 참고 사례                 | 2차 참고 사례               |
|-------------------|-------------------------------|-----------------------------|
| P.1 Cover         | #1 Tableau Goldestan / #7 Qlik | #11 Visier / #14 Vena       |
| P.2 Workforce     | #2 Tableau Lintao             | #9 AIHR Workforce Structure |
| P.3 Productivity  | #21 Damodaran / #11 People Cost| #6 Qlik / #18 Databox       |
| P.4 BU Heatmap    | #1 #3 Tableau                 | #6 Qlik 7 Examples          |
| P.5~7 Drill-down  | #6 Qlik / #11 Visier          | #20 Quantize 8 Examples     |
| P.8 Talent Risk   | #3 Tableau Shuvashis / #16    | #11 Visier / #13 Case       |
| P.9 Engagement    | #5 Tableau / #16 Klipfolio    | #11 Visier #6번 보드        |
| P.10 Span         | #6 Qlik / #11 Visier #5번보드  | (Visier·McKinsey 본문)      |
| P.11 External WF  | #11 Visier People Cost / #18  | (Deloitte 2025 Trends 본문) |
| P.12 Watchlist    | #15 Improvado / #6 Qlik       | #17 Klipfolio Recruitment   |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

---

## 8. 출처 (References)

### 7-1. 표준 / Framework
- ISO. *ISO 30414:2018 — Human resource management — Guidelines for internal and external human capital reporting.* https://www.iso.org/standard/69338.html
- ISO. *ISO 30414:2025 — Human resource management — Requirements and recommendations for human capital reporting and disclosure.* https://www.iso.org/standard/30414
- The Conference Board. *Overview of ISO 30414 Human Capital Reporting Standards.* https://www.conference-board.org/pdf_free/Overview-of-ISO-30414-Human-Capita-Reporting-Standards-Conference-Board.pdf

### 7-2. 컨설팅 리포트 / 학술
- Deloitte. *Key HR Metrics for Chief Human Resources Officers.* https://www.deloitte.com/us/en/services/consulting/articles/key-hr-metrics-for-chros.html
- Deloitte. *2025 Global Human Capital Trends.* https://www.deloitte.com/us/en/services/consulting/articles/human-capital-and-hr-trends-thought-leadership.html
- McKinsey & Company. *HR Monitor 2025.* https://www.mckinsey.com/~/media/mckinsey/business%20functions/people%20and%20organizational%20performance/our%20insights/hr%20monitor%202025/hr-monitor-2025.pdf
- McKinsey & Company. *Organizational Health Index — Overview & Evidence.* https://www.mckinsey.com/solutions/orgsolutions/overview/organizational-health-index
- McKinsey & Company. *Organizational health is (still) the key to long-term performance.* https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/organizational-health-is-still-the-key-to-long-term-performance
- Gallup. *Q12 Meta-Analysis 11th Edition: The Relationship Between Engagement at Work and Organizational Outcomes.* https://www.gallup.com/workplace/321725/gallup-q12-meta-analysis-report.aspx
- Gallup. *Span of Control: What's the Optimal Team Size for Managers?* https://www.gallup.com/workplace/700718/span-control-optimal-team-size-managers.aspx
- Gartner. *Top HR Trends and CHRO Priorities That Matter Most in 2026.* https://www.gartner.com/en/human-resources/trends/top-priorities-for-hr-leaders
- Visier. *Mastering Span of Control: A Comprehensive HR Walkthrough.* https://www.visier.com/blog/span-of-control-hr-guide/
- Visier. *10 Critical Succession Planning Metrics for 2025.* https://www.visier.com/blog/succession-planning-metrics/
- McKinsey & Company. *How to identify the right "spans of control" for your organization.* https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/how-to-identify-the-right-spans-of-control-for-your-organization

### 7-3. 정량 벤치마크
- HRBench. *Revenue per Employee: 2025 Benchmarks by Industry + Formula.* https://www.hrbench.com/resource/learn/revenue-per-employee
- HRBench. *Span of Control: Formula, Benchmarks & Why It Predicts Turnover.* https://www.hrbench.com/resource/learn/span-of-control
- CFO.com. *How to measure productivity with revenue per employee.* https://www.cfo.com/news/productivity-revenue-per-employee-metric-of-the-month-perry-wiggins/720503/
- NetSuite. *What Percentage of Sales or Gross Revenue Should Go Toward Payroll?* https://www.netsuite.com/portal/resource/articles/financial-management/small-business-payroll-percentage.shtml
- Damodaran (NYU Stern). *Employee Metrics by Sector (US).* https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Employee.html
- Center for American Progress. *There Are Significant Business Costs to Replacing Employees.* https://www.americanprogress.org/article/there-are-significant-business-costs-to-replacing-employees/
- Forma. *What's the real cost of turnover? How to calculate employee replacement costs.* https://www.joinforma.com/resources/employee-replacement-costs

### 7-4. KPI 정의·실무
- AIHR. *Attrition Rate: Definition, Formula, Analysis, and Free Calculator.* https://www.aihr.com/blog/attrition-rate/
- AIHR. *10 Succession Planning Metrics You Should Know.* https://www.aihr.com/blog/succession-planning-metrics/
- AIHR. *An HR's Guide to Calculating Span of Control.* https://www.aihr.com/blog/calculating-span-of-control/
- AIHR Institute. *Why Regrettable Attrition Is a Warning Signal for Every Organization.* https://www.aihr-institute.com/blog/why-regrettable-attrition-is-a-warning-signal-for-every-organization
- Spring Health. *Regrettable Attrition: Leading Indicators and How to Prevent It.* https://www.springhealth.com/blog/regrettable-attrition-leading-indicators-how-to-prevent-it
- Qlik. *HR Dashboard: 7 Key Examples and Best Practices.* https://www.qlik.com/us/dashboard-examples/hr-dashboard
- Outsail. *HRIS Data Analytics: Turning HR Metrics into Executive Dashboards That Drive Decisions.* https://www.outsail.co/post/hris-data-analytics-turning-hr-metrics-into-executive-dashboards
- One Model. *Key Metrics for Succession Planning.* https://www.onemodel.co/blog/succession-planning-metrics
- ExecOnline. *Bench Strength Basics.* https://www.execonline.com/measure-bench-strength/

### 7-5. 기업 사례
- peopleHum. *How Google is using people analytics to completely reinvent HR.* https://www.peoplehum.com/blog/how-google-is-using-people-analytics-to-completely-reinvent-hr
- ResearchGate. *Redefining HR using people analytics: the case of Google.* https://www.researchgate.net/publication/323936892_Redefining_HR_using_people_analytics_the_case_of_Google
- HR Tech Central. *IBM Workforce Management Initiative Case Study.* https://www.hrtechcentral.com/case-study/ibm/
- Effectory. *People Analytics: 5 Real Case Studies (Microsoft, Unilever, etc.).* https://www.effectory.com/knowledge/people-analytics-5-real-case-studies/
- myHRfuture. *Nestlé's 4B Methodology to Strategic Workforce Planning.* https://www.myhrfuture.com/digital-hr-leaders-podcast/nestles-4b-methodology-to-strategic-workforce-planning
- Field Service USA. *How Siemens Takes HR and Workforce Planning Digital.* https://fieldserviceusa.wbresearch.com/blog/how-siemens-takes-hr-and-workforce-planning-digital
- myHRfuture. *People Analytics in 2020: Growth, Leading Practices, Case Studies and Ethics (Bersin/Deloitte).* https://www.myhrfuture.com/blog/2020/1/27/people-analytics-in-2020-growth-leading-practices-case-studies-and-ethics

---

## 9. Appendix — 단계별 도입 로드맵

```
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
|  2026.Q2 ─ Phase 1 Quick Win                                            |
|   ┃ A3·A4·B1·B2·B3·B4 산출 자동화 (현 ERP+급여+손익 데이터로 가능)     |
|   ┃ Hero KPI 6대 + BU Heatmap 도입                                      |
|   ┃ 2026.Q2 인사위원회부터 신 양식 시범 운영                            |
|                                                                         |
|  2026.Q3~Q4 ─ Phase 2 분석 강화                                         |
|   ┃ Engagement(Q12 또는 OHI), Span of Control, Successor 추가          |
|   ┃ TCOW·외부인력 효율 KPI 분기화                                       |
|   ┃ HCM AX Phase 2(시각화·분석 자동화)와 동기화                         |
|                                                                         |
|  2027.Q1~ ─ Phase 3 예측·시나리오                                       |
|   ┃ Predictive Attrition (Visier 표준 87% 정확도 모델)                  |
|   ┃ EBIT-Engagement 회귀, What-if Workforce Planning                    |
|   ┃ ESG 공시(K-ESG·KCGS) 외부 보고로 확장                                |
ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
```

> 본 문서는 인사기획실의 **Plan 단계** 산출물이며, 데이터 검증·BU별 협의·도구 선정을 거쳐 분기별 시범 → 정식 양식으로 전환을 권고드립니다. 모든 정량 벤치마크는 위 7. 출처 절의 권위 자료를 기준으로 인용하였습니다.
