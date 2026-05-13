# Result: HCROI OFS(별도재무제표) 모드 구현

- 날짜: 2026-05-12
- 상태: 완료
- 참조 plan: `plan-hcroi-ofs-260512.md`

## 요약

HCROI 파이프라인에 OFS(별도재무제표) 모드를 추가 구현했다. 풀무원 식품 계열 9개 entry(8개 법인 + 합산)에 대해 2024년 데이터를 수집·검증한 결과 전사 PASS. F001 법인은 fnlttSinglAcntAll API 미지원으로 ZIP XML 직접 파싱으로 처리했으며, 법인별 emp 레이블 상이(종업원급여/인건비/급여), 영업손실 괄호 음수 처리, 올가홀푸드 오매칭 방지(trim_to_subtotal) 등 특이사항을 파악·반영했다.

## 수정 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `hcroi/CLAUDE.md` | OFS 9개 entry 법인표 추가, fs_div 규칙 CFS고정→Q1선택으로 변경 |
| `hcroi/.claude/GOTCHAS.md` | G-009 신규 추가(OFS 법인별 특이사항 5항목), 전체 중복·과다 설명 정비 → G-001~G-009 109줄로 재작성 |
| `hcroi/.claude/agents/hcroi-collector.md` | OFS 수집 절차, parse_amount_paren / trim_to_subtotal / parse_financial_from_xml / aggregate_sum 함수 추가, extract_emp_robust v3 (prefer 파라미터), A001→F001 fallback 문서화 |
| `hcroi/.claude/agents/hcroi-auditor.md` | OFS 2024 기준값 9개 entry 추가, H-A 소스 정책 표(api/xml/api+xml/estimated) 추가 |
| `output/HANDOFF.md` | OFS 2025 수집용 handoff 문서 전면 재작성 |
| `output/HCROI_사업단위_260512_OFS.csv` | 풀무원식품·푸드머스·합산 2024 행 저장 (나머지 6개 법인 행 미추가) |

## 핵심 설계 결정 및 이유

**F001 법인 전량 ZIP XML 직접 파싱**  
fnlttSinglAcntAll API가 F001 법인에 대해 status=013 반환 → `parse_financial_from_xml()` 함수로 대체. 9자리+ 숫자 패턴으로 주석번호 자동 스킵, `parse_amount_paren()`으로 괄호 음수 처리.

**emp 레이블 우선순위: 종업원급여 → 인건비 → 급여(독립 단어)**  
풀무원푸드앤컬처='급여', 올가홀푸드='인건비' 케이스 발견. `(?<!\S)키워드(?!\S)` 독립 단어 매칭으로 오추출 방지.

**trim_to_subtotal() — 합계 이전 절단**  
올가홀푸드 '비용의 성격별' 섹션 내에 '기타장기종업원급여부채 2,108'이 있어 오매칭 발생 → '합 계' 이전까지만 슬라이스 후 파싱.

**풀무원녹즙 = corp_code 00694076 (풀무원헬스케어)**  
CORPCODE.xml 내 00444569 공시 없음(사명변경). 헬스케어 법인 감사보고서 내부 법인명이 '풀무원녹즙'으로 표기됨.

**풀무원샘물 별도 rcept_no**  
F001 list 응답에서 연결(末尾 1225)이 먼저 반환됨. `_00760.xml` 포함 여부로 별도 판별, 없으면 인접 rcept_no 시도.

**합산 entry HCROI 산식**  
`(풀무원식품 op + 푸드머스 op + 합산 emp) / 합산 emp` — HCROI 산술합 금지.

**OFS/CFS 섹션 판별: 역방향 3000자 탐색 (G-006 연장 적용)**  
'비용의 성격별' 위치 이전 3000자에서 CFS/OFS 키워드 탐색. `prefer='OFS'` 시 별도재무제표·당사는·회사는 키워드 우선.

## 빌드/타입체크 결과

해당 없음 (Python 스크립트, 타입체크 미적용)  
검증: `test_ofs_batch3.py` 실행 결과 전사 PASS (±0.0001 이내)

## 테스트 체크리스트

- [x] 풀무원식품 2024 OFS HCROI = 0.9819968879 ✅
- [x] 푸드머스 2024 OFS HCROI = 3.1220922927 ✅
- [x] 풀무원식품+푸드머스 합산 HCROI = 1.5433855294 (검증값 없음)
- [x] 풀무원샘물 2024 OFS HCROI = 1.4485453340 ✅
- [x] 풀무원다논 2024 OFS HCROI = 1.2220009958 ✅
- [x] 풀무원건강생활 2024 OFS HCROI = 0.4286866906 ✅
- [x] 풀무원녹즙 2024 OFS HCROI = 0.9320554401 ✅
- [x] 풀무원푸드앤컬처 2024 OFS HCROI = 1.1958323111 ✅
- [x] 올가홀푸드 2024 OFS HCROI = 1.2324861963 ✅
- [ ] 매출액 파싱 (F001 법인 전체 None — 미해결)
- [ ] OFS CSV 전체 9개 법인 행 완성
- [ ] OFS 2025 수집
- [ ] BOTH 모드 CSV 구현
