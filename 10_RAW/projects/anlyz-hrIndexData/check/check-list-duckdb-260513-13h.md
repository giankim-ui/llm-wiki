<span style="color:red">**DB 점검 체크리스트 — 순서대로 하나씩 확인 (비개발자용, 2026-05-13 재작성)**</span>

아래 STEP 1부터 순서대로 진행하세요. 각 STEP에 SQL 쿼리가 있으면 DuckDB에 그대로 붙여넣고 실행하면 됩니다.

---

## STEP 1 🔴 2023·2024 연도 숫자 검증 (가장 먼저)

**무엇을 확인하나요?**
DB에 들어간 2023·2024년 인원 합계가 엑셀 원본 숫자와 맞는지 확인합니다.
2025년은 이미 검증됐지만, 2023·2024는 아직 대조가 안 된 상태입니다.

**어떻게 하나요?**
아래 SQL을 실행하면 연도·분기별 DB 합계가 나옵니다.

```sql
SELECT year, quarter, SUM(headcount) AS db_sum
FROM fact_headcount
GROUP BY year, quarter
ORDER BY year;
```

**통과 기준**: 출력된 숫자를 엑셀 "전사총계" 시트 21번째 행 값과 비교 → 일치하면 OK

---

## STEP 2 🟡 직군 분류 오류 비율 확인

**무엇을 확인하나요?**
직군을 제대로 인식 못 한 데이터가 'OPER(현장직)' 로 몰려 들어갔을 수 있습니다.
OPER 비율이 지나치게 높으면 분류 기준을 손봐야 합니다.

**어떻게 하나요?**
아래 SQL로 직군별 비율을 확인합니다.

```sql
SELECT emp_type_code, COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM fact_headcount
GROUP BY emp_type_code
ORDER BY cnt DESC;
```

**통과 기준**: OPER 비율이 **70% 미만**이면 정상 / 70% 이상이면 담당자에게 확인 요청

---

## STEP 3 🟡 헤드카운트 실적값 입력 여부 확인

**무엇을 확인하나요?**
DB에 '실적 인원(headcount_actual)' 칸이 있는데, 값이 실제로 들어갔는지 아직 확인되지 않았습니다.

**어떻게 하나요?**
아래 SQL로 연도별 입력 건수를 확인합니다.

```sql
SELECT year,
       COUNT(*) FILTER (WHERE headcount_actual IS NOT NULL) AS actual_filled,
       COUNT(*) AS total
FROM fact_headcount
GROUP BY year;
```

**통과 기준**: `actual_filled` 값이 0보다 크면 입력된 것 / 0이면 빈값이므로 담당자 확인 필요

---

## STEP 4 🟡 사업부(BU) 목록 누락 확인

**무엇을 확인하나요?**
알고 있는 사업부가 DB에 모두 들어갔는지 직접 눈으로 확인합니다.
이 항목은 숫자가 아니라 **사람이 판단**해야 합니다.

**어떻게 하나요?**
아래 SQL로 연도별 사업부 수와 전체 목록을 확인합니다.

```sql
-- 연도별 사업부 수 (기대: 2023=19개, 2024=20개, 2025=28개)
SELECT year, COUNT(DISTINCT bu_id) AS bu_count
FROM fact_headcount
GROUP BY year
ORDER BY year;

-- 전체 사업부 목록
SELECT DISTINCT bu_id, bu_name FROM dim_bu ORDER BY bu_level, bu_name;
```

**통과 기준**: 목록에서 빠진 사업부가 없는지 직접 확인 → 이상 없으면 OK