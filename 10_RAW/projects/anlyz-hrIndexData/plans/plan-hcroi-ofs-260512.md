# Plan — HCROI 파이프라인 OFS 모드 전 구현

작성일: 2026-05-12
작업 디렉토리: `C:/Users/Pulmuone/OneDrive - 풀무원/HR-indexData/`

---

## Context

HANDOFF.md 우선순위 1번 (OFS 지원) 전 구현. **풀무원 식품 계열 8개 법인 + 1개 합산 entry = 9개 entry** 산출.
동종사 비교는 본 구현 범위 밖 (CFS와 달리 동종업계평균 컬럼 없음).

**왜**: 기존 CFS(연결) 산출물은 식품통합MBU 단위 HCROI를 표현 못함. 식품 계열 자회사별 인건비생산성을 별도 재무제표 기준으로 산출해야 식품통합MBU 단위 의사결정 가능. 검증 기준값은 `archive/BU_CC/`의 6개 xlsx에 2024 기준으로 이미 확보됨.

**산출물**: `output/HCROI_사업단위_260512_OFS.csv` (9개 entry 컬럼, 동종업계평균 없음)

---

## 대상 9개 Entry

| # | Entry | corp_code | xlsx 검증 기준값 (2024 HCROI) | 단위 |
|---|---|---|---|---|
| 1 | 풀무원식품㈜ | 00684732 (기확보) | 0.9819968879 | 천원 |
| 2 | 푸드머스㈜ | 신규 (corp_name 매칭) | 3.1220922927 | 천원 |
| 3 | **풀무원식품+푸드머스** | (#1+#2 합산) | — (산출) | 원 |
| 4 | 풀무원샘물㈜ | 신규 | 1.4485453340 | 원 |
| 5 | 풀무원다논㈜ | 신규 | 1.2220009958 | 원 |
| 6 | 풀무원건강생활㈜ | 신규 | 0.4286866906 | 원 |
| 7 | ㈜풀무원녹즙 | 신규 | 0.9320554401 | 원 |
| 8 | ㈜풀무원푸드앤컬처 | 신규 | 1.1958323111 | 원 |
| 9 | 올가홀푸드㈜ | 신규 | 1.2324861963 | 원 |

**합산 규칙** (#3):
```
sum_op   = op_food + op_foodmerce
sum_emp  = emp_food + emp_foodmerce
HCROI_합 = (sum_op + sum_emp) / sum_emp   # HCROI 산술합 금지
```

---

## 구현 단계

### Step 1. corp_code 신규 확보 (CORPCODE.xml corp_name 매칭)

캐시: `output/.cache/_probe/corpCode/CORPCODE.xml` (재다운로드 불필요)

```python
# 비상장사 매칭: stock_code 없음 → corp_name exact/contains 매칭
targets = {
    '푸드머스': None, '풀무원샘물': None, '풀무원다논': None,
    '풀무원건강생활': None, '풀무원녹즙': None, '풀무원푸드앤컬처': None,
    '올가홀푸드': None,
}
for item in root.findall('list'):
    name = (item.findtext('corp_name') or '').strip()
    for key in targets:
        if key in name and targets[key] is None:
            targets[key] = item.findtext('corp_code')
```

**주의**: 동명 유사 법인 다수 가능성 (예: "풀무원샘물" vs "풀무원샘물판매") → 정확 매칭 안되면 사용자 확인.

### Step 2. rcept_no 확보 — A001 → A002 fallback

`hcroi/.claude/agents/hcroi-collector.md` Step H-2 확장:

```bash
# 1차: 사업보고서 (A001)
curl ".../list.json?...&pblntf_ty=A&pblntf_detail_ty=A001"
# 결과 없으면 2차: 감사보고서 (F: 외부감사보고서)
curl ".../list.json?...&pblntf_ty=F&pblntf_detail_ty=F001"
# 둘 다 없으면 null + warning (auditor PARTIAL PASS)
```

**근거**: 비상장 자회사(샘물·다논·건강생활·녹즙·푸드앤컬처·올가홀푸드)는 A001 미제출 가능, 외부감사 대상이면 F001 제출.

### Step 3. extract_emp_robust OFS 모드 추가

`hcroi/.claude/agents/hcroi-collector.md` L110-148 함수 시그니처 확장:

```python
def extract_emp_robust(xml_dir: str, prefer: str = 'CFS'):
    """
    prefer='CFS': '연결' 키워드 우선 (현행)
    prefer='OFS': '별도'/'당사' 키워드 우선, '연결' 키워드 있는 섹션 제외
    """
    CFS_KW = ['연결재무제표', '연결 재무제표', '연결실체', '연결회사']
    OFS_KW = ['별도재무제표', '별도 재무제표', '당사는', '회사는']
    # ... 기존 로직 ...
    # 섹션 라벨 판별: pos 직전 3000자에서 키워드 탐색
    pre = clean[max(0,pos-3000):pos]
    is_cfs = any(k in pre for k in CFS_KW)
    is_ofs = any(k in pre for k in OFS_KW) and not is_cfs
    
    if prefer == 'OFS' and is_ofs and ofs_result is None:
        ofs_result = (emp_val, welfare_val)
    elif prefer == 'CFS' and is_cfs and cfs_result is None:
        cfs_result = (emp_val, welfare_val)
    # ...
    target = ofs_result if prefer == 'OFS' else cfs_result
    return target if target is not None else fallback_result
```

**왜 역방향 탐색**: G-006 — '연결'/'별도' 라벨은 상위 섹션 헤딩에 위치, "비용의 성격별" 이후 500자엔 표 데이터만 있음.

### Step 4. fnlttSinglAcntAll OFS 호출 + 캐시

```bash
# fs_div=OFS 로 변경
curl ".../fnlttSinglAcntAll.json?...&fs_div=OFS"
# 캐시 명명: {corp}_ofs_{year}.json
```

**주의**: 비상장 자회사는 fnlttSinglAcntAll API 응답 없을 수 있음 (사업보고서 미제출 시).
이 경우 → ZIP XML 직접 파싱으로 매출액·영업이익 추출 fallback 필요. PoC 후 결정.

### Step 5. 합산 entry 계산 (Aggregator)

`hcroi/.claude/agents/hcroi-collector.md` H-6 후처리 단계 추가:

```python
def aggregate_sum(rows, members, label):
    """members 리스트의 op_income·emp_total 합 → 새 행 생성"""
    op_sum  = sum(r['op_income'] for r in rows if r['corp'] in members and r['op_income'])
    emp_sum = sum(r['emp_total'] for r in rows if r['corp'] in members and r['emp_total'])
    rev_sum = sum(r['revenue']   for r in rows if r['corp'] in members and r['revenue'])
    return {
        'corp': label, 'fs_div': 'OFS+sum',
        'op_income': op_sum, 'emp_total': emp_sum, 'revenue': rev_sum,
        'hcroi': (op_sum + emp_sum) / emp_sum if emp_sum else None,
        'wage_ratio': emp_sum / rev_sum if rev_sum else None,
    }

# 사용
rows.append(aggregate_sum(rows, ['풀무원식품㈜', '푸드머스㈜'], '풀무원식품+푸드머스'))
```

### Step 6. hcroi-auditor OFS 검증값 추가

`hcroi/.claude/agents/hcroi-auditor.md` (xlsx 기준값 8개 + 합산 1개) 추가.
허용 오차 HCROI ±0.0001.

### Step 7. CSV 출력

`output/HCROI_사업단위_260512_OFS.csv` UTF-8 BOM.

```csv
연도,항목,풀무원식품㈜,푸드머스㈜,풀무원식품+푸드머스,풀무원샘물,풀무원다논,풀무원건강생활,풀무원녹즙,풀무원푸드앤컬처,올가홀푸드
2024,HCROI,0.981997,3.122092,...
2024,매출액대비인건비,...
2024,영업이익(원),...
2024,종업원급여(원),...
2024,매출액(원),...
2025,...
```

미수집 셀 = 공란. 추정·역산 금지.

---

## 검증 기준값 (2024 OFS — 원 단위 환산)

| 법인 | 영업이익 | 종업원급여 | HCROI |
|---|---|---|---|
| 풀무원식품㈜ | -1,012,915,000 | 56,263,328,000 | 0.9819968879 |
| 푸드머스㈜ | 42,457,248,000 | 20,007,258,000 | 3.1220922927 |
| **합산** | 41,444,333,000 | 76,270,586,000 | **1.5433857** |
| 풀무원샘물㈜ | 5,397,435,265 | 12,033,199,000 | 1.4485453340 |
| 풀무원다논㈜ | 2,500,270,902 | 11,262,431,020 | 1.2220009958 |
| 풀무원건강생활㈜ | -5,565,274,353 | 9,741,195,000 | 0.4286866906 |
| ㈜풀무원녹즙 | -879,832,927 | 12,949,277,000 | 0.9320554401 |
| ㈜풀무원푸드앤컬처 | 24,081,475,403 | 122,969,877,977 | 1.1958323111 |
| 올가홀푸드㈜ | 2,695,729,455 | 11,595,223,706 | 1.2324861963 |

**식품통합MBU xlsx 단위 주의**: 풀무원식품·푸드머스 행 값은 **천원** 단위로 기록 → ×1000 환산 필요.

---

## 핵심 파일 (수정 대상)

| 파일 | 변경 내용 |
|---|---|
| `hcroi/CLAUDE.md` | Phase A Q1 OFS 활성화, 대상 9 entry 추가, 산출물 OFS 항목 추가 |
| `hcroi/.claude/agents/hcroi-collector.md` | `extract_emp_robust(prefer=)` 시그니처 확장, A001→F001 fallback, fs_div=OFS, 9 entry corp_code 표, `aggregate_sum` 추가 |
| `hcroi/.claude/agents/hcroi-auditor.md` | OFS 검증 기준값 8개 + 합산 1개 추가 |
| `hcroi/.claude/GOTCHAS.md` | G-009 신규: OFS 모드 키워드·fallback·천원 단위 환산 주의 |

---

## 캐시 (재사용 + 신규)

- 기확보 (CFS 시점에 수집된 ZIP/XML 재사용 가능 — 동일 rcept_no면 OFS 섹션도 같은 ZIP에 포함):
  - `pulmuwon_food_2024_xml/`, `pulmuwon_food_2025_xml/`
- 신규 (7사 × 2년):
  - `{corp}_ofs_{year}.json` (fnlttSinglAcntAll)
  - `{corp}{year}.zip`, `{corp}{year}_xml/` (document.xml)
- 신규 corp 명명 컨벤션:
  - foodmerce, samul, danon, healthcare, nokjeup, foodnculture, orga

---

## 검증 (Verification)

### Step-by-step end-to-end test

1. **corp_code Step 1 단독 실행** → 7개 신규 corp_code 모두 정상 추출 확인 (동명 모호성 체크)
2. **풀무원식품·푸드머스 2024 PoC** → OFS API + ZIP 파싱 → xlsx 검증값 ±0.0001 일치 확인
3. **합산 entry** → (sum_op + sum_emp)/sum_emp ≈ 1.5433857 검증
4. **나머지 6사 2024** → 각 xlsx 기준값과 cross-check (G-002 패턴 cross-check)
5. **2025 전체** → 검증값 없음, PARTIAL PASS 허용. 출력 → 수기 sanity check
6. **CSV 출력** → utf-8-sig BOM, 9 entry 컬럼 헤더, 공란 정책 준수

### 회사별 emp 패턴 미확정 → cross-check 필수

| 회사 | 예상 패턴 | 비고 |
|---|---|---|
| 풀무원식품 | emp 단독 (CFS와 동일 가정) | HANDOFF.md 'emp 단독' |
| 푸드머스 | 미확정 | xlsx emp=20B원 cross-check |
| 풀무원샘물 | 미확정 | xlsx emp=12B원 |
| 풀무원다논 | 미확정 | xlsx emp=11.3B원 |
| 풀무원건강생활 | 미확정 | xlsx emp=9.7B원 |
| 풀무원녹즙 | 미확정 | xlsx emp=12.9B원 |
| 풀무원푸드앤컬처 | 미확정 | xlsx emp=123B원 |
| 올가홀푸드 | 미확정 | xlsx emp=11.6B원 |

→ `select_emp_total()` 으로 emp 단독 vs emp+welfare 자동 판별 (HCROI ±0.0001 일치하는 쪽 선택).

### FAIL 처리 정책

- **사업보고서·감사보고서 모두 없음**: null + warning, PARTIAL PASS 진행
- **emp 패턴 cross-check 실패**: null + critical, FAIL → 사용자 보고 후 중단
- **2024 검증값과 ±0.0001 초과 차이**: FAIL → 중단

---

## 위험 요소·미해결

1. **비상장사 fnlttSinglAcntAll API 가용성**: 풀무원샘물·다논·건강생활·녹즙·푸드앤컬처·올가홀푸드 일부는 API에서 매출액·영업이익 응답 없을 수 있음. ZIP XML 직접 파싱 fallback이 필요할 수 있음 → PoC 1사로 먼저 검증.
2. **CORPCODE.xml corp_name 모호성**: "풀무원샘물" 매칭 시 "풀무원샘물판매" 같은 별도 법인 매칭될 위험 → 1차 결과 사용자 확인 필요.
3. **OFS 키워드 fallback 취약성** (G-006 확장): '별도'/'당사' 키워드가 표 직전에 없을 수 있음 → fallback 동작 시 raw value 로그 출력.

---

## 산출물 체크리스트 (구현 완료 정의)

- [ ] 7개 신규 corp_code CORPCODE.xml 매칭 성공
- [ ] 8개 법인 2024 OFS HCROI xlsx 기준값과 ±0.0001 일치
- [ ] 합산 entry 1.5433857 산출 정합 확인
- [ ] 9 entry × 2개년 × 5항목 CSV 출력 (utf-8-sig BOM)
- [ ] hcroi-collector.md / hcroi-auditor.md / GOTCHAS.md (G-009) 업데이트
- [ ] HANDOFF.md 갱신 — OFS 완료 표시, 잔여 항목(BOTH 모드 등) 인계
