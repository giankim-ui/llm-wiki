# Plan: HC backdata DuckDB 스키마 설계 (P1)

작성일: 2026-05-12
선행: `archive/handoff-schema-260511.md`, `archive/plan-dash-research-260511.md`
대상 산출물: **schema.yaml + ddl.sql 2개 파일만** (extract/load/HTML 패치는 별도 plan)

> <span style="color:red">**📝 현재 라운드 = 코멘트 16 (raw 추가 검증 + DDL SCD Type 2 정정)**</span>
>
> <span style="color:red">**raw 발견 1**: A 컬럼 마크는 '소' 가 아니라 **'계'** (예: "식품통합 MBU계"). 2023 은 A 컬럼 거의 비어있어 **C 컬럼 어미 '계'** 로 합계 행 식별. → §2.1·§4.2 schema.yaml `subtotal_marker` 룰 정정</span>
>
> <span style="color:red">**raw 발견 2**: '전사총계' R26 검증 수식은 **2025 만 존재** (9개 셀: J23=D23+G23, R23=J23+O23, X23=R23+U23 등 누적 합산 검증). 2023/2024 는 R26 없음 → 다른 anchor 필요 → §7 위험 5 명세 정정</span>
>
> <span style="color:red">**raw 발견 3**: 2025 시트 목록에 '온라인' 이미 존재 → dim_bu seed 시점 오류. 2025 = 독립 BU, 2026 = 식품통합 산하. SCD Type 2 패턴 적용 (PK = bu_id + effective_from)</span>

> 💬 **사용자 원본 코멘트 16**: "응 진행하자" (직전 메시지에서 제안한 raw 추가 검증 + DDL 정정 진행 신호)

---

## 1. Context — 왜 이 plan 인가

`handoff-schema-260511.md` 의 Q1~Q4 결정 대기 4건이 해소되지 않은 채 멈춰 있었다. 사용자는 직전 `plan-backdata-hc-260512.md` 에서 **인원(HC)만 먼저 깊게 분석**할 것을 지시했고, 본 plan 에서 실 엑셀 3개년을 deep dive 한 결과를 토대로:

- handoff Q1~Q4 의 최종 조합을 **사용자 확정 답으로 갱신** (아래 §3)
- **2023 / 2024 / 2025 3개년 schema diff 를 본 plan 에서 *함께 검토* (적재 X, 검토 only)** (코멘트 10 의도 정정 반영)
  - **의도 정정**: 본 plan 은 3개년 데이터를 한 번에 *적재* 하는 게 아니라, **3개년 schema diff 를 함께 검토** 하여 이후 연도(2022·2026·2027 등) 확장 시에도 같은 스키마로 적재 가능한 **견고한 schema** 를 확보한다. 실 적재는 P3 (load_duckdb.py) 로 분리.
  - DDL 은 한 벌 (연도 무관), schema.yaml 의 `sources` 블록은 3개년 diff 흡수 패턴을 **미리 제시** (실 적재 코드는 다음 plan)
  - 2025 → '요약' 시트 leaf grain (BU→부문/실 2단계), 2023/2024 → '전사총계' 시트 BU level (구조 drift 확인됨)
- 본 phase 산출은 **schema.yaml + ddl.sql** 두 파일에 한정 (extract/load 는 다음 plan)

목적: extract_excel.py 작성 직전까지의 "데이터 모델 합의" 를 1 회 닫는다 — **3개년 schema diff 검토 + 향후 연도 확장 견고성 확보**.

---

## 2. 실 엑셀 구조 — 사실 정리 (deep dive 결과)

### 2.1 인원현황 1번 파일 (1.인원현황_풀무원 전사_v0.66_취합_250519...xlsx)

**시트 28개**, 본 plan 이 사용하는 시트만:

| 시트 | 크기 | 헤더 위치 | 데이터 행 | 본 plan 용도 |
|---|---|---|---|---|
| `요약` | 212×33 | R4~R6 (병합 41건) | R7~R212 | **fact_headcount 의 primary source** |
| `관계인력(PPT)` | 35×21 | R2~R3 | R16~R35 (A1:E15 더미 제외) | **fact_related_personnel** |
| `전사총계` | 32×30 | R2~R4 | R5~R25 | **검증 대조표** (P3 검증 SQL) |
| 백데이터 (식품통합MBU, 샘물, CFO 등 23개) | 가변 | 가변 | 가변 | 본 phase scope 외 (참조 only) |

**요약 시트 컬럼 (실 헤더 재확인 2026-05-12 — 코멘트 1·2 반영):**
| 셀 | 헤더 (R4~R5 원문) | 의미 | 본 plan 매핑 |
|---|---|---|---|
| A | (병합 헤더 없음) | 소계 마크 (실제는 **'계'** 텍스트) — **단 2025 만 채워있고 2023 거의 비어있음** | <span style="color:red">합계 행 식별은 'C 컬럼 어미가 "계"' 룰로 (3개년 통용)</span> |
| B | "사업단위" | **MBU / SBU** = `bu_level=1` | MBU 의 첫 행에만 채워있고 이하 빈 셀 → forward-fill 필요 |
| C | "부문/실" | **본부 단위 (부문·실·팀)** = `bu_level=2` | 본 plan 의 grain leaf |
| D | "25년 T/O" | **당해연도 T/O 인원 (계획)** | `fact_headcount.headcount` 핵심 컬럼 |
| E | "25년도 감원인원" | 당해연도 실제 감원 | 본 plan 미사용 (별도 fact 가능) |
| F~AD | "증감/사유", "기준일자", "퇴직(원직/공채)" 등 | 직군별 분해 + 변동 지표 | schema.yaml 매핑 (§4.3) |

> 사용자 코멘트 1 ("본부/실 컬럼 추가") 반영: C 컬럼이 이미 엑셀 헤더 상 **"부문/실"** 임 — 표에 명시.

**연도 일반화 (코멘트 2 반영):**

D 컬럼은 매년 "당해 스냅샷 연도의 T/O 인원". DDL 컬럼명은 `headcount` 로 일반화하고, **연도는 `fact_headcount.year` 가 보유**한다. 본 plan 의 전략:

- **DDL 은 한 벌** (`fact_headcount`, `dim_bu` 등은 연도 무관)
- **schema.yaml 의 `sources` 블록만 연도별 분리** (`hc_2023`, `hc_2024`, `hc_2025`, `hc_2026`…) — 각자 시트명·헤더 행·컬럼 매핑 보유
- 향후 빌드 시 (P2/P3 별도 plan) `extract_excel.py` 가 모든 sources 를 순회 적재 → `fact_headcount` 한 테이블에 multi-year row 누적. 본 plan 은 그 패턴을 schema 레벨에서 미리 확정만 한다.

