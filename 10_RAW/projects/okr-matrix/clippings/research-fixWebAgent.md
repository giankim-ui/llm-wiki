# 웹앱 수정을 위한 에이전트/스킬 기반 접근법 연구

> 작성일: 2026-04-14  
> 목적: 완성된 웹앱 수정 작업의 효율화를 위한 에이전트 & 스킬 체계 설계  
> 대상 프로젝트: `C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\OKR\okr-matrix-app`

---

## 1. 현재 워크플로우 분석

```
┌─────────────────────────────────────────────────────────────────┐
│  (1) Draft Research  →  (2) Refine  →  (3) Review              │
│       [Human]            [Opus]         [Human]                 │
│                                                                 │
│  (4) Plan  →  (5) Split Plan  →  (6) Deploy                    │
│     [Opus]      [Claude]          [Claude]                      │
└─────────────────────────────────────────────────────────────────┘
```

### 현재 구조의 강점

| 단계 | 강점 |
|------|------|
| **(1)→(2)→(3)** | Human-in-the-loop으로 품질 보장 |
| **(5) Split Plan** | Context rot 방지 → 장기 작업에서 핵심 |
| **역할 분리** | 연구/계획/실행의 명확한 구분 |

### 잠재적 약점 & 병목

#### 1. 컨텍스트 단절 문제
```
Split된 Plan들 사이에서 "전체 그림"을 잃을 위험
→ 각 split이 독립적으로 실행되면 일관성 저하
```

#### 2. 피드백 루프 부재
```
(6) Deploy 후 문제 발생 시 어느 단계로 롤백?
→ 현재 구조에선 불명확
```

#### 3. 범용 에이전트의 한계
```
웹앱 수정은 매우 다양한 도메인:
- Frontend (React/Vue/CSS)
- Backend (API/DB)
- DevOps (배포/환경)
→ 하나의 범용 에이전트가 모두 잘하기 어려움
```

---

## 2. 개선 아이디어

### Idea 1: 스킬 기반 모듈화

```
┌─────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                    │
│            (워크플로우 제어 & 컨텍스트 관리)              │
└────────────────────────┬────────────────────────────────┘
                         ▼
             ┌──────────────────────┐
             │    Research Skill    │
             │  - 코드 분석          │
             │  - 의존성 파악        │
             │  - 영향도 분석        │
             └──────────┬───────────┘
                        │ research_result
                        ▼
             ┌──────────────────────┐
             │     Plan Skill       │
             │  - 변경 계획 수립     │
             │  - 리스크 평가        │
             │  - Split 계획        │
             └──────────┬───────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │   Validate Skill     │
             │  - Dry-run           │
             │  - 타입/린트 검사     │
             └──────────┬───────────┘
                        │
           ┌────────────┴────────────┐
           ▼                         ▼
┌──────────────────┐    ┌──────────────────────────────┐
│  Frontend Skill  │    │  Backend Skill (이후 개발)    │
│  - UI 수정       │    │  - API 수정                  │
│  - 스타일링      │    │  - DB 마이그레이션            │
└──────────────────┘    │  → appendix-backend-future.md│
  ← 현재 범위           └──────────────────────────────┘
```

**구조 원칙**: Research → Plan 순차 실행으로 종합 분석, Execution 단계에서만 변경 유형별 분기  
**현재 범위**: Research/Plan/Validate/Frontend Skill 구현. Backend Skill은 이후 개발.

---

### Idea 2: Context Preservation Layer 추가

```python
# 개념적 구조
class ContextManager:
    def __init__(self):
        self.global_context = {
            "project_structure": {},    # 전체 구조
            "modification_history": [], # 변경 이력
            "constraints": [],          # 제약 조건
            "decisions": []             # 결정 사항 (왜 이렇게 했는지)
        }

    def inject_to_split(self, split_task):
        """각 split에 필요한 컨텍스트만 주입"""
        relevant_context = self.filter_relevant(split_task)
        return f"{relevant_context}\n\n{split_task}"
```

**효과**: Split해도 일관성 유지

---

### Idea 3: 워크플로우에 Validation 단계 추가

```
현재:  Plan → Split → Deploy

개선:  Plan → Split → [Dry-run/Preview] → Validate → Deploy
                            ↓
                      문제시 (4)로 회귀
```

