# 웹앱 수정 에이전트/스킬 시스템 구현 계획

> 작성일: 2026-04-15  
> 기반 연구: [research-fixWebAgent.md](research-fixWebAgent.md)  
> 재사용 전략: `OKR/.claude/agents/web-build.md` → `AGENT_ORCHESTRATOR.md`에 구조 차용  
> 현재 개발 범위: 프론트엔드 및 로컬 서버 수정만 포함

---

## 1. 생성 파일 목록

| 순서 | 파일명 | 생성 경로 | 출처 |
|:----:|--------|-----------|------|
| 1 | `AGENT_ORCHESTRATOR.md` | `agents/` | **web-build.md 차용** |
| 2 | `SKILL_RESEARCH.md` | `agents/skills/` | research 초안 기반 |
| 3 | `SKILL_PLAN.md` | `agents/skills/` | 신규 |
| 4 | `SKILL_FRONTEND.md` | `agents/skills/` | 신규 |
| 5 | `SKILL_VALIDATE.md` | `agents/skills/` | 신규 |
| 6 | `TEMPLATE_UI_CHANGE.md` | `agents/templates/` | research Idea 4 기반 |
| 7 | `PROJECT_CONTEXT.md` | `OKR/okr-matrix-app/.claude/` | 신규 (템플릿) |
| 8 | `MODIFICATION_LOG.md` | `OKR/okr-matrix-app/.claude/` | 신규 (빈 파일) |

---

## 2. 실행 순서

```
Step 1 (기반)   : AGENT_ORCHESTRATOR.md
Step 2 (스킬)   : SKILL_RESEARCH → SKILL_PLAN → SKILL_FRONTEND → SKILL_VALIDATE
Step 3 (템플릿) : TEMPLATE_UI_CHANGE.md
Step 4 (프로젝트): PROJECT_CONTEXT.md → MODIFICATION_LOG.md
```

> `PROJECT_CONTEXT.md`는 생성 후 실제 프로젝트 정보를 직접 채워야 합니다.

---

## 3. AGENT_ORCHESTRATOR.md

**경로**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\agents\AGENT_ORCHESTRATOR.md`

**web-build.md에서 차용한 내용**:
- 5단계 워크플로우 구조 및 단계별 승인 게이트
- 에러 처리 프로토콜 (수정안 3개 → 사용자 선택)
- 베스트 프랙티스 5가지
- 명령어 레퍼런스 표 형식
- 컨텍스트 관리 원칙 (메인 컨텍스트 최소화)

**web-build.md 대비 변경 내용**:
- Phase 3 Execute(서브에이전트) → Phase 3 Split + Phase 5 Deploy(스킬)
- Phase 5 Ship(번들링) 제거 — 로컬 앱, 번들링 불필요
- Context Preservation Layer 추가 (PROJECT_CONTEXT.md + MODIFICATION_LOG.md 로드)
- Context rot 방지 규칙 추가 (2000줄 split 기준)

---

**파일 내용:**

~~~markdown
# 웹앱 수정 오케스트레이터

> 역할: 완성된 웹앱의 수정 작업을 체계적으로 관리합니다.
> 직접 코드를 작성하지 않으며, 스킬을 호출하고 컨텍스트를 유지합니다.

---

## 핵심 흐름

```
[세션 초기화] → [Research] → [Plan] → [Split] → [Validate] → [Deploy]
```

모든 작업은 위 순서를 따릅니다. **각 단계 완료 후 사용자 확인 없이 다음 단계 진행 금지.**

---

## 세션 시작 시 필수 로드 (Context Preservation Layer)

세션 시작 시 반드시 아래 파일을 읽고 컨텍스트로 유지합니다:

1. `[project]/.claude/PROJECT_CONTEXT.md` — 기술 스택, 디렉토리 구조, 제약 조건
2. `[project]/.claude/MODIFICATION_LOG.md` — 이전 변경 이력
3. `agents/AGENT_ORCHESTRATOR.md` (이 파일)

```
## 세션 초기화 프롬프트
다음 파일들을 읽고 컨텍스트로 유지해주세요:
1. `.claude/PROJECT_CONTEXT.md`
2. `.claude/MODIFICATION_LOG.md`
3. `../agents/AGENT_ORCHESTRATOR.md`

