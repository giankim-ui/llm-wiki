# 웹앱 수정 에이전트/스킬 시스템 구현 계획 v2

> 작성일: 2026-04-15  
> 기반 연구: [research-fixWebAgent.md](research-fixWebAgent.md)  
> 재사용 전략: `OKR/.claude/agents/web-build.md` → `AGENT_ORCHESTRATOR.md`에 구조 차용  
> 현재 개발 범위: 프론트엔드 및 로컬 서버 수정만 포함  
> **v2 업데이트**: 보완 사항 18개 항목 추가

---

## 📋 v2 보완 사항 요약

| 구분 | 보완 영역 | 상태 |
|------|----------|------|
| 1 | 롤백 메커니즘 상세화 | ✅ 추가 |
| 2 | 병렬 작업 충돌 방지 | ✅ 추가 |
| 3 | 스킬 간 의존성 그래프 | ✅ 추가 |
| 4 | 성능 벤치마크 기준 | ✅ 추가 |
| 5 | 보안 검증 체크리스트 | ✅ 추가 |
| 6 | 접근성(A11y) 검증 | ✅ 추가 |
| 7 | 상태 관리 변경 가이드 | ✅ 추가 |
| 8 | API 버전 호환성 | ✅ 추가 |
| 9 | 캐시 무효화 전략 | ✅ 추가 |
| 10 | 모니터링/알림 연동 | ✅ 추가 |
| 11 | 긴급 수정(Hotfix) 프로세스 | ✅ 추가 |
| 12 | 다국어/i18n 변경 가이드 | ✅ 추가 |
| 13 | 테스트 커버리지 기준 | ✅ 추가 |
| 14 | 문서 자동 생성 | ✅ 추가 |
| 15 | 스킬 확장 인터페이스 | ✅ 추가 |
| 16 | 컨텍스트 압축 전략 | ✅ 추가 |
| 17 | 에러 복구 시나리오 | ✅ 추가 |
| 18 | 메트릭 수집/분석 | ✅ 추가 |

---

## 1. 생성 파일 목록

| 파일명 | 경로 | 설명 |
|--------|------|------|
| AGENT_ORCHESTRATOR.md | `agents/` | 메인 오케스트레이터 |
| SKILL_RESEARCH.md | `agents/skills/` | 코드 분석 스킬 |
| SKILL_PLAN.md | `agents/skills/` | 수정 계획 스킬 |
| SKILL_FRONTEND.md | `agents/skills/` | 프론트엔드 수정 스킬 |
| SKILL_VALIDATE.md | `agents/skills/` | 검증 스킬 |
| SKILL_ROLLBACK.md | `agents/skills/` | **[v2 추가]** 롤백 스킬 |
| SKILL_SECURITY.md | `agents/skills/` | **[v2 추가]** 보안 검증 스킬 |
| TEMPLATE_UI_CHANGE.md | `agents/templates/` | UI 변경 템플릿 |
| TEMPLATE_HOTFIX.md | `agents/templates/` | **[v2 추가]** 긴급 수정 템플릿 |
| PROJECT_CONTEXT.md | `[project]/.claude/` | 프로젝트 컨텍스트 |
| MODIFICATION_LOG.md | `[project]/.claude/` | 수정 이력 |
| ROLLBACK_REGISTRY.md | `[project]/.claude/` | **[v2 추가]** 롤백 포인트 레지스트리 |

---

## 2. 실행 순서

```
Step 1 (기반)   : AGENT_ORCHESTRATOR.md
Step 2 (스킬)   : SKILL_RESEARCH → SKILL_PLAN → SKILL_FRONTEND → SKILL_VALIDATE
Step 3 (보조)   : SKILL_ROLLBACK, SKILL_SECURITY (필요 시)
Step 4 (템플릿) : TEMPLATE_UI_CHANGE.md, TEMPLATE_HOTFIX.md
Step 5 (프로젝트): PROJECT_CONTEXT.md → MODIFICATION_LOG.md → ROLLBACK_REGISTRY.md
```

> `PROJECT_CONTEXT.md`는 생성 후 실제 프로젝트 정보를 직접 채워야 합니다.

---

## 3. AGENT_ORCHESTRATOR.md

**경로**: `[project]/agents/AGENT_ORCHESTRATOR.md`

### 핵심 내용

~~~markdown
# 웹앱 수정 오케스트레이터

> 역할: 완성된 웹앱의 수정 작업을 체계적으로 관리합니다.
> 직접 코드를 작성하지 않으며, 스킬을 호출하고 컨텍스트를 유지합니다.

---

## 핵심 흐름

```
[세션 초기화] → [Research] → [Plan] → [Split] → [Validate] → [Deploy]
                    ↓           ↓         ↓          ↓
               [Rollback Point 생성 - 각 단계 완료 시]
```

모든 작업은 위 순서를 따릅니다. **각 단계 완료 후 사용자 확인 없이 다음 단계 진행 금지.**

---

## 세션 시작 시 필수 로드 (Context Preservation Layer)

세션 시작 시 반드시 아래 파일을 읽고 컨텍스트로 유지합니다:

1. `[project]/.claude/PROJECT_CONTEXT.md` — 기술 스택, 디렉토리 구조, 제약 조건
2. `[project]/.claude/MODIFICATION_LOG.md` — 이전 변경 이력
3. `[project]/.claude/ROLLBACK_REGISTRY.md` — **[v2]** 롤백 포인트 목록
4. `agents/AGENT_ORCHESTRATOR.md` — 본 문서

