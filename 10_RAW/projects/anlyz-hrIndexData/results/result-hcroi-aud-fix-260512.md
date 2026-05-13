# Result: HCROI Audit 재정의 + 매출액 파싱 수정

- 날짜: 2026-05-12
- 상태: 완료
- 참조 plan: plan-hcroiRe-260512-v2.0.0.md

## 요약

1. **Audit 재정의**: 기존 audit이 xlsx 2024 기준값 회귀 테스트에 불과하고 2023·2025는 skip → 원칙 준수(산식) + YoY 이상치 탐지로 전면 교체. 모든 연도 검증.
2. **파이프라인 게이트 수정**: `audit()` 반환값이 무시되고 CSV가 항상 출력되던 구조 → `ok, warns = audit()` 후 `if ok: build_csv()` 로 게이트 작동.
3. **매출액 파싱 수정**: F001 XML에서 각주번호(`22,29`)가 `매출액` 직후 삽입되어 `[^0-9()]{0,80}?` regex가 막혀 모든 OFS 법인 rev=None → `[\s\S]{0,120}?`로 교체. 오리온 2023 단위 누락(`m.start()` → `m.start(1)`) 추가 수정.
4. **Audit warn → CSV 하단 기록**: `#WARN` 행으로 CSV 하단 append.

## 수정 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `collect_hcroi.py` | `audit_ofs/cfs` 전면 재작성 (A-1 Null, A-2 YoY), 반환값 `(bool, warns)`, `build_csv` warns 파라미터 추가, `main()` 게이트 수정, 매출액 regex `[\s\S]{0,120}?` + `m.start(1)` |
| `hcroi/.claude/agents/hcroi-auditor.md` | Check 정의 전면 교체 (H-A~H-E 삭제 → A-1~A-3) |
| `hcroi/.claude/GOTCHAS.md` | G-012 업데이트: 잘못된 패턴 → 올바른 패턴 + 재발 방지 주의사항 |
| `output/HCROI_사업단위_260512_OFS.csv` | 전 법인 매출액 복원, `#WARN` 4건 하단 추가 |
| `output/HCROI_사업단위_260512_CFS.csv` | `#WARN` 3건 하단 추가 |

## 핵심 설계 결정 및 이유

**Audit = 원칙 준수 + YoY 이상치 (xlsx cross-check 아님)**
- 기존 정의 오류: audit이 "2024 기준값과 일치하는가"만 검사 → 2023·2025 완전 skip
- 새 정의: 수집 원칙(산식) + 전년도 대비 이상치(HCROI Δ>0.3, emp Δ>30%) 탐지
- Warning은 CSV 출력을 막지 않음 (PARTIAL PASS). 현재 critical check 없음.

**`[\s\S]{0,120}?` — 각주번호 건너뛰기**
- F001 XML 손익계산서: `매출액 22,29 675,923,666,343` 구조 (각주번호가 레이블과 금액 사이)
- 구 regex `[^0-9()]`은 숫자 불허 → `22`에서 중단, rev=None
- `[\s\S]`은 모든 문자 허용 → 각주번호 스킵 후 올바른 금액 매칭
- `(?!\s*원가)` 추가: `매출액원가` 오매칭 방지

**`m.start(1)` — 인라인 단위 선언 포착**
- 오리온 2023 XML: `(단위: 천원) 매출액 2,812,935,635` 구조 — 단위가 레이블 직전
- 기존 `_nearest_mult(m.start(), ...)`: 매치 시작(매출액 위치) 이전 역탐색 → 단위 누락 → ×1 적용 → 2.8B (오류)
- `m.start(1)`: 캡처된 숫자 직전 역탐색 → 레이블-숫자 사이 인라인 단위 포착 → ×1000 → 2.8T (정상)

## 빌드/타입체크 결과

해당 없음 (Python 단일 스크립트). 실행 검증으로 대체.

## 테스트 체크리스트

- [x] OFS 9사 2023·2024·2025 rev 전부 추출 (rev=None 경고 소멸)
- [x] 오리온 2023 CFS rev 2,812,935,635,000 (×1000 정상 적용)
- [x] OFS 2024 AUDIT PASS (기준값 대조)
- [x] CFS 2024 AUDIT PASS (기준값 대조)
- [x] CSV 하단 `#WARN` 행 기록 확인 (OFS 4건, CFS 3건)
- [x] `audit()` FAIL 시 CSV 미출력 게이트 구조 확인
- [ ] 오뚜기 2023 rev=68B 미수정 (XML 내 하위 매출 항목 오매칭 — HCROI 계산 무영향, 별도 이슈)