## 오늘의 작업
- 작업명: [예: OKR 대시보드 UI 개선]
- 세션 폴더: `.claude/sessions/YYYY-MM-DD_작업명/`

## 수정 요청
[여기에 구체적인 수정 사항 기술]

---
위 내용을 바탕으로 Research 단계부터 시작해주세요.
```

---

## Phase 1: Research (조사)

```yaml
목적: 수정 요청의 영향도 파악 및 리스크 식별
참조: agents/skills/SKILL_RESEARCH.md
산출물: research_result (영향 파일 목록, 의존성, 리스크)
```

체크리스트:
- [ ] 수정 대상 파일 식별
- [ ] 의존성(import, props, state) 추적
- [ ] Breaking change 가능성 검토
- [ ] 롤백 포인트 확인

---

## Phase 2: Plan (계획)

```yaml
목적: research_result 기반 구체적 수정 계획 수립
참조: agents/skills/SKILL_PLAN.md
산출물: 파일별 변경 명세, 작업 순서, 예상 라인 수
```

필수 확인 템플릿:
```
## 수정 계획 확인
1. 수정 파일: [목록]
2. 변경 방식: [추가/수정/삭제]
3. 예상 총 라인 수: [숫자]
4. Split 필요 여부: [Y/N]
위 내용이 맞으면 Split 단계로 진행하겠습니다.
```

---

## Phase 3: Split (분할)

```yaml
목적: context rot 방지를 위해 계획을 독립 태스크로 분할
기준: 1회 작업량 = 2000줄 이내
산출물: sessions/[날짜]_[작업명]/03_splits/ 하위 split_01.md, split_02.md, ...
```

Split 규칙:
- 각 split은 독립적으로 실행 가능해야 함
- 각 split에 필요한 컨텍스트(파일 경로, 의존 관계) 포함
- split 간 순서 의존성 명시

---

## Phase 4: Validate (검증)

```yaml
목적: 배포 전 변경사항 사전 검증
참조: agents/skills/SKILL_VALIDATE.md
산출물: 검증 리포트 (proceed / rollback)
```

체크포인트:
- [ ] TypeScript 타입 오류 없음
- [ ] 린트 통과
- [ ] 임포트 경로 정확
- [ ] 핵심 기능 smoke test

---

## Phase 5: Deploy (배포)

```yaml
목적: 검증된 계획에 따라 실제 코드 수정
참조: agents/skills/SKILL_FRONTEND.md
산출물: 수정된 코드 + MODIFICATION_LOG.md 업데이트
```

배포 후 필수:
- MODIFICATION_LOG.md에 변경 내역 기록
- 다음 세션을 위한 PROJECT_CONTEXT.md 업데이트 (필요 시)

---

## 명령어 레퍼런스

| 명령어 | 단계 | 설명 |
|--------|------|------|
| `/research [주제]` | Phase 1 | SKILL_RESEARCH 실행 |
| `/plan` | Phase 2 | SKILL_PLAN 실행 |
| `/split` | Phase 3 | 계획을 독립 태스크로 분할 |
| `/validate` | Phase 4 | SKILL_VALIDATE 실행 |
| `/deploy [split_id]` | Phase 5 | 특정 split 배포 |
| `/status` | 전체 | 현재 진행 상황 확인 |
| `/rollback [phase]` | 전체 | 특정 단계로 회귀 |

---

## 단계별 승인 게이트

```
[Research ✓] → [Plan ✓] → [Split ✓] → [Validate ✓] → [Deploy]
```

---
## 에러 처리 프로토콜

```yaml
에러 발생 시:
  1. 문제 상황 정확히 기술
  2. 해결 방안 3가지 이상 도출
  3. 사용자에게 선택지 제시
  4. 선택된 방안으로 재실행
  5. MODIFICATION_LOG.md에 발생 이유와 해결 방법 기록
