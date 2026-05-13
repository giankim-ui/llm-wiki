# HR 데이터 파이프라인 에이전트 플레이북

> 이 문서는 Claude 에이전트가 풀무원 HR 엑셀 → DuckDB 파이프라인을 신규 구축할 때 앞에 붙이는 시스템 프롬프트/플레이북이다.  
> 인원현황(HC) 구축 과정에서 1시간 이상 소요된 병목을 분석하고, 이후 **인건비 · 지원조직 · 퇴사율** 파이프라인에서 같은 실수를 반복하지 않기 위해 작성.

---

## 1. 왜 1시간 걸렸나 — 병목 분석

| # | 병목 | 소요 | 근본 원인 | 재발 방지 |
|---|---|---|---|---|
| 1 | `data_start_row` 오진단 | ~15 min | related_sheet processed=1이 나왔는데 원인 추적에 `_explore` 스크립트를 3번 새로 작성 | **Pre-flight 스크립트 1개로 모든 시트 구조를 먼저 출력** (아래 §3) |
| 2 | `actual_column` 오판 (I vs M) | ~10 min | I=파견만, M=도급+파견 합계임을 header 읽기 전에 가정했다 | 컬럼 매핑 전 반드시 header row를 읽고 한국어 레이블과 컬럼을 1:1 대응 확인 |
| 3 | `emp_type_columns` 불완전 | ~15 min | auto_detect가 P='합계' 컬럼에서 멈춰 T·W 누락; 2024/2023은 역방향 검증 없이 스킵 | 명시적 6컬럼 매핑 사용, auto_detect 금지; 3개년 모두 동일 검증 로직 적용 |
| 4 | `bu_name_to_id` PK 충돌 | ~15 min | 같은 부서명('대표', '생산담당')이 여러 BU 그룹에 존재 → OR IGNORE로 258명 손실 | lv2_id = `parent_id::dept_slug` 형태로 scope 포함 |
| 5 | 검증 앵커 불일치 | ~5 min | 요약 시트 SUM 수식 범위가 개별 행 합산과 ±8 차이 | tolerance=±15 적용, 엄격 동등 비교 금지 |

**총평**: 전체 시간의 75%가 "진단 → 가설 → 스크립트 작성 → 재실행" 반복 사이클에 소비됨.  
Pre-flight 단계에서 시트 구조를 한 번에 파악했다면 30분 이내 완료 가능했다.

---

## 2. 파이프라인 구축 순서 (필수 준수)

```
Step 0  파일 탐색        — 대상 엑셀 파일 목록, 시트명 확인
Step 1  Pre-flight       — 구조 스캔 스크립트 실행 (§3)
Step 2  Schema 초안      — 스캔 결과 기반으로 schema.yaml 작성
Step 3  LIMIT=1 검증     — 1행만 처리해 컬럼 매핑 확인
Step 4  LIMIT=5 검증     — 소계 skip 로직, BU 이름 확인
Step 5  전체 실행        — 3개년 모두, 검증 앵커 확인
Step 6  mypy --strict    — 타입 체크 통과 필수
Step 7  임시 스크립트 삭제 — _explore*.py, _verify*.py 모두 제거
```

---

## 3. Pre-flight 진단 스크립트 (재사용 템플릿)

새 파이프라인 시작 시 **가장 먼저** 아래 스크립트를 실행해 구조를 파악한다.  
출력 결과를 schema.yaml 작성의 입력으로 사용한다.