| 추가 단계 | 역할 |
|-----------|------|
| **Dry-run** | 실제 적용 전 영향 범위 시뮬레이션 |
| **Validate** | 타입 체크, 린트, 테스트 자동 실행 |

---

### Idea 4: 변경 유형별 템플릿화

```yaml
# 스킬 템플릿 예시
modification_types:
  ui_change:
    research_focus: ["컴포넌트 구조", "스타일 의존성"]
    risk_areas: ["반응형", "접근성"]
    validation: ["visual regression test"]

  # api_change / dependency_update → 이후 개발 (appendix-backend-future.md 참조)
```

**효과**: 변경 유형 감지 → 자동으로 적합한 스킬/체크리스트 적용  
**현재 적용 범위**: `ui_change`만 사용. 나머지 템플릿은 부록 참조.

---

### 종합 개선 워크플로우

```
┌────────────────────────────────────────────────────────────────────┐
│                        개선된 워크플로우                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  (1) Draft Research [Human]                                        │
│           ↓                                                        │
│  (2) Refine + 변경유형 분류 [Opus] ←── 템플릿 참조                  │
│           ↓                                                        │
│  (3) Review + Context 저장 [Human]                                 │
│           ↓                                                        │
│  (4) Plan [Opus] ←── 특화 스킬 호출 (Frontend/로컬서버)             │
│                      (Backend/DevOps는 이후 개발 → 부록 참조)        │
│           ↓                                                        │
│  (5) Split + Context Injection [Claude]                            │
│           ↓                                                        │
│  (5.5) Dry-run & Validate [Claude] ←── 자동 검증                   │
│           ↓ (실패시 4로 회귀)                                       │
│  (6) Deploy [Claude]                                               │
│           ↓                                                        │
│  (7) Post-deploy Check [자동화] ←── 헬스체크, 스모크 테스트         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 실행 우선순위

| 우선순위 | 개선 항목 | 구현 난이도 | 효과 |
|:--------:|-----------|:-----------:|:----:|
| 🥇 | Context Preservation Layer | 중 | 높음 |
| 🥈 | Validation 단계 추가 | 낮음 | 높음 |
| 🥉 | 변경유형별 템플릿 | 중 | 중간 |
| 4 | 스킬 모듈화 (프론트엔드 범위) | 높음 | 높음 |

> **현재 개발 범위**: `okr-matrix-app`은 **로컬 서버 기반 프론트엔드** 앱입니다.  
> 현재는 **프론트엔드 및 로컬 서버 내 수정만** 진행하며, 백엔드(API/DB/DevOps) 관련 개발은 이후 단계로 분리합니다.  
> → 백엔드 이후 개발 계획은 **[부록: 백엔드 이후 개발](appendix-backend-future.md)** 을 참조하세요.
---

## 3. 실제 적용 방법

### 3-1. 권장 디렉토리 구조

```
C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\
│
├── _agents/                          # 🔧 범용 에이전트/스킬 (모든 프로젝트 공유)
│   ├── AGENT_ORCHESTRATOR.md         # 메인 오케스트레이터
│   ├── skills/
│   │   ├── SKILL_RESEARCH.md         # 리서치 스킬
│   │   ├── SKILL_PLAN.md             # 플래닝 스킬
│   │   ├── SKILL_FRONTEND.md         # 프론트엔드 수정 스킬
│   │   ├── SKILL_VALIDATE.md         # 검증 스킬
│   │   └── SKILL_BACKEND.md          # (이후 개발 → 부록 참조)
│   └── templates/
│       ├── TEMPLATE_UI_CHANGE.md
│       ├── TEMPLATE_REFACTOR.md
│       └── TEMPLATE_API_CHANGE.md    # (이후 개발 → 부록 참조)
│
├── OKR/
│   └── okr-matrix-app/               # 🎯 실제 웹앱 프로젝트
│       ├── src/
│       ├── package.json
│       ├── ...
│       │
│       └── .claude/                  # 📋 프로젝트별 컨텍스트
│           ├── PROJECT_CONTEXT.md    # 프로젝트 구조/규칙
│           ├── MODIFICATION_LOG.md   # 변경 이력
│           └── sessions/             # 세션별 작업 기록
│               └── 2024-01-15_ui-refactor/
│                   ├── 01_research.md
│                   ├── 02_plan.md
│                   └── 03_splits/
│
└── _templates/                       # 📝 기타 템플릿
```

---

### 3-2. 핵심 파일 내용

#### `_agents/AGENT_ORCHESTRATOR.md`

```markdown
# Web App Modification Orchestrator

