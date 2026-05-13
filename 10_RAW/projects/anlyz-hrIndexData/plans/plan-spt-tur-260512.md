# Plan: 지원조직 + 퇴사율 DuckDB 스키마 설계 (P1-b)

작성일: 2026-05-12
선행: `archive/dashboard/plan-hc-schema-260512.md` (HC 스키마 P1-a)
대상 산출물: **schema.yaml + ddl.sql 의 *증분*** — 지원조직 / 퇴사율 sources·테이블 추가

> <span style="color:red">**📝 현재 라운드 = 1 — 2026-05-12 사용자 코멘트 5건 반영본**: ① 'R' 표기 의미(행 번호) 정정 + 표 헤더 통일, ② 소계·합계 행 룰 풀어 설명, ③ 퇴사율 컬럼 매핑 표 펼침, ④ DDL 증분 의문 해소, ⑤ 위험/미결 비개발자 친화 설명 + 모호점 2건 askquestion 결정 반영.</span>

> **본 plan 의 범위**: 직전 HC plan 의 결정사항(SCD Type 2 `dim_bu`, 직군 6종, schema.yaml + ddl.sql 분리, quarter=2 통일, PII 2-layer)을 **그대로 재사용**. 본 plan 은 그 위에 **지원조직 fact + 퇴사율 fact** 두 영역만 추가한다. DDL 은 한 벌(연도 무관), schema.yaml `sources` 블록은 3개년(지원조직) / 2개년(퇴사율) diff 흡수 패턴 명세.

---

## 1. Context — 직전 plan 과의 관계

| 영역 | 직전 plan (HC) | 본 plan (지원조직 + 퇴사율) |
|---|---|---|
| 대상 시트 | `요약` / `관계인력(PPT)` / `전사총계` | 지원조직 시트 / 퇴사율현황 시트 |
| fact 추가 | `fact_headcount`, `fact_related_personnel` | `fact_support_personnel`, `fact_turnover_rate` |
| dim 재사용 | `dim_bu` (SCD Type 2), `dim_employment_type` | **그대로 재사용 — 추가 정의 없음** |
| 적재 PK 패턴 | `(year, quarter, bu_id, emp_type_code)` | 동일 grain (BU level=1 부정 — 지원조직 grain 명세 §3) |
| schema.yaml `sources` | hc_2023 / hc_2024 / hc_2025 | spt_2023 / spt_2024 / spt_2025 + tur_2024 / tur_2025 |

**전제 (직전 plan 에서 이미 확정)**:
- 5월 1일 snapshot → `quarter=2` 통일
- BU 명 시계열 drift → `dim_bu.effective_from/to` + schema.yaml `bu_aliases` 흡수
- 직군 6종 (EXEC/MGMT/OPER/FIELD/CONT/PART) — 단, 지원조직·퇴사율 시트는 자체 직군 분해가 다름 → schema.yaml `employment_type_mapping.aliases` 만 보강

---

## 2. 실 엑셀 구조 — deep dive 결과

<span style="color:red">### 2.1 지원조직 — 3개년 raw 검증 (코멘트 ① 반영: 'R' 표기 정정)</span>

> 💬 **사용자 원본 코멘트 1**: "위 '헤더' '데이터' 에 'R'이 무슨뜻이야? 엑셀 R열에는 딱히 기준 될 만한 값이 없어"

<span style="color:red">**표기 정정**: 본 문서에서 `R{숫자}` = **행(row) 번호**의 줄임표기 (예: `R9` = 9번째 행). 엑셀 18번째 컬럼인 'R열'과 무관. 이하 모든 표·본문에서 "행 9" / "9행" 으로 풀어 쓰고, 셀 좌표는 컬럼+행 형식("B9", "M22") 유지.</span>

| 연도 | 파일 | 시트 | 크기 (행×열) | 헤더 위치 (행) | 데이터 범위 (행) | 직군 분해 | 구조 |
|---|---|---|---|---|---|---|---|
| 2025 | `2.지원조직_250501부…xlsx` | `Sheet1 (3)` | 38×27 | 9행·11행 | 13~31행 | 경영간부/운영직/현장직/계약직 (4종) | **좌측(D~J = 24년 비교) + 우측(L~X = 25년 TO/현재)** 단일 블록 |
| 2024 | `2.지원조직_240513.xlsx` | `Sheet1` | 35×25 | 9행·11행 | 13~30행 | 경영간부/운영직/현장직/임시직 (4종) | 동일 (좌측 22년 초 + 우측 24년) |
| 2023 | `2.지원조직인력__230517.xlsx` | `지원조직` | 74×21 | **3행·5행 + 31행·33행 (2-block)** | 7~23행 + 35~52행 | **블록1**: M/S·P3·P2·임시직 (5종) / **블록2**: 경영간부/운영직/현장직/임시직 (4종) | **2개 블록 분리** |

**핵심 정정 (2023 특이성)**:
- 2023 은 한 시트에 **두 개의 분리된 표** 존재:
  - 블록1 (3~24행): "22년 초 vs 23년 5/1 비교" — 직군 5종 (경영간부, M/S, P3, P2, 임시직)
  - 블록2 (31~53행): "23년 TO vs 23년 5/1 비교" — 직군 4종 (24/25 와 호환)
