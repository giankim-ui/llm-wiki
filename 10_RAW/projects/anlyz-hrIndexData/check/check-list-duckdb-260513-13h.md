현재 DB 점검 사항

🔴 미완료 — result 체크리스트에 명시

2024·2023 외부 앵커 검증 미완

result 파일 76행: [ ] 2024·2023 외부 앵커 검증 (해당 연도 요약 시트 grand total 컬럼 구조 상이 — 추후 확인)

- 2025는 R26 검증식 9개 스캔으로 통과했지만, 2023/2024는 R26 없음
- plan §위험 5 기준: 전사총계 R21 "전사 총계계" row 와 DB SUM 직접 매칭 필요
- 아래 SQL 실행 후 엑셀 전사총계 시트 R21 값과 비교

SELECT year, quarter, SUM(headcount) AS db_sum
FROM fact_headcount
GROUP BY year, quarter
ORDER BY year;

---
🟡 확인 권장

① 직군 fallback 적재 비율

plan §위험 2: fallback_bucket=OPER 적재된 행이 10% 초과면 schema.yaml 보강 필요. 첫 빌드 후 사용자 확인 라운드로 명시됨.

-- fallback 의심: source_row 기반으로 매핑 실패 추정은 어렵지만
-- 직군별 비율이 OPER로 쏠려있으면 fallback 가능성
SELECT emp_type_code, COUNT(*) AS cnt,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM fact_headcount
GROUP BY emp_type_code
ORDER BY cnt DESC;

OPER 비율이 70%+ 이면 T(현장직 정규직), W(계약직) 컬럼 외 미인식 컬럼이 fallback된 것.

② headcount_actual 컬럼 적재 여부

DDL에 headcount_actual 컬럼이 있는데 result 파일에 언급 없음. NULL인지 실값 들어갔는지 미확인.

SELECT year, COUNT(*) FILTER (WHERE headcount_actual IS NOT NULL) AS actual_filled,
       COUNT(*) AS total
FROM fact_headcount GROUP BY year;

③ 연도별 BU 수 목록

plan §8.2 점검 ⑥: 아는 BU가 다 있는지 도메인 눈으로 확인 필요.

SELECT year, COUNT(DISTINCT bu_id) AS bu_count
FROM fact_headcount GROUP BY year ORDER BY year;
-- 기대: 2023=19, 2024=20, 2025=28 (plan 명시값)

-- 빠진 BU 의심 확인
SELECT DISTINCT bu_id, bu_name FROM dim_bu ORDER BY bu_level, bu_name;

④ SCD Type 2 시계열 연결 확인

로하스케어→건강생활→건강케어MBU, CSO→CHO/CCO/Corp/CFO 분화가 effective_from/to로 제대로 들어갔는지.

SELECT bu_id, bu_name, effective_from, effective_to
FROM dim_bu
WHERE bu_id IN ('health-care-mbu', 'cso-legacy', 'cho', 'cco', 'online')
ORDER BY bu_id, effective_from;

---
우선순위 요약

┌──────┬────────────────────────────┬────────────────────────────────┐
│ 순위 │            항목            │              근거              │
├──────┼────────────────────────────┼────────────────────────────────┤
│ 1    │ 2023·2024 앵커 검증        │ result 체크리스트 미완         │
├──────┼────────────────────────────┼────────────────────────────────┤
│ 2    │ 직군 fallback 비율         │ plan 명시 "첫 빌드 후 확인"    │
├──────┼────────────────────────────┼────────────────────────────────┤
│ 3    │ headcount_actual NULL 여부 │ result 언급 없음 → 미확인      │
├──────┼────────────────────────────┼────────────────────────────────┤
│ 4    │ BU 목록 누락 확인          │ 도메인 지식 필요 (사용자 판단) │
└──────┴────────────────────────────┴────────────────────────────────┘

2023·2024 앵커 검증이 가장 시급합니다 — 지금 DB에 7,900명대 두 연도가 맞게 들어갔는지 숫자 근거가 없는 상태입니다.

result: 적재 완료된 DuckDB에서 점검 필요 항목 4개 정리 (2023/2024 앵커 검증 미완 + 직군 fallback 비율 + headcount_actual 적재 여부 + BU 목록 도메인 확인)