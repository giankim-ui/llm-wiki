# Handoff: HC Pipeline P1 완료 → P2 진입 대기

작성일: 2026-05-12
작업 디렉토리: `C:\Users\Pulmuone\OneDrive - 풀무원\HR-indexData\`
선행 handoff: `archive/handoff-schema-260511.md`
관련 plan: `archive/dashboard/plan-hc-schema-260512.md`

---

## 시도한 것

1. `plan-hc-schema-260512.md` 세부 분석 및 라운드별 수정 — handoff-schema-260511.md 의 Q1~Q4 미결 사항 해소 + 3개년 raw 엑셀 deep dive 결과 반영
2. raw 추가 검증 — A 컬럼 마크('소' vs '계'), 전사총계 R26 검증 수식 유무, 온라인 BU 시점 확인
3. DDL SCD Type 2 정정 — `dim_bu` PK를 `bu_id` 단일 → `(bu_id, effective_from)` 복합으로 변경
4. `pipeline/` 디렉토리 생성 및 두 산출물 파일 작성
5. DuckDB Python 모듈로 `ddl.sql` 전체 실행 검증 + PyYAML `safe_load` 검증
6. 사용자 도메인 검증 (AskUserQuestion 4건) — 직군 6종, 관계인력 컬럼, 검증 anchor, grain 깊이
7. schema.yaml 오류 수정 — 관계인력 `actual_column: I` → `M` (3개년), 검증 anchor 2,804 → 8,197 현재원

---

## 성공한 것

### P1 산출물 (완료)

| 파일 | 상태 | 비고 |
|---|---|---|
| `pipeline/ddl.sql` | 완료 — DuckDB 실행 통과 | 테이블 4개, 뷰 1개, 직군 시드 6종, BU 시드 19 row |
| `pipeline/schema.yaml` | 완료 — PyYAML safe_load 통과 | hc_2023/2024/2025 sources 3개, actual_column=M 확정 |
| `pipeline/verify_ddl.py` | 완료 — 검증 도구 | 재검증 필요 시 `python pipeline/verify_ddl.py` |

### 확정된 설계 결정

| 항목 | 결정 | 근거 |
|---|---|---|
| 직군 분류 | 6종 EXEC/MGMT/OPER/FIELD/CONT/PART | 사용자 확인 |
| 관계인력 actual 컬럼 | M 컬럼 (I 아님) | 사용자 확인 |
| 검증 anchor (2025 Q2) | headcount_actual 현재원 합계 = **8,197** (PART 제외) | 사용자 확인 |
| Grain 깊이 | 부문/실(level 2) 기본, 팀(level 3) 확장 가능 | DDL 이미 N단계 재귀 설계 |
| BU 시계열 | SCD Type 2, PK=(bu_id, effective_from) | raw 검증 결과 |
| 합계 행 식별 | C 컬럼 어미 '계' (3개년 통용) | raw 검증 확정 |
| 5월 snapshot | quarter=2 고정 | 풀무원 인사 사이클 |
| 3개년 엑셀 구조 | '요약' 시트 187/190/212×33, 헤더 구조 3개년 cell-level 동일 | raw 검증 |

### DDL 구조 요약

```
dim_bu                 SCD Type 2, PK=(bu_id, effective_from), N단계 재귀 parent_id
dim_employment_type    직군 6종 시드
fact_headcount         year/quarter/bu_id/emp_type_code, headcount(T/O) + headcount_actual(현재원)
fact_related_personnel 관계인력, planned(H컬럼) + actual(M컬럼)
view_dashboard_bus     level=1 BU rollup, 6 emp_type 컬럼 + tot, 연도 필터 없음
```

---

## 실패한 것 / 막힌 것

### 미완료 — P2 진입 전 확인 필요

1. **BU 시계열 매핑 사용자 미검증** — dim_bu seed 의 연도별 BU 매핑이 실제 조직과 맞는지 미확인. 특히 시계열 무변동 BU (식품통합MBU, 샘물, 다논, NA, 중국, 일본, ORGA, FDD 등) 는 ddl.sql seed 에 없고 extract 단계에서 동적 INSERT 예정 — alias 확정 필요.

2. **2023/2024 검증 anchor 수치 미확정** — 2025 현재원 8,197 만 확정. 2023/2024 의 현재원 합계 미확인.

3. **관계인력 actual=M 2023/2024 미확인** — 2025 기준으로 M 확정. 2023/2024 도 동일 컬럼인지 엑셀 직접 확인 필요.

4. **`fact_related_personnel.bu_id` FK 설계 주의** — DDL 에 `REFERENCES dim_bu(bu_id)` 가 있으나 dim_bu PK 가 복합 `(bu_id, effective_from)` 이므로 단순 FK 불성립. DuckDB 는 현재 통과하나 Postgres 이행 전 수정 필요.

---

## 다음 단계

### 즉시 (P2 시작 전 권장)

1. **관계인력 actual 컬럼 2023/2024 확인** — `10-RAW/HC/2023.05/`, `2024.05/` 엑셀 열어 `관계인력(PPT)` 시트 M 컬럼 헤더 확인
2. **시계열 무변동 BU alias 확정** — bu_aliases 에 식품통합MBU/샘물/다논/NA/ORGA/FDD 등 시트명 변형 추가

### P2 plan 신규 작성 (`extract_excel.py`)

```
입력:  pipeline/schema.yaml
출력:  pipeline/hr.duckdb (fact_headcount, fact_related_personnel 적재)
처리 순서:
  1. sources 순회 (hc_2023 → 2024 → 2025)
  2. '요약' B/C 컬럼 forward-fill → dim_bu upsert (SCD Type 2)
  3. C 컬럼 어미 '계' 행 skip (합계 행)
  4. D=headcount(T/O), E=headcount_actual(현재원)
  5. L/M/N (또는 auto_detect) → emp_type_code 매핑
  6. 관계인력(PPT) A1:E15 skip → H=planned, M=actual
  7. validation_sheet anchor 대조 (headcount_actual=8,197)
검증:  LIMIT=1 → 2 → BU 단위 → 전체 순서 필수 (incremental)
```

주의사항:
- 원본 엑셀 절대 수정 금지 — `openpyxl(data_only=True, read_only=True)`
- `hr.duckdb` 공유용, `_internal.duckdb` 로컬 only → `.gitignore` 추가
- 팀(level 3) 확장: 요약 시트 들여쓰기 depth 감지 로직 추가 — schema 변경 불필요

### P3 이후

- `load_duckdb.py` → 집계 결과 공유 저장소 커밋
- `build_dashboard.py` → HTML 패치
- 인건비 / HCROI / 퇴직 raw 엑셀 별도 plan

---

## 참고 파일 경로

| 역할 | 경로 |
|---|---|
| 본 세션 plan | `archive/dashboard/plan-hc-schema-260512.md` |
| DDL | `pipeline/ddl.sql` |
| 스키마 매핑 | `pipeline/schema.yaml` |
| 검증 스크립트 | `pipeline/verify_ddl.py` |
| 엑셀 2025 | `10-RAW/HC/2025.05/1.인원현황_풀무원 전사_*.xlsx` |
| 엑셀 2024 | `10-RAW/HC/2024.05/1.인원현황_*.xlsx` |
| 엑셀 2023 | `10-RAW/HC/2023.05/1.인원현황_*.xlsx` |