- → 본 plan 적재 대상은 **블록2만** (24/25 와 grain 일치). 블록1 은 raw 보존, schema.yaml 에 `skip_block` 명시
- "T/O 대비" 컬럼 명세는 24/25 우측 블록과 동일 구조

**임시직 vs 계약직 명칭 drift**: 2024 까지 "임시직", 2025 "계약직". 같은 직군 코드 `CONT` 로 통일 (alias 추가)

<span style="color:red">**소계·합계 행 식별 룰 (3개년 통용) — 코멘트 ② 반영: 풀어 설명**</span>

> 💬 **사용자 원본 코멘트 2**: "이부분은 무슨말인지 모르겠음 다시 구체적으로 설명해봐"

<span style="color:red">**왜 필요한가 (비개발자용 설명)**</span>: 엑셀 시트에는 **진짜 데이터 행** (예: "샘물_지원조직 = 20명") 과 **요약 행** (예: "소계 = 346명", "지원 인력 합계 = 647명") 이 섞여 있다. 요약 행은 위의 진짜 데이터 행을 다시 합산한 값이므로 **DB에 그대로 적재하면 같은 사람을 두 번 세는 결과**가 된다. → extract 단계에서 요약 행을 식별해 skip 해야 한다.

<span style="color:red">**식별 방법 (3개년 모두 같은 패턴)**</span>:

| 행의 위치 (컬럼·텍스트) | 의미 | 처리 |
|---|---|---|
| **C 컬럼** 값이 "소계" | 좌측 블록(전사지원/사업지원 카테고리)의 소계 | skip |
| **M 컬럼** 값이 "소계" | 우측 블록의 소계 | skip |
| **B 컬럼** 값이 "지원 인력 합계" | 시트 전체 합계 (좌측) | skip |
| **L 컬럼** 값이 "지원 인력 합계" | 시트 전체 합계 (우측) | skip |
| 그 외 행 | 진짜 데이터 (지원조직 단위) | `fact_support_personnel` 에 적재 |

**사업단위 구분 (적재되는 진짜 데이터 행의 카테고리)**:
- **B 컬럼**: "전사지원" 또는 "(HQ)" → 본사 지원조직 (CFO/CHO/CCO 등)
- **B 컬럼**: "사업지원" 또는 "사업" → BU 별 지원조직 (식품통합/샘물/다논 등)
- 본 plan 은 이 구분을 `fact_support_personnel.support_category` 컬럼에 그대로 보존 (대시보드에서 본사 vs 사업 부문 별도 보고 시 활용)

### 2.2 퇴사율 — 2개년 raw 검증

| 연도 | 파일 | 시트 | 크기 (행×열) | 헤더 위치 (행) | BU 데이터 범위 (행) | 회고 컬럼 | PII 시트 |
|---|---|---|---|---|---|---|---|
| 2025 | `3.퇴사율현황…v0.81…xlsx` | `퇴사율현황` | 38×32 | 1·2·3행 | 4~26행 | 24/23/22/21 (G~R) + **25 예측치(E·F)** | 25년·24년 퇴사자 / 25년·24년 재직자 (4시트, 사번·주민번호 포함) |
| 2024 | `3.퇴사율현황…24.05.01부.xlsx` | `퇴사율현황` | 32×28 | 5·6·7행 | 8~21행 | 23/22/21 + 24 예측치 | 없음 |

**5개년 회고 데이터 처리 — 사용자 답변 반영**:

| 파일\연도 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| 2025 파일 | (skip — 2024 파일에 양보) | ✅ 적재 (확정) | ✅ 적재 (확정) | ✅ 적재 (확정) | ✅ 적재 **(예측치)** |
| 2024 파일 | ✅ 적재 (가장 옛 회고만) | skip | skip | skip (예측치) | — |

**룰 정형화** ("LATEST-FILE-WINS for confirmed + 예측치는 latest 만"):
- `is_forecast` 플래그 컬럼 추가 — `fact_turnover_rate.is_forecast=TRUE` 면 예측치 (5/1 시점 부분 데이터 × 3 식)
- 각 파일에서 적재할 연도 셋 (extract 단계 룰):
  - **2025 파일** → year ∈ {2022, 2023, 2024} (confirmed, `is_forecast=FALSE`) + year=2025 (forecast, `is_forecast=TRUE`)
  - **2024 파일** → year ∈ {2021} (confirmed, `is_forecast=FALSE`) — 2022~2023 은 2025 파일에 더 안정된 confirmed 값 있어 양보
  - **향후 2026 파일** → year ∈ {2025} (confirmed — 이전의 forecast 값을 confirmed 로 update) + year=2026 (forecast)
- 즉 **(year, is_forecast)** 가 `fact_turnover_rate` PK 의 일부. 같은 연도가 forecast → confirmed 로 update 시 동일 row 갱신

**PII 시트 — 본 plan 제외 (사용자 확정)**:
- 25년·24년 퇴사자(888·2377 rows) / 25년·24년 재직자(7037·7112 rows) 는 본 plan scope **외**
- 사번·주민번호·이직회사·퇴직사유 등 포함 → 별도 plan 으로 분리 (`_internal.duckdb` 적재 패턴은 직전 plan Q3 결정 그대로)

