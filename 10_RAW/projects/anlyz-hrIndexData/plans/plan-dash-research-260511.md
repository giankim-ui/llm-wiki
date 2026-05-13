# HR Dashboard 실행 방안 (Research)

작성일: 2026-05-11  
대상 산출물: `hr_dashboard_v4-byM.html` (3탭: 인원·인건비·생산성) 의 하드코딩 데이터를 **실 raw 엑셀**로 교체  
참고(미적용): `HR_Dashboard_Plan.md` 787줄 마스터, `handoff.md` — 전략 재설계는 본 플랜의 scope 아님  
원칙 (raw plan 명시): ① 정확성 ② 원본 무수정 ③ 최단시간 ④ 재사용성

---

## 1. Context — 왜 이 플랜이 필요한가

목업 HTML 은 `BUS[]`, `TURN_DATA`, `PEER_HCROI` 등 **모든 데이터가 인라인 JS 상수로 하드코딩**돼 있다. raw 엑셀(`10-RAW/HC` 외)을 어떻게 이 구조로 흘려넣을지를 결정해야 한다. 사용자가 원한 결정 포인트는:

> (A) 엑셀을 한 폴더에 모은다 → (B) 파싱·JSON 추출 → (C) **혹은 더 빠르고 효율적인 방안**

본 research 는 (C)의 후보를 비교하고 권장안을 제시한다.

---

## 2. 현 상태 인벤토리 (사실 확인)

| 영역 | 현황 | 갭 |
|---|---|---|
| 원본 엑셀 (HC) | `10-RAW/HC/` 인원현황·지원조직 2 개 (~1 MB) | **인건비·HCROI·퇴직 엑셀 미확보** — 위치/소유자 식별 필요 |
| 보고 PPTX | `10-RAW/DB-Report-F/` 13 개 (~76 MB) | 본문 텍스트·표는 `_handoff_assets/extracted_chapters/` 13 JSON 으로 추출 완료 — KPI 시계열 backfill 에 재활용 가능 |
| 파싱 인프라 | `_handoff_assets/extract_pptx.py` (재실행 가능) | 엑셀 파서 부재 |
| 시각화 | `hr_dashboard_v4-byM.html` (Chart.js 4.4.1, 정적 JS 하드코딩, 18 차트 / 30+ KPI) | fetch·외부 데이터 주입 지점 없음 |

**사용자 응답 반영 (2026-05-11 확정)**
1. 인건비 / HCROI / 퇴직 raw 엑셀 위치 → **별도 폴더에 존재, 현재 미공유** (P6 진입 전 공유 필요)
2. 갱신 주기 → **분기 단위 추가**. **자동화는 본 phase 범위 외** (수동 빌드 1 명령으로 충분)
3. ERP/급여원장 직접 접근 → **현재 불가**, 추후 별도 phase 에서 검토

→ 본 phase 의 스코프는 (a) 분기 1 회 수동 빌드로 (b) raw 엑셀 → 대시보드 갱신을 완료하는 것까지로 한정.

---

## 3. 목업 HTML 의 데이터 모델 역설계

`hr_dashboard_v4-byM.html` 가 요구하는 데이터 스키마 (인라인 `BUS[]` 분석 결과):

```text
BU 레벨 레코드 (배열 1 행 = 1 BU)
  id, name                                   ← BU 마스터
  bgt, act, ur(=act/bgt*100)                 ← 인건비 (예산/실적/집행율)
  nPl, nAct, nr(=nAct/nPl*100)               ← NNR (계획/실적/달성율)
  lr(=act/nAct*100)                          ← 인건비율
  cb                                         ← CEBIT-예산
  c26/f26/o26/g26                            ← 고용형태별 인원 (계약/현장/운영/경영간부)
  tot                                        ← 관계인력 합계
  turn                                       ← 퇴사율(%)
  pat                                        ← 패턴/표시용 메타
BUS_PREV[BU] = {tot, g, o, f, c}             ← 전년 동분기 비교
TURN_DATA[] = {bu, head, quit, cur, est, y24, g, o}   ← 퇴직 상세
PEER_HCROI = {풀무원, 오리온, 오뚜기, CJ}    ← 정적 비교 (수동 유지)
```