```

---

## 컨텍스트 관리 원칙

- 메인 대화창의 복잡도 최소화
- 상세 구현은 스킬 파일로 분리
- 각 split 완료 후 결과 요약만 보고

---

## 베스트 프랙티스

1. **작은 단위로 나누기**: 복잡한 수정은 2000줄 이내 split으로 분해
2. **빈번한 피드백**: 각 단계마다 사용자 확인
3. **병렬 처리**: 독립적인 파일 수정은 동시 진행 가능
4. **문서화**: 모든 변경 사항을 MODIFICATION_LOG.md에 기록
5. **재사용**: 이전 sessions/ 기록을 참조하여 유사 패턴 활용
~~~

---

## 4. SKILL_RESEARCH.md

**경로**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\agents\skills\SKILL_RESEARCH.md`

---

**파일 내용:**

~~~markdown
# Research Skill

## Purpose
수정 대상 코드베이스를 분석하고 변경 영향도를 파악합니다.

## Input Required
- 수정 요청 사항 (무엇을 바꾸고 싶은지)
- PROJECT_CONTEXT.md
- MODIFICATION_LOG.md (이전 변경 이력)

## Analysis Checklist

### 1. 구조 분석
- [ ] 관련 파일 목록 식별
- [ ] 컴포넌트/모듈 의존성 맵핑
- [ ] 데이터 흐름 추적

### 2. 영향도 분석
- [ ] 직접 영향 받는 파일
- [ ] 간접 영향 받는 파일 (import하는 곳)
- [ ] 상태(state)를 공유하는 컴포넌트

### 3. 리스크 식별
- [ ] Breaking changes 가능성
- [ ] 사이드 이펙트 예상 영역
- [ ] 롤백 포인트

## Output Template

```yaml
research_result:
  request_summary: "..."
  affected_files:
    direct: []
    indirect: []
  dependencies:
    - from: "파일A"
      to: "파일B"
      type: "import/props/state"
  risks:
    - level: "high/medium/low"
      description: "..."
      mitigation: "..."
  estimated_lines: 0
  split_needed: false
```
~~~

---

## 5. SKILL_PLAN.md

**경로**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\agents\skills\SKILL_PLAN.md`

---

**파일 내용:**

~~~markdown
# Plan Skill

## Purpose
research_result를 받아 구체적인 수정 계획과 split 구조를 수립합니다.

## Input Required
- research_result (SKILL_RESEARCH 출력)
- PROJECT_CONTEXT.md

## Planning Checklist

### 1. 수정 명세
- [ ] 파일별 변경 사항 (추가/수정/삭제)
- [ ] 변경 전/후 핵심 코드 스니펫
- [ ] 파일별 예상 라인 수

### 2. 작업 순서
- [ ] 의존성을 고려한 파일 수정 순서
- [ ] 병렬 처리 가능한 작업 식별

### 3. Split 판단
- [ ] 총 예상 라인 수 계산
- [ ] 2000줄 초과 시 → split 계획 수립
- [ ] 2000줄 이하 시 → split 없이 단일 deploy

## Output Template

```yaml
plan_result:
  summary: "..."
  total_estimated_lines: 0
  split_needed: false
  file_changes:
    - file: "src/components/..."
      type: "modify"
      changes: "..."
      estimated_lines: 0
  execution_order:
    - step: 1
      files: []
      parallelizable: false
  split_plan:
    - split_id: "split_01"
      files: []
      estimated_lines: 0
      depends_on: []
```
~~~

---

## 6. SKILL_FRONTEND.md

**경로**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\agents\skills\SKILL_FRONTEND.md`

---

**파일 내용:**

~~~markdown
# Frontend Skill

## Purpose
검증된 split 계획에 따라 프론트엔드 코드를 실제 수정합니다.