<span style="color:red">### 2.3 퇴사율현황 시트 컬럼 매핑 — 코멘트 ③ 반영: 5개년 매트릭스 표</span>

> 💬 **사용자 원본 코멘트 3**: "이것도 **5개년 회고 데이터 처리 — 사용자 답변 반영** 처럼 표로 만들어봐 보기가 너무 안좋아"

<span style="color:red">**BU 식별 컬럼 (2025 파일 공통)**</span>:

| 셀 | 헤더 텍스트 | 의미 | DDL 매핑 |
|---|---|---|---|
| A | "부문" | 부문 그룹 (국내식품제조유통/해외식품제조유통/건강케어제조유통/식품서비스유통/Corporate Office) — forward-fill 필요 | 적재 안 함 (조회용) |
| B | "조직명" | BU 명 (식품통합 MBU / 샘물SBU / NA MBU 등) | `bu_aliases` → `dim_bu.bu_id` lookup |

<span style="color:red">**연도별 컬럼 매트릭스 (2025 파일)** — 같은 시트에 5년치 회고가 가로로 펼쳐짐</span>:

| 연도 | 재직자수 컬럼 | 퇴사자수 컬럼 | 퇴사율 컬럼 | 연환산 컬럼 | 시점 (quarter) | is_forecast | 본 plan 적재? |
|---|---|---|---|---|---|---|---|
| **2025** | C (5/1 재직자) | D (1.1~5.1 부분치) | E (D/C) | F (D/C × 3) | 2 (5/1 snapshot) | **TRUE** | ✅ 적재 (예측치) |
| **2024** | G (12/31 재직자) | H (1년치) | I (H/G) | — | 4 (12/31 확정) | FALSE | ✅ 적재 (확정치) |
| **2023** | J (12/31 재직자) | K (1년치) | L (K/J) | — | 4 | FALSE | ✅ 적재 (확정치) |
| **2022** | M (12/31 재직자) | N (1년치) | O (N/M) | — | 4 | FALSE | ✅ 적재 (확정치) |
| **2021** | P (12/31 재직자) | Q (1년치) | R (Q/P) | — | 4 | FALSE | ❌ **skip — 2024 파일 양보** |

<span style="color:red">**연도별 컬럼 매트릭스 (2024 파일)** — 2025 파일 대비 1년 shift, 헤더 위치만 다름</span>:

| 연도 | 재직자수 컬럼 | 퇴사자수 컬럼 | 퇴사율 컬럼 | 연환산 컬럼 | is_forecast | 본 plan 적재? |
|---|---|---|---|---|---|---|
| **2024** | C (5/1 재직자) | D (1.1~5.1 부분치) | E | F (× 3) | TRUE | ❌ skip (2025 파일에 더 정확한 확정치) |
| **2023** | G | H | I | — | FALSE | ❌ skip (2025 파일 양보) |
| **2022** | J | K | L | — | FALSE | ❌ skip (2025 파일 양보) |
| **2021** | M | N | O | — | FALSE | ✅ **적재 (가장 옛 회고 — 2025 파일에는 없음)** |

**행 구조 (2025 파일, BU 데이터 행 4~26행 이후)**:

| 행 | 의미 | 처리 |
|---|---|---|
| **27행** | 전사 총계 anchor (C=2886, D=99) | 적재 skip + 검증 anchor |
| 28행 | 국내 소계 (C=2108) | skip + 검증 |
| 29~34행 | 재단·CEO·중국·제외 등 sub-그룹 (대부분 `#DIV/0!`) | skip (의미 없음) |
| 35행 | "요약" 행 | skip |
| **36행** | 해외 소계 (C=778) | skip + 검증 |

---

## 3. 본 plan 산출물 — DDL 증분 + schema.yaml 증분

<span style="color:red">### 3.1 `pipeline/ddl.sql` 에 추가될 테이블 — 코멘트 ④ 반영: 증분 안전성 설명</span>

> 💬 **사용자 원본 코멘트 4**: "엑셀 파일이 다른데 증분 해도 문제 없나?"

<span style="color:red">**왜 안전한가 (비개발자용 설명)**</span>:
- **`ddl.sql` 은 "데이터베이스 안의 테이블 골격"을 정의하는 파일** — 어느 엑셀에서 데이터가 오든 상관없음. 같은 DuckDB 안에 `fact_headcount` / `fact_support_personnel` / `fact_turnover_rate` 가 **서로 다른 테이블**로 공존하므로 충돌 0.
- **엑셀 파일별 분기는 `schema.yaml` 의 `sources` 블록이 담당** — 인원현황 엑셀 → `fact_headcount` 적재, 지원조직 엑셀 → `fact_support_personnel` 적재, 퇴사율 엑셀 → `fact_turnover_rate` 적재. extract 코드가 `sources` 블록을 읽어 "어느 엑셀 → 어느 테이블" 라우팅.
- **즉 ddl.sql 증분은 "DuckDB 에 새 테이블 칸 추가"** 일 뿐, 직전 plan 의 인원 테이블에 영향 없음. 같은 .sql 한 파일에 모두 적어도 / 별도 파일로 나눠도 결과 동일 — 본 plan 은 한 파일에 모두 두는 방식 (관리 편의).