---

## Phase 1: Research (분석)

**호출 스킬**: `SKILL_RESEARCH.md`

### 입력
- 사용자 수정 요청
- PROJECT_CONTEXT.md

### 출력
```yaml
impact_analysis:
  affected_files: [파일 목록]
  affected_components: [컴포넌트 목록]
  dependency_chain: [의존성 체인]
  risk_level: low | medium | high | critical
  estimated_complexity: 1-10

# [v2 추가] 보안 영향 분석
security_impact:
  auth_affected: boolean
  data_flow_changed: boolean
  external_api_affected: boolean
  requires_security_review: boolean
```

### 승인 게이트
- [ ] 사용자가 영향 범위 확인
- [ ] risk_level이 high 이상이면 추가 논의 필요
- [ ] **[v2]** security_impact 확인 후 진행

---

## Phase 2: Plan (계획)

**호출 스킬**: `SKILL_PLAN.md`

### 입력
- Phase 1 결과
- 이전 수정 이력 참조

### 출력
```yaml
modification_plan:
  summary: "한 줄 요약"
  steps:
    - id: 1
      description: "작업 설명"
      files: [대상 파일]
      type: add | modify | delete | refactor
      rollback_strategy: "롤백 방법"  # [v2 추가]
      estimated_lines: 예상 라인 수

  # [v2 추가] 의존성 그래프
  dependency_graph:
    step_1: []
    step_2: [step_1]
    step_3: [step_1, step_2]

  # [v2 추가] 병렬 실행 가능 그룹
  parallel_groups:
    group_1: [step_1, step_4]  # 독립적으로 병렬 실행 가능
    group_2: [step_2, step_3]  # group_1 완료 후 실행

  total_estimated_lines: 전체 예상 라인 수
  rollback_point_id: "RP-YYYYMMDD-001"  # [v2 추가]
```

### 승인 게이트
- [ ] 사용자가 계획 승인
- [ ] 500줄 이상 변경 시 분할 검토
- [ ] **[v2]** 롤백 전략 확인

---

## Phase 3: Split (분할)

### Context Rot 방지 규칙

| 기준 | 액션 |
|------|------|
| 파일당 2000줄 초과 | 컴포넌트 분리 권장 |
| 단일 함수 100줄 초과 | 함수 분할 권장 |
| 순환 의존성 감지 | 구조 재설계 필요 |

### 분할 원칙
1. **단일 책임**: 각 split은 하나의 기능 변경만 담당
2. **테스트 가능**: 각 split은 독립적으로 테스트 가능해야 함
3. **롤백 가능**: 각 split은 독립적으로 롤백 가능해야 함

---

## Phase 4: Execute (실행)

**호출 스킬**: `SKILL_FRONTEND.md`

### 실행 프로토콜

```
for each split in plan.splits:
    1. 현재 상태 스냅샷 생성
    2. SKILL_FRONTEND 호출
    3. SKILL_VALIDATE 호출
    4. 성공 시: 다음 split 진행
    5. 실패 시: 에러 처리 프로토콜 실행
```

### [v2 추가] 병렬 실행 조건

병렬 실행은 다음 조건을 **모두** 만족할 때만 허용:
- 파일 중복 없음
- 공유 상태 변경 없음
- import 의존성 없음

---

## Phase 5: Validate (검증)

**호출 스킬**: `SKILL_VALIDATE.md`

### 검증 체크리스트

```yaml
validation:
  static_analysis:
    - [ ] TypeScript 컴파일 성공
    - [ ] ESLint 에러 없음
    - [ ] 순환 의존성 없음

  functional:
    - [ ] 기존 테스트 통과
    - [ ] 새 기능 테스트 작성
    - [ ] E2E 테스트 (해당 시)

  # [v2 추가] 성능 검증
  performance:
    - [ ] 번들 사이즈 증가 < 10%
    - [ ] LCP 변화 < 200ms
    - [ ] CLS < 0.1
    - [ ] 메모리 누수 없음

  # [v2 추가] 보안 검증
  security:
    - [ ] XSS 취약점 없음
    - [ ] CSRF 보호 유지
    - [ ] 민감 데이터 노출 없음
    - [ ] 인증/인가 로직 무결성

  # [v2 추가] 접근성 검증
  accessibility:
    - [ ] ARIA 라벨 적절성
    - [ ] 키보드 네비게이션
    - [ ] 색상 대비 4.5:1 이상
    - [ ] 스크린 리더 호환
```

---

## Phase 6: Deploy (배포)

### 배포 전 체크리스트
- [ ] 모든 검증 통과
- [ ] MODIFICATION_LOG.md 업데이트
- [ ] ROLLBACK_REGISTRY.md 업데이트
- [ ] 사용자 최종 승인

### [v2 추가] 배포 전략

```yaml
deployment_strategy:
  type: immediate | staged | canary

  staged:
    phase_1: 10% 트래픽
    phase_2: 50% 트래픽
    phase_3: 100% 트래픽
    rollback_threshold: error_rate > 1%

  canary:
    initial_percentage: 5%
    increment: 10%
    observation_period: 30min
```

---

## 에러 처리 프로토콜

### 레벨별 대응

