# AX 배치 프로세스 재개 가이드

> 작성일: 2026-04-23 | 상태: **구현 대기 (내일 재개)**

---

## 현재 상태

| 항목 | 상태 |
|------|------|
| 현행 batch_01~11.json | ✅ 완료 (275건, 2021~2025 전체) |
| 현행 bundle.html | ✅ 정상 동작 (1,037 KB, seedVersion 2026-04-23-2006) |
| merge_ax_results.py 캐시 버그 | ✅ 수정 완료 (자동 타임스탬프 버전) |
| GOTCHAS.md | ✅ 생성 완료 |
| **run_batches.py** | ❌ 미구현 (내일 할 것) |
| **prepare_batches.py 연도 필터** | ❌ 미구현 (내일 할 것) |

---

## 내일 구현할 것

### 목표
- 연도 필터: **2025+2024만** (234건 / 10배치 / 현행 대비 15% 절감)
- 세션당 **4배치**씩 실행 → /clear 주기 = 3회 (배치 1-4 → /clear → 5-8 → /clear → 9-10)
- `/clear` 해도 파일 기반으로 진행상태 자동 복원

### 구현 파일 2개

#### 1. `analysis/prepare_batches.py` 수정
`--years` 옵션 추가 (기본값: 2025 2024)

```python
# 추가할 내용 (argparse)
parser.add_argument('--years', nargs='+', type=int, default=[2025, 2024])
# 필터 적용
items = [i for i in candidates if i['year'] in args.years]
```

실행 예시:
```bash
python analysis/prepare_batches.py --years 2025 2024
# → input_batch_01~10.json 재생성 (234건 / 10배치)
```

#### 2. `analysis/run_batches.py` 신규 생성

```python
"""
잔여 배치를 탐지해 4개씩 Haiku background agent로 실행.
완료 후 merge + build 자동 수행.
잔여 있으면 /clear 재개 안내 출력.

사용법: Claude Code에서 "run_batches.py 실행해줘" 요청 (직접 python 실행 불가 — Haiku Agent 호출 필요)
"""
from pathlib import Path
import json

BATCHES_DIR = Path("analysis/output/ax_batches")
SESSION_SIZE = 4  # 세션당 배치 수

# 전체 input 목록
all_inputs = sorted(BATCHES_DIR.glob("input_batch_*.json"))
# 완료된 배치 = 대응하는 batch_XX.json 존재
def batch_num(p): return p.stem.split("_")[-1]
done = {batch_num(p) for p in BATCHES_DIR.glob("batch_*.json")}
remaining = [p for p in all_inputs if batch_num(p) not in done]

if not remaining:
    print("✅ 전체 완료. merge_ax_results.py → npm run build → inline-bundle.py 실행")
else:
    next_batch = remaining[:SESSION_SIZE]
    print(f"잔여 {len(remaining)}배치 중 {len(next_batch)}개 실행 예정:")
    for p in next_batch:
        print(f"  {p.name}")
    # → Claude Code가 이 목록을 보고 Haiku Agent 4개 병렬 실행
```

> ⚠️ `run_batches.py`는 정보 출력용. **실제 Haiku Agent 실행은 Claude Code가 담당.**  
> 사용자는 "run_batches.py 확인하고 다음 배치 실행해줘"라고 요청하면 됨.

---

## 내일 재개 순서

### Step 1 — 새 배치 준비 (기존 batch_*.json 삭제 후 재생성)
```bash
# 기존 결과 초기화 (2025+2024 필터로 새로 만들 것이므로)
del analysis\output\ax_batches\batch_*.json

# 연도 필터 적용해 input 재생성
python analysis/prepare_batches.py --years 2025 2024
# → input_batch_01~10.json 생성 (234건)
```

### Step 2 — 세션 1 (배치 1~4)
Claude Code에 요청:
> "run_batches.py 확인하고 다음 4배치 Haiku 실행해줘"

Claude가 자동으로:
1. 잔여 배치 탐지
2. 배치 1~4 Haiku background 실행
3. 완료 후 merge + build
4. "`/clear 후 '다음 배치 실행해줘' 요청`" 안내

### Step 3 — /clear 후 세션 2 (배치 5~8)
> "다음 배치 실행해줘"

### Step 4 — /clear 후 세션 3 (배치 9~10)
> "다음 배치 실행해줘"

### Step 5 — 완료 확인
```bash
# 브라우저에서 bundle.html 열기
# 전영효(183669) → AX 추천 보라색 chip + hover 상세 설명 확인
```

---

## 참고: 현재 워크플로 명령어

```bash
# 전체 merge + 버전 업 + 빌드 (데이터 변경 후 항상 이 순서)
python analysis/merge_ax_results.py
cd ax-interview-app
npm run build
python inline-bundle.py
```

---

## GOTCHAS 요약

1. **merge 후 반드시 people.json 버전 업** → `merge_ax_results.py`가 자동 처리 (수동 금지)
2. **ax_tech enum 외 값 금지** → 허용: RPA/자동화 | AI분석/인사이트 | 챗봇/RAG | 문서자동화 | 데이터시각화 | OCR/데이터추출 | 알림/스케줄링
3. **Haiku 결과는 반드시 파일로 저장** → `run_in_background=True` + 에이전트 내 Write 도구
4. **세션당 4배치** → 초과 시 컨텍스트 과부하