```
[ddl.sql 한 파일]
├─ CREATE TABLE dim_bu              ← 직전 plan
├─ CREATE TABLE dim_employment_type ← 직전 plan
├─ CREATE TABLE fact_headcount      ← 직전 plan (인원현황 엑셀)
├─ CREATE TABLE fact_related_personnel ← 직전 plan (관계인력 시트)
├─ CREATE TABLE fact_support_personnel ← 본 plan (지원조직 엑셀)  ← 신규
├─ CREATE TABLE fact_turnover_rate     ← 본 plan (퇴사율 엑셀)    ← 신규
├─ CREATE VIEW view_dashboard_bus      ← 직전 plan
├─ CREATE VIEW view_support_by_bu      ← 본 plan                  ← 신규
└─ CREATE VIEW view_turnover_timeline  ← 본 plan                  ← 신규
```

```sql
-- ─── 지원조직 fact (직군 분해 — fact_headcount 와 grain 일치) ───
-- BU level=1 + 지원조직 단위. 4직군 분해 (EXEC/MGMT/OPER/FIELD/CONT 중 4개).
-- 2023 의 M/S·P3·P2 직군 (블록1) 은 본 테이블 미적재 (raw 보존).
CREATE TABLE fact_support_personnel (
  year                INTEGER,
  quarter             INTEGER,                     -- 5/1 → 2 고정
  bu_id               VARCHAR,                     -- dim_bu 참조 (view 에서 effective join)
  support_org_name    VARCHAR NOT NULL,            -- raw 조직명 (예: "식품통합_지원조직(경영지원/브랜드본부/구매)")
  support_category    VARCHAR,                     -- '전사지원' | '사업지원' (B/L 컬럼)
  emp_type_code       VARCHAR REFERENCES dim_employment_type(emp_type_code),
  headcount           INTEGER,                     -- TO (계획)
  headcount_actual    INTEGER,                     -- 5/1 실제
  source_file         VARCHAR,
  source_row          INTEGER,
  PRIMARY KEY (year, quarter, support_org_name, emp_type_code)
);

-- ─── 퇴사율 fact (BU level=1 grain) ───
-- 4개년 회고 + 당해 예측치를 한 테이블에 누적. is_forecast 플래그로 구분.
-- 같은 연도 row 가 (예측치 → 확정치) 로 update 가능 → PK 에 is_forecast 포함하지 않음.
CREATE TABLE fact_turnover_rate (
  year                INTEGER,
  quarter             INTEGER,                     -- 5/1 → 2 (예측치) / 12/31 → 4 (확정치)
  bu_id               VARCHAR,
  headcount_year_end  INTEGER,                     -- 재직자수 (확정: 12/31 / 예측: 5/1)
  leaver_count        INTEGER,                     -- 퇴사자수 (확정: 1.1~12.31 / 예측: 1.1~5.1)
  turnover_rate       DECIMAL(8,6),                -- leaver / year_end (raw 그대로 — 예측치는 부분)
  turnover_rate_annualized DECIMAL(8,6),           -- 예측치 연환산 (rate × 3). 확정치는 NULL
  is_forecast         BOOLEAN NOT NULL,            -- TRUE = 5/1 부분치 기반 예측, FALSE = 12/31 확정
  source_file         VARCHAR,                     -- 어느 파일에서 적재됐는지 (replay 용)
  source_row          INTEGER,
  PRIMARY KEY (year, quarter, bu_id)
);

-- 대시보드 view: 지원조직 rollup (BU level=1 단위 합산)
CREATE VIEW view_support_by_bu AS
SELECT
  s.year,
  s.quarter,
  s.bu_id,
  b.bu_name,
  s.support_category,
  SUM(CASE WHEN s.emp_type_code = 'EXEC'  THEN s.headcount END) AS exec_cnt,
  SUM(CASE WHEN s.emp_type_code = 'MGMT'  THEN s.headcount END) AS mgmt_cnt,
  SUM(CASE WHEN s.emp_type_code = 'OPER'  THEN s.headcount END) AS oper_cnt,
  SUM(CASE WHEN s.emp_type_code = 'FIELD' THEN s.headcount END) AS field_cnt,
  SUM(CASE WHEN s.emp_type_code = 'CONT'  THEN s.headcount END) AS cont_cnt,
  SUM(s.headcount)         AS to_total,
  SUM(s.headcount_actual)  AS actual_total
FROM fact_support_personnel s
JOIN dim_bu b ON b.bu_id = s.bu_id
GROUP BY s.year, s.quarter, s.bu_id, b.bu_name, s.support_category;

-- 대시보드 view: 퇴사율 timeline (BU 별 4개년 + 당해 예측치)
CREATE VIEW view_turnover_timeline AS
SELECT
  t.year,
  t.bu_id,
  b.bu_name,
  t.headcount_year_end,
  t.leaver_count,
  t.turnover_rate,
  t.turnover_rate_annualized,
  t.is_forecast
FROM fact_turnover_rate t
JOIN dim_bu b ON b.bu_id = t.bu_id
ORDER BY t.bu_id, t.year;

-- 직군 alias 보강 (employment_type_mapping 에 추가 alias 만)
-- ※ DDL 변경 없음 — schema.yaml 만 갱신 (§3.2)
```