## Role
완성된 웹앱의 수정 작업을 체계적으로 관리하는 오케스트레이터입니다.

## Workflow
1. **Research Phase** → SKILL_RESEARCH.md 참조
2. **Plan Phase** → SKILL_PLAN.md 참조  
3. **Split Phase** → Context rot 방지를 위한 작업 분할 (context rot 방지는 한 번에 2천줄 이상 작업시 발생 하므로 1회 분량은 2천줄 내외에서 분할하여 진행)
4. **Validate Phase** → SKILL_VALIDATE.md 참조
5. **Deploy Phase** → 실제 코드 수정

## Commands
- `/research [주제]` - 리서치 스킬 실행
- `/plan` - 플래닝 스킬 실행
- `/split` - 계획을 독립 태스크로 분할
- `/validate` - 변경사항 검증
- `/deploy [split_id]` - 특정 분할 작업 실행

## Context Loading
세션 시작 시 반드시 로드:
1. PROJECT_CONTEXT.md (프로젝트 구조)
2. MODIFICATION_LOG.md (이전 변경 이력)
3. 현재 작업의 research/plan 문서

## Output Format
모든 출력은 `C:/Users/Pulmuone/OneDrive - 풀무원/!Claude/자료/sessions/[날짜]_[작업명]/`에 저장
```

---

#### 'C:/Users/Pulmuone/OneDrive - 풀무원/!Claude/agents/skills/SKILL_RESEARCH.md`

```markdown
# Research Skill

## Purpose
수정 대상 코드베이스를 분석하고 변경 영향도를 파악합니다.

## Input Required
- 수정 요청 사항 (무엇을 바꾸고 싶은지)
- 프로젝트 컨텍스트 (PROJECT_CONTEXT.md)

## Analysis Checklist
### 1. 구조 분석
- [ ] 관련 파일 목록 식별
- [ ] 컴포넌트/모듈 의존성 맵핑
- [ ] 데이터 흐름 추적

### 2. 영향도 분석
- [ ] 직접 영향 받는 파일
- [ ] 간접 영향 받는 파일 (import하는 곳)
- [ ] 테스트 파일

### 3. 리스크 식별
- [ ] Breaking changes 가능성
- [ ] 사이드 이펙트 예상 영역
- [ ] 롤백 포인트

## Output Template
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
  recommendations: []
```

---

#### `OKR/okr-matrix-app/.claude/PROJECT_CONTEXT.md`

```markdown
# OKR Matrix App - Project Context

## Tech Stack
- Frontend: [React/Vue/etc.]
- State Management: [Redux/Zustand/etc.]
- Styling: [TailwindCSS/CSS Modules/etc.]
- Build Tool: [Vite/CRA/etc.]

## Directory Structure
src/
├── components/     # UI 컴포넌트
├── pages/          # 페이지 컴포넌트
├── hooks/          # 커스텀 훅
├── store/          # 상태 관리
├── utils/          # 유틸리티
├── types/          # 타입 정의
└── api/            # API 호출(현재는 미사용)

## Key Conventions
- 컴포넌트 네이밍: PascalCase
- 파일 네이밍: kebab-case
- 상태 관리 패턴: [설명]

## Known Issues / Tech Debt
- [ ] 이슈1
- [ ] 이슈2

## 수정 시 주의사항
- [프로젝트 특화 규칙들]
```

---

### 3-3. 세션 시작 위치 및 프롬프트

#### 세션 시작 위치

```
📍 시작 위치: C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\OKR\okr-matrix-app
```

이 위치에서 시작하는 이유:
- 프로젝트 파일에 직접 접근 가능
- `.claude/` 폴더에서 컨텍스트 로드
- 상위의 `_agents/`도 참조 가능

---

#### 세션 초기화 프롬프트

```
# 세션 초기화 프롬프트

## 컨텍스트 로드
다음 파일들을 읽고 컨텍스트로 유지해주세요:
1. `.claude/PROJECT_CONTEXT.md`
2. `.claude/MODIFICATION_LOG.md`
3. `../_agents/AGENT_ORCHESTRATOR.md`

## 오늘의 작업
- 작업명: [예: OKR 대시보드 UI 개선]
- 세션 폴더: `.claude/sessions/YYYY-MM-DD_작업명/`

## 수정 요청
[여기에 구체적인 수정 사항 기술]

---
위 내용을 바탕으로 Research 단계부터 시작해주세요.
```