| 레벨 | 조건 | 대응 |
|------|------|------|
| L1 | 문법 에러 | 자동 수정 시도 (1회) |
| L2 | 로직 에러 | 수정안 3개 제시 → 사용자 선택 |
| L3 | 구조적 문제 | 롤백 후 재계획 |
| L4 | 치명적 오류 | 즉시 롤백 + 사용자 알림 |

### [v2 추가] 에러 복구 시나리오

```yaml
error_recovery:
  scenario_1:
    trigger: "빌드 실패"
    action: "마지막 성공 커밋으로 롤백"
    notification: "사용자 + 로그"

  scenario_2:
    trigger: "런타임 에러 급증"
    action: "자동 롤백 + 원인 분석"
    notification: "사용자 + 상세 리포트"

  scenario_3:
    trigger: "성능 저하 감지"
    action: "경고 + 롤백 준비"
    notification: "사용자 확인 요청"
```

---

## [v2 추가] 롤백 메커니즘

### 롤백 포인트 생성

```yaml
rollback_point:
  id: "RP-20260415-001"
  created_at: "2026-04-15T10:30:00Z"
  phase: "Phase 2 완료"
  files_snapshot:
    - path: "src/components/Button.tsx"
      hash: "abc123"
      content_backup: ".claude/backups/Button.tsx.bak"
  state_snapshot:
    - store: "userStore"
      schema_hash: "def456"
  dependencies_snapshot:
    package_lock_hash: "ghi789"
```

### 롤백 실행

```
ROLLBACK PROTOCOL:
1. 롤백 포인트 선택
2. 파일 복원
3. 의존성 복원 (필요 시)
4. 검증 실행
5. MODIFICATION_LOG 업데이트 (롤백 기록)
```

---

## [v2 추가] 긴급 수정(Hotfix) 프로세스

```
[긴급 요청] → [영향 최소화 분석] → [빠른 수정] → [핵심 검증만] → [즉시 배포]
                                                      ↓
                                            [사후 전체 검증]
```

### Hotfix 조건
- 프로덕션 크리티컬 버그
- 보안 취약점 발견
- 데이터 무결성 위협

### Hotfix 제한
- 최대 50줄 변경
- 새 기능 추가 금지
- 리팩토링 금지

---

## [v2 추가] 병렬 작업 충돌 방지

### 파일 락 메커니즘

```yaml
file_lock:
  path: "src/components/Header.tsx"
  locked_by: "session_abc123"
  locked_at: "2026-04-15T10:00:00Z"
  expires_at: "2026-04-15T10:30:00Z"
  operation: "SKILL_FRONTEND"
```

### 충돌 해결 전략

| 상황 | 전략 |
|------|------|
| 같은 파일 수정 시도 | 대기 또는 병합 제안 |
| 의존 컴포넌트 수정 중 | 순차 실행으로 전환 |
| 공유 상태 수정 | 락 필수 + 검증 강화 |

---

## [v2 추가] 상태 관리 변경 가이드

### 상태 변경 영향 분석

```yaml
state_change_analysis:
  store_name: "userStore"
  change_type: add_field | remove_field | modify_type | restructure

  affected_consumers:
    - component: "UserProfile"
      usage: "useUserStore().name"
      action_required: "타입 업데이트"
    - component: "Header"
      usage: "useUserStore().isLoggedIn"
      action_required: "없음"

  migration_needed: boolean
  backward_compatible: boolean
```

### 마이그레이션 전략

```
1. 새 필드 추가 → 기본값 설정
2. 필드 제거 → deprecated 마킹 → 다음 버전에서 제거
3. 타입 변경 → 변환 유틸리티 제공
4. 구조 변경 → 점진적 마이그레이션
```

---

## [v2 추가] API 버전 호환성(->이후 개발. appendix-backend-future.md에 추가할 것. 현재 미진행)

### API 변경 체크

```yaml
api_compatibility:
  endpoint: "/api/users"
  current_version: "v2"
  changes:
    - field: "email"
      change: "required → optional"
      backward_compatible: true
    - field: "phone"
      change: "string → object"
      backward_compatible: false
      migration_path: "v2 → v3 어댑터 사용"
```

### 버전 관리 원칙
- Breaking change: 메이저 버전 증가
- 새 필드 추가: 마이너 버전 증가
- 버그 수정: 패치 버전 증가

---

## [v2 추가] 캐시 무효화 전략(->이후 개발. appendix-backend-future.md에 추가할 것. 현재 미진행)


```yaml
cache_invalidation:
  triggers:
    - "정적 자산 변경"
    - "API 응답 구조 변경"
    - "사용자 데이터 스키마 변경"

  strategies:
    static_assets:
      method: "content hash in filename"
      example: "main.[hash].js"

    api_cache:
      method: "cache-control header update"
      scope: "affected endpoints only"

    local_storage:
      method: "version key check"
      migration: "자동 마이그레이션 또는 클리어"
```

---

## [v2 추가] 모니터링 및 알림 연동

```yaml
monitoring:
  metrics:
    - name: "error_rate"
      threshold: "> 1%"
      action: "alert + auto_rollback_prepare"

    - name: "response_time_p95"
      threshold: "> 2000ms"
      action: "alert"

    - name: "memory_usage"
      threshold: "> 80%"
      action: "alert + scale_check"

  alerts:
    channels:
      - type: "slack"
        webhook: "${SLACK_WEBHOOK_URL}"
      - type: "email"
        recipients: ["team@example.com"]

    severity_mapping:
      critical: ["slack", "email", "pager"]
      warning: ["slack"]
      info: ["log_only"]
```

---