```python
# pipeline/_preflight.py  — 새 파이프라인 구축 시 복사해서 사용
"""Pre-flight: 엑셀 시트 구조 스캔 (헤더·데이터 첫 5행·마지막 5행)."""
import openpyxl, unicodedata, sys

fp = sys.argv[1]  # 파일 경로
wb = openpyxl.load_workbook(fp, data_only=True, read_only=True)
print(f"시트 목록: {wb.sheetnames}\n")

for sn in wb.sheetnames:
    ws = wb[sn]
    print(f"{'='*60}\n[{sn}]")
    
    # 헤더 영역 (1-7행)
    print("  -- 헤더 rows 1-7 --")
    for rnum in range(1, 8):
        rows = list(ws.iter_rows(min_row=rnum, max_row=rnum, max_col=30, values_only=True))
        if not rows: break
        non_none = [(i, v) for i, v in enumerate(rows[0]) if v is not None]
        if non_none:
            col_str = "  ".join(f"{chr(65+i) if i<26 else 'A'+chr(65+i-26)}={repr(str(v))[:15]}"
                                for i, v in non_none[:15])
            print(f"    row{rnum}: {col_str}")
    
    # 데이터 첫 5행
    print("  -- 데이터 rows 7-12 --")
    for rnum in range(7, 13):
        rows = list(ws.iter_rows(min_row=rnum, max_row=rnum, max_col=30, values_only=True))
        if not rows: break
        non_none = [(i, v) for i, v in enumerate(rows[0]) if v is not None]
        if non_none:
            col_str = "  ".join(f"{chr(65+i) if i<26 else 'A'+chr(65+i-26)}={repr(str(v))[:12]}"
                                for i, v in non_none[:15])
            print(f"    row{rnum}: {col_str}")
    
    # 데이터 마지막 영역 (max_row-10 ~ max_row)
    # read_only에서는 ws.max_row 신뢰도 낮으므로 행 수 직접 탐색
    print("  -- 데이터 마지막 20행 (빈 행 제외) --")
    last_rows = []
    for rnum in range(200, 7, -1):
        rows = list(ws.iter_rows(min_row=rnum, max_row=rnum, max_col=30, values_only=True))
        if not rows: continue
        non_none = [(i, v) for i, v in enumerate(rows[0]) if v is not None]
        if non_none:
            last_rows.append((rnum, non_none))
            if len(last_rows) >= 20: break
    for rnum, non_none in reversed(last_rows):
        col_str = "  ".join(f"{chr(65+i) if i<26 else 'A'+chr(65+i-26)}={repr(str(v))[:12]}"
                            for i, v in non_none[:15])
        print(f"    row{rnum}: {col_str}")

wb.close()
```

**실행**: `python pipeline/_preflight.py "<엑셀파일경로>"`  
**확인 항목**: 헤더 행 수, data_start_row, data_end_row, 컬럼 레이블-번호 매핑

---

## 4. 풀무원 HR 엑셀 공통 패턴

### 4-1. 요약 시트 (인원현황 primary_sheet)

| 구조 요소 | 패턴 | 주의사항 |
|---|---|---|
| 헤더 | 3-4단 병합 헤더 (rows 4-6) | `data_start_row`는 실제 데이터 첫 행 (보통 7) |
| B컬럼 | BU/SBU 그룹명, 셀 병합으로 첫 행만 값 존재 | read_only 모드에서 forward-fill 필수 |
| C컬럼 | 부서명 (소계 행은 suffix '계') | `subtotal_marker.suffix: 계` 로 skip |
| P컬럼 | 소계 컬럼 ('합계' 레이블) | auto_detect가 여기서 멈춤 → **명시적 매핑 필수** |
| AA컬럼 | 행별 총합 | 검증 anchor 용도 (SUM 수식 범위 ±8 차이 있을 수 있음) |
| 소계 행 | C끝='계' (식품통합 MBU계, NA MBU계 등) | 그랜드 총계 행은 B에만 값, C=None |
| 기타 인원 현황 | data_end_row 이후 별도 섹션 | L~W 컬럼 값=0, 무시해도 무방 |

**2025년 기준 emp_type 컬럼 매핑 (고정값, 연도별 동일)**:
```yaml
emp_type_columns:
  L: EXEC    # 경영간부직
  M: MGMT    # 운영관리/연구전문
  N: OPER    # 운영실무직
  O: FIELD   # 현장직(사무)
  T: FIELD   # 현장직 정규직  ← P='합계' 뒤에 있어 auto_detect 놓침
  W: CONT    # 계약직
```

### 4-2. 관계인력(PPT) 시트 (related_sheet)

| 구조 요소 | 패턴 | 주의사항 |
|---|---|---|
| `data_start_row` | **7** (헤더 4-6행) | 이전 버전은 16으로 잘못 설정 → processed=1 |
| BU 컬럼 | G컬럼 | 구분/합계 행은 '합계', '소계', '총계' 포함 → skip |
| 실제인원 컬럼 | **M컬럼** (도급+파견 합계) | I컬럼=파견만, M컬럼=합계 → **M 사용** |
| BU명 특수 케이스 | 'NA MBU3)', '중국 MBU4)' 등 주석 번호 | `re.sub(r"\s*\d+\)\s*$", "", bu_name)` 으로 제거 |

### 4-3. BU ID 생성 규칙