→ 필요한 **소스 테이블 6 종**: ① 인원마스터 ② 관계인력 ③ 인건비(고용형태×BU×월) ④ NNR/예산 ⑤ 퇴사 ⑥ 영업이익(법인). 이 중 ①·②는 현재 `HC/` 에 부분 존재, ③~⑥은 위치 미확정.

---

## 4. 파이프라인 옵션 비교

| # | 방안 | 환경 의존 | 갱신 자동화 | 재사용성 | 학습곡선 | 비고 |
|---|---|---|---|---|---|---|
| **A** | 한 폴더 통합 + Power Query (Excel 내장 ETL) | Excel만 | 새 파일 떨궈도 새로고침 1 회 | 중 | 낮음 | 신규 도구 0. **단점**: HTML 자동 주입 불가 — 별도 export 단계 필요 |
| **B** | 폴더 통합 + Python(pandas) → JSON | Python | `python build.py` 1 명령 | 중상 | 중 | 사용자가 던진 기본안. JSON 을 HTML fetch 또는 inject |
| **C** | 폴더 통합 + Python → **DuckDB (네이티브 테이블)** | Python+DuckDB | 동일 | **상** | 중 | SQL 로 임의 KPI 조회. 단일 `.duckdb` 파일. in-process |
| **D** | SQLite 단일 DB 파일 | Python+sqlite | 동일 | 상 | 중 | Excel·Power BI·Tableau 모두 connector 존재 |
| **E** | Long-format **단일 CSV/Parquet** + JSON 빌드 | Python | 동일 | 최상(이론) | 낮음 | 한 행 = (year, quarter, bu, kpi_id, value, unit, source) — **사용자 우려로 기각** (아래 참조) |

### Long-format(E) 기각 사유 (사용자 피드백 반영)

- 인건비 raw 는 **사원 1 명 × 12 개월 × 3 개년** 구조 → long 으로 펼치면 사원 N × 36 행, 추가로 항목별(기본급/상여/4대보험/…) 행 분해 시 수십~수백만 행으로 폭증.
- 인원/퇴직/HCROI 도 엑셀 스키마가 **소스별 비일관** → long 으로 강제 정규화 시 (a) 매핑 정의 비대 (b) 로딩·집계 비용 ↑.
- BU 가 단순 1-레벨이 아니라 **사업단위 트리(BU → 사업부 → 팀)** 로 확장될 가능성 → long-format 한 장에 트리를 욱여넣으면 path/level 컬럼 추가 부담.

→ **DuckDB 네이티브 테이블(소스별 wide / star-schema fact)** 가 더 적합. DuckDB 는 컬럼나·압축 내장으로 wide 테이블도 빠르게 처리.

### DuckDB ↔ Supabase(PostgreSQL) 호환성 — 사전 검증

이후 Supabase 마이그레이션이 예정된 점을 고려하여 호환성을 명시:

| 항목 | DuckDB | Supabase(Postgres) | 마이그레이션 경로 |
|---|---|---|---|
| SQL 방언 | PostgreSQL-호환 (대부분의 표준 SQL·집계·윈도우 함수) | Postgres 15 | 거의 무수정 |
| 타입 | INTEGER / BIGINT / DOUBLE / VARCHAR / DATE / TIMESTAMP / DECIMAL | 동일 명칭 존재 | 1:1 매핑 |
| Export | `COPY … TO 'x.parquet'` / `'x.csv'`, `EXPORT DATABASE` | `\copy`, `pg_dump`, `pg_parquet` 확장 | Parquet 또는 CSV 중간포맷 |
| 직접 연결 | **`postgres` 확장**: `ATTACH 'postgres://…' AS pg; INSERT INTO pg.schema.t SELECT * FROM duck_t;` | — | **DuckDB → Supabase 직접 INSERT 가능** |
| 스키마 DDL | 호환 가능한 부분집합으로 작성 시 그대로 이식 | — | `CREATE TABLE` 그대로 복붙 가능 |