## [v2 추가] 다국어(i18n) 변경 가이드(->이후 개발. appendix-backend-future.md에 추가할 것. 현재 미진행)
### i18n 변경 체크리스트

```yaml
i18n_change:
  type: add_key | modify_key | remove_key | add_language

  checklist:
    - [ ] 모든 지원 언어에 키 추가
    - [ ] 기본 언어 폴백 확인
    - [ ] 플레이스홀더 일관성 검증
    - [ ] RTL 언어 레이아웃 확인 (해당 시)
    - [ ] 번역 길이에 따른 UI 테스트
```

### 자동 검증

```
1. 누락된 번역 키 감지(삭제)
2. 미사용 번역 키 감지(삭제)
3. 플레이스홀더 불일치 감지
```

---

## [v2 추가] 테스트 커버리지 기준

```yaml
test_coverage:
  minimum_thresholds:
    statements: 80%
    branches: 75%
    functions: 80%
    lines: 80%

  critical_paths:
    - path: "src/auth/*"
      minimum: 95%
    - path: "src/payment/*"
      minimum: 95%
    - path: "src/components/*"
      minimum: 70%

  new_code_requirement:
    coverage: 90%
    exception_process: "PR에서 정당성 설명 필요"
```

---

## [v2 추가] 문서 자동 생성

### 변경 시 자동 업데이트 대상

```yaml
auto_documentation:
  triggers:
    - "컴포넌트 props 변경"
    - "API 엔드포인트 변경"
    - "타입 정의 변경"

  outputs:
    - type: "component_docs"
      tool: "Storybook 자동 업데이트"
    - type: "api_docs"
      tool: "OpenAPI spec 재생성"
    - type: "type_docs"
      tool: "TypeDoc 실행"

  changelog:
    format: "conventional commits"
    auto_generate: true
```

---

## [v2 추가] 스킬 확장 인터페이스

### 새 스킬 추가 규격

```yaml
skill_interface:
  required_sections:
    - "역할 정의"
    - "입력 스키마"
    - "출력 스키마"
    - "에러 처리"
    - "의존 스킬"

  registration:
    file: "agents/skills/SKILL_[NAME].md"
    orchestrator_update: "AGENT_ORCHESTRATOR.md에 등록"

  lifecycle_hooks:
    before_execute: "선행 조건 검증"
    after_execute: "결과 검증 + 로깅"
    on_error: "에러 핸들링 + 알림"
```

### 스킬 의존성 선언

```yaml
skill_dependencies:
  SKILL_FRONTEND:
    requires: [SKILL_RESEARCH, SKILL_PLAN]
    optional: [SKILL_SECURITY]

  SKILL_VALIDATE:
    requires: [SKILL_FRONTEND]
    optional: []
```

---

## [v2 추가] 컨텍스트 압축 전략

### 대용량 컨텍스트 처리

```yaml
context_compression:
  triggers:
    - "총 컨텍스트 > 100KB"
    - "파일 수 > 20개"

  strategies:
    level_1:
      action: "주석 및 빈 줄 제거"
      reduction: "~20%"

    level_2:
      action: "관련 없는 파일 제외"
      reduction: "~40%"

    level_3:
      action: "함수 시그니처만 유지"
      reduction: "~70%"

    level_4:
      action: "핵심 로직만 추출"
      reduction: "~85%"

  preservation_priority:
    - "변경 대상 파일"
    - "직접 의존 파일"
    - "타입 정의"
    - "설정 파일"
```

---

## [v2 추가] 메트릭 수집 및 분석

### 수집 메트릭

```yaml
metrics_collection:
  per_session:
    - "총 수정 시간"
    - "롤백 횟수"
    - "에러 발생 횟수"
    - "사용된 스킬 목록"

  per_modification:
    - "변경 라인 수"
    - "영향 받은 파일 수"
    - "테스트 통과율"
    - "검증 소요 시간"

  aggregated:
    - "평균 수정 성공률"
    - "가장 빈번한 에러 유형"
    - "스킬별 사용 빈도"
    - "롤백 원인 분석"
```

### 분석 리포트

```
주간 리포트:
- 총 수정 건수
- 성공/실패 비율
- 평균 소요 시간
- 개선 권장 사항
```

~~~

---

## 4. SKILL_RESEARCH.md

**경로**: `agents/skills/SKILL_RESEARCH.md`

~~~markdown
# SKILL_RESEARCH: 코드 분석 스킬

> 역할: 수정 요청에 대한 영향 범위 분석
> 호출자: AGENT_ORCHESTRATOR (Phase 1)

---

## 입력

```yaml
input:
  request: "사용자 수정 요청 원문"
  project_context: "PROJECT_CONTEXT.md 내용"
  modification_log: "최근 수정 이력 (최대 10건)"
```

---

## 분석 프로세스

### Step 1: 요청 파싱
- 핵심 키워드 추출
- 수정 유형 분류 (UI/로직/데이터/스타일)

### Step 2: 파일 탐색
```
1. 키워드 기반 파일 검색
2. import/export 체인 추적
3. 공유 컴포넌트 식별
```

### Step 3: 영향 범위 산정
- 직접 영향: 수정 대상 파일
- 간접 영향: 의존 파일
- 잠재 영향: 동적 import, 조건부 렌더링

### [v2 추가] Step 4: 보안 영향 분석
```
1. 인증/인가 로직 포함 여부
2. 사용자 입력 처리 변경
3. 외부 API 호출 변경
4. 민감 데이터 흐름 변경
```

