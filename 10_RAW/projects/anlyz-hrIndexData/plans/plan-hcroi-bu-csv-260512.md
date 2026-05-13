# Plan — HCROI · 매출액대비인건비 사업단위 CSV 자동 작성

작업 디렉토리: `C:/Users/Pulmuone/OneDrive - 풀무원/HR-indexData/`
근거 plan: `archive/plan-hcroiRe-260512-v2.0.0.md`
작성일: 2026-05-12

---

## 1. Context (왜)

- **목적**: 기존 수작업 양식(`archive/인건비생산성(HCROI)_사업단위(지주사)_250520.xlsx`)을 자동화하여, 풀무원 사업단위 2사 + 동종사 4사의 **HCROI** 와 신규지표 **매출액 대비 인건비**를 단일 CSV로 산출.
- **현행 한계**:
  - 기존 xlsx는 시트 7개 + 수기 셀 입력 + 빈 연도 다수(2021·2022 미입력) → 무겁고 갱신 어려움
  - `매출액 대비 인건비` 지표 미포함
- **목표 산출물**: '사업단위명' 1개 시트 구조를 따른 가벼운 CSV. 매 회 실행시 사용자에게 재무제표 기준·연도 범위를 인터랙티브로 받음.
- **인프라**: 기존 `S-anlyz-kr/.claude/agents/data-collector-agent.md` (OpenDART API 1순위) 재사용.

---

## 2. Scope

### 2.1 대상 회사 6사 (기존 양식 고정)

| 구분 | 회사 | 비고 |
|---|---|---|
| ① 사업단위 | (주)풀무원 | 지주 |
| ① 사업단위 | 풀무원식품㈜ | 식품 자회사 |
| ② 동종사 | CJ제일제당 | DART 097950 (KOSPI) |
| ② 동종사 | 대상 | DART 001680 |
| ② 동종사 | 오리온 | DART 271560 |
| ② 동종사 | 오뚜기 | DART 007310 |

corp_code 는 OpenDART `/company.json?stock_code={ticker}` 로 실행 시 조회 (하드코딩 금지 — G-KR-001).

### 2.2 인터랙티브 입력 (매 실행시 사용자에게 질문)

1. **재무제표 기준** — `1) 단독(OFS)`  /  `2) 연결(CFS)`  /  `3) 둘 다 병기`
2. **연도 범위** — 자유 입력(예: `2021-2024`, `2024`, `최근 3년`)

### 2.3 데이터 항목 (회사 × 연도)

| 필드 | 단위 | 출처 |
|---|---|---|
| `revenue` 매출액 | 원 | OpenDART `fnlttSinglAcntAll` (account_id=`ifrs-full_Revenue` 또는 한글명 "매출액") |
| `op_income` 영업이익 | 원 | OpenDART `fnlttSinglAcntAll` (account_id=`dart_OperatingIncomeLoss` 또는 "영업이익") |
| `employee_benefits` 종업원급여 | 원 | **사업보고서 주석 — 비용의 성격별 분류** (API 미지원, Chrome/Bash 다운로드 필요) |

### 2.4 계산 산식 (cross-check 검증 완료)

```
HCROI               = (영업이익 + 종업원급여) / 종업원급여
매출액대비인건비    = 종업원급여 / 매출액
동종업계평균(HCROI) = AVG(CJ, 대상, 오리온, 오뚜기)
동종업계평균(인건비비율) = AVG(CJ, 대상, 오리온, 오뚜기)
```

검증: 풀무원 2024 ⇒ (91,829,407,927 + 555,619,073,000) / 555,619,073,000 = **1.165274** ✅ (기존 셀과 일치)

---

## 3. 산출물 (Output)

### 3.1 파일

- 디렉토리: `HR-indexData/output/` (신설)
- 파일명: `HCROI_사업단위_{YYMMDD}_{기준}.csv`
  - 기준 = `OFS` | `CFS` | `BOTH`
  - 예: `HCROI_사업단위_260512_OFS.csv`
- 인코딩: **UTF-8 with BOM** (Excel 한글 깨짐 방지)
- 구분자: 쉼표 (`,`)

### 3.2 CSV 레이아웃 (기존 '사업단위명' 시트 모방)