→ **결론**: SQL·타입을 Postgres 표준 부분집합으로 한정해 작성하면 마이그레이션은 (a) `EXPORT DATABASE` → Supabase `\copy`, 또는 (b) DuckDB `postgres` 확장으로 직접 push, 둘 다 1 시간 이내 가능. **본 phase 에서 DuckDB 채택해도 lock-in 없음**.

### 권장: **C — DuckDB 네이티브, 소스별 fact 테이블 (star-schema)**

- **저장 레이어**: 단일 `hr.duckdb` 파일
  - `dim_bu` (bu_id, bu_name, parent_id, effective_from, effective_to) ← BU 트리·시계열 변경 대응
  - `fact_headcount` (year, quarter, bu_id, employment_type, headcount)
  - `fact_labor_cost` (year, month, bu_id, employee_id 또는 집계키, account_code, amount) ← raw 보존
  - `fact_turnover` (year, quarter, bu_id, head, quit, current, estimated)
  - `fact_hcroi` (year, quarter, company, hcroi, revenue, ebit)
  - 필요 시 `view_dashboard_bus` 등 dashboard 직결 view 로 집계
- **조회 레이어**: DuckDB SQL (Postgres 호환 부분집합으로 제한)
- **배포 레이어**: `build_dashboard.py` 가 view 쿼리 → HTML 의 `BUS[]` 구조로 JSON 직렬화 → `data/dashboard.json`
- **HTML 변경**: 하드코딩 `const BUS = [...]` → `const BUS = await fetch('data/dashboard.json').then(r=>r.json())`

**이유**
1. 4 원칙 충족: 원본 read-only(②), 1 명령 갱신(③), SQL 로 결정론적 검증(①), 소스별 fact 분리로 재사용성(④).
2. wide/star-schema 라 raw 엑셀과 시각적 매핑이 쉬워 검증 비용 ↓ (long 보다 디버그 용이).
3. BU 트리 확장·시계열 변경은 `dim_bu` 의 effective_from/to 로 흡수.
4. Supabase 이행은 별 lock-in 없이 가능 (위 호환성 표).
5. DuckDB 는 단일 파일·zero-config — 신규 서버·라이선스 0.

---

## 5. 폴더·산출물 구조 (제안)

```text
HR-indexData/
├── 10-RAW/                       (수정 금지)
│   ├── HC/                       기존
│   ├── LaborCost/                ★ 신규 — 인건비 엑셀 모으기
│   ├── HCROI/                    ★ 신규
│   └── Turnover/                 ★ 신규
├── pipeline/
│   ├── extract_excel.py          xlsx → pandas DataFrame (소스별 wide 유지)
│   ├── schema.yaml               시트·헤더·BU 별칭·KPI 산식 정의
│   ├── load_duckdb.py            DataFrame → DuckDB fact 테이블 적재 (idempotent)
│   ├── ddl.sql                   dim_bu / fact_* / view_* (Postgres 호환 부분집합)
│   └── build_dashboard.py        DuckDB 쿼리 → data/dashboard.json
├── data/
│   ├── hr.duckdb                 단일 DB 파일 (Supabase 이행 시 export 원천)
│   └── dashboard.json            HTML 이 fetch 하는 최종 산출물
├── dist/
│   └── hr_dashboard.html         hr_dashboard_v4-byM.html 의 fetch 버전
└── archive/                      plan/result 보관 (본 파일)
```

---

## 6. 단계별 실행 순서

P0(사용자 인터뷰)는 §2 응답으로 완료. 본 phase 는 P1 부터 시작.