---

## 출력

```yaml
output:
  impact_analysis:
    affected_files:
      - path: "src/components/Button.tsx"
        change_type: modify
        risk: low
      - path: "src/pages/Home.tsx"
        change_type: modify
        risk: medium

    dependency_chain:
      Button.tsx:
        imported_by: [Home.tsx, Dashboard.tsx]
        imports: [utils/cn.ts, types/button.ts]

    risk_level: medium
    risk_factors:
      - "공유 컴포넌트 수정"
      - "3개 페이지에 영향"

    estimated_complexity: 5
    estimated_time: "2시간"

  # [v2 추가]
  security_impact:
    auth_affected: false
    data_flow_changed: false
    external_api_affected: false
    requires_security_review: false

  # [v2 추가]
  state_impact:
    stores_affected: []
    context_affected: []
    local_state_changes: ["Button 내부 상태"]
```

---

## 에러 처리

| 에러 | 대응 |
|------|------|
| 파일 찾기 실패 | 유사 파일명 제안 |
| 순환 의존성 감지 | 경고 + 영향 범위 확대 |
| 분석 불가 영역 | 명시적 표시 + 수동 검토 요청 |
~~~

---

## 5. SKILL_PLAN.md

**경로**: `agents/skills/SKILL_PLAN.md`

~~~markdown
# SKILL_PLAN: 수정 계획 스킬

> 역할: 상세 수정 계획 수립
> 호출자: AGENT_ORCHESTRATOR (Phase 2)
> 선행 스킬: SKILL_RESEARCH

---

## 입력

```yaml
input:
  impact_analysis: "SKILL_RESEARCH 출력"
  user_request: "원본 요청"
  constraints: "PROJECT_CONTEXT의 제약 조건"
```

---

## 계획 수립 프로세스

### Step 1: 작업 분해
- 원자적 작업 단위로 분해
- 각 작업의 독립성 확보

### Step 2: 순서 결정
```
1. 의존성 기반 정렬
2. 리스크 낮은 작업 우선
3. 테스트 가능 단위로 그룹화
```

### [v2 추가] Step 3: 병렬화 분석
```
1. 파일 중복 검사
2. 상태 의존성 검사
3. 병렬 실행 가능 그룹 식별
```

### [v2 추가] Step 4: 롤백 전략 수립
```
1. 각 단계별 롤백 포인트 정의
2. 롤백 순서 결정 (역순)
3. 데이터 마이그레이션 롤백 계획
```

---

## 출력

```yaml
output:
  modification_plan:
    id: "PLAN-20260415-001"
    summary: "버튼 컴포넌트 호버 효과 개선"

    steps:
      - id: 1
        description: "Button 컴포넌트 스타일 수정"
        files: [src/components/Button.tsx]
        type: modify
        changes:
          - "hover 상태 CSS 추가"
          - "transition 속성 추가"
        estimated_lines: 15
        rollback_strategy: "이전 스타일 복원"
        test_required: true

      - id: 2
        description: "Button 스토리 업데이트"
        files: [src/components/Button.stories.tsx]
        type: modify
        changes:
          - "hover 상태 스토리 추가"
        estimated_lines: 20
        rollback_strategy: "스토리 삭제"
        test_required: false

    # [v2 추가]
    dependency_graph:
      step_1: []
      step_2: [step_1]

    # [v2 추가]
    parallel_groups:
      - [step_1]  # 먼저 실행
      - [step_2]  # step_1 완료 후

    total_estimated_lines: 35
    total_estimated_time: "30분"

    # [v2 추가]
    rollback_point:
      id: "RP-20260415-001"
      restore_sequence: [step_2, step_1]  # 역순
```

---

## 계획 검증

```yaml
validation:
  - [ ] 모든 영향 파일 포함
  - [ ] 순환 의존성 없음
  - [ ] 각 단계 독립 테스트 가능
  - [ ] 롤백 전략 명확
  - [ ] 예상 시간 합리적
```
~~~

---

## 6. SKILL_FRONTEND.md

**경로**: `agents/skills/SKILL_FRONTEND.md`

~~~markdown
# SKILL_FRONTEND: 프론트엔드 수정 스킬

> 역할: 실제 코드 수정 실행
> 호출자: AGENT_ORCHESTRATOR (Phase 4)
> 선행 스킬: SKILL_PLAN

---

## 입력

```yaml
input:
  plan_step: "현재 실행할 계획 단계"
  current_file_content: "수정 대상 파일 현재 내용"
  project_conventions: "코딩 컨벤션"
```

---

## 수정 프로세스

### Step 1: 사전 검증
- 파일 존재 확인
- 락 상태 확인
- 현재 내용 해시 검증

### Step 2: 수정 실행
```
1. 백업 생성
2. 수정 적용
3. 포맷팅 (Prettier)
4. 린트 검사 (ESLint)
```

### [v2 추가] Step 3: 실시간 검증
```
1. TypeScript 컴파일 체크
2. import 경로 유효성
3. 사용된 변수/함수 존재 확인
```

---

## 수정 원칙

### 코드 스타일
- 기존 코드 스타일 유지
- 프로젝트 컨벤션 준수
- 불필요한 변경 최소화

### [v2 추가] 성능 고려
- 불필요한 리렌더링 방지
- 메모이제이션 적절히 사용
- 번들 사이즈 증가 최소화