## Input Required
- 실행할 split 문서 (sessions/[날짜]/03_splits/split_XX.md)
- PROJECT_CONTEXT.md
- MODIFICATION_LOG.md

## 수정 전 필수 확인
- [ ] split 문서 완전히 읽음
- [ ] 이전 split 완료 확인 (depends_on 있는 경우)
- [ ] 수정 대상 파일 현재 상태 Read로 확인

## 수정 원칙
- 요청된 변경만 수행 (범위 초과 금지)
- 기존 코드 스타일/컨벤션 유지
- 수정 완료 후 임포트 경로 확인

## 수정 후 필수 작업
- [ ] 변경된 파일 목록 정리
- [ ] 예상치 못한 부수 효과 여부 확인
- [ ] MODIFICATION_LOG.md 업데이트 내용 준비

## Output

```
수정 완료 보고:
  수정된 파일: []
  변경 내용 요약: "..."
  주의 사항: "..."
  MODIFICATION_LOG 업데이트 필요: Y/N
```
~~~

---

## 7. SKILL_VALIDATE.md

**경로**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\agents\skills\SKILL_VALIDATE.md`

---

**파일 내용:**

~~~markdown
# Validate Skill

## Purpose
코드 수정 후 배포 전에 변경사항을 검증합니다.

## Input Required
- 수정된 파일 목록
- PROJECT_CONTEXT.md (빌드 명령어, 실행 방법)

## Validation Checklist

### 1. 정적 분석
- [ ] TypeScript 타입 오류 없음 (`tsc --noEmit`)
- [ ] 린트 오류 없음 (`eslint`)
- [ ] 임포트 경로 유효

### 2. Smoke Test
- [ ] 앱 정상 기동 (`npm run dev`)
- [ ] 수정된 기능 기본 동작
- [ ] 연관 기능 이상 없음

### 3. 롤백 조건

아래 항목 중 하나라도 해당하면 Plan 단계로 회귀:
- TypeScript 오류 다수 (5건 이상)
- 앱 기동 실패
- 핵심 기능 동작 불가

## Output

```yaml
validate_result:
  static_analysis:
    typescript: "pass/fail"
    eslint: "pass/fail"
    imports: "pass/fail"
  smoke_test:
    app_starts: true/false
    modified_feature: "pass/fail"
    related_features: "pass/fail"
  decision: "proceed/rollback"
  rollback_reason: ""
```
~~~

---

## 8. TEMPLATE_UI_CHANGE.md

**경로**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\agents\templates\TEMPLATE_UI_CHANGE.md`

---

**파일 내용:**

~~~markdown
# UI Change Template

변경 유형이 UI 수정인 경우 Research와 Validate 단계에서 이 템플릿을 추가로 적용합니다.

## Research 체크리스트 (UI 특화)
- [ ] 컴포넌트 구조 파악 (부모/자식 관계)
- [ ] 스타일 의존성 (CSS 모듈, Tailwind 클래스 등)
- [ ] 반응형 처리 여부
- [ ] 접근성 요소 (aria 속성, 키보드 탐색)

## Risk Areas
- 반응형 레이아웃 깨짐
- 기존 스타일과 충돌
- 부모 컴포넌트 레이아웃 영향

## Validate 체크리스트 (UI 특화)
- [ ] 주요 해상도 확인 (모바일 375px / 태블릿 768px / 데스크톱 1280px)
- [ ] 인터랙티브 상태 확인 (hover / focus / disabled / loading)
- [ ] 다크/라이트 모드 (해당하는 경우)
~~~

---

## 9. PROJECT_CONTEXT.md