| Phase | 작업 | 산출물 | 검증 |
|---|---|---|---|
| **P1** | `schema.yaml` + `ddl.sql` — BU 별칭(식품통합·NA·일본 등), 고용형태 코드, KPI 산식, fact 테이블 DDL(Postgres 호환) | 2 파일 | 목업 HTML 의 `BUS[]` 필드 ↔ view 컬럼 1:1 매핑 표 |
| **P2** | `extract_excel.py` — `HC/` 2 개 엑셀부터. 헤더 행 자동 탐지 + 시트별 매핑. **LIMIT=1 → 2 → 전체 순** 검증 (메모리 글로벌 룰) | 함수 + 단위 테스트 | 인원 합계가 목업의 8,134 와 ±1% 이내 |
| **P3** | `load_duckdb.py` — DataFrame → DuckDB fact 테이블 적재 (re-run idempotent) | `hr.duckdb` 1 개 | `SELECT COUNT(*), SUM(headcount) FROM fact_headcount` 검증 |
| **P4** | `build_dashboard.py` — 18 차트별 SQL → `dashboard.json` | json 1 개 | json schema 가 기존 `BUS[]` 와 deep-equal |
| **P5** | HTML 패치 — 하드코딩 1 줄 → fetch. **원본 무수정**, `dist/` 에 복사본 | hr_dashboard.html | 브라우저에서 18 차트 정상 렌더, console error 0 |
| **P6** | 인건비/HCROI/퇴직 엑셀 ingestion 추가 (raw 공유 시점에 진입) | extract_excel 확장 + fact_* 적재 | 차트별 모의수치 → 실수치 교체 |
| **P7** | `run.ps1` — pipeline 순차 실행 1 명령. 자동화·스케줄러 불필요(분기 1 회 수동) | 1 스크립트 | end-to-end 5 분 이내 갱신 |

---

## 7. 핵심 설계 결정

| 결정 | 채택 | 기각안 / 이유 |
|---|---|---|
| 저장 포맷 | **DuckDB 단일 파일 (`hr.duckdb`)** | SQLite — DDL 표현력·집계 성능 열위. Parquet 단독 — 트랜잭션·view·idempotent upsert 어려움 |
| 조회 엔진 | DuckDB in-process | Postgres/MySQL — 서버 운영 비용. Excel-Power Query — 코드 버전관리 어려움 |
| 데이터 모델 | **Star-schema (소스별 fact_* 테이블 + dim_bu)** | Long-format(E) — 사원×월×년 폭증 + 트리 BU 수용 어려움(사용자 우려). Wide 한 장 — 소스 이질성 흡수 못함 |
| Supabase 호환 | DDL·SQL 을 **Postgres 호환 부분집합** 으로 한정. type=INTEGER/BIGINT/DOUBLE/VARCHAR/DATE/TIMESTAMP/DECIMAL 만 사용 | DuckDB 전용 타입(STRUCT/LIST/MAP) — 이행 시 변환 비용 |
| HTML 주입 | 빌드 시 정적 `data/dashboard.json` + fetch | HTML 안에 `<script>` inline — diff 가독성 ↓, 캐싱 어려움 |
| 시각화 도구 | **현 Chart.js 유지** (목업 그대로) | Power BI / Tableau — 사용자가 "최초 목업 스타일" 명시. 도구 교체 scope 아님 |
| 원본 보호 | `10-RAW/` read-only, 빌드는 `data/` 에만 기록 | — (raw plan 원칙 ②) |
| BU 별칭·시계열 | `dim_bu` 테이블 + `schema.yaml` 단일 사전 | 코드 하드코딩 — 매번 PR 발생. 사용자 문서 어휘(식품통합·NA·일본)와 엑셀 시트명 사이 alias 필요 |
| 자동화 | **없음 (분기 1 회 수동 `run.ps1`)** | 사용자 §2 응답 반영. cron/Task Scheduler 도입은 본 phase 외 |

---

## 8. 위험 / 미결사항