```csv
연도,항목,(주)풀무원,풀무원식품㈜,CJ제일제당,대상,오리온,오뚜기,동종업계평균
2024,HCROI,1.165274,1.192939,1.456683,1.326893,2.482714,1.531316,1.699402
2024,매출액대비인건비,,,,,,,
2024,영업이익(원),91829407927,51702496473,1553017638000,176941145485,543587778241,222014509063,
2024,종업원급여(원),555619073000,267973332000,3400644768000,541282000000,366616649000,417858069000,
2024,매출액(원),,,,,,,
2023,HCROI,...
```

- `BOTH` 선택시: 항목명 뒤 `(단독)` / `(연결)` 접미사 → 행 수 2배
- 미수집 값: 공란 (null). 추정·역산 금지 (data-collector-agent 원칙).

---

## 4. Implementation Pipeline

### Phase A — 사용자 인터뷰 (인터랙티브)

`AskUserQuestion` 으로:
- Q1. 재무제표 기준 = OFS / CFS / BOTH / 직접 입력
- Q2. 연도 범위 = 자유 텍스트

### Phase B — corp_code 일괄 조회 (Bash + OpenDART)

6사 각각:
```bash
curl "https://opendart.fss.or.kr/api/company.json?crtfc_key=$DART_API_KEY&corp_code={X}"
# (주)풀무원·풀무원식품은 stock_code 미보유시 corpCode.xml 다운로드 후 회사명 매칭)
```
- 상장사 4사(CJ·대상·오리온·오뚜기)는 `stock_code` 로 직접 조회
- (주)풀무원(017810)·풀무원식품 corp_code 는 `corpCode.xml` ZIP 받아 회사명 매칭
- 결과 캐시: `output/.cache/corp_codes.json`

### Phase C — 재무제표 본문 수집 (매출액·영업이익)

회사 × 연도 매트릭스 순회:
```bash
curl "https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json?crtfc_key=$DART_API_KEY&\
corp_code={code}&bsns_year={YEAR}&reprt_code=11011&fs_div={OFS|CFS}"
```
- 응답 JSON `list[]` 에서 다음 키 파싱:
  - `account_id = "ifrs-full_Revenue"` 또는 `account_nm` 포함 "매출액" → `thstrm_amount`
  - `account_id = "dart_OperatingIncomeLoss"` 또는 `account_nm == "영업이익"` → `thstrm_amount`
- 캐시: `output/.cache/financials_{corp}_{year}_{fs_div}.json`

### Phase D — 종업원급여 추출 (가장 까다로움)

OpenDART 정형 API 미지원 → **사업보고서 원문 다운로드 후 텍스트 파싱**.

1. `list.json` 으로 회사·연도별 사업보고서 `rcpNo` 확보 (G-KR-002 회피)
2. `document.xml` API (DART 공시원본 ZIP) 다운로드:
   ```bash
   curl "https://opendart.fss.or.kr/api/document.xml?crtfc_key=$DART_API_KEY&rcpNo={rcpNo}" -o tmp.zip
   unzip tmp.zip -d output/.cache/dart_raw/{corp}_{year}/
   ```
3. ZIP 내 XML 들에서 **"비용의 성격별 분류"** 또는 **"종업원급여"** 섹션 grep
4. 표 파싱: 종업원급여 = `급여 + 퇴직급여 + 4대보험(복리후생비 일부) + 인센티브 + 기타`
   - 단순 "종업원급여" 합계 행이 있으면 그 값 사용
   - 없으면 구성요소 합산 → null 처리 (추정 금지, 사용자 확인 필요)
5. document.xml 실패시 Chrome Fallback (G-KR-005, G-KR-010):
   - `dsaf001/main.do?rcpNo={rcpNo}` 진입 → `find("비용의 성격별 분류")` → `scroll_to` → `screenshot`
   - **픽셀 좌표 하드코딩 금지**

### Phase E — 산식 적용 + CSV 출력

- Python `pandas` 로 DataFrame 조립
- 동종업계평균 = CJ·대상·오리온·오뚜기 4사 단순평균 (null 제외 후 평균)
- `df.to_csv(path, encoding='utf-8-sig', index=False)`

### Phase F — Verification (필수)

CSV 작성 후 기존 xlsx 와 cross-check:

| 검증 항목 | 기준값 (기존 xlsx) | 허용 오차 |
|---|---|---|
| (주)풀무원 2024 HCROI | 1.165274 | ±0.0001 |
| 풀무원식품 2024 HCROI | 1.192939 | ±0.0001 |
| CJ제일제당 2024 HCROI | 1.456683 | ±0.0001 |
| 대상 2024 HCROI | 1.326893 | ±0.0001 |
| 오리온 2024 HCROI | 2.482714 | ±0.0001 |
| 오뚜기 2024 HCROI | 1.531316 | ±0.0001 |
| 동종업계평균 2024 HCROI | 1.528004 | ±0.001 |