### [v2 추가] 접근성 고려
- 시맨틱 HTML 사용
- ARIA 속성 적절히 적용
- 키보드 네비게이션 지원

---

## 출력

```yaml
output:
  modification_result:
    file: "src/components/Button.tsx"
    status: success | partial | failed

    changes_made:
      - line: 15
        type: add
        content: "className={cn(styles.button, isHovered && styles.hovered)}"
      - line: 20
        type: modify
        before: "background: blue"
        after: "background: var(--primary-color)"

    backup_path: ".claude/backups/Button.tsx.20260415-103000"

    # [v2 추가]
    validation:
      typescript: pass
      eslint: pass
      prettier: pass

    # [v2 추가]
    performance_check:
      bundle_size_change: "+0.5KB"
      render_impact: "none"
```

---

## 에러 처리

| 에러 | 대응 |
|------|------|
| 파일 락 | 대기 (최대 30초) 후 재시도 |
| 타입 에러 | 수정안 제시 |
| 린트 에러 | 자동 수정 시도 |
| 충돌 감지 | 사용자에게 선택권 제공 |
~~~

---

## 7. SKILL_VALIDATE.md

**경로**: `agents/skills/SKILL_VALIDATE.md`

~~~markdown
# SKILL_VALIDATE: 검증 스킬

> 역할: 수정 결과 검증
> 호출자: AGENT_ORCHESTRATOR (Phase 5)
> 선행 스킬: SKILL_FRONTEND

---

## 검증 레벨

### Level 1: 정적 분석 (필수)
```yaml
static_analysis:
  - typescript_compile: "tsc --noEmit"
  - eslint: "eslint --ext .ts,.tsx"
  - circular_deps: "madge --circular"
```

### Level 2: 단위 테스트 (필수)
```yaml
unit_tests:
  - existing_tests: "영향 받은 파일의 기존 테스트"
  - new_tests: "새 기능에 대한 테스트 (필요 시)"
  - coverage_check: "커버리지 감소 방지"
```

### Level 3: 통합 테스트 (선택)
```yaml
integration_tests:
  - component_integration: "컴포넌트 간 상호작용"
  - api_integration: "API 연동 테스트"
```

### [v2 추가] Level 4: 성능 테스트
```yaml
performance_tests:
  - bundle_size: "webpack-bundle-analyzer"
  - lighthouse: "LCP, FID, CLS 측정"
  - memory_leak: "Chrome DevTools Memory"
```

### [v2 추가] Level 5: 보안 테스트
```yaml
security_tests:
  - xss_check: "DOMPurify 적용 확인"
  - csrf_check: "토큰 검증 유지"
  - auth_check: "인증 로직 무결성"
  - dependency_audit: "npm audit"
```

### [v2 추가] Level 6: 접근성 테스트
```yaml
accessibility_tests:
  - axe_core: "자동화된 a11y 검사"
  - keyboard_nav: "Tab 순서 확인"
  - screen_reader: "VoiceOver/NVDA 호환"
```

---

## 출력

```yaml
output:
  validation_result:
    overall_status: pass | warn | fail

    static_analysis:
      typescript: pass
      eslint: pass
      circular_deps: pass

    tests:
      total: 45
      passed: 45
      failed: 0
      skipped: 2
      coverage: 82%

    # [v2 추가]
    performance:
      bundle_size: 
        before: "250KB"
        after: "252KB"
        change: "+0.8%"
        status: pass  # < 10% threshold

      lighthouse:
        lcp: "1.2s"
        fid: "50ms"
        cls: "0.05"
        status: pass

    # [v2 추가]
    security:
      xss: pass
      csrf: pass
      auth: pass
      dependencies: 
        vulnerabilities: 0
        status: pass

    # [v2 추가]
    accessibility:
      violations: 0
      warnings: 2
      status: pass

    recommendations:
      - "Button 컴포넌트에 대한 추가 테스트 권장"
```

---

## 실패 시 프로토콜

```
1. 실패 원인 분석
2. 수정안 3개 생성
3. 사용자에게 선택 요청
4. 선택된 수정안 적용
5. 재검증
```
~~~

---

## 8. [v2 추가] SKILL_ROLLBACK.md

**경로**: `agents/skills/SKILL_ROLLBACK.md`

~~~markdown
# SKILL_ROLLBACK: 롤백 스킬

> 역할: 안전한 롤백 실행
> 호출자: AGENT_ORCHESTRATOR (에러 발생 시)

---

## 롤백 유형

### Type 1: 단계 롤백
- 마지막 완료 단계만 롤백
- 가장 빠르고 안전

### Type 2: 전체 롤백
- 특정 롤백 포인트로 복원
- 여러 단계 한 번에 롤백

### Type 3: 선택적 롤백
- 특정 파일만 롤백
- 부분 복구에 사용

---

## 롤백 프로세스

```yaml
rollback_process:
  step_1: "롤백 대상 확인"
  step_2: "현재 상태 백업 (롤백 실패 대비)"
  step_3: "롤백 포인트에서 파일 복원"
  step_4: "의존성 복원 (필요 시)"
  step_5: "검증 실행"
  step_6: "로그 업데이트"
```

---

## 입력

```yaml
input:
  rollback_type: step | full | selective
  rollback_point_id: "RP-20260415-001"
  selective_files: []  # 선택적 롤백 시
```

---

## 출력