### 3.2 `pipeline/schema.yaml` 에 추가될 sources 블록

```yaml
# (직전 plan 의 sources 블록 끝에 append)

  # ─── 지원조직 2025 ───
  spt_2025:
    file_glob: "10-RAW/HC/2025.05/2.지원조직_*.xlsx"
    year: 2025
    quarter: 2
    primary_sheet:
      sheet_name: "Sheet1 (3)"                # raw 시트명 그대로 (개정 시 fuzzy match)
      header_rows: [9, 11]                    # R9 카테고리, R11 직군 분해
      data_start_row: 13
      data_end_row: 31                        # R32 = 소계, R33 = 합계 → skip
      # 우측 블록만 사용 (좌측 D~J 는 전년도 비교 — 적재 skip)
      bu_columns:
        category: L                           # '전사지원' | '사업지원'
        org_name: M                           # 지원조직명
      to_column: N                            # 25년 TO 경영간부
      emp_type_columns:                       # R11 직군 분해 (우측 블록 N~Q)
        N: EXEC                               # 경영간부 (사용자 코멘트: 풀무원 경영간부 = EXEC 매핑)
        O: OPER                               # 운영직
        P: FIELD                              # 현장직
        Q: CONT                               # 계약직 (2024 임시직과 동일 코드)
      actual_columns:                         # 25/5/1 현재 인원 (R11 S~V)
        S: EXEC
        T: OPER
        U: FIELD
        V: CONT
      subtotal_skip:
        - column: C
          values: ["소계"]
        - column: M
          values: ["소계"]
        - column: B
          values: ["지원 인력 합계"]
        - column: L
          values: ["지원 인력 합계"]

  # ─── 지원조직 2024 ───
  spt_2024:
    file_glob: "10-RAW/HC/2024.05/2.지원조직_*.xlsx"
    year: 2024
    quarter: 2
    primary_sheet:
      sheet_name: "Sheet1"
      header_rows: [9, 11]
      data_start_row: 13
      data_end_row: 30                        # R31/R32 = 소계/합계
      bu_columns:
        category: L
        org_name: M
      emp_type_columns:                       # 우측 (24년 TO)
        N: EXEC
        O: OPER
        P: FIELD
        Q: CONT                               # "임시직" → CONT alias
      actual_columns:
        S: EXEC
        T: OPER
        U: FIELD
        V: CONT
      subtotal_skip:
        - column: C
          values: ["소계"]
        - column: M
          values: ["소계"]
        - column: L
          values: ["지원 인력 합계"]

  # ─── 지원조직 2023 — 블록2만 적재 (블록1 skip) ───
  spt_2023:
    file_glob: "10-RAW/HC/2023.05/2.지원조직인력_*.xlsx"
    year: 2023
    quarter: 2
    primary_sheet:
      sheet_name: "지원조직"
      # 블록1 (R3~R24) skip — 직군 5종 (M/S/P3/P2) 이 24/25 와 호환 안 됨
      block_skip_rows: [3, 24]
      header_rows: [31, 33]                   # 블록2 헤더
      data_start_row: 35
      data_end_row: 52                        # R45 소계, R52 소계, R53 합계 skip
      bu_columns:
        category: B                           # '전사지원(HQ)' | '사업지원'
        org_name: C
      emp_type_columns:                       # 블록2 (D~G = 23년 TO)
        D: EXEC                               # 경영간부
        E: OPER                               # 운영직
        F: FIELD                              # 현장직
        G: CONT                               # 임시직
      actual_columns:                         # 5/1 현재 (I~L)
        I: EXEC
        J: OPER
        K: FIELD
        L: CONT
      subtotal_skip:
        - column: C
          values: ["소계"]
        - column: B
          values: ["지원 인력 합계"]

  # ─── 퇴사율 2025 ───
  tur_2025:
    file_glob: "10-RAW/HC/2025.05/3.퇴사율현황*.xlsx"
    file_year: 2025
    primary_sheet:
      sheet_name: "퇴사율현황"
      header_rows: [1, 2, 3]
      data_start_row: 4
      data_end_row: 26                        # R27 = 전사 총계, R28 = 국내 → skip
      bu_columns:
        category: A                           # 부문 (forward-fill)
        bu_name: B                            # BU 명
      year_blocks:                            # 사용자 답변: 2025 파일은 22/23/24 confirmed + 25 forecast
        - year: 2025
          is_forecast: true
          headcount_column: C                 # 5/1 재직자
          leaver_column: D                    # 1.1~5.1 퇴사자
          rate_column: E
          rate_annualized_column: F
          quarter: 2
        - year: 2024
          is_forecast: false
          headcount_column: G                 # 24.12.31 재직자
          leaver_column: H                    # 24년 퇴사자
          rate_column: I
          quarter: 4
        - year: 2023
          is_forecast: false
          headcount_column: J
          leaver_column: K
          rate_column: L
          quarter: 4
        - year: 2022
          is_forecast: false
          headcount_column: M
          leaver_column: N
          rate_column: O
          quarter: 4
        # year=2021 은 본 파일에서 skip — 2024 파일이 적재
      validation:
        total_row: 27                         # 전사 총계 anchor
        total_headcount_column: C             # 2886
        domestic_row: 28                      # 국내 소계 2108
        overseas_row: 36                      # 해외 소계 778

  # ─── 퇴사율 2024 — 가장 옛 회고 (2021) 만 적재 ───
  tur_2024:
    file_glob: "10-RAW/HC/2024.05/3.퇴사율현황*.xlsx"
    file_year: 2024
    primary_sheet:
      sheet_name: "퇴사율현황"
      header_rows: [5, 6, 7]                  # 1년 shift
      data_start_row: 8
      data_end_row: 21
      bu_columns:
        bu_name: B                            # 부문 컬럼 없음
      year_blocks:                            # 사용자 답변: 2024 파일은 2021 만 적재 (나머지 양보)
        - year: 2021
          is_forecast: false
          headcount_column: M
          leaver_column: N
          rate_column: O
          quarter: 4
        # year=2022/2023/2024 는 본 파일에서 skip — 2025 파일에서 더 안정된 값 사용
      validation:
        total_row: 22
        domestic_row: 23
        overseas_row: 31

# 직군 alias 보강 (employment_type_mapping 갱신 부분만)
employment_type_mapping:
  EXEC:
    aliases: ["임원", "대표", "EXEC", "본부장 이상", "Executive", "경영진", "경영간부"]
    # ※ 지원조직 시트의 "경영간부" 는 EXEC 으로 매핑 (BU별 1명 패턴 — 풀무원 호칭 관습)
    # ※ 인원 '요약' 시트의 "경영간부직" (R6 L 컬럼) 은 여전히 MGMT (다년 다수 인력)
    # 시트별 컨텍스트 분기 필요 — extract_excel.py 에서 sheet_name 기준 매핑
  CONT:
    aliases: ["계약직", "계약", "임시직", "임시직원", "임시"]
    # 지원조직 2024 "임시직" → 2025 "계약직" 으로 명칭 변경. 동일 코드.

# 퇴사율 BU 명 → dim_bu 매핑 보강 (기존 bu_aliases 에 추가)
bu_aliases:
  - canonical: "Corp"
    aliases: ["전사지원", "Corp.", "Corp"]
  - canonical: "CSO"
    aliases: ["풀무원_전략경영원(CSO)", "CSO"]
  - canonical: "CTO"
    aliases: ["풀무원_풀무원기술원(CTO)", "CTO"]
  # 기존 식품통합/샘물/다논/NA/중국/일본/푸드앤컬처 는 직전 plan bu_aliases 사용
```

