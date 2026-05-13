# Handoff: Dashboard 스키마 설계 결정 대기

작성일: 2026-05-11
재개 예정: 2026-05-12
관련 plan: `archive/plan-dash-research-260511-v1.X.md` (Section 5·7 패치 대기)

---

## 현재 위치

- plan-dash-research-260511 의 1차 패치 완료 (사용자 인라인 코멘트 7건 반영)
- 그 직후 추가 검토 요청: **BU 트리 깊이 + 직군 분류 axis 가 스키마 설계에 반영되지 않았음** 확인
- §5 / §7 의 `dim_bu(parent_id)` 와 `fact_headcount(employment_type)` 는 placeholder 수준 — 다음 phase 진입 전 다시 설계 필요
- 해당 결정 4건이 미정인 상태에서 멈춤

---

## 의사결정 대기 — 4 항목

각 항목에 답이 정해지면 plan §5(폴더·DDL), §7(결정 표), §8(위험) 을 1회 더 패치하고 P1 진입.

### Q1. BU 트리 최대 깊이

| 옵션 | 내용 | 코멘트 |
|---|---|---|
| **A** | 사업단위 → 실/본부 (2단계) | 가장 흔한 인사보고 구조. drill-down 1단계 |
| B | 사업단위 → 실/본부 → 팀 (3단계) | 팀 leaf raw 가 있어야 의미. dim_bu row 수 ↑ |
| C | 임의 N단계 (parent_id 재귀) | 깊이 제약 0, 재귀 CTE 표준 작성 |
| D | 사업단위만 (1단계) | 현 mockup 유지, 향후 확장 시 schema 변경 |

→ **추천: A

### Q2. 직군 axis 범위

| 옵션 | 내용 | 코멘트 |
|---|---|---|
| **A** | 현 4종(c/f/o/g) + 임원 (5종) | dim_employment_type 5 row. 가장 가벼움 |
| B | 직군 + 직급 2축 | fact 행 단위 = (BU, period, 직군, 직급) |
| C | 직군 + 성별 + 연령대 다축 | ISO 30414 류 본격 분해 |
| D | 현 mockup 4종만 | 확장 안 함 |

→ **추천: A** (임원 분리는 사용자가 명시. 다축은 데이터 확보 후 phase 2)

### Q3. 개인정보(사원별 원본 데이터) 처리 방식

**상황**: 원본 엑셀에는 사번·이름·소속·연봉 같은 사원 개인정보가 들어있다. 대시보드 화면에는 "사업단위별 합계 인원" 같은 **집계 숫자만** 필요하다. 사원별 원본을 어디까지 어떻게 보관할지가 쟁점.

| 옵션 | 한 줄 설명 | 쉽게 풀면 |
|---|---|---|
| **A** | 2단 저장 (원본=내 PC, 집계=공유) | 사원별 원본은 내 PC 로컬 파일에만 두고 git·공유폴더엔 안 올림. 합계 숫자만 공유 저장소에 커밋해서 팀과 본다 |
| B | 원본 즉시 폐기 | 엑셀에서 합계만 뽑고 사원별 데이터는 바로 버린다. 가장 안전하지만 나중에 재계산·검증 불가 |
| C | 원본 보관하되 사번 가림 | 사원별 데이터는 유지하되 사번을 알아볼 수 없게 변환(해시). 누가 누군지 모르는 상태로 통계만 가능 |

**용어 풀이**
- *원본(stg, staging)*: 엑셀에서 막 뽑은 사원 한 명 = 한 줄짜리 데이터
- *집계(fact)*: "2026 Q1 식품BU 임원 5명" 같이 합쳐진 숫자만 남긴 결과
- *.gitignore*: git에 안 올릴 파일 목록. 여기 적힌 파일은 내 PC에만 존재
- *해시*: 사번 `2024001` 을 `a3f9b2c1...` 같이 되돌릴 수 없는 문자로 바꾸는 것

→ **추천: A** — 사원별 원본은 로컬 DB 파일(`_internal.duckdb`)로 두고 git 제외. 집계 결과(`fact_*` 테이블)만 공유 저장소 커밋. 재계산이 필요하면 내 PC 원본에서 다시 돌리고, 외부 유출 위험은 최소화.

### Q4. 본 phase 대시보드 출력 범위

| 옵션 | 내용 |
|---|---|
| **A** | 현 mockup 그대로 (BU 레벨, data layer 만 확장 대비) |
| B | BU + 실/본부 drill-down UI 추가 |
| C | BU + 직군 cross-tab 추가 |

→ **추천: A** — drill-down UI 는 별도 phase. 현 phase 는 데이터 파이프라인 안착에 집중.

---

## 추천 조합 (속행 시 default)

사용자가 별다른 지시 없이 "추천대로 가자" 라고 하면 적용할 조합:

```
Q1=C (임의 N단계, 확장 보장)
Q2=A (직군 5종)
Q3=A (stg/fact 2-layer)
Q4=A (현 mockup 유지)
```

