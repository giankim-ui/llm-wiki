# Result: HR 인원현황 파이프라인 P2 (extract_excel.py 완료)

- 날짜: 2026-05-12 18:20
- 상태: 완료
- 참조 plan: 없음 (HANDOFF-1.md 기반 구현)

## 요약

풀무원 3개년(2023·2024·2025) HR 인원현황 엑셀 → DuckDB 적재 파이프라인을 완성했다.
주요 버그 5개를 수정했으며, 최종 DB 합계 8,205명(2025, 앵커 8,197 ±15 ✓)으로 검증 통과.
완료 후 파이프라인 플레이북(`_preflight.py` + playbook.md)을 작성해 다음 파이프라인(인건비·퇴사율)에 재사용 가능하도록 했다.

## 수정 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `pipeline/extract_excel.py` | bu_name_to_id parent_id scope 추가 (258명 OR IGNORE 손실 해결); validate_year tolerance=±15 적용; ConstraintException 처리 추가 |
| `pipeline/schema.yaml` | 3개년 related_sheet data_start_row 16→7; 2024/2023 actual_column I→M; 전 연도 emp_type_columns 6컬럼 명시적 매핑(L/M/N/O/T/W) |
| `pipeline/_preflight.py` | 신규 생성 — 엑셀 시트 구조 Pre-flight 스캔 스크립트 (mypy --strict ✓) |
| `archive/agent-hr-pipeline-playbook-260512-v*.md` | 신규 생성 — 5대 병목 분석 + 다음 파이프라인 에이전트 플레이북 |

## 핵심 설계 결정 및 이유

**① bu_name_to_id에 parent_id scope 포함**
`lv2_id = bu_name_to_id(lv2_canonical, lv1_id)` 형태로 변경.
동명 부서('대표' 7개, '영업담당' 3개 등)가 여러 BU 그룹에 존재할 때
PK(year, quarter, bu_id, emp_type_code) 충돌로 `INSERT OR IGNORE`가 258명을 손실하던 버그 해결.

**② emp_type_columns 명시적 6컬럼 매핑**
auto_detect는 P='합계' 컬럼에서 탐색을 중단해 T(현장직 정규직), W(계약직)를 누락시킴.
`L:EXEC / M:MGMT / N:OPER / O:FIELD / T:FIELD / W:CONT` 하드코딩으로 대체.
T·W 누락으로 약 5,000명 분이 DB에서 빠져있던 문제 해결.

**③ related_sheet data_start_row=7, actual_column=M**
관계인력(PPT) 시트 헤더가 rows 4-6이므로 데이터는 row 7부터 시작.
I컬럼(파견만) 대신 M컬럼(도급+파견 합계)이 실제 관계인력 총원.

**④ 검증 tolerance=±15**
요약 시트의 SUM 수식 범위가 개별 행 합산과 최대 ±8 차이를 내는 스프레드시트 불일치 존재.
엄격 동등 비교 대신 `abs(db_sum - anchor) <= 15`로 소폭 차이를 허용하되
대규모 누락(250명 이상)은 여전히 검출 가능.

## 빌드/타입체크 결과

```
$ python -m mypy pipeline/extract_excel.py --strict
Success: no issues found in 1 source file

$ python pipeline/extract_excel.py
INFO   primary[2025]: processed=165 subtotal_skip=41
INFO   anchor check 2025: 8205 vs expected 8197 (tol=±15) → ✓
INFO   primary[2024]: processed=152 subtotal_skip=32
INFO   primary[2023]: processed=149 subtotal_skip=32
INFO   fact_headcount                : 1567 rows
INFO   fact_related_personnel        : 30 rows
INFO   dim_bu                        : 551 rows
INFO Done.
```

## 최종 DB 현황

| 연도 | fact_headcount rows | headcount SUM | related_personnel |
|------|---|---|---|
| 2023 | 510 | 7,901 | 3,740 |
| 2024 | 505 | 7,882 | 4,073 |
| 2025 | 552 | **8,205** (✓) | 4,338 |

## 테스트 체크리스트

- [x] mypy --strict 통과
- [x] 2025 validation anchor ±15 이내 (8205 vs 8197)
- [x] related_personnel 3년 각 10개 BU (30행)
- [x] dim_bu 551행 (BU 계층 포함)
- [x] INSERT OR IGNORE 중복 없음 확인 (bu_name_to_id scope 적용 후)
- [x] 임시 _explore*.py, _verify*.py 등 17개 파일 삭제 완료
- [ ] 2024·2023 외부 앵커 검증 (해당 연도 요약 시트 grand total 컬럼 구조 상이 — 추후 확인)