→ "25년도" 라는 표현은 본 plan 본문에서 "당해연도" 또는 "스냅샷 연도" 로 통일. 코드/DDL/스키마 컬럼명에는 연도 hardcode 금지.

**관계인력(PPT) 시트 (확정):**

```
A1:E15 : 더미 (무시)
F열~U열 (R16~) : 사업단위별 관계인력 (파견·용역)
  G : 사업단위
  H : 25년도 T/O
  I : 실제 인원
  J~N : 변동 지표
  R17 합계: head=4395, actual=2663 (참고치)
```


**전사총계 시트 (실 헤더 재확인 2026-05-12 — 사용자 코멘트 3 'G=예산?' 정정):**
R2~R4 가 3단 병합 헤더. 정확한 컬럼:

| 셀 | R3 카테고리 | R4 메트릭 | 의미 |
|---|---|---|---|
| A | — | — | 사업단위명 (예: "식품통합 MBU요약") |
| B | — | — | 부문 (예: "음료식품군내수사업부") |
| C | — | — | 사업단위 short (예: "식품통합 MBU") |
| **D** | **경영진/임원** | 25년 TO | EXEC 직군 계획 인원 |
| E | 경영진/임원 | 현재 | EXEC 직군 실제 인원 |
| F | 경영진/임원 | TO대비 | (현재 - TO) |
| **G** | **관리 (사무직)** | 25년 TO | **MGMT/OPER 직군 계획 인원** (※ "예산" 아님!) |
| H | 관리 | 현재 | 관리 직군 실제 인원 |
| I | 관리 | TO대비 | (현재 - TO) |
| **J** | **소계** | 25년 TO | D + G 합 (전체 인원) |
| K | 소계 | 현재 | E + H 합 |
| L | 소계 | TO대비 | (현재 - TO) |
| **M** | **관계인력** | 25년 TO | CONT 직군 (파견·용역) 계획 |
| N | 관계인력 | 현재 | CONT 실제 |

> 사용자 코멘트 정정: G 는 "예산" 이 아니라 **"관리(사무직) 직군의 25년 TO 인원수"**. 인원 엑셀에 예산 금액은 없음. (이전 분석 오류 — Explore agent 의 헤더 추론 실패. 본 라운드에서 raw R4 헤더 'TO\n대비' 등 재확인 후 정정.)

**전사총계 행 구조:**

| 행 | 의미 |
|---|---|
| R5~R22 | 21개 사업단위별 데이터 |
| **R23** | **전체 합계** (검증 anchor — D=142, G=2662, J=2804, M=74) |
| R24 | 국내 소계 |
| R25 | 해외 소계 |

→ 본 plan 의 검증 anchor: `fact_headcount` 적재 후 SUM(headcount) == 전사총계 R23.J (= 2804) 또는 부분 직군별로 D/G/M 매칭.

### 2.2 지원조직 / 퇴사율 — 본 plan scope 외

사용자 지시 ("우리는 '요약', '관계인력(PPT)' 만 기반 데이터로 있으면 됨") 에 따라 본 phase 미사용. drift 만 기록:

- 지원조직: 2023(R5 헤더, 1행)→2024(R11, 4행 multi-header)→2025(동일) — P6 진입 시 헤더 위치 분기 처리
- 퇴사율: 2024(요약만)→2025(요약+개인 이력 4시트, 분기 컬럼 추가) — fact_turnover 는 별도 phase

### 2.3 2023/2024/2025 drift — 코멘트 14 raw deep dive 결과 정정

이전 분석은 시트명을 뒤바꿔 보고함. 실제 raw cell dump 결과:

| 항목 | 2023.05 | 2024.05 | 2025.05 | 본 plan 대응 |
|---|---|---|---|---|
| 인원 1번 시트 수 | 19 | 20 | 28 | 연도별 sources 블록 |
| **'요약' 시트 크기** | **187×33** | **190×33** | **212×33** | **3개년 모두 '요약' 시트 primary (leaf grain 동일)** |
| **'전사총계' 시트 크기** | **25×27** | **24×28** | **32×30** | 검증 anchor 만 사용 (적재 X) |
| '요약' R4 헤더 | B=사업단위, C=본부/실 | B=사업단위, C=본부/실 | B=사업단위, C=본부/실 | **3개년 100% 일치** |
| '요약' R6 직군 분해 | 경영간부직/운영관리·연구전문/운영실무직 | 동일 | 동일 | **3개년 100% 일치** |
| BU drift 처리 | 로하스케어_SBU | 건강생활_SBU | 건강케어MBU + 건강생활 | `dim_bu.effective_from/to` 같은 조직 시계열 연결 (코멘트 14-1) |
| 2025 신규 BU | — | — | CHO, CCO, Corp, CFO, COO, FI, B2E, 리빙케어, 온라인 | 2023/2024 의 통합운영FU·CSO·직속 분화 (코멘트 14-3) |