**1개라도 어긋나면 즉시 중단** → 데이터 출처·산식 재검토 후 사용자 보고.

---

## 5. 핵심 파일 · 참조 자료

| 경로 | 역할 |
|---|---|
| `HR-indexData/archive/인건비생산성(HCROI)_사업단위(지주사)_250520.xlsx` | 산식·레이아웃 reference (변경 금지) |
| `HR-indexData/S-anlyz-kr/.claude/agents/data-collector-agent.md` | OpenDART 수집 패턴 (재사용) |
| `HR-indexData/S-anlyz-kr/.claude/GOTCHAS/GOTCHAS.md` | G-KR-001 ~ G-KR-013 필독 |
| `HR-indexData/S-anlyz-kr/CLAUDE.md` | Source Allowlist · Null Policy |
| **신설** `HR-indexData/output/` | CSV 산출물 디렉토리 |
| **신설** `HR-indexData/output/.cache/` | DART 응답·다운로드 ZIP 캐시 (재실행 비용 절감) |

---

## 6. 운영 원칙 (data-collector-agent CLAUDE.md 준수)

- **Source Allowlist 엄수**: opendart API + dart.fss.or.kr (Chrome only) + finance.naver.com. 그 외 검색 금지.
- **Null Policy**: 미확인 수치 = 공란. 추정·2차소스 사용 금지.
- **fetch_method 기록**: 캐시 JSON 에 `api | chrome | unavailable` 명시.
- **재무제표 기준 일관성**: 한 CSV 안에서 OFS / CFS 혼용 금지 (BOTH 옵션은 행 분리로 처리).
- **단위 통일**: 원본은 원(₩) 단위. 가공·반올림 금지.
- **재실행 멱등성**: `output/.cache/` 가 있으면 API 재호출 스킵 → 동일 결과 재현 가능.

---

## 7. Verification (사용자가 직접 돌릴 절차)

```powershell
# 1. 산출물 존재 확인
ls "C:/Users/Pulmuone/OneDrive - 풀무원/HR-indexData/output/"

# 2. 2024년 HCROI 6사 값 → 기존 xlsx 값과 일치하는지 비교
python -c "import pandas as pd; df = pd.read_csv('output/HCROI_사업단위_260512_OFS.csv'); print(df[df['항목']=='HCROI'])"

# 3. 매출액대비인건비 신설 컬럼 모두 채워졌는지
python -c "import pandas as pd; df = pd.read_csv('output/HCROI_사업단위_260512_OFS.csv'); print(df[df['항목']=='매출액대비인건비'].isna().sum())"

# 4. 동종업계평균 산출 검증 (2024 HCROI 평균 ≈ 1.699)
```

검증 실패시: `output/.cache/` 의 `financials_*.json` · `dart_raw/*/` 원본을 사용자에게 보고 후 산식·파싱 로직 디버그.

---

## 8. 미해결 위험 · 사용자 결정 보류 항목

1. **종업원급여 자동 파싱 신뢰도**: DART 사업보고서 주석은 회사마다 표 양식·계정명이 달라 100% 자동 파싱 보장 불가.
   - 1차 실패시: 사람이 사업보고서 PDF 보고 수치 직접 입력하는 fallback CSV 행 비워두기.
2. **2025년 사업보고서**: 회계연도 종료 후 90일 이내 제출이므로 2024 회계연도 보고서는 2025-03 ~ 04 제출. 2026-05 시점에는 2024 까지만 안정 수집 가능. 2025 회계연도는 데이터 없음.
3. **(주)풀무원·풀무원식품 corp_code 사전 확인**: stock_code 미보유 풀무원식품은 corpCode.xml 매칭 검색 필요 — 동명사 충돌 시 사용자 확인.

---

## 9. 다음 단계

이 plan 승인 후 구현 시:
- Phase A → AskUserQuestion 2회 (재무제표 기준, 연도 범위)
- Phase B~E → Bash + Python 일괄 실행
- Phase F → 자동 cross-check + 결과 보고

구현 신호: "구현해줘" / "Phase A 시작" / "ExitPlanMode 호출해줘"
