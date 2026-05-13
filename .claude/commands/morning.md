---
description: 출근 브리핑 — DAILY.md 강제 갱신 후 내용 출력
---

## 목적
`scripts/daily_brief.py`를 **강제 실행**해 DAILY.md를 최신 상태로 갱신하고 내용을 콘솔에 출력한다.
(SessionStart hook의 `--skip-if-today`와 달리 언제든 수동 갱신 가능)

## 처리 순서

### 1. 스크립트 실행

```powershell
python "C:\Users\Pulmuone\OneDrive - 풀무원\20-Obsidian\scripts\daily_brief.py"
```

`--skip-if-today` 없이 호출 → 항상 최신 상태로 덮어쓰기.

### 2. DAILY.md 내용 출력

스크립트 완료 후 DAILY.md 전체 내용을 사용자에게 마크다운으로 보여준다.

```powershell
Get-Content "C:\Users\Pulmuone\OneDrive - 풀무원\20-Obsidian\DAILY.md" -Encoding UTF8
```

### 3. 완료 보고

```
[morning] DAILY.md 갱신 완료 — {오늘 날짜} {HH:MM}
```

## 인자
$ARGUMENTS