**경로**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\OKR\okr-matrix-app\.claude\PROJECT_CONTEXT.md`

> 생성 후 아래 `[채울 내용]` 항목을 실제 프로젝트 정보로 직접 채워야 합니다.

---

**파일 내용:**

~~~markdown
# OKR Matrix App — Project Context

> 최초 작성: YYYY-MM-DD  
> 마지막 업데이트: YYYY-MM-DD  
> 세션 시작 시 반드시 이 파일을 로드합니다.

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| Frontend | [채울 내용: 예 React 18, TypeScript] |
| Styling | [채울 내용: 예 TailwindCSS] |
| State | [채울 내용: 예 Zustand] |
| Build | [채울 내용: 예 Vite] |
| 실행 | 로컬 서버 (`npm run dev`) |

---

## 디렉토리 구조

```
src/
├── components/     # [주요 컴포넌트 설명]
├── pages/          # [페이지 컴포넌트 설명]
├── hooks/          # [커스텀 훅 설명]
├── store/          # [상태 관리 설명]
├── utils/          # [유틸리티 설명]
└── types/          # [타입 정의 설명]
```

---

## 주요 컨벤션

- 컴포넌트 네이밍: PascalCase
- 파일 네이밍: kebab-case
- [채울 내용: 기타 프로젝트 특화 규칙]

---

## 수정 시 주의사항

- [채울 내용: 중요한 제약 조건]

---

## 알려진 이슈 / Tech Debt

- [ ] [채울 내용]
~~~

---

## 10. MODIFICATION_LOG.md

**경로**: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\OKR\okr-matrix-app\.claude\MODIFICATION_LOG.md`

---

**파일 내용:**

~~~markdown
# Modification Log

> 세션 시작 시 반드시 이 파일을 로드합니다.
> 각 Deploy 단계 완료 후 아래 형식으로 업데이트합니다.

---

## 로그 형식

```
## YYYY-MM-DD — [작업명]

### 수정 파일
- `경로/파일.tsx`: 변경 내용 요약

### 이유
변경 이유

### 주의 사항
다음 수정 시 알아야 할 사항 (없으면 생략)
```

---

<!-- 아래에 로그 추가 (최신 순) -->
~~~

---

## 11. 완료 체크리스트

### 최초 1회 설정

- [ ] `agents/skills/` 폴더 생성
- [ ] `agents/templates/` 폴더 생성
- [ ] `AGENT_ORCHESTRATOR.md` 생성
- [ ] `SKILL_RESEARCH.md` 생성
- [ ] `SKILL_PLAN.md` 생성
- [ ] `SKILL_FRONTEND.md` 생성
- [ ] `SKILL_VALIDATE.md` 생성
- [ ] `TEMPLATE_UI_CHANGE.md` 생성
- [ ] `PROJECT_CONTEXT.md` 생성 → **실제 프로젝트 정보 채우기**
- [ ] `MODIFICATION_LOG.md` 생성

### 첫 세션 시작 전

- [ ] `PROJECT_CONTEXT.md`에 실제 기술 스택 / 디렉토리 구조 기입
- [ ] `okr-matrix-app` 디렉토리에서 Claude Code 실행
- [ ] 세션 초기화 프롬프트 실행 (AGENT_ORCHESTRATOR.md 내 템플릿 참조)

---

## 부록: web-build.md 차용 대조표

| web-build.md 원본 | AGENT_ORCHESTRATOR.md 적용 | 변경 이유 |
|-------------------|---------------------------|-----------|
| Phase 3: Execute (ui-specialist + logic-architect) | Phase 3: Split + Phase 5: Deploy (SKILL_FRONTEND) | 신규 생성 → 기존 앱 수정으로 목적 변경 |
| Phase 5: Ship (번들링) | 제거 | 로컬 서버 앱, 번들링 불필요 |
| 단계별 승인 게이트 | 그대로 차용 | — |
| 에러 처리 프로토콜 | 그대로 차용 + MODIFICATION_LOG 기록 추가 | — |
| 베스트 프랙티스 5가지 | 내용 수정 후 차용 | split/문서화 중심으로 조정 |
| 명령어 레퍼런스 표 형식 | `/split`, `/deploy` 추가 후 차용 | — |
| 컨텍스트 관리 원칙 | 그대로 차용 | — |