### 추천 조합 기반 DDL 초안 (검토용)

```sql
-- dim_bu: 적응 리스트 (재귀 CTE 로 임의 깊이 rollup)
CREATE TABLE dim_bu (
  bu_id           VARCHAR PRIMARY KEY,
  parent_id       VARCHAR REFERENCES dim_bu(bu_id),
  bu_name         VARCHAR NOT NULL,
  bu_level        INTEGER,                     -- 0=root, 1=사업단위, 2=실/본부, ...
  effective_from  DATE,
  effective_to    DATE
);

CREATE TABLE dim_employment_type (
  emp_type_code   VARCHAR PRIMARY KEY,         -- 'EXEC','OPER','FIELD','CONT','MGMT'
  emp_type_name   VARCHAR NOT NULL,
  display_order   INTEGER
);

CREATE TABLE fact_headcount (
  year            INTEGER,
  quarter         INTEGER,
  bu_id           VARCHAR REFERENCES dim_bu(bu_id),
  emp_type_code   VARCHAR REFERENCES dim_employment_type(emp_type_code),
  headcount       INTEGER,
  PRIMARY KEY (year, quarter, bu_id, emp_type_code)
);

CREATE TABLE fact_labor_cost (
  year            INTEGER,
  month           INTEGER,
  bu_id           VARCHAR REFERENCES dim_bu(bu_id),
  emp_type_code   VARCHAR REFERENCES dim_employment_type(emp_type_code),
  budget_amount   DECIMAL(18,0),
  actual_amount   DECIMAL(18,0),
  PRIMARY KEY (year, month, bu_id, emp_type_code)
);

CREATE TABLE fact_turnover (
  year            INTEGER,
  quarter         INTEGER,
  bu_id           VARCHAR REFERENCES dim_bu(bu_id),
  head_begin      INTEGER,
  quit            INTEGER,
  head_current    INTEGER,
  head_estimated  INTEGER,
  PRIMARY KEY (year, quarter, bu_id)
);

CREATE TABLE fact_hcroi (
  year            INTEGER,
  quarter         INTEGER,
  company         VARCHAR,         -- '풀무원','오리온','오뚜기','CJ'
  hcroi           DECIMAL(10,4),
  revenue         DECIMAL(18,0),
  ebit            DECIMAL(18,0),
  PRIMARY KEY (year, quarter, company)
);

-- 대시보드 직결 view: 사업단위(level=1)로 rollup
CREATE VIEW view_dashboard_bus AS
WITH RECURSIVE bu_tree AS (
  SELECT bu_id, bu_id AS root_id, 0 AS depth FROM dim_bu WHERE bu_level=1
  UNION ALL
  SELECT c.bu_id, t.root_id, t.depth+1
  FROM dim_bu c JOIN bu_tree t ON c.parent_id = t.bu_id
)
SELECT
  t.root_id AS bu_id,
  b.bu_name,
  SUM(CASE WHEN h.emp_type_code='EXEC'  THEN h.headcount END) AS exec_cnt,
  SUM(CASE WHEN h.emp_type_code='MGMT'  THEN h.headcount END) AS g26,
  SUM(CASE WHEN h.emp_type_code='OPER'  THEN h.headcount END) AS o26,
  SUM(CASE WHEN h.emp_type_code='FIELD' THEN h.headcount END) AS f26,
  SUM(CASE WHEN h.emp_type_code='CONT'  THEN h.headcount END) AS c26,
  SUM(h.headcount) AS tot
FROM bu_tree t
JOIN dim_bu b      ON b.bu_id = t.root_id
JOIN fact_headcount h ON h.bu_id = t.bu_id
WHERE h.year=2026 AND h.quarter=1
GROUP BY t.root_id, b.bu_name;
```

검증 SQL (P3 진입 시):
```sql
SELECT SUM(headcount) FROM fact_headcount WHERE year=2026 AND quarter=1;
-- 기대값 8,134 ± 1%
```

---

## 미해결·후속 항목

- **인건비/HCROI/퇴직 raw 엑셀** — 별도 폴더에 존재하나 미공유. P6 진입 전 사용자 공유 대기
- **Supabase 이행 시점** — 별도 phase. 본 phase 의 DDL 은 Postgres 호환 부분집합으로 한정 작성 (위 DDL 초안 준수)
- **자동화** — 본 phase 외. `run.ps1` 수동 1명령 갱신만 구현

---

## 재개 절차 (내일 picking up)

1. 이 파일을 펴서 Q1~Q4 답 확인 (또는 "추천대로" 지시)
2. plan §5(폴더·DDL 블록), §7(결정 표), §8(위험) 패치 — Edit only, Write 금지
3. P1 `schema.yaml` + `ddl.sql` 초안 작성 시작
4. raw 엑셀 (`10-RAW/HC/` 2개) 로 P2 prototype, LIMIT=1 → 2 → 전체 검증