```yaml
output:
  rollback_result:
    status: success | partial | failed

    restored_files:
      - path: "src/components/Button.tsx"
        from_hash: "abc123"
        to_hash: "def456"
        status: success

    failed_files: []

    validation:
      typescript: pass
      tests: pass

    log_entry:
      timestamp: "2026-04-15T11:00:00Z"
      action: "rollback"
      reason: "빌드 실패"
      rollback_point: "RP-20260415-001"
```
~~~

---

## 9. [v2 추가] SKILL_SECURITY.md

**경로**: `agents/skills/SKILL_SECURITY.md`

~~~markdown
# SKILL_SECURITY: 보안 검증 스킬

> 역할: 보안 관점의 코드 검증
> 호출자: AGENT_ORCHESTRATOR (보안 영향 감지 시)

---

## 검증 항목

### XSS 방지
```yaml
xss_check:
  - innerHTML 사용 금지 (dangerouslySetInnerHTML 제외)
  - 사용자 입력 이스케이프 확인
  - DOMPurify 적용 확인
```

### CSRF 방지
```yaml
csrf_check:
  - 토큰 검증 로직 유지
  - SameSite 쿠키 설정
  - Origin 헤더 검증
```

### 인증/인가
```yaml
auth_check:
  - 보호된 라우트 유지
  - 토큰 만료 처리
  - 권한 검사 로직
```

### 민감 데이터
```yaml
sensitive_data_check:
  - 로그에 민감 정보 노출 금지
  - 로컬 스토리지에 토큰 저장 경고
  - API 응답에서 불필요한 데이터 제거
```

---

## 출력

```yaml
output:
  security_result:
    overall_status: pass | warn | fail

    findings:
      - severity: high | medium | low | info
        type: "xss_vulnerability"
        location: "src/components/Comment.tsx:25"
        description: "innerHTML 직접 사용"
        recommendation: "DOMPurify 적용 필요"

    recommendations:
      - "Content Security Policy 헤더 추가 권장"
```
~~~

---

## 10. PROJECT_CONTEXT.md 템플릿

**경로**: `[project]/.claude/PROJECT_CONTEXT.md`

~~~markdown
# 프로젝트 컨텍스트

> 최종 업데이트: YYYY-MM-DD
> 버전: 1.0.0

---

## 기술 스택

| 구분 | 기술 | 버전 |
|------|------|------|
| 프레임워크 | React | 18.x |
| 언어 | TypeScript | 5.x |
| 상태관리 | Zustand | 4.x |
| 스타일링 | Tailwind CSS | 3.x |
| 빌드 | Vite | 5.x |
| 테스트 | Vitest + RTL | - |

---

## 디렉토리 구조

```
src/
├── components/     # 재사용 컴포넌트
├── pages/          # 페이지 컴포넌트
├── hooks/          # 커스텀 훅
├── store/          # Zustand 스토어
├── utils/          # 유틸리티 함수
├── types/          # 타입 정의
├── api/            # API 클라이언트
└── styles/         # 글로벌 스타일
```

---

## 주요 컨벤션

### 네이밍
- 컴포넌트: PascalCase (Button.tsx)
- 유틸리티: camelCase (formatDate.ts)
- 상수: SCREAMING_SNAKE_CASE
- 타입/인터페이스: PascalCase + I/T 접두사 없음

### 컴포넌트 구조
```tsx
// 1. imports
// 2. types
// 3. constants
// 4. component
// 5. styles (if any)
// 6. exports
```

### 상태 관리
- 전역 상태: Zustand
- 서버 상태: TanStack Query
- 로컬 상태: useState/useReducer

---

## 제약 조건

- IE 미지원
- 최소 브라우저: Chrome 90+, Firefox 88+, Safari 14+
- 모바일 퍼스트 반응형
- 다크모드 지원 필수

---

## 알려진 이슈 / Tech Debt

- [ ] 레거시 클래스 컴포넌트 마이그레이션 필요
- [ ] 테스트 커버리지 60% → 80% 목표

---

## 중요 의존성

```json
{
  "react": "^18.2.0",
  "typescript": "^5.0.0",
  "zustand": "^4.4.0",
  "tailwindcss": "^3.4.0"
}
```
~~~

---

## 11. MODIFICATION_LOG.md 템플릿

**경로**: `[project]/.claude/MODIFICATION_LOG.md`

~~~markdown
# 수정 이력

---

## [2026-04-15] Button 호버 효과 개선

### 요약
버튼 컴포넌트에 호버 시 부드러운 색상 전환 효과 추가

### 변경 파일
- `src/components/Button.tsx` (modify)
- `src/components/Button.stories.tsx` (modify)

### 변경 내용
```diff
+ className={cn(styles.button, isHovered && styles.hovered)}
+ transition: background-color 0.2s ease;
```

### 테스트 결과
- 단위 테스트: 45/45 통과
- 커버리지: 82%

### 롤백 포인트
- ID: RP-20260415-001
- 백업: `.claude/backups/20260415-103000/`

---

## [이전 기록...]
~~~

---

## 12. [v2 추가] ROLLBACK_REGISTRY.md 템플릿

**경로**: `[project]/.claude/ROLLBACK_REGISTRY.md`

~~~markdown
# 롤백 포인트 레지스트리

---

## 활성 롤백 포인트

| ID | 생성일시 | 설명 | 상태 |
|----|----------|------|------|
| RP-20260415-001 | 2026-04-15 10:30 | Button 호버 효과 | active |
| RP-20260414-002 | 2026-04-14 15:00 | Header 레이아웃 | active |

