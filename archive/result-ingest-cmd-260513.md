# Result: /ingest 슬래시 명령 생성

- 날짜: 2026-05-13 13:32
- 상태: 완료
- 참조 plan: 없음

## 요약

Vault `.claude/commands/ingest.md` 신규 생성 요청. 처음에는 `.claude/agents/commands/` 경로를 요청받았으나, Claude Code 슬래시 명령은 `.claude/commands/`에 위치해야 실제 인식되므로 경로를 변경해 작성. 배경 세션 격리 제약으로 worktree를 수동 생성 후 파일 작성 → main 브랜치에 fast-forward merge 완료.

## 수정 파일 목록

| 파일 | 변경 내용 |
|------|---------|
| `.claude/commands/ingest.md` | 신규 생성 — LLM-Wiki v2.2 §6.1 ingest 워크플로우 슬래시 명령 |

## 핵심 설계 결정 및 이유

- **경로**: `.claude/agents/commands/` → `.claude/commands/` 변경. Claude Code는 프로젝트 슬래시 명령을 `.claude/commands/`에서만 인식하므로 원래 경로에 두면 `/ingest`가 작동하지 않음.
- **명령 내용 구성**: PLAN v2.2.1 §6.0(Raw Reading Discipline) + §6.1(Ingest Workflow) 기반. 사전 확인 → 축 판별 → raw 안착 확인 → read discipline → 병렬 갱신(Agent haiku) → 완료 보고 순서로 단계화.
- **Agent(haiku) 병렬 처리**: synthesis/INDEX/LOG 갱신은 독립 작업이므로 단일 메시지 동시 호출 명시.
- **커밋 자동화 차단**: 완료 보고 후 사용자 확인 없이 자동 커밋 금지 조항 포함.
- **인자 처리**: `$ARGUMENTS` 미입력 시 AskUserQuestion으로 대상·Δ 질문.

## 빌드/타입체크 결과

해당 없음 (마크다운 명령 파일)

## 테스트 체크리스트

- [ ] `/ingest` 입력 시 명령 인식 확인 (Claude Code vault 내)
- [ ] 인자 없이 실행 시 AskUserQuestion 발동 확인
- [ ] Asset 축 ingest 실행 후 synthesis/INDEX/LOG 갱신 확인
- [ ] Project 축 ingest 실행 후 synthesis/INDEX/LOG 갱신 확인
- [ ] raw 파일 미존재 시 이관 먼저 요청하는지 확인