```python
# ❌ 잘못된 방식: 같은 부서명이 여러 BU에 있으면 PK 충돌
lv2_id = bu_name_to_id(lv2_canonical)

# ✅ 올바른 방식: parent scope 포함
lv1_id = bu_name_to_id(lv1_canonical)          # lv1은 parent 없음
lv2_id = bu_name_to_id(lv2_canonical, lv1_id)  # lv2는 lv1 하위로 scope
```

**주요 충돌 사례** (반드시 scope 포함해야 하는 이유):

| 부서명 | 등장 BU 수 | 손실 인원 |
|---|---|---|
| 대표 | 7개 그룹 | 6명 (1인×6) |
| 영업담당 | 3개 그룹 | 54명 |
| 생산담당 | 2개 그룹 | 95명 |
| 경영지원본부 | 2개 그룹 | 65명 |
| (합계) | — | **258명** |

---

## 5. 검증 앵커 설정 지침

```python
# validate_year 내 앵커 설정 방법
ANCHORS: dict[int, int] = {
    2025: 8197,   # 요약 시트 row150 AA 값 (전사 총 계 해외법인 포함)
    # 2024, 2023: 요약 시트 grand total AA가 None → 앵커 미설정
}
TOLERANCE = 15  # 수식 범위 차이로 ±8 발생 가능, 15로 여유 설정

# ❌ 엄격 동등 비교 금지
ok = db_sum == anchor

# ✅ tolerance 비교 사용
ok = abs(db_sum - anchor) <= TOLERANCE
```

**앵커 값 찾는 법**:
1. 요약 시트에서 B컬럼='전사 총 계 (해외법인 포함)' 인 행 탐색
2. 해당 행의 AA컬럼 값 사용
3. openpyxl data_only 모드에서 None이면 → 수동 확인 또는 앵커 설정 생략

---

## 6. schema.yaml 체크리스트

새 파이프라인의 schema.yaml 작성 후 아래 항목을 순서대로 확인한다.

### primary_sheet 검증
- [ ] `data_start_row`: Pre-flight 출력에서 첫 데이터 행 번호 확인 (보통 7)
- [ ] `data_end_row`: 마지막 데이터 행 확인 (섹션 구분자 행 이전)
- [ ] `bu_columns.level1` (B), `bu_columns.level2` (C): 실제 컬럼 레이블 확인
- [ ] `subtotal_marker.suffix`: 한국어 소계 행 suffix ('계')
- [ ] `emp_type_columns`: **명시적 매핑 필수**, auto_detect 금지
  - 각 컬럼의 한국어 헤더와 emp_type_code 1:1 대응 표 작성 후 입력
- [ ] `headcount_column`, `headcount_actual_column`: 재직·현재 컬럼 확인

### related_sheet 검증
- [ ] `data_start_row`: **7** (헤더 4-6행 구조 기준)
- [ ] `bu_column`: BU명이 있는 컬럼 (보통 G)
- [ ] `actual_column`: 합계 컬럼 (**M**, 파견만인 I 금지)
- [ ] BU명 주석 번호 제거 로직 확인 (`\s*\d+\)\s*$`)

### 3개년 교차 검증
- [ ] 2025 → 2024 → 2023 순서로 컬럼 구조 동일 여부 확인
- [ ] 연도별 processed 건수가 유사한지 확인 (크게 다르면 data_start_row 문제)
- [ ] related_sheet processed=10 (MBU/SBU 10개) 확인

---

## 7. 이후 파이프라인 적용 가이드

### 인건비 (Labor Cost) 파이프라인

**예상 시트 구조**: 월별/분기별 MBU×직군 교차표
- Pre-flight에서 확인할 것: 금액 컬럼 위치, 통화 단위(천원/만원), 소계 행 패턴
- 주의: 금액 셀에 `#N/A`, `#VALUE!` 오류값 존재 시 `_to_int()` None 처리 확인
- PK 설계: `(year, quarter, month, bu_id, cost_type_code)`
- BU ID: 동일한 lv1::lv2 scope 전략 사용

**추가 확인 항목**:
```python
# 인건비는 누적/월별 혼재 가능
# Pre-flight에서 반드시 확인
if '누적' in sheet_name or '누계' in sheet_name:
    # 월별 → 누적 변환 로직 필요
```

### 지원조직 (Supporting Org) 파이프라인