---

## RP-20260415-001

```yaml
id: RP-20260415-001
created_at: "2026-04-15T10:30:00Z"
description: "Button 호버 효과 개선 전"
phase: "Phase 2 완료"

files:
  - path: "src/components/Button.tsx"
    hash: "abc123def456"
    backup: ".claude/backups/Button.tsx.20260415-103000"

restore_command: |
  # 자동 복원
  skill_rollback --point RP-20260415-001

  # 수동 복원
  cp .claude/backups/Button.tsx.20260415-103000 src/components/Button.tsx

expires_at: "2026-04-22T10:30:00Z"  # 7일 후 자동 삭제
```

---

## 만료된 롤백 포인트

| ID | 생성일시 | 만료일시 | 사유 |
|----|----------|----------|------|
| RP-20260408-001 | 2026-04-08 | 2026-04-15 | 자동 만료 |
~~~

---

## 13. [v2 추가] TEMPLATE_HOTFIX.md

**경로**: `agents/templates/TEMPLATE_HOTFIX.md`

~~~markdown
# 긴급 수정(Hotfix) 템플릿

> 용도: 프로덕션 크리티컬 버그 신속 수정
> 제한: 최대 50줄 변경, 새 기능 추가 금지

---

## Hotfix 요청

```yaml
hotfix_request:
  severity: critical | high
  issue: "[이슈 설명]"
  affected_users: "[영향 범위]"
  reported_at: "YYYY-MM-DD HH:MM"
```

---

## 빠른 분석 (10분 이내)

```yaml
quick_analysis:
  root_cause: "[원인]"
  fix_approach: "[수정 방향]"
  files_to_modify: [파일 목록]
  estimated_lines: N
  risk: low | medium
```

---

## 수정 내용

```diff
[변경 내용]
```

---

## 핵심 검증만 (15분 이내)

- [ ] TypeScript 컴파일
- [ ] 해당 기능 직접 테스트
- [ ] 회귀 가능성 검토

---

## 배포 후 TODO

- [ ] 전체 테스트 스위트 실행
- [ ] 모니터링 강화 (24시간)
- [ ] 근본 원인 분석 및 정식 수정 계획
~~~

---

## 14. 베스트 프랙티스

### 1. 점진적 수정
- 한 번에 하나의 기능만 수정
- 각 수정은 독립적으로 테스트/롤백 가능해야 함

### 2. 컨텍스트 최소화
- 필요한 파일만 로드
- 대용량 파일은 관련 부분만 추출

### 3. 선제적 검증
- 수정 전 타입 체크
- 수정 중 실시간 린트
- 수정 후 전체 검증

### 4. 문서화 자동화
- 모든 변경은 MODIFICATION_LOG에 기록
- 롤백 포인트 자동 생성
- 변경 diff 보존

### 5. 안전한 실패
- 에러 시 자동 롤백
- 상태 손상 방지
- 복구 경로 항상 확보

### [v2 추가] 6. 보안 우선
- 모든 사용자 입력 검증
- 민감 데이터 로깅 금지
- 정기적 의존성 감사

### [v2 추가] 7. 성능 의식
- 번들 사이즈 모니터링
- 불필요한 리렌더링 방지
- 메모리 누수 감지

### [v2 추가] 8. 접근성 고려
- 시맨틱 마크업 사용
- 키보드 네비게이션 지원
- 스크린 리더 호환성

---

## 15. 명령어 레퍼런스

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/research [요청]` | 영향 분석 시작 | `/research 버튼 색상 변경` |
| `/plan` | 계획 수립 | Phase 1 완료 후 |
| `/execute` | 수정 실행 | Phase 2 승인 후 |
| `/validate` | 검증 실행 | Phase 4 완료 후 |
| `/deploy` | 배포 | Phase 5 통과 후 |
| `/rollback [ID]` | 롤백 실행 | `/rollback RP-20260415-001` |
| `/status` | 현재 상태 | 언제든지 |
| `/log` | 수정 이력 | 언제든지 |
| `/hotfix [이슈]` | 긴급 수정 | `/hotfix 로그인 버튼 미작동` |
| `/security` | 보안 검사 | 보안 영향 감지 시 |
| `/metrics` | 메트릭 조회 | 언제든지 |

---

## 16. 체크리스트: 구현 완료 확인

- [ ] AGENT_ORCHESTRATOR.md 생성
- [ ] SKILL_RESEARCH.md 생성
- [ ] SKILL_PLAN.md 생성
- [ ] SKILL_FRONTEND.md 생성
- [ ] SKILL_VALIDATE.md 생성
- [ ] SKILL_ROLLBACK.md 생성 **(v2)**
- [ ] SKILL_SECURITY.md 생성 **(v2)**
- [ ] TEMPLATE_UI_CHANGE.md 생성
- [ ] TEMPLATE_HOTFIX.md 생성 **(v2)**
- [ ] PROJECT_CONTEXT.md 템플릿 생성
- [ ] MODIFICATION_LOG.md 템플릿 생성
- [ ] ROLLBACK_REGISTRY.md 템플릿 생성 **(v2)**
- [ ] 실제 프로젝트에 적용 테스트

---

## 변경 이력

| 버전 | 일자 | 변경 내용 |
|------|------|----------|
| v1.0 | 2026-04-15 | 초기 버전 |
| v2.0 | 2026-04-15 | 18개 보완 항목 추가 |
