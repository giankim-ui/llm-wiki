# Plan: 전역 커맨드 /P.S · /R.S 추가

## Context
Plan 모드 종료 시 plan 파일을 `cwd/archive`로 이동하는 작업, 그리고 구현 완료 후 result를 저장하는 작업이 매번 수동으로 이루어지고 있다. 이를 두 개의 전역 슬래시 커맨드로 자동화하여 워크플로우를 단순화한다.

---

## 대상 파일 (신규 생성 2개)

| 파일 | 역할 |
|------|------|
| `C:\Users\Pulmuone\.claude\commands\P.S.md` | `/P.S` 전역 커맨드 |
| `C:\Users\Pulmuone\.claude\commands\R.S.md` | `/R.S` 전역 커맨드 |

---

## 커맨드 1: `/P.S` (Plan.Save)

**동작:**
1. `C:\Users\Pulmuone\.claude\plans\` 폴더에서 **가장 최근 수정된 `.md` 파일** 1개를 찾는다 (PowerShell `Get-ChildItem ... | Sort LastWriteTime -Desc | Select -First 1`)
2. 파일이 없으면 `plans/ 폴더에 저장된 plan 파일이 없습니다.` 출력 후 종료
3. 이동 대상 경로: `{cwd}/archive/plan-{2-4단어-kebab-요약}.md`
   - 요약은 plan 파일 내용(첫 `# ` 제목 또는 파일명)에서 자동 추출
   - `archive/` 폴더 없으면 먼저 생성
4. `mv` (Bash) 또는 PowerShell `Move-Item` 으로 이동
5. hook이 자동으로 버전 서픽스 부여 → 최종 파일명: `archive/plan-{요약}-v1.0.md`
6. `플랜 저장 완료: {최종 경로}` 출력

**$ARGUMENTS 처리:**
- 인자가 있으면 → 요약 키워드로 사용 (파일명에 반영)
- 없으면 → plan 파일 제목에서 자동 추출

---

## 커맨드 2: `/R.S` (Result.Save)

**동작:**
1. 최근 대화 맥락에서 완료된 작업 내용을 추출
2. 아래 형식으로 result 문서 작성:
   ```
   # Result: {작업 제목}
   버전·날짜·상태·참조 plan

   ## 요약 (문제 원인 + 해결 방식)
   ## 수정 파일 목록 (파일명 + 변경 내용)
   ## 핵심 설계 결정 및 이유
   ## 빌드/타입체크 결과
   ## 테스트 체크리스트
   ```
3. 저장 경로: `{cwd}/archive/result-{2-4단어-kebab-요약}.md`
   - `archive/` 없으면 생성
4. hook이 버전 서픽스 자동 부여
5. `결과 저장 완료: {최종 경로}` 출력

**$ARGUMENTS 처리:**
- 인자가 있으면 → 요약 키워드로 사용
- 없으면 → 최근 완료 작업 제목에서 자동 추출

---

## 구현 순서

1. `C:\Users\Pulmuone\.claude\commands\P.S.md` Write
2. `C:\Users\Pulmuone\.claude\commands\R.S.md` Write

두 파일 모두 독립적 → 병렬 생성 가능

---

## 검증

- `/P.S` 호출 → `plans/` 최신 파일이 `cwd/archive/plan-*.md` 로 이동 확인
- `/R.S` 호출 → `cwd/archive/result-*.md` 생성 및 내용 확인