### 3.3 매핑 규칙 명세 (P2 extract 단계용)

1. **지원조직 "경영간부" → EXEC 매핑 (시트 컨텍스트 분기)**:
   - HC 인원현황 '요약' 시트의 "경영간부직" = MGMT (R6 L 컬럼, BU별 다수)
   - 지원조직 시트의 "경영간부" = EXEC (지원조직별 1명 패턴, BU 대표급)
   - extract_excel.py 에서 `source.sheet_name in ['Sheet1', 'Sheet1 (3)', '지원조직']` 면 EXEC 매핑

2. **퇴사율 BU drift 흡수**: 퇴사율 시트는 BU 명 표기가 짧음 ("Corp" / "CSO"). `bu_aliases` 의 canonical name 으로 정규화 후 `dim_bu.bu_id` lookup. effective_from/to 로 연도별 BU 매칭.

3. **`is_forecast` 갱신 룰 (향후 2026 파일 적재 시)**:
   ```
   2026 파일 적재 시 → year=2025 의 기존 row (is_forecast=TRUE) 를
   2026 파일의 G열(2025.12.31 재직자) / H열(2025년 퇴사자) 값으로 UPDATE,
   is_forecast=FALSE 로 변경 + quarter=4 갱신
   ```
   → extract_excel.py 는 INSERT 가 아닌 UPSERT 패턴 사용 (PK = year+quarter+bu_id 충돌 시 갱신)

---

## 4. 핵심 설계 결정

| 결정 | 채택 | 기각안 / 이유 |
|---|---|---|
| 지원조직 2023 블록 처리 | **블록2 (R31~R53) 만 적재, 블록1 skip** | 블록1 직군(M/S/P3/P2) 이 24/25 와 호환 안 됨 → 시계열 비교 불가. raw 보존만 |
| 임시직 vs 계약직 | **`CONT` 코드 통일 + alias 보강** | 별도 코드 분리 → emp_type 표 부풀림 |
| 지원조직 grain | **`(year, quarter, support_org_name, emp_type_code)`** | bu_id 만으로는 "지원조직 단위" 표현 불가 (같은 BU에 여러 지원조직) |
| 퇴사율 회고 컬럼 처리 | **각 파일에서 가장 옛 회고 1개 + 최신 파일이 confirmed truth (사용자 답변)** | latest-file-wins all, all-rows long-format — 중복 또는 row 폭증 |
| 예측치 처리 | **`is_forecast` BOOLEAN + 같은 PK 로 UPSERT** | 별도 테이블 분리 → join 부담 |
| `turnover_rate_annualized` | **DDL 별도 컬럼** (5/1 × 3 식) | view 에서 계산 → raw 식 보존 못함 (E·F 컬럼 둘 다 raw) |
| PII 사원 시트 | **본 plan 제외 (사용자 확정)** | 본 plan 에서 정의 → scope 부풀림. 별도 plan 으로 분리 |
| 퇴사율 grain | **BU level=1 (요약치)** | 사원 단위 → PII 시트에서 처리 (별도 plan) |
| 부문(category) 컬럼 | **`support_category` 만 보존, `dim_bu` 에 별도 row 안 만듦** | 부문 = (국내식품제조유통 등) 은 BU 보고용 그룹이지 조직 단위 아님 |