> **핵심 정정**: 이전 plan 의 "radical re-layout / 2023~2024 BU only / 2025 부문/실 leaf" 결론은 시트명 혼동에서 비롯한 오류. 실제로는 **3개년 '요약' 시트가 cell-level 거의 동일** (연도 prefix '23/'24/'25 만 다름). 따라서 schema.yaml 의 hc_2023 / hc_2024 / hc_2025 블록이 거의 같은 구조로 통일됨 → 견고성 확보 ✅

---

## 3. handoff Q1~Q4 최종 답 (사용자 확정)

| 항목 | handoff 추천 | 본 plan 확정 | 근거 |
|---|---|---|---|
| Q1. BU 트리 깊이 | C (N단계 재귀) | **C** | 요약 시트가 MBU→부서→팀 3단계까지 있어 N단계 보장 필요 |
| Q2. 직군 axis | A (5종) | **A** | 임원 분리 명시. EXEC/MGMT/OPER/FIELD/CONT |
| Q3. PII 처리 | A (2-layer) | **A** | `_internal.duckdb` 로컬, `hr.duckdb` 공유. .gitignore 필수 |
| Q4. 본 phase UI | A (mockup 유지) | **A** | drill-down UI 는 phase 외 |
| **신규 Q5**. schema 검토 시계열 | — | **2023/2024/2025 3개년 schema diff *검토* (적재 X — 실 적재는 다음 plan)** | 코멘트 10 — 향후 연도 확장 견고성 확보 |
| **신규 Q6**. 인원 grain | — | **3개년 모두 '요약' 시트 부문/실 leaf (코멘트 14 deep dive 정정)** | 시트명 혼동 정정 — 3개년 동일 |
| **신규 Q7**. 직군 매핑 | — | **6종: EXEC/MGMT/OPER/FIELD/CONT(계약직)/PART(관계인력) — 코멘트 14-2** | 풀무원 실제 분류 (옵션 2 + CONT 재정의 + 관계인력 추가) |
| **신규 Q8**. P1 scope | — | **schema.yaml + ddl.sql 만** | extract/load 는 다음 plan |

---

## 4. P1 산출물 — schema.yaml + ddl.sql

### 4.1 `pipeline/ddl.sql` (Postgres 호환 부분집합)

```sql
-- 사업단위 마스터 (SCD Type 2 — 같은 bu_id 가 시계열로 여러 row, 코멘트 16 raw 검증)
-- 이름·parent_id 변경 = 새 row + effective_from 진입. 이전 row 의 effective_to 종료.
CREATE TABLE dim_bu (
  bu_id           VARCHAR,                        -- slug (시계열 안정 ID)
  effective_from  DATE,                           -- 이 row 의 유효 시작일
  effective_to    DATE,                           -- 이 row 의 유효 종료일 (현재 유효면 NULL)
  parent_id       VARCHAR,                        -- 같은 bu_id 의 어느 effective row 든 참조 가능
  bu_name         VARCHAR NOT NULL,
  bu_level        INTEGER,                        -- 0=root, 1=MBU/SBU, 2=부문/실
  source_sheet    VARCHAR,
  PRIMARY KEY (bu_id, effective_from)             -- SCD Type 2 복합 PK
);

-- 직군(고용형태) 6종 — 코멘트 14-2 반영
-- EXEC/MGMT/OPER/FIELD/CONT(계약직)/PART(관계인력)
CREATE TABLE dim_employment_type (
  emp_type_code   VARCHAR PRIMARY KEY,            -- 'EXEC','MGMT','OPER','FIELD','CONT','PART'
  emp_type_name   VARCHAR NOT NULL,
  display_order   INTEGER
);

-- 인원 fact (요약 시트 → bu_level=2 까지 적재, level=1 은 rollup view 로)
-- 연도 무관: year 컬럼이 스냅샷 연도. 2023/2024/2025/... 한 테이블에 누적. (코멘트 2 반영)
CREATE TABLE fact_headcount (
  year            INTEGER,
  quarter         INTEGER,                        -- 풀무원 인사 5월 1일 snapshot → quarter=2 고정
  bu_id           VARCHAR,                        -- dim_bu 참조 (PK 변경으로 단순 FK 불가, view 에서 effective_from <= year < effective_to 로 join)
  emp_type_code   VARCHAR REFERENCES dim_employment_type(emp_type_code),
  headcount       INTEGER,                        -- 계획 인원 (TO)
  headcount_actual INTEGER,                       -- 실제 인원 (전사총계 E/H 컬럼 출처)
  source_file     VARCHAR,                        -- 원본 파일명 (audit)
  source_row      INTEGER,                        -- 원본 행 번호 (audit)
  PRIMARY KEY (year, quarter, bu_id, emp_type_code)
);

-- 관계인력 (파견·용역 외주 인력) — planned/actual 한 행에 함께 (코멘트 3 반영)
-- 관계인력은 직군 분해 없음 (전체가 CONT 성격이라 emp_type_code 제거)
CREATE TABLE fact_related_personnel (
  year            INTEGER,
  quarter         INTEGER,
  bu_id           VARCHAR REFERENCES dim_bu(bu_id),
  planned         INTEGER,                        -- 엑셀 H 컬럼 = T/O (계획)
  actual          INTEGER,                        -- 엑셀 I 컬럼 = 실제 인원
  PRIMARY KEY (year, quarter, bu_id)
);

-- 대시보드 직결 view: 사업단위(level=1) 로 rollup, 모든 연도 노출 (year 필터 제거)
-- build_dashboard.py 가 WHERE year=? 로 원하는 스냅샷 선택
CREATE VIEW view_dashboard_bus AS
WITH RECURSIVE bu_tree AS (
  SELECT bu_id, bu_id AS root_id, 0 AS depth FROM dim_bu WHERE bu_level = 1
  UNION ALL
  SELECT c.bu_id, t.root_id, t.depth + 1
  FROM dim_bu c JOIN bu_tree t ON c.parent_id = t.bu_id
)
SELECT
  h.year,
  h.quarter,
  t.root_id AS bu_id,
  b.bu_name,
  SUM(CASE WHEN h.emp_type_code = 'EXEC'  THEN h.headcount END) AS exec_cnt,
  SUM(CASE WHEN h.emp_type_code = 'MGMT'  THEN h.headcount END) AS mgmt_cnt,
  SUM(CASE WHEN h.emp_type_code = 'OPER'  THEN h.headcount END) AS oper_cnt,
  SUM(CASE WHEN h.emp_type_code = 'FIELD' THEN h.headcount END) AS field_cnt,
  SUM(CASE WHEN h.emp_type_code = 'CONT'  THEN h.headcount END) AS cont_cnt,
  SUM(CASE WHEN h.emp_type_code = 'PART'  THEN h.headcount END) AS part_cnt,  -- 코멘트 14-2 신규
  SUM(h.headcount) AS tot
FROM bu_tree t
JOIN dim_bu b         ON b.bu_id = t.root_id
JOIN fact_headcount h ON h.bu_id = t.bu_id
GROUP BY h.year, h.quarter, t.root_id, b.bu_name;

-- 직군 시드 (6종 — 코멘트 14-2 풀무원 실제 분류)
INSERT INTO dim_employment_type VALUES
  ('EXEC',  '임원/대표',                  1),  -- 요약 시트 R7,R15,R23 등 'BU 대표' 행
  ('MGMT',  '경영간부직',                 2),  -- 요약 시트 R6 L 컬럼
  ('OPER',  '운영관리·연구전문',          3),  -- 요약 시트 R6 M 컬럼
  ('FIELD', '운영실무직+현장직',          4),  -- 요약 R6 N 컬럼 + 전사총계 '현장직'
  ('CONT',  '계약직',                     5),  -- 직접 고용 계약직 (정규직 외)
  ('PART',  '관계인력(도급/파견)',         6); -- 관계인력(PPT) 시트 — 외주

-- BU mapping 시드 (코멘트 14-1·14-3 — 2023→2024→2025 시계열 매핑)
-- 같은 조직의 이름 변천 = effective_from/to 로 시계열 연결
INSERT INTO dim_bu (bu_id, parent_id, bu_name, bu_level, source_sheet, effective_from, effective_to) VALUES
  -- 건강케어 계열 (이름 변천: 로하스케어 → 건강생활 → 건강케어MBU+건강생활)
  ('health-care-mbu',   NULL, '로하스케어_SBU',  1, '요약', '2023-01-01', '2023-12-31'),
  ('health-care-mbu',   NULL, '건강생활_SBU',    1, '요약', '2024-01-01', '2024-12-31'),
  ('health-care-mbu',   NULL, '건강케어MBU',     1, '요약', '2025-01-01', NULL),
  ('health-life',       'health-care-mbu', '건강생활', 2, '요약', '2025-01-01', NULL),
  -- 통합운영FU → COO 이름 변경
  ('coo',               NULL, '통합운영FU',      1, '요약', '2023-01-01', '2024-12-31'),
  ('coo',               NULL, 'COO',             1, '요약', '2025-01-01', NULL),
  -- CSO 분화 → CHO/CCO/Corp/CFO
  ('cso-legacy',        NULL, 'CSO',             1, '요약', '2023-01-01', '2024-12-31'),
  ('cho',               NULL, 'CHO',             1, '요약', '2025-01-01', NULL),
  ('cco',               NULL, 'CCO',             1, '요약', '2025-01-01', NULL),
  ('corp',              NULL, 'Corp',            1, '요약', '2025-01-01', NULL),
  ('cfo',               NULL, 'CFO',             1, '요약', '2025-01-01', NULL),
  -- 직속 분화 → FI (건강케어혁신), B2E/리빙케어 (신성장SBU), 온라인 (식품통합 MBU 26년)
  ('jiksok-legacy',     NULL, '직속',            1, '요약', '2023-01-01', '2024-12-31'),
  ('health-innovation', NULL, '건강케어혁신',     1, '요약', '2025-01-01', NULL),
  ('fi',                'health-innovation', 'FI',    2, '요약', '2025-01-01', NULL),
  ('new-growth-sbu',    NULL, '신성장SBU',        1, '요약', '2025-01-01', NULL),
  ('b2e',               'new-growth-sbu', 'B2E',      2, '요약', '2025-01-01', NULL),
  ('living-care',       'new-growth-sbu', '리빙케어', 2, '요약', '2025-01-01', NULL),
  -- 온라인: raw 검증 결과 2025 시트 이미 존재 → 독립 BU (직속 사라져 무부모). 2026 부터 식품통합 산하 (코멘트 16 정정)
  ('online',            NULL,                '온라인', 1, '요약', '2025-01-01', '2025-12-31'),
  ('online',            'food-mbu',          '온라인', 2, '요약', '2026-01-01', NULL);
-- 시계열 무변동 BU (식품통합 / 다논 / 샘물 / NA / 중국 / 일본 / 푸드앤컬처 / FDD / ORGA 등) 는
-- schema.yaml bu_aliases 에서 normalize 후 일괄 INSERT (생략).
```

**타입 제한 (Supabase 호환 부분집합):** `INTEGER`, `VARCHAR`, `DATE`, `DECIMAL` 만 사용. STRUCT/LIST/MAP 금지.

### 4.2 `pipeline/schema.yaml` (3개년 diff 검토용 sources 패턴 — 코멘트 10 의도 정정 반영)

**전략**: 본 plan 은 **schema 검토** 단계 — 3개년 (2023/2024/2025) 의 sources 블록 패턴을 **미리 제시** 하여 향후 2022·2026·2027 도 같은 패턴으로 1분 작업이 되도록 검증. **실 적재 (extract_excel.py 작성·실행) 는 본 plan scope 외** — P2/P3 별도 plan. DDL 은 한 벌 (연도 무관). schema.yaml 의 sources 블록만 시트명·헤더 위치·컬럼 매핑의 drift 를 흡수.

```yaml
version: 1

# 연도별 sources — 시트·헤더 위치 drift 흡수
sources:

  # ─── 2025 (현행 — '요약' 시트 212행 grain) ───
  hc_2025:
    file_glob: "10-RAW/HC/2025.05/1.인원현황_*.xlsx"
    year: 2025
    quarter: 2                            # 5월 1일 snapshot
    primary_sheet:
      sheet_name: "요약"
      header_rows: [4, 5, 6]              # 3단 병합 헤더
      data_start_row: 7
      data_end_row: 212
      bu_columns:
        level1: B                         # MBU/SBU (forward-fill)
        level2: C                         # 부문/실
      subtotal_marker:                   # 합계 행 식별 — raw 검증 결과 (코멘트 16): A 컬럼 '소' 잘못, C 컬럼 어미 '계' 가 3개년 통용
        column: C
        suffix: "계"                     # 예: "식품통합 MBU계", "푸드앤컬쳐 MBU계"              # '소' = MBU 합계 행 (skip)
      headcount_column: D                 # 당해연도 T/O
      headcount_actual_column: E          # 실제 인원
      emp_type_columns:
        auto_detect: true                 # F~AD 헤더 fuzzy match
        fallback_bucket: OPER
    related_sheet:
      sheet_name: "관계인력(PPT)"
      skip_range: "A1:E15"                # 더미
      header_rows: [2, 3]
      data_start_row: 16
      bu_column: G
      planned_column: H                   # T/O 계획
      actual_column: I                    # 실제 인원
    validation_sheet:
      sheet_name: "전사총계"
      total_row: 23                       # 전체 합계 anchor
      exec_to_column: D                   # 경영진 TO
      mgmt_to_column: G                   # 관리(사무직) TO  ← 사용자 코멘트 'G=예산?' 정정 반영
      total_to_column: J                  # 소계 (D+G)
      related_to_column: M                # 관계인력 TO

  # ─── 2024 (코멘트 14 raw deep dive: '요약' 190×33, 2025 와 동일 구조) ───
  hc_2024:
    file_glob: "10-RAW/HC/2024.05/1.인원현황_*.xlsx"
    year: 2024
    quarter: 2
    primary_sheet:
      sheet_name: "요약"                  # 2023~2025 모두 '요약' 시트가 primary (시트명 혼동 정정)
      header_rows: [4, 5, 6]              # R4 사업단위/본부/실, R5 메트릭, R6 직군 분해
      data_start_row: 7
      data_end_row: 190
      bu_columns:
        level1: B                         # MBU/SBU (forward-fill)
        level2: C                         # 본부/실
      subtotal_marker:                   # 합계 행 식별 — raw 검증 결과 (코멘트 16): A 컬럼 '소' 잘못, C 컬럼 어미 '계' 가 3개년 통용
        column: C
        suffix: "계"                     # 예: "식품통합 MBU계", "푸드앤컬쳐 MBU계"
      headcount_column: D                 # '24년 초 T/O
      headcount_actual_column: E          # '24년초 재직인원
      emp_type_columns:                   # R6 명시적 매핑 (3개년 동일)
        L: MGMT                           # "경영간부직"
        M: OPER                           # "운영관리/연구전문"
        N: FIELD                          # "운영실무직"
    related_sheet:
      sheet_name: "관계인력(PPT)"
      skip_range: "A1:E15"
      data_start_row: 16
      bu_column: G
      planned_column: H
      actual_column: I
    validation_sheet:
      sheet_name: "전사총계"
      total_row: 21                       # "전사 총계계"
      mgmt_to_column: C                   # 경영간부직 24년TO
      oper_to_column: F                   # 운영직 24년TO
      field_to_column: N                  # 현장직 24년TO

  # ─── 2023 (코멘트 14 raw deep dive: '요약' 187×33, 2025 와 동일 구조) ───
  hc_2023:
    file_glob: "10-RAW/HC/2023.05/1.인원현황_*.xlsx"
    year: 2023
    quarter: 2
    primary_sheet:
      sheet_name: "요약"
      header_rows: [4, 5, 6]
      data_start_row: 7
      data_end_row: 187
      bu_columns:
        level1: B
        level2: C
      subtotal_marker:                   # 합계 행 식별 — raw 검증 결과 (코멘트 16): A 컬럼 '소' 잘못, C 컬럼 어미 '계' 가 3개년 통용
        column: C
        suffix: "계"                     # 예: "식품통합 MBU계", "푸드앤컬쳐 MBU계"
      headcount_column: D                 # '23년 초 T/O
      headcount_actual_column: E
      emp_type_columns:
        L: MGMT
        M: OPER
        N: FIELD
    related_sheet:
      sheet_name: "관계인력(PPT)"
      skip_range: "A1:E15"
      data_start_row: 16
      bu_column: G
      planned_column: H
      actual_column: I
    validation_sheet:
      sheet_name: "전사총계"
      total_row: 21                       # "전사 총계"
      mgmt_to_column: B
      oper_to_column: E
      field_to_column: M

  # ─── 2026+ (향후 추가) ───
  # hc_2026:
  #   file_glob: "10-RAW/HC/2026.05/1.인원현황_*.xlsx"
  #   ... (hc_2025 블록 복제 — '요약' 시트 동일 구조 가정)

bu_aliases:                             # dim_bu.bu_name 정규화 (시트명 ↔ 정식명)
  - canonical: "식품통합MBU"
    aliases: ["식품통합 MBU", "식품통합MBU구", "음료식품 MBU"]
  - canonical: "샘물"
    aliases: ["샘물MBU", "샘물 MBU"]
  - canonical: "다논SBU"
    aliases: ["다논 SBU"]
  - canonical: "NA MBU"
    aliases: ["NA", "북미 MBU"]
  - canonical: "푸드앤컬처MBU"
    aliases: ["푸드&컬처 MBU", "푸드앤컬처 MBU"]
  - canonical: "건강케어MBU"
    aliases: ["건강케어 MBU"]
  # extract_excel.py 에서 사용자 확인 후 보강

# 코멘트 14-2 정정 반영 — 풀무원 실제 분류 6종
# 사용자 인라인 코멘트 ("경영간부=임원") 으로 EXEC 매핑 정정
employment_type_mapping:
  EXEC:                                 # 임원 (BU 대표 행)
    aliases: ["임원", "대표", "EXEC", "본부장 이상", "Executive", "경영진"]
    # 요약 시트의 R7/R15/R23 등 'XX MBU 대표' 행이 EXEC 적재
  MGMT:                                 # 경영간부직 (요약 R6 L 컬럼)
    aliases: ["경영간부직", "경영간부", "관리직", "팀장", "MGMT", "M/S"]
    # 사용자 코멘트 "경영간부=임원" 은 풀무원 호칭 관습 — DB 분류는 MGMT 유지 (EXEC 와 분리)
  OPER:                                 # 운영관리·연구전문 (요약 R6 M 컬럼)
    aliases: ["운영관리", "연구전문", "운영관리/연구전문", "사무직", "OPER", "P3", "P2"]
  FIELD:                                # 운영실무직 + 현장직 (요약 R6 N + 전사총계 현장직)
    aliases: ["운영실무직", "운영실무", "현장직", "현장", "생산직", "FIELD"]
  CONT:                                 # 계약직 (정규직 외 직접 고용) — 코멘트 14-2 재정의
    aliases: ["계약직", "계약", "임시직원", "임시"]
  PART:                                 # 관계인력 (도급/파견 외주) — 코멘트 14-2 신규 추가
    aliases: ["관계인력", "도급", "파견", "외주", "PART", "도급/파견"]
    # '관계인력(PPT)' 시트 전체가 PART 로 적재
```

### 4.3 매핑 규칙 — extract 단계에서 적용 (참고)

본 phase 산출은 schema.yaml + ddl.sql 두 개. 아래는 P2(extract) 에서 어떻게 쓰일지 명세 — DDL 검토 시 ambiguity 제거용.

1. **BU 트리 구축 (`dim_bu`)**: 요약 시트 B/C 컬럼을 row scan.
   - B 채워있고 C 비어있음 → MBU/SBU = level 1 (parent_id = NULL)
   - B 비어있고 C 채워있음 → 직전 B 의 자식 = level 2 (parent_id = 직전 B 의 bu_id)
   - 추가 들여쓰기 (요약 시트의 일부 행) → level 3 까지 parent_id 체인
   - `bu_id` = slugify(`bu_name`) + 부모 경로 prefix

2. **직군 매핑**: 요약 시트 F~AD 컬럼 헤더를 schema.yaml `employment_type_mapping.aliases` 와 fuzzy match. 매칭 실패 → `fallback_bucket=OPER` 적재 + log.

3. **5월 snapshot → Q2**: 풀무원 인사 엑셀은 매년 5월 1일 기준 → `year=2025, quarter=2` 로 통일.

---

## 5. 폴더 구조 (P1 산출물 배치)

```
HR-indexData/
├── 10-RAW/HC/2025.05/               (read-only)
├── pipeline/                        ★ 본 phase 신규
│   ├── schema.yaml                  ★ 산출 #1
│   └── ddl.sql                      ★ 산출 #2
└── archive/dashboard/
    └── plan-backdata-hc-260512.md   (이 plan 의 archive 사본 — 사용자 정리 명령 후)
```

---

## 6. 핵심 설계 결정

| 결정          | 채택                                                                                            | 기각안 / 이유                                               |
| ----------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| schema 검토 시계열 | **2023 / 2024 / 2025 3개년 schema diff *검토* (적재 X — 실 적재는 다음 plan)** | 2025 only — 향후 연도 확장 견고성 부족. 3개년 패턴으로 schema 확정 후 적재는 P3 plan |
| 인원 grain    | **3개년 모두 '요약' 시트 BU→본부/실 leaf (코멘트 14 정정)**     | 2023~2024 BU only — 시트명 혼동 오류                       |
| BU 트리       | **dim_bu(parent_id) N단계 재귀 + 시계열 effective_from/to**                                                                  | 2단계 고정 — 팀 leaf 누락. 시계열 무시 — drift 흡수 못함                                     |
| 직군 axis     | **6종 (EXEC/MGMT/OPER/FIELD/CONT/PART) — 코멘트 14-2**                                                            | 5종 — 관계인력(PART) 누락                                    |
| 직군 매핑       | **schema.yaml + 자동 추론 + fallback=OPER**                                                       | 사용자 매핑표 수기 — 작성 부담                                     |
| BU 별칭       | **schema.yaml bu_aliases** + dim_bu effective_from/to                                         | 코드 하드코딩 — drift 흡수 못함                                  |
| 5월 snapshot | **quarter=2 통일**                                                                              | year+month — fact_headcount PK 분기 grain 와 충돌           |
| Audit       | **fact_headcount.source_file/source_row**                                                     | 별도 audit 테이블 — overkill                                |
| 백데이터 시트     | **본 phase 미적재** (`식품통합MBU` 등 23개)                                                             | raw 보존 — 사용자가 명시 "기반 데이터 아님"                           |
| Supabase 호환 | DDL 타입을 INTEGER/VARCHAR/DATE/DECIMAL 로 한정                                                     | DuckDB 전용 STRUCT — 이행 비용                               |

---

## 7. 위험 / 미결사항 (사용자 코멘트 4·5·6·7 반영 — 쉬운 설명)

### 위험 1. 요약 시트 B 컬럼 "병합" 처리 (코멘트 4 — 쉽게)
**문제**: 엑셀 '요약' 시트에서 같은 MBU 이름이 여러 행에 걸쳐 한 칸으로 합쳐져 있다 (셀 병합). 예:
- R7 의 B 컬럼 = `"식품통합 MBU"` (눈에 보임)
- R8~R13 의 B 컬럼 = **빈 셀** (실제로는 R7 의 'MBU' 가 세로 병합으로 덮고 있음)
- R14 = MBU 합계 행 (A='소' 표시)

코드가 그대로 읽으면 R8~R13 은 '소속 MBU 없음' 으로 인식 → 부모-자식 관계 깨짐.

**해결 (P2 단계 적용)**:
- 규칙: "B 가 빈 셀이면 직전 행의 B 값을 그대로 채워 넣는다" (forward-fill)
- 합계 행 (A 컬럼에 '소' 마크) 은 `dim_bu` 적재에서 skip → 중복 방지

### 위험 2. 직군 자동 매핑 실패율 (그대로 유지)

F~AD 헤더 텍스트가 다년간 비표준화. `fallback_bucket=OPER` 로 흡수하되 **첫 빌드 후 사용자 확인 round 필요** (매핑 미스 비율 > 10% 이면 schema.yaml 매핑표 보강).

### 위험 3. 관계인력 시트 — 계획/실적 저장 방식 (코멘트 5 — 쉽게)
**문제**: '관계인력(PPT)' 시트에는 같은 BU 에 대해 두 개 숫자가 있다:
- H 컬럼 = "계획 인원 (T/O)" — 예: 4,395
- I 컬럼 = "실제 인원" — 예: 2,663
-> 비교를 하려면 H,I 가 아니라 H, M 컬럼 간 비교 해야함

이 둘을 DB 에 어떻게 저장할지 두 가지 선택지:
- (a) **한 행에 두 컬럼**: `(bu_id, planned, actual)` → SELECT 한 번에 계획·실적 비교 가능
- (b) **두 행으로 분리**: `(bu_id, kind='planned', value)` 와 `(bu_id, kind='actual', value)` → fact_headcount 와 grain 통일

**결정 (a) 채택** → DDL `fact_related_personnel` 에 `planned`, `actual` 컬럼 두 개로 정의 (§4.1 갱신 반영). 비교 SQL 이 단순해진다.

### 위험 4. PII 의미 정정 (코멘트 6 반영)
**용어 정정**: PII = **Personally Identifiable Information (개인식별정보)** — 사번·이름·연봉·주민번호 등 한 사람을 특정할 수 있는 데이터. "운영직" (직군 OPER) 과는 다른 의미.

**본 plan 의 적용**:
- 본 phase 가 *검토·확정한* grain 은 **부문/실 합계 (집계치)** 까지 (실 적재는 P3). 사원 한 명을 특정하는 정보가 들어가지 않음.
- 따라서 PII 위험 **해당 없음**.
- 백데이터 시트 (식품통합MBU 등) 에는 사원 단위 행이 있을 수 있으나 본 plan 은 적재 안 함.

→ 사용자 의문 "운영직까지만 세분화" 는 *grain* 결정 (BU→부문/실 까지) 이지 *PII* 와 무관. 본 plan 그대로 안전.

### 위험 5. <span style="color:red">검증 anchor — 코멘트 16 raw 검증으로 명세 확정</span>

**raw 검증 결과 (코멘트 16)** — R26 검증 수식은 **2025 만 존재**:

| 연도   | R26 검증식                                                                       | anchor 전략                        |
| ---- | ----------------------------------------------------------------------------- | -------------------------------- |
| 2025 | ✅ 9개 TRUE/FALSE 식 (`J23=(D23+G23)`, `R23=(J23+O23)`, `X23=(R23+U23)` 등 누적 합산) | R26 의 9개 셀 스캔 → 모두 TRUE 면 통과     |
| 2024 | ❌ 없음                                                                          | '전사총계' R21 "전사 총계계" 행과 SUM 직접 매칭 |
| 2023 | ❌ 없음                                                                          | '전사총계' R21 "전사 총계" 행과 SUM 직접 매칭  |

**검증 절차 (연도별 분기)**:

```
2025:
  1. '전사총계' R26 의 9개 검증식 스캔 → 모두 TRUE 여야 OK
  2. FALSE 발견 시: 어느 카테고리 (J/R/X) 의 합산이 깨졌는지 식별 →
     '요약' 시트에서 해당 BU 영역 dump → 사용자에게 보고
  3. 모두 TRUE → SUM(fact_headcount.headcount WHERE year=2025) 가
     전사총계 R23.J (= 2,804 소계) 와 일치 확인

2024:
  1. R26 없음 → R21 "전사 총계계" 와 SUM 직접 매칭
  2. 차이 발견 시 '요약' 시트 'XX MBU계' (C 컬럼 어미 '계') 행 단위 dump

2023:
  1. R26 없음 → R21 "전사 총계" 와 SUM 직접 매칭
  2. 동일 절차
```

```sql
-- 통과 검증 SQL (P3 시점, 모든 연도)
SELECT year, quarter, SUM(headcount) FROM fact_headcount
GROUP BY year, quarter ORDER BY year;
-- 기대치: 각 연도 '전사총계' R23.J (2025) 또는 R21 (2023/2024) 값과 일치
```

### 위험 6. BU 시계열 drift 처리 — 코멘트 14-3 (직속 분화)

**문제**: 풀무원 조직개편으로 BU 가 (a) 이름만 변경 (b) 자식으로 분화 (c) 다른 부모로 이전 케이스 다발.

**확인된 케이스 (코멘트 14-3)**:
- (a) 통합운영FU → COO (2025) — 단순 이름 변경
- (b) CSO → CHO/CCO/Corp/CFO (2025) — 1개가 4개로 분화
- (c) 직속 자체 사라지고 자식들이 새 부모로 이전:
  - FI → 건강케어혁신 (신규 부모)
  - B2E·리빙케어 → 신성장SBU (신규 부모)
  - 온라인 → 식품통합MBU (2026년 이전)

**대응 (DDL `dim_bu` seed 에 적용)**:
- `bu_id` 는 시계열 안정 (예: `coo` — 이름 바뀌어도 같은 ID)
- `bu_name` 은 연도별로 다른 row (effective_from/to 로 구분)
- `parent_id` 변경 = 이전 부모 row 의 effective_to 종료 + 신규 부모 row 의 effective_from 시작
- 시계열 비교 시 `bu_id` 기준으로 JOIN 하면 같은 조직의 다년 추이 일관

**검증 SQL (P3 시점)**:
```sql
-- 같은 bu_id 의 다년 비교 (이름 변경 흡수)
SELECT year, bu_id, bu_name, SUM(headcount)
FROM fact_headcount JOIN dim_bu USING (bu_id)
WHERE bu_id = 'health-care-mbu'  -- 로하스 → 건강생활 → 건강케어
GROUP BY year, bu_id, bu_name
ORDER BY year;
```

엑셀 자체에서 둘이 안 맞으면 raw 엑셀 오류로 보고 사용자에게 fix 요청 후 재빌드. mockup 8,134 와는 **무관** (mockup 은 가상 더미값).

---

## 8. 검증 — 비개발자 점검 가이드 (코멘트 11 반영, 체크리스트 7개로 확장)
본 plan 은 schema 설계 단계로 **코드 실행이 없음**. 검증은 (a) Claude 가 자동 실행하는 syntax 체크 + (b) 사용자가 도메인 지식으로 답하는 7가지 점검 으로 구성.

### 8.1 Claude 자동 실행 (사용자는 대기만)

```
python -c "import yaml; yaml.safe_load(open('pipeline/schema.yaml'))"
→ 결과: 'OK' 또는 'syntax error 라인 N'
```

```
duckdb :memory: < pipeline/ddl.sql
→ 결과: 5개 테이블·뷰 생성 (dim_bu, dim_employment_type, fact_headcount, fact_related_personnel, view_dashboard_bus)
        + 직군 5종 row 생성
```

둘 다 에러 없이 통과해야 OK. 에러 나면 Claude 가 수정 후 재시도.

### 8.2 사용자 점검 7가지 카테고리 (비개발자가 도메인 지식으로 판단)

각 항목은 **"엑셀·인사 분류표 보고 직접 판단 가능"** 한 형태로 설계. 코드·SQL 몰라도 OK.

#### 점검 ① — 사업단위 (BU) 이름 일관성

**왜 중요한가**: 2023 의 "미래조직_SBU" 와 2024 의 "신규조직혁신_SBU" 가 *같은 조직* 이면 alias 로 묶어야 시계열 비교 가능. 다른 조직이면 별개 BU.

**확인 방법**: Claude 가 제시할 "연도별 BU 명 매트릭스" 표에서 같은 행 안 이름들이 *같은 조직인지* 표시.

| 2023     | 2024       | 2025     | 사용자 판단             |
| -------- | ---------- | -------- | ------------------ |
| 미래조직_SBU | 신규조직혁신_SBU | (없음?)    | ☐ 같음 / ☐ 다름 / ☐ 모름 |
| FDD SBU  | FDD SBU    | FDD      | ☐ 같음 / ☐ 다름        |
| 식품통합MBU  | 식품통합MBU    | 식품통합 MBU | ☐ 같음 / ☐ 다름        |

**판단 기준**: "이 조직이 같은 일을 하는 같은 팀인가?" — 조직개편 통보 받은 적 있으면 그 기준으로.

#### 점검 ② — 시트 grain (깊이) 가 의도와 맞는가

**왜 중요한가**: 2025 는 '요약' 시트로 **부문/실 단위** 까지 (2단계). 2023/2024 는 '전사총계' 로 **BU 단위만** (1단계).

| 연도 | 데이터 깊이 | 예시 |
|---|---|---|
| 2023 | BU 만 | "식품통합MBU 합계 = 720명" |
| 2024 | BU 만 | "식품통합MBU 합계 = 730명" |
| 2025 | BU + 부문/실 | "식품통합MBU = 742명, 장류영양 = 359명, 글로벌통합 = 188명..." |

**판단**:
- ☐ 이 깊이 차이 OK (2025 만 세분화)
- ☐ 2023/2024 도 부문/실 보고싶음 → 별도 raw 엑셀 위치 확인 필요
- ☐ 2025 도 BU 만 보면 됨 (단순화)

#### 점검 ③ — 직군 5종 매핑 (가장 중요)

**왜 중요한가**: 모든 사람이 5가지 중 하나로 분류. 회사 인사 분류와 안 맞으면 통계 어긋남.

| 코드 | Claude 의 정의 | 사용자 검증 |
|---|---|---|
| EXEC | 임원급 (본부장 이상) | ☐ 맞음 / ☐ 풀무원 기준은 ___ |
| MGMT | 경영간부 (팀장급) | ☐ 맞음 / ☐ 풀무원 기준은 ___ |
| OPER | 운영 (사무직 사원) | ☐ 맞음 / ☐ 풀무원 기준은 ___ |
| FIELD | 현장 (생산직) | ☐ 맞음 / ☐ 풀무원 기준은 ___ |
| CONT | 계약·임시·파견 | ☐ 맞음 / ☐ 풀무원 기준은 ___ |

**판단**: 풀무원 인사 분류표 옆에 두고 — 5가지로 다 분류되나? 분류 안 되는 직군 (예: "촉탁직", "전문직", "교육직") 있는지?

#### 점검 ④ — 엑셀 컬럼 의미 정확성

**왜 중요한가**: Claude 가 "G 컬럼 = 관리(사무직) TO" 라고 가정한 게 실제 맞는지. 이미 한 번 "예산 아니다" 정정 사례 있음.

| 시트 | 컬럼 | 2023 추정 | 2024 추정 | 2025 raw 확정 | OK? |
|---|---|---|---|---|---|
| 전사총계 | D | 25년 TO | 24년 TO | 임원/경영진 TO | ☐ |
| 전사총계 | G | ? | ? | 관리/사무직 TO | ☐ |
| 전사총계 | M | ? | ? | 관계인력 TO | ☐ |
| 요약 | B | (해당없음) | (해당없음) | 사업단위 | ☐ |
| 요약 | C | (해당없음) | (해당없음) | 부문/실 | ☐ |

**판단**: 각 컬럼이 진짜 그 의미인지. 의심스러우면 엑셀 직접 열어 헤더 확인.

#### 점검 ⑤ — 인원 합계 검증 anchor

**왜 중요한가**: 빌드 끝나면 DB 의 숫자가 엑셀과 같아야. 어디를 비교해야 "OK" 인지 사전 합의.

```
2025 빌드 결과:    2,804 명
엑셀 전사총계 R23: 2,804 명
차이:              0  ✅
```

**판단**:
- ☐ 이 수치가 평소 보고서의 "전사 인원" 과 같은지
- ☐ 풀무원 전체가 2,804 가 아니라 8,000+ (정규직만, 관계인력 제외 등 기준 차이) → 검증 기준 재정의 필요

#### 점검 ⑥ — 누락된 BU 가 없는가

**왜 중요한가**: 시트 매핑 오류 → 특정 BU 통째 누락 가능.

| 연도   | 적재된 BU 목록                     | BU 수 | 누락 의심 |
| ---- | ----------------------------- | ---- | ----- |
| 2023 | 식품통합, 건강생활, FDD SBU, ...      | 19   | ?     |
| 2024 | 식품통합, 공급망, ORGA SBU, ...      | 20   | ?     |
| 2025 | 식품통합, 샘물, 다논, NA, 중국, 일본, ... | 28   | ?     |

**판단**: 사용자가 아는 풀무원 모든 BU 가 이 목록에 다 있나? 빠진 게 있으면 그 BU 의 raw 엑셀 위치 확인.

#### 점검 ⑦ — 관계인력 (파견·용역) 처리 방식

**왜 중요한가**: 정규직과 외주 인력을 합쳐 볼 때 / 분리해 볼 때 모두 필요. 사용자 보고 방식과 맞아야.

Claude 의 현재 설계:
- `fact_headcount` = 정규직 (직군 5종 분해)
- `fact_related_personnel` = 관계인력 (planned/actual 한 행)
- 합계는 둘 다 SUM

**판단**:
- ☐ 분리 저장이 적절 (대부분 보고서가 분리)
- ☐ 1개 테이블에 직군 추가 (예: "관계인력") 로 합치고 싶음
- ☐ 관계인력 자체를 본 plan 에서 빼고 싶음


### 8.3 사용자 답변 양식 예시

위 7가지에 대해 사용자는 아래 양식으로 회신:

```
점검 ①: BU 매트릭스
  - "미래조직_SBU = 신규조직혁신_SBU" 같음 ✅
  - "FDD SBU 2023 vs FDD 2025" 다름 (사업 종료)
  - "3~6행 OK, 나머지 인사팀 확인 필요"

점검 ②: grain
  - OK. 2025 만 부문/실까지면 충분

점검 ③: 직군 5종
  - EXEC, MGMT, OPER, FIELD, CONT OK
  - "촉탁직" 분류 필요. CONT 와 별도로 가야 함

점검 ④: 컬럼 의미
  - 전사총계 G = 관리 OK
  - 요약 C = 부문/실 OK

점검 ⑤: 검증 anchor
  - 2804 는 임원+관리만. 전체는 8000+
  - 검증 기준 = 임원+관리만 OK

점검 ⑥: BU 누락
  - 2023 "리빙케어" 빠진 듯. 확인 필요

점검 ⑦: 관계인력
  - 분리 저장 OK
```

각 항목에 OK / 수정 필요 / 모름 으로 답하면 Claude 가 schema.yaml·ddl.sql 에 반영.



### 8.4 통과 시 다음 plan 진입

7가지 모두 OK 또는 patch 완료 → P2 (`extract_excel.py`) 별도 plan 으로 진입. 본 plan 의 schema.yaml/ddl.sql 이 P2 의 입력이 된다.

---

## 9. 본 plan 의 비-목표 / 본 plan 의 마무리 (코멘트 9 반영)
### ✓ 본 plan 안에서 **마무리되는** 항목 (코멘트 10 의도 정정 반영)

- **2023/2024/2025 3개년 schema diff 검토 + sources 패턴 확정** — §4.2 에 hc_2023 / hc_2024 / hc_2025 sources 블록 패턴 제시. 향후 hc_2026 추가는 동일 패턴으로 1분 작업.
- DDL 한 벌이 **모든 연도를 수용 가능한 형태** 로 확정 (연도 hardcode 없음, 직군 5종 표준화). 실 적재는 다음 plan.
- BU 명 drift (예: 2023 "미래조직_SBU" → 2024 "신규조직혁신_SBU") 흡수 패턴 정립 — `bu_aliases` + `dim_bu.effective_from/to`.
- **※ 명시**: 본 plan 은 *schema 검토·확정* 단계. 실 데이터 적재 (extract_excel.py + load_duckdb.py 작성·실행) 는 본 plan scope 외 — P2/P3 별도 plan.

### ✗ 본 plan 의 **비-목표** (다음 plan 으로 분리)

- `extract_excel.py` / `load_duckdb.py` / `build_dashboard.py` 코드 구현
- 지원조직·퇴사율·인건비·HCROI 적재 (raw 미공유 또는 사용자 지시 scope 외)
- HTML fetch 패치 (P5 별도 plan)
- 자동화·스케줄러 (phase 외)

---

## 10. 진행 절차

1. 본 plan 사용자 재검토 (코멘트 반영본) → 추가 수정 없으면 v2.0 으로 확정
2. `구현해줘` 명시 신호 받으면 P1 작성 시작:
   - `pipeline/ddl.sql` Write
   - `pipeline/schema.yaml` Write (hc_2023 / hc_2024 / hc_2025 sources 블록 포함)
3. §8 검증 자동 단계 (yaml safe_load + DuckDB execute) 통과 확인
4. P1 종료 시 result 파일 작성 (`archive/dashboard/result-hc-schema-260512.md`)
5. P2 (`extract_excel.py`) 는 별도 plan 으로 진입