**예상 시트 구조**: 지원 부서별 인원/비용 배분 테이블
- Pre-flight에서 확인: 배분 기준 컬럼 (직접/간접, 배분율)
- 주의: 퍼센트 셀이 0.0~1.0 범위인지 0~100 범위인지 확인
- 소계 행: suffix '계' 외에 '합' 포함 행도 skip 필요할 수 있음
- BU명: 지원조직은 lv1 없이 단독 부서명인 경우 많음 → lv1_id=None

### 퇴사율 (Attrition) 파이프라인

**예상 시트 구조**: 월별 입사/퇴사 인원, 누적 퇴사율
- Pre-flight에서 확인: 입사/퇴사 컬럼 위치, 자발적/비자발적 구분
- 주의: 퇴사율은 분모(기초인원)와 분자(퇴사인원)를 함께 저장
- PK 설계: `(year, quarter, month, bu_id, separation_type_code)`
- 비율 컬럼은 DB에 `DOUBLE` 타입, 원본 인원수는 `INTEGER`

```yaml
# 퇴사율 schema.yaml 예시
primary_sheet:
  sheet_name: 퇴사현황
  data_start_row: 7
  emp_type_columns:        # 퇴사 유형 컬럼
    C: VOLUNTARY            # 자발적 퇴사
    D: INVOLUNTARY          # 비자발적
    E: RETIREMENT           # 정년퇴직
  subtotal_marker:
    column: B
    suffix: 계
```

---

## 8. 공통 함정 목록 (Known Pitfalls)

| 함정 | 증상 | 진단 | 해결 |
|---|---|---|---|
| data_start_row 오설정 | processed=1 또는 너무 적음 | Pre-flight 행 번호 확인 | 실제 데이터 시작 행으로 수정 |
| auto_detect 컬럼 누락 | DB sum이 기대값보다 현저히 낮음 | header 행에서 '합계' 컬럼 위치 확인 | 명시적 emp_type_columns 사용 |
| BU 이름 scope 미설정 | OR IGNORE로 인원 손실 | 동명 부서명 목록 확인 | lv2_id에 parent_id 포함 |
| 수식 셀 None 반환 | 일부 컬럼 합계 불일치 | data_only=True 모드 한계 | tolerance 검증으로 처리 |
| 주석 번호 BU명 | 'NA MBU3)' 등 미매칭 | dim_bu 테이블 확인 | `re.sub(r"\s*\d+\)\s*$", "")` |
| ConstraintException re-run | 두 번째 실행 시 에러 | seed INSERT 중복 | `except (CatalogException, ConstraintException): pass` |
| 한글 NFC/NFD 불일치 | 시트명 or 셀값 매칭 실패 | `unicodedata.normalize("NFC", s)` | 모든 문자열 NFC 정규화 |
| read_only 병합 셀 | B컬럼 첫 행만 값, 나머지 None | forward-fill 로직 확인 | `if lv1_val: current_lv1 = lv1_val` |

---

## 9. 에이전트 사용 시 시스템 프롬프트

다음 텍스트를 새 파이프라인 세션 시작 시 컨텍스트로 전달한다:

```
당신은 풀무원 HR 데이터 DuckDB 파이프라인을 구축하는 에이전트입니다.
반드시 아래 순서를 따르세요:

1. [Pre-flight] pipeline/_preflight.py를 실행해 시트 구조를 먼저 파악
2. [Schema 초안] 파악된 구조로 schema.yaml 작성
3. [LIMIT=1] 1행 처리로 컬럼 매핑 확인
4. [LIMIT=5] 5행 처리로 소계 skip·BU 이름 확인
5. [전체 실행] 3개년 전체, 검증 앵커 확인
6. [mypy] --strict 통과 필수

지켜야 할 규칙:
- emp_type_columns: auto_detect 절대 금지, 명시적 컬럼 매핑만 사용
- bu_name_to_id: lv2는 반드시 lv1_id를 parent로 포함
- related_sheet: data_start_row=7, actual_column=M (합계)
- 검증: tolerance=±15, 엄격 동등 비교 금지
- any 타입 금지 (mypy --strict 준수)
- 임시 스크립트(_explore*.py 등)는 완료 후 즉시 삭제

일반적인 한국어 HR 엑셀 패턴:
- 헤더: rows 4-6 (3단 병합)
- 데이터 시작: row 7
- B컬럼: 상위 BU (병합 셀, forward-fill 필요)
- C컬럼: 하위 부서 (suffix '계'는 소계 행)
- 소계/총계 skip: C.endswith('계') or C in ['합계','소계','총계']
```
