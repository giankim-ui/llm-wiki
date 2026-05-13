# 부록: 백엔드 이후 개발 계획

> 작성일: 2026-04-14  
> 상태: **보류 (이후 개발)**  
> 연계 문서: [research-fixWebAgent.md](research-fixWebAgent.md)  
>
> **보류 이유**: 현재 `okr-matrix-app`은 로컬 서버 기반 프론트엔드 앱으로, 백엔드(API/DB/DevOps) 구성이 없습니다.  
> 이 문서는 이후 백엔드가 추가되는 시점에 활성화할 계획과 설계를 담습니다.

---

## 이 문서를 열기 전 읽어야 할 문서

이후 개발 시 아래 문서를 순서대로 읽어 맥락을 파악하세요.

| 순서 | 문서 | 경로 | 목적 |
|:----:|------|------|------|
| 1 | **research-fixWebAgent.md** | `자료/okr-fix-plan/v1.2/research-fixWebAgent.md` | 전체 에이전트/스킬 설계 원본. 현재 범위(프론트) + 이후 범위(백엔드) 구분 설명 |
| 2 | **PROJECT_CONTEXT.md** | `OKR/okr-matrix-app/.claude/PROJECT_CONTEXT.md` | 앱의 기술 스택, 디렉토리 구조, 제약 조건 — 백엔드 설계 전 반드시 확인 |
| 3 | **MODIFICATION_LOG.md** | `OKR/okr-matrix-app/.claude/MODIFICATION_LOG.md` | 프론트엔드에서 이미 변경된 사항. 백엔드 API 설계 시 기존 데이터 흐름 파악에 필요 |
| 4 | **AGENT_ORCHESTRATOR.md** | `agents/AGENT_ORCHESTRATOR.md` | 오케스트레이터 워크플로우. 백엔드 스킬 추가 시 이 파일에 `/deploy-backend` 커맨드 추가 필요 |

---

## 1. 백엔드 스킬 설계 (SKILL_BACKEND.md 초안)

아래 내용은 `_agents/skills/SKILL_BACKEND.md` 파일로 생성할 때 사용합니다.

```markdown
# Backend Skill

## Purpose
API 수정, DB 스키마 변경, 서버 사이드 로직 수정 작업을 담당합니다.

## 적용 조건
- REST API 엔드포인트 추가/수정/삭제
- DB 마이그레이션 필요 시
- 서버 사이드 비즈니스 로직 변경 시

## Input Required
- 수정 요청 사항
- 현재 API 스펙 (OpenAPI/Swagger 또는 라우터 파일)
- DB 스키마 정보
- PROJECT_CONTEXT.md

## Analysis Checklist
### 1. API 영향도 분석
- [ ] 수정 대상 엔드포인트 식별
- [ ] 해당 API를 호출하는 프론트엔드 위치 파악
- [ ] 요청/응답 스키마 변경 여부 확인

### 2. DB 영향도 분석
- [ ] 스키마 변경 범위
- [ ] 기존 데이터 마이그레이션 필요 여부
- [ ] 롤백 스크립트 준비

### 3. 하위 호환성 검토
- [ ] Breaking change 여부
- [ ] 버전 관리 전략 (v1/v2 분리 등)
- [ ] 프론트엔드 동시 배포 필요 여부

## Output Template
backend_research_result:
  endpoint_changes:
    - path: "/api/..."
      method: "GET/POST/PUT/DELETE"
      change_type: "add/modify/remove"
      frontend_callers: []
  db_changes:
    - table: "..."
      type: "add_column/modify/drop"
      migration_required: true/false
  breaking_changes: []
  rollback_plan: "..."
```

---

## 2. 변경 유형 템플릿 (이후 개발용)

### API 변경 템플릿 (TEMPLATE_API_CHANGE.md)

```yaml
api_change:
  research_focus:
    - "엔드포인트 사용처 전수 조사"
    - "데이터 스키마 (요청/응답)"
    - "인증/권한 처리 방식"
  risk_areas:
    - "하위 호환성 (기존 프론트엔드 호출 깨짐 여부)"
    - "인증 토큰/세션 처리"
    - "에러 응답 형식 변경"
  validation:
    - "integration test"
    - "contract test (프론트-백 인터페이스 검증)"
    - "Postman/Thunder Client로 수동 검증"
  rollback:
    - "이전 엔드포인트 유지 기간 정의"
    - "DB 롤백 스크립트 준비"
```

### 의존성 업데이트 템플릿 (TEMPLATE_DEPENDENCY_UPDATE.md)

```yaml
dependency_update:
  research_focus:
    - "CHANGELOG / breaking changes 확인"
    - "peer dependencies 충돌 여부"
    - "deprecated API 사용 여부"
  risk_areas:
    - "버전 충돌 (프론트/백 공유 패키지)"
    - "런타임 동작 변경"
    - "빌드 도구 호환성"
  validation:
    - "전체 테스트 스위트 실행"
    - "빌드 정상 확인"
    - "주요 기능 수동 smoke test"
```

---

## 3. DevOps / 배포 고려사항

현재는 로컬 서버 실행(`npm run dev` 등)이 전부이나, 이후 배포 환경 구성 시 아래를 참고합니다.

| 항목 | 현재 | 이후 목표 |
|------|------|-----------|
| 실행 방식 | 로컬 서버 (수동) | Docker / PM2 등 프로세스 관리 |
| 환경 변수 | `.env.local` | 환경별 분리 (`.env.prod`) |
| 배포 파이프라인 | 없음 | CI/CD (GitHub Actions 등) |
| 헬스체크 | 없음 | `/health` 엔드포인트 + 모니터링 |

---

## 4. 워크플로우 확장 시 추가할 단계

`research-fixWebAgent.md`의 종합 워크플로우에 아래 단계를 추가해야 합니다.

```
현재 (프론트엔드):
  Plan → Split → [Validate] → Deploy

백엔드 추가 후:
  Plan → Split → [Dry-run/Preview] → Validate → Deploy (프론트)
                                              → Deploy (백엔드 + DB 마이그레이션)
                                              → Post-deploy Check (헬스체크, 스모크 테스트)
```

**추가 필요 파일**:
- `_agents/skills/SKILL_BACKEND.md` (이 문서 섹션 1 참조)
- `_agents/templates/TEMPLATE_API_CHANGE.md`
- `_agents/templates/TEMPLATE_DEPENDENCY_UPDATE.md`
- `AGENT_ORCHESTRATOR.md`에 `/deploy-backend` 커맨드 추가

---

## 5. 활성화 체크리스트

백엔드 개발을 시작할 때 아래 순서로 진행하세요.

- [ ] `PROJECT_CONTEXT.md` 업데이트 — 백엔드 기술 스택, API 스펙 추가
- [ ] `SKILL_BACKEND.md` 생성 (위 섹션 1 내용 기반)
- [ ] `TEMPLATE_API_CHANGE.md` 생성 (섹션 2 기반)
- [ ] `AGENT_ORCHESTRATOR.md` 수정 — `/deploy-backend` 커맨드, Context Loading에 API 스펙 추가
- [ ] `research-fixWebAgent.md` 업데이트 — "이후 개발" 표시 제거, 백엔드 스킬 정식 포함
- [ ] `MODIFICATION_LOG.md` 확인 — 프론트엔드 변경 이력 파악 후 API 인터페이스 설계