---

### 3-4. 단계별 프롬프트 예시

#### (1) Draft Research — Human 작성

```
## 내 초안 리서치

### 수정하고 싶은 것
- OKR 테이블의 정렬 기능 추가
- 진행률 컬럼에 프로그레스 바 시각화

### 내가 파악한 관련 파일
- src/components/OKRTable.jsx
- src/components/ProgressCell.jsx (새로 만들어야 할 듯)

### 우려 사항
- 기존 테이블 성능에 영향?
```

#### (2) Refine Research — Claude 실행

```
/research 실행

위 초안을 바탕으로:
1. 내가 놓친 관련 파일이 있는지 분석
2. 의존성 맵 작성
3. 리스크 평가
4. SKILL_RESEARCH.md 템플릿에 맞춰 정리
```

#### (4) Plan — Claude 실행

```
/plan 실행

Research 결과를 바탕으로:
1. 구체적인 수정 계획 수립
2. 파일별 변경 사항 명세
3. 작업 순서 정의
4. 예상 소요 시간

SKILL_PLAN.md 형식에 맞춰 작성
```

#### (5) Split Plan — Claude 실행

```
/split 실행

위 계획을 context rot 방지를 위해 분할:
- 각 split은 독립적으로 실행 가능해야 함
- 각 split에 필요한 컨텍스트 포함
- split 간 의존성 명시

출력 위치: .claude/sessions/[현재세션]/03_splits/
```

#### (6) Deploy — Claude 실행

```
/deploy split_01

Split 01을 실행합니다:
- 해당 split 문서 로드
- 코드 수정 수행
- 변경 사항 MODIFICATION_LOG.md에 기록
```

---

## 4. 빠른 시작 체크리스트

### 최초 1회 설정

- [ ] `!Claude/_agents/` 폴더 생성
- [ ] `AGENT_ORCHESTRATOR.md` 파일 생성 및 작성
- [ ] `_agents/skills/` 폴더 생성
- [ ] `SKILL_RESEARCH.md` 생성 및 작성
- [ ] `SKILL_PLAN.md` 생성 및 작성
- [ ] `SKILL_FRONTEND.md` 생성 및 작성
- [ ] `SKILL_BACKEND.md` 생성 및 작성 ← **이후 개발** ([부록](appendix-backend-future.md) 참조)
- [ ] `SKILL_VALIDATE.md` 생성 및 작성
- [ ] `_agents/templates/` 폴더 생성
- [ ] `okr-matrix-app/.claude/` 폴더 생성
- [ ] `PROJECT_CONTEXT.md` 작성 (프로젝트 분석)
- [ ] `MODIFICATION_LOG.md` 생성 (빈 파일로 시작)

### 매 작업 시작 시

- [ ] 새 세션 폴더 생성: `.claude/sessions/YYYY-MM-DD_작업명/`
- [ ] 세션 초기화 프롬프트 실행
- [ ] Research → Plan → Split → (Validate) → Deploy 순서 진행
- [ ] 완료 후 `MODIFICATION_LOG.md` 업데이트

---

## 5. 실용적 팁

### Claude Desktop / Claude.ai 사용 시

```
세션 시작할 때 관련 파일들을 첨부하거나
파일 내용을 프롬프트에 직접 포함시키세요.

예: "다음은 PROJECT_CONTEXT.md 내용입니다: ..."
```

### Claude Code (CLI) 사용 시

```bash
# okr-matrix-app 디렉토리에서 실행
claude

# .claude/ 폴더 또는 CLAUDE.md를 자동 인식
```

---

## 6. 구조 확장 시 참고

동일한 `_agents/` 구조를 다른 프로젝트에도 재사용 가능합니다.  
새 프로젝트 추가 시:

1. `!Claude/[프로젝트명]/[앱폴더]/.claude/` 생성
2. `PROJECT_CONTEXT.md` 신규 작성
3. `MODIFICATION_LOG.md` 빈 파일로 생성
4. `_agents/`는 공유 그대로 사용

```
!Claude/
├── _agents/          ← 모든 프로젝트가 공유
├── OKR/
│   └── okr-matrix-app/.claude/
├── [다음 프로젝트]/
│   └── [앱폴더]/.claude/
└── [또 다른 프로젝트]/
    └── [앱폴더]/.claude/
```