1. **[최대 위험] 엑셀 헤더 비일관성** — 풀무원 인사 엑셀은 다년간 누적되며 시트명·헤더 위치·컬럼 순서가 제각각일 가능성 매우 높음 (사용자 확인). 대응: `schema.yaml` 에 **파일·시트별 override 블록** 을 1급 시민으로 두고, 헤더 자동 탐지(키워드 fuzzy match) + 실패 시 명시적 매핑. P2 에서 LIMIT=1 검증 시 우선 처리.
2. **[고위험] BU 정의 변경** — 조직개편으로 BU 명·구성이 자주 바뀌어 시계열이 끊길 위험 높음 (사용자 확인). 대응: `dim_bu` 에 `bu_alias`, `effective_from`, `effective_to`, `parent_id` 를 두고 fact 는 시점의 `bu_id` 만 참조 → 별칭 변동은 dim 갱신으로만 흡수.
3. **퇴직 데이터의 PII** — 개인 단위 raw 가 포함되면 git 커밋 금지. `data/` 는 .gitignore, 집계치만 산출.
4. **HCROI 의 손익원장 의존** — raw plan 의 핵심 4 카테고리 중 가장 외부 시스템 의존도 높음. 분기말 D+15 이후만 가능 (handoff §G 와 동일 제약).

(이전 안의 PPTX JSON 활용 항목은 제거 — 사용자 확인: 엑셀 DB화 완료 후 PPTX 추출본은 불필요.)

---

## 9. End-to-end 검증 시나리오

빌드 한 번에 다음이 모두 성공해야 한다.

1. `python pipeline/load_duckdb.py` — `hr.duckdb` 생성, `fact_headcount` row count > 0, `dim_bu` row count = BU 수.
2. `python pipeline/build_dashboard.py` — `dashboard.json` 생성, `BUS` 배열 길이 = BU 수, 모든 필드 not-null.
3. 단위 검증 SQL — `SELECT bu_id, SUM(headcount) FROM fact_headcount WHERE quarter='2026Q1' GROUP BY bu_id` 합계가 목업의 8,134 와 ±1% 이내.
4. `python -m http.server 8000 --directory dist` → 브라우저에서 `hr_dashboard.html` 열람 → 18 차트 모두 렌더, console error 0.
5. 임의 엑셀 1 개 추가 후 `run.ps1` 재실행 → 5 분 이내 대시보드 갱신.
6. **Supabase 호환 spot-check** — `EXPORT DATABASE 'tmp_export'` 후 `tmp_export/schema.sql` 가 Postgres `psql` 에서 unsupported syntax 없이 파싱되는지 확인.

---

## 10. 다음 액션 (사용자 결정 요청)

**[즉시 진행 가능 — 사용자 답변 반영 후]**
- P1 `schema.yaml` + `ddl.sql` 초안 — 목업 HTML 의 `BUS[]` 필드 ↔ DuckDB view 컬럼 매핑, Postgres 호환 DDL
- P2 prototype — `10-RAW/HC/` 2 개 엑셀로 wide DataFrame 추출 PoC (LIMIT=1 → 2 → 전체)
- P3 DuckDB 적재 — `fact_headcount` + `dim_bu` 만 우선 채워 인원 합계 8,134 검증

**[raw 공유 대기 — P6 전제]**
- 인건비 raw (별도 폴더에 존재, 미공유)
- HCROI raw (별도 폴더에 존재, 미공유)
- 퇴직 raw (별도 폴더에 존재, 미공유)

**[추후 별도 phase]**
- ERP·급여원장 직접 접근 (현재 불가)
- Supabase 마이그레이션 (본 phase 산출물은 호환 부분집합으로 작성하여 lock-in 회피)

---

## 11. 비-목표 (Out of Scope, 명시)

- `HR_Dashboard_Plan.md` 의 12장 재설계·6대 KPI 축·ISO 30414·Hero KPI 6개 도입 — 본 플랜은 **목업 그대로의 3탭**만 채운다.
- Power BI / Tableau 이행
- Engagement·OHI·승계계획·예측 모델 (마스터플랜 Phase 2~3)
- 외부 공시·K-ESG 수준의 데이터 거버넌스

위 항목은 본 파이프라인이 안착한 뒤 별도 plan 으로 분리.