---

<span style="color:red">## 5. 위험 / 미결 — 코멘트 ⑤ 반영: 비개발자 친화 설명 + 모호점 2건 확정</span>

> 💬 **사용자 원본 코멘트 5**: "전체 다 이게 무슨 뜻? 비개발자 입장 쉽게 다시 알려주고 모호한 사항은 askuserquestion 을 반드시 사용해서 결정"

각 위험을 "왜 문제가 되나 → 어떻게 막나" 2 단계로 풀어 설명. 모호점 2건은 askquestion 으로 결정 완료 (각 위험 끝에 "사용자 확정" 표기).

---

### 위험 1. 지원조직 시트명이 매년 바뀐다 (예: `Sheet1` → `Sheet1 (3)`)

**왜 문제가 되나**: 코드가 "정확한 시트명"으로 엑셀을 열면, 시트명이 바뀌는 순간 빌드가 실패한다. 풀무원 인사팀이 매년 엑셀을 새로 만들 때 시트명을 임의로 바꿔온 이력이 있음:
- 2023 = `지원조직`
- 2024 = `Sheet1`
- 2025 = `Sheet1 (3)` ← 파워포인트 붙여넣기로 시트가 늘어나면서 자동 번호 부여

**어떻게 막나 (사용자 확정 — askquestion 응답)**:
- ① 우선 `schema.yaml` 에 명시한 정확한 시트명으로 열기 시도
- ② 실패하면 fuzzy fallback — `Sheet*` 패턴 + 시트 안 9행 1번째 컬럼이 "구분" 인지 / 11행 5번째 컬럼이 "경영" 인지 확인 → 매치되면 그 시트가 지원조직 시트
- ③ 둘 다 실패하면 빌드 중단 + 사용자 안내 ("시트명이 바뀌었습니다. schema.yaml 갱신 필요")

---

### 위험 2. 퇴사율 시트의 BU 명이 매우 축약되어 `dim_bu` 와 매칭 안 될 수 있다

**왜 문제가 되나**: 퇴사율 시트는 "Corp" / "CSO" / "직속" 같이 짧게 적혀 있는데, `dim_bu` 마스터에는 "풀무원_전략경영원(CSO)" 같이 풀네임으로 저장돼 있음. 코드가 그대로 join 하면 매칭 실패 → 그 BU 의 퇴사율 데이터가 통째로 누락.

**어떻게 막나**:
- `schema.yaml` 의 `bu_aliases` 에 미리 매핑 등록 ("Corp" ↔ "전사지원" ↔ "Corp." 모두 같은 BU)
- 첫 빌드 시 매칭 실패한 BU 목록을 화면에 출력 → 사용자가 보고 alias 추가 → 재빌드
- 매년 1회 정도 새 BU 가 추가될 때 같은 패턴 반복 (5분 작업)

---

### 위험 3. 예측치(2025 5/1 부분치) 가 다음 해에도 확정치로 안 바뀌고 남는다

**왜 문제가 되나**: 2025 파일은 2025년 5/1 시점 부분 데이터를 "예측치"로 적재 (`is_forecast=TRUE`). 1년 후 2026 파일이 들어오면 2025 의 *진짜* 1년치 확정 데이터가 G/H 컬럼에 있음 → 기존 예측치 row 를 확정치로 update 해야 함. 깜빡 잊으면 통계 그래프에 "2025 = 예측치" 가 계속 박혀 있게 됨.

**어떻게 막나**:
- extract 코드에 명시적 UPSERT 패턴 — 같은 PK `(year=2025, quarter=4, bu_id)` 가 이미 있으면 update + `is_forecast=FALSE` 로 강제 전환
- 검증 SQL 1줄: `SELECT * FROM fact_turnover_rate WHERE is_forecast=TRUE AND year < <현재년도>` 결과가 0 행이어야 통과
- 위 SQL 을 build_dashboard.py 가 매번 실행해 0 이 아니면 경고 출력

---

### 위험 4. DB 에 적재된 합계가 엑셀 합계와 안 맞는다 (수치 검증)

**왜 문제가 되나**: 엑셀 매핑·skip 룰 어딘가에서 한 줄이라도 빠지거나 중복 합산되면 전체 인원수·퇴사율이 어긋난다. 빌드가 "에러 없이 성공" 해도 통계가 틀린 무서운 상황.

**어떻게 막나 — 시트의 합계 셀을 anchor 로 매번 자동 대조**:

| 영역 | 검증 anchor (엑셀 시트) | DuckDB SQL | 일치해야 할 값 |
|---|---|---|---|
| 지원조직 actual 합계 | 33행 S+T+U+V (2025 파일) | `SELECT SUM(headcount_actual) FROM fact_support_personnel WHERE year=2025` | 622 (= 39+537+3+43) |
| 지원조직 TO 합계 | 33행 N+O+P+Q (2025 파일) | `SELECT SUM(headcount) FROM fact_support_personnel WHERE year=2025` | 647 (= 39+565+4+39) |
| 퇴사율 전사 재직자 | 27행 C (2025 파일) | `SELECT SUM(headcount_year_end) FROM fact_turnover_rate WHERE year=2025 AND is_forecast=TRUE` | 2886 |
| 퇴사율 전사 퇴사자 | 27행 D (2025 파일) | `SELECT SUM(leaver_count) FROM fact_turnover_rate WHERE year=2025 AND is_forecast=TRUE` | 99 |

- 차이 발견 시: 어느 BU 가 누락 / 중복인지 자동 진단 SQL 출력 → 사용자 확인 후 schema.yaml 패치

---

### 위험 5. 지원조직 시트 좌측 블록(전년도 비교 데이터) 적재 여부

**왜 문제가 되나**: 2024/2025 파일의 D~J 컬럼은 "전년도 비교"용 데이터인데, 같은 데이터가 직전 plan 의 인원현황 '요약' 시트에서도 적재됨 → 중복 적재하면 같은 사람 2번 셈.

**어떻게 막나 (사용자 확정 — askquestion 응답)**:
- 좌측 블록은 **skip** (현재 plan 유지) — 인원현황 '요약' 시트가 이미 같은 연도 데이터를 BU 단위로 cover
- 좌측 블록은 raw 엑셀에만 보존, DB 적재 X
- 향후 "지원조직 단위 시계열 추이" 필요 시 별도 plan 으로 재개

---

## 6. 검증 — 비개발자 점검 가이드

### 6.1 Claude 자동 실행

```
python -c "import yaml; yaml.safe_load(open('pipeline/schema.yaml'))"     → OK
duckdb :memory: < pipeline/ddl.sql                                         → 7개 테이블·뷰 생성
```

### 6.2 사용자 점검 5가지

#### 점검 ① — 지원조직 4직군 매핑 정확성

| 시트 직군 라벨 | Claude 매핑 | 사용자 확인 |
|---|---|---|
| 경영간부 | EXEC | ☐ 맞음 / ☐ MGMT 가 맞음 |
| 운영직 | OPER | ☐ |
| 현장직 | FIELD | ☐ |
| 임시직 (2024) / 계약직 (2025) | CONT (통일) | ☐ |

#### 점검 ② — 지원조직 2023 블록1 (M/S/P3/P2) 무시 OK?
- ☐ OK (24/25 와 호환 안 되므로 skip 적절)
- ☐ 블록1 도 필요 — 별도 fact 테이블 만들어야

#### 점검 ③ — 퇴사율 예측치 처리 룰
사용자 답변 정형화:
- 2025 파일 → 2022/2023/2024 confirmed + 2025 예측치
- 2024 파일 → 2021 confirmed 만
- ☐ 이 룰 OK / ☐ 다른 룰

#### 점검 ④ — 검증 anchor 적합성

| 영역 | 검증 anchor | 기대치 (2025) |
|---|---|---|
| 지원조직 TO 합계 | 시트 R33 N+O+P+Q | 39 + 565 + 4 + 39 = 647 |
| 지원조직 actual 합계 | 시트 R33 S+T+U+V | 39 + 537 + 3 + 43 = 622 |
| 퇴사율 전사 재직자 | 시트 R27.C | 2886 |
| 퇴사율 전사 퇴사자 | 시트 R27.D | 99 |

#### 점검 ⑤ — BU 명 매칭 (alias 보강 필요한 누락)
첫 빌드 후 매칭 실패 목록 사용자 확인 round 1회.

---

## 7. 비-목표 / 본 plan 마무리

### ✓ 본 plan 안에서 마무리되는 항목
- `fact_support_personnel` / `fact_turnover_rate` DDL 정의 — `pipeline/ddl.sql` 에 append
- `spt_2023` / `spt_2024` / `spt_2025` / `tur_2024` / `tur_2025` schema.yaml sources 블록
- 직군 alias 보강 + BU alias 보강 (`employment_type_mapping` + `bu_aliases`)

### ✗ 본 plan 의 비-목표
- 25년 퇴사자·재직자 등 PII 시트 (사용자 확정 제외) — 별도 plan
- 인건비·HCROI — 다른 plan
- extract_excel.py / load_duckdb.py 코드 (P2/P3 별도 plan)

---

## 8. 진행 절차

1. 본 plan 사용자 재검토 → 추가 코멘트 반영 후 v2.0 확정
2. `구현해줘` 명시 신호 받으면:
   - `pipeline/ddl.sql` 에 §3.1 의 3개 신규 객체 append (Edit)
   - `pipeline/schema.yaml` 에 §3.2 의 5개 sources + alias 보강 append (Edit)
3. §6.1 자동 검증 통과 확인
4. result 파일 작성 (`archive/dashboard/result-spt-tur-260512.md`)
5. P2 (`extract_excel.py`) plan 으로 진입 — HC + 지원조직 + 퇴사율 통합 extract
