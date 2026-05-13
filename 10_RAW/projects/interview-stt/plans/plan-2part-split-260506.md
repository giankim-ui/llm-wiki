# Plan: 2-part 분할 (긴급 ROI 관리자 이동 v1.0 · 업무 요약 재설계 v2.1)

## Meta

v2.0 archive 파일(`plan-work-summary-objectives-v2.0.md`)의 손글씨 주석에서 **두 방향의 변경**이 드러났으며 사용자 확인으로 **둘을 분리**하기로 확정:
- **Part B (긴급, 선 실행)**: ROI/Tier 표시 전부 관리자 페이지로 이동 + "왜 낮은지" 세부 설명
- **Part A (후속)**: 업무 요약 세션을 **KR 상위 Task 군집(HR 업무 도메인) 분류** 시각화로 재설계 + AX 목표 → RecommendedTasks 통합

사용자 참조로 지목된 OKR matrix HTML 은 **계층구조(Objective→KR→Task→SubTask) 개념만** 차용. 동 HTML 의 4-Quadrant(긴급·중요) 분류 체계는 본 프로젝트와 무관 — 이전 설계안에서 후보로 고려했으나 폐기.

본 plan 승인 후 archive 에 **두 개 파일로 분할 배치**:
- `Interview/archive/plan-roi-admin-move-v1.0.md` ← Part B
- `Interview/archive/plan-work-summary-objectives-v2.1.md` ← Part A (v2.0 주석 정제본)

v2.0 원본은 보존 (사용자 손주석 아카이브).

---

# Part B — plan-roi-admin-move-v1.0 (긴급 · 선 실행)

## Context

피면담자가 화면을 볼 수 있는 면담장에서 ROI 점수·Tier·5지표 그래프 등 **평가성 지표가 노출되는 리스크**가 있다. 현재 좌측 목록(PersonRow) 과 우측 상세(PersonDetailPane → RoiBreakdown) 양쪽에 모두 표시된다. v2.0 에서 이 전부를 관리자 전용 페이지(`SensitivePage`)로 이동시키고, 관리자가 "왜 이 사람 점수/등급이 낮은지"를 즉시 이해할 수 있도록 **자연어+근거 chip 복합 설명**을 추가한다.

## Design

### 면담 화면(면담카드)에서 제거

1. **PersonRow (`PersonRow.tsx:22-35`)**: ROI 숫자 + Tier 배지 block 삭제. 남는 정보: 이름 · 팀 · 설문 제출 배지.
2. **PersonListPane (`PersonListPane.tsx:24-28`)**: `roi_total` 내림차순 정렬 제거 → **면담 상태 그룹(예정 → 진행중 → 완료 → 취소) + 각 그룹 내 이름 가나다순** 으로 교체.
3. **PersonDetailPane (`PersonDetailPane.tsx:107-111`)**: `<RoiBreakdown>` 섹션 + 바로 위 "AX ROI 분석" 제목 + 주변 Separator 제거. 상단 헤더의 Tier 뱃지(§80-88)도 제거(이름·팀·직급·설문제출 유지).

### 관리자 페이지 추가 (`SensitivePage.tsx` 우측 패널)

우측 패널 헤더 아래(현재 §228 평가 원문 ScrollArea 바로 위)에 **2단 카드** 삽입:

1. **AX ROI 상세 진단** 카드 상단
   - 총점 + Tier (큰 글씨)
   - 5개 지표 horizontal bar (기존 RoiBreakdown 재활용)
2. **지표별 "왜 이 점수인가" 설명 리스트** — 자연어 + 근거 chip
   - 5개 지표 각각 세로 나열
   - 한 지표 = `[지표명] [점수] [⚠️ 낮음/중간/높음 뱃지] + 1-2문장 나레이티브 + [근거 chip 여러 개]`

### 신규 유틸: `src/lib/roi/explain.ts`

```ts
export interface ExplainItem {
  key: 'r' | 'p' | 'o' | 'a' | 'g'
  label: string         // '반복성', '자동화잠재력', ...
  score: number
  level: 'low' | 'mid' | 'high'
  message: string       // 자연어 한두 문장
  evidence: string[]    // ['pain_summary 없음', '미응답자']
}

export function explainScore(
  baseline: RoiBaseline,
  survey: SurveyResponse | null,
  person: Person,
  objScore?: { ax_hits?: number; weight_avg?: number; gap?: number }
): ExplainItem[]
```

#### 설명 룰 테이블

| 지표 | 임계 | level | message | evidence |
|------|------|-------|---------|----------|
| **R** | <40 | low | "설문 미제출로 반복성 추정 불가 → 기본값 적용" | pain_summary 없음, 미응답자 |
| **R** | 40~60 | mid | "비효율 언급 확인됨 — 빈도 키워드는 약함" | pain_summary 있음, 빈도 약함 |
| **R** | ≥60 | high | "반복 업무 다수 언급 — 자동화 우선순위 높음" | 매일/주N 키워드 N건 |
| **P** | <30 | low | "목표에 AX 관련 키워드 미검출" | ax_hits: 0 |
| **P** | 30~60 | mid | "일부 목표에 AX 관련 단서 있음" | ax_hits: N |
| **P** | ≥60 | high | "목표 대다수가 AX 관련 — 잠재력 높음" | ax_hits: N+ |
| **O** | <15 | low | "실무자 직급, 직책 없음 — 조직 파급력 제한적" | level: X, no_position |
| **O** | 15~30 | mid | "중간 리더십 범위" | level: X |
| **O** | ≥30 | high | "경영 간부 또는 직책 보유 — 조직 영향 큼" | level: X, position |
| **A** | <25 | low | "AI 도구 사용 경험 미확인" | 미응답 or 빈 응답 |
| **A** | 25~50 | mid | "1~2종 AI 도구 사용 경험" | tools: ChatGPT 등 |
| **A** | ≥50 | high | "다수 AI 도구 경험 — 얼리 어답터" | tools: N개 |
| **G** | =0 | high | "자기-CL 평가 정렬됨 — 갭 없음" | gap: 0 |
| **G** | 0<x<30 | mid | "경미한 자기 과대평가" | gap: N |
| **G** | ≥30 | low | "자기-CL 큰 차이 — 변화관리 리스크" | gap: N |

`level` 해석: G 는 낮을수록 좋음(리스크 적음), 나머지 4개는 낮을수록 나쁨. 카드 뱃지 표시는 직관과 일치하도록 "낮음/중간/높음" 을 **ROI 기여도 관점**으로 통일 (G 는 이미 `max(0, 갭)` 변환 후 값이므로 **높을수록 위험**으로 메시지 작성).

## Critical Files

| 파일 | 변경 |
|------|------|
| `ax-interview-app/src/components/person-list/PersonRow.tsx` | lines 22-35 ROI 블록 제거 |
| `ax-interview-app/src/components/person-list/PersonListPane.tsx` | lines 24-28 정렬 로직 교체 (면담 상태 + 가나다) |
| `ax-interview-app/src/components/person-card/PersonDetailPane.tsx` | §80-88 Tier 뱃지 제거, §107-111 RoiBreakdown 섹션 제거 |
| `ax-interview-app/src/App.tsx` | `<SensitivePage>` 에 `surveys` prop 추가 (explain 에 필요) |
| `ax-interview-app/src/components/admin/SensitivePage.tsx` | props 확장(`surveys`) + 우측 패널에 RoiBreakdown + explainScore 카드 삽입 |
| `ax-interview-app/src/lib/roi/explain.ts` | **신규** — explainScore 유틸 |
| `ax-interview-app/src/components/admin/RoiExplainCard.tsx` | **신규** — ExplainItem[] 렌더 |

**읽기만**: `analysis/04_roi_matrix.py` (설명 룰 근거), `types/schema.ts` (RoiBaseline, SurveyResponse)

## 구현 단계

1. **T1** `explain.ts` 유틸 작성 (순수 함수, React 의존성 없음). 단위테스트는 수동 콘솔로 대체.
2. **T2** `RoiExplainCard.tsx` 작성 (ExplainItem[] 받아 렌더).
3. **T3** `SensitivePage.tsx` 우측 패널 헤더(§220-227) 아래에 `<RoiBreakdown baseline={selectedBaseline} />` + `<RoiExplainCard items={explainScore(...)} />` 조건부 렌더. baseline 탐색 로직 추가.
4. **T4** `App.tsx` 에서 `<SensitivePage surveys={surveys} />` 전달.
5. **T5** `PersonDetailPane.tsx` — Tier 뱃지(§81-86) 및 RoiBreakdown 섹션(§107-111) 제거.
6. **T6** `PersonRow.tsx` — ROI/Tier 블록(§22-35) 제거. Layout grid 재조정 (이름을 메인 영역 전체로).
7. **T7** `PersonListPane.tsx` — 정렬 로직 교체. 상태 우선순위 `scheduled < in_progress < completed < canceled` + 내부에서 `person.name.localeCompare` (ko).
8. **T8** `pnpm build` 성공 → `python inline-bundle.py` 재생성.

## Verification

```bash
cd "Interview/ax-interview-app" && pnpm exec tsc --noEmit   # 0 error
pnpm build                                                    # 0 error
python inline-bundle.py                                       # bundle.html 생성
```

UI 수동:
| 검증 | 기대 |
|------|------|
| 좌측 목록 | 이름·팀·설문제출 뱃지만 표시. ROI/Tier 뱃지 전부 사라짐 |
| 좌측 정렬 | 예정 그룹 상단 → 진행중 → 완료 → 취소. 각 그룹 가나다순 |
| 우측 상세 | Tier 뱃지·ROI 분석 섹션 사라짐. 이름/팀/직급/설문제출만 |
| 관리자 페이지 (🔒 관리자 클릭 후 행 선택) | 우측에 **총점+5지표 bar** → **5개 설명 카드** → 평가 원문 순 |
| 설명 카드 샘플 (Tier D) | R 35점 ⚠️낮음 "설문 미제출..." + chip | 
| 설명 카드 샘플 (Tier S/A) | P 60+ 높음 "목표 대다수가 AX..." |

---

# Part A — plan-work-summary-objectives-v2.1 (후속)

## Context

v2.0 파일 주석("긴급성 떨어지므로 추가 구현")에 따라 **Part B 이후** 실행. v2.0 plan 은 "연도별 활동 + 전략/운영 비율 + AX 이력 3종" 시각화였으나 사용자 주석에서 **목표 건수/유형 분포는 중요하지 않음**, 대신 **TASK 상위 군집(업무 도메인) 분류**가 필요하다고 전환.

### 참조 해석 정정 (사용자 추가 설명)

사용자가 참조로 지목한 `Smartmeeting/10_HR_IN_Meeting_DB/okr_matrix.html` 은 **Objective → KR → Task → SubTask 4계층 구조 개념**만 참조 대상이다. 같은 파일에 있는 4-Quadrant(긴급·중요 매트릭스 em1~em4) 체계는 **본 프로젝트와 무관 — 사용하지 않음**.

핵심 시사점:
- 현재 `objectives.json` 한 레코드 = **KR 수준** (= `objective.title` 이 KR 단위)
- v2.1 시각화의 방향은 이 KR 들을 **상위의 Task 군집(= HR 업무 도메인)** 으로 묶어 분포를 보여주는 것
- SubTask 까지의 세분화는 현 seed 에 데이터 없음 → 본 plan 범위 외 (면담 기록/과제화 단계에서 수집)

### 사용자 최종 요구

1. 업무 요약에는 해당 인원의 목표가 **어떤 업무 영역(채용/복리후생/교육 …)** 에 속하는지가 보여야 함. 중요도는 **weight 합** 으로 판단.
2. AX 관련 과거 목표는 별도 섹션이 아닌 **하단 RecommendedTasks 섹션과 통합**.
3. 설문 미제출자에게도 동일하게 도메인 분석 표시.

## Design

### 12개 HR 업무 도메인 taxonomy (사용자 확정)

위 Context "참조 해석 정정" 에 따라, 아래 12개 도메인은 **KR(= `objectives.title`) 위에 올려놓는 Task 상위 군집**으로 해석. 면담자 입장에서 "이 사람이 어떤 업무 계열을 담당하는가"를 한 눈에 파악하는 용도.


1. 채용·온보딩
2. 복리후생
3. 교육·인재개발
4. 평가·보상
5. 조직문화
6. 인사기획·HR IT
7. 보고·거버넌스
8. 글로벌·해외 HR
9. 노무·법무
10. 데이터·분석
11. 시설·안전
12. 기타 운영 (매칭 실패 시 폴백)

### 분류 로직 (`src/lib/classify/hr-domain.ts`)

```ts
export interface HrDomain { id: string; label: string; keywords: string[] }

export const HR_DOMAINS: HrDomain[] = [
  { id: 'recruit',    label: '채용·온보딩',    keywords: ['채용','온보딩','영입','신입','경력입사','지원자'] },
  { id: 'welfare',    label: '복리후생',        keywords: ['복리','복지','경조','사내복지','휴가','건강검진'] },
  { id: 'edu',        label: '교육·인재개발',   keywords: ['교육','인재개발','학습','연수','세미나','강의','수료','리더십'] },
  { id: 'eval',       label: '평가·보상',       keywords: ['평가','보상','성과','연봉','인센티브','승진','C.L','CL평가'] },
  { id: 'culture',    label: '조직문화',        keywords: ['조직문화','소통','워크숍','이벤트','사내행사','몰입'] },
  { id: 'plan',       label: '인사기획·HR IT',  keywords: ['인사기획','HR IT','시스템','SAP','HRIS','경영간부','발령'] },
  { id: 'report',     label: '보고·거버넌스',   keywords: ['보고','거버넌스','보고서','정책','규정','프로세스','감사'] },
  { id: 'global',     label: '글로벌·해외 HR',  keywords: ['글로벌','해외','GHR','중국','미국','일본','법인'] },
  { id: 'labor',      label: '노무·법무',       keywords: ['노무','법무','노조','단체협약','근태','근로','준법'] },
  { id: 'data',       label: '데이터·분석',     keywords: ['데이터','분석','대시보드','리포트','통계','KPI','시각화'] },
  { id: 'facility',   label: '시설·안전',       keywords: ['시설','안전','점검','보안','관리동','건물'] },
  { id: 'etc',        label: '기타 운영',       keywords: [] },
]

export function classifyObjective(title: string): string {
  for (const d of HR_DOMAINS) {
    if (d.keywords.some(k => title.includes(k))) return d.id
  }
  return 'etc'
}
```

`first-match wins` 전략. 여러 카테고리 키워드가 겹치면 배열 순서 우선순위.

### 집계 및 시각화 (WorkSummaryCard)

```ts
// 각 카테고리별 건수 + weight 합
const domainStats = useMemo(() => {
  const m: Record<string, { count: number; weightSum: number; recent: string[] }> = {}
  for (const o of myObjs) {
    const id = classifyObjective(o.title)
    const w = o.weight ?? 1.0  // weight null → 기본 1.0
    if (!m[id]) m[id] = { count: 0, weightSum: 0, recent: [] }
    m[id].count++
    m[id].weightSum += w
    if (m[id].recent.length < 2) m[id].recent.push(`${o.year} ${o.title}`)
  }
  return HR_DOMAINS
    .map(d => ({ ...d, ...m[d.id] }))
    .filter(d => d.count > 0)
    .sort((a, b) => b.weightSum - a.weightSum)
}, [myObjs])
```

**시각화**: 카테고리별 horizontal bar
```
채용·온보딩  ▰▰▰▰▰▰▰▰  5건 · 중요도 40%
교육·인재개발 ▰▰▰▰▰      3건 · 중요도 25%
평가·보상    ▰▰▰        2건 · 중요도 15%
...
```

- row = `[카테고리명 120px] [bar flex, width = weightSum / maxWeight * 100%] [건수] [weight%]`
- 최상위 카테고리는 진한 슬레이트-700, 이후 슬레이트-500 → 슬레이트-400 그라데이션
- 마우스 호버 시 `recent` 목표 2건 툴팁 (shadcn tooltip)

### 섹션 재구성

```
📋 업무 요약
├─ (제출자만) 비효율 포인트  [기존]
├─ (제출자만) AI 도구 / 데이터 저장  [기존]
├─ (제출자만) DX 관심  [기존]
├─ ────────── Separator ──────────
├─ 업무 도메인 분포  [신규 — 전원 표시]
└─ (objectives 0건 → "목표 데이터 없음" 안내)
```

- 미제출자 + objectives ≥1: 상단 회색 info 배지 "설문 미제출 — 목표 데이터 기반 분석" + 도메인 분포만
- 미제출자 + objectives 0: "목표 데이터 없음"

### AX 목표 → RecommendedTasks 통합

현재 `RecommendedTasks.tsx` 는 priority 1~3 QW 카드 + custom task Dialog. 상단 헤더(§81-93) 아래에 **과거 AX 목표 배너** 조건부 삽입:

```tsx
{axObjs.length > 0 && (
  <div className="mb-3 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2.5">
    <p className="text-xs font-semibold text-blue-700 mb-1.5">과거 AX 관련 목표 — 추천 근거</p>
    <ul className="space-y-0.5">
      {axObjs.map((o, i) => (
        <li key={i} className="text-xs text-slate-700 flex gap-2">
          <span className="text-slate-400 shrink-0">{o.year}</span>
          <span className="truncate">{o.title}</span>
        </li>
      ))}
    </ul>
  </div>
)}
```

`axObjs` 는 PersonDetailPane 에서 WorkSummaryCard 와 RecommendedTasks 양쪽에 전달(혹은 RecommendedTasks 쪽으로만 전달하고 WorkSummaryCard 에서는 제외). 사용자 "AX 관련 목표 추천… 하단 추천과제와는 통합할것" 에 따라 **WorkSummaryCard 에서는 AX 목표 섹션 삭제**, RecommendedTasks 로만.

## Critical Files

| 파일 | 변경 |
|------|------|
| `ax-interview-app/src/lib/classify/hr-domain.ts` | **신규** — 12 도메인 LUT + classifyObjective |
| `ax-interview-app/src/components/person-card/WorkSummaryCard.tsx` | Props 확장(objectives, employeeId) + 도메인 bar 섹션 추가 + AX 섹션 제거 |
| `ax-interview-app/src/components/person-card/RecommendedTasks.tsx` | Props 확장(`axObjs?`) + 헤더 아래 AX 배너 조건부 렌더 |
| `ax-interview-app/src/components/person-card/PersonDetailPane.tsx` | Props 확장(objectives) + axObjs 계산 + WorkSummaryCard/RecommendedTasks 에 전달 |
| `ax-interview-app/src/App.tsx` | `<PersonDetailPane>` 에 `objectives={objectives}` 전달 |

**읽기만**: `types/schema.ts` (Objective), `lib/seed/loader.ts` (getObjectives 이미 export)

## 구현 단계

1. **T1** `hr-domain.ts` LUT + classifyObjective 작성. 수동 sanity: 목표 title 20개 샘플에 대해 분류 정확도 확인 — 70% 이상 합리적이면 통과.
2. **T2** `WorkSummaryCard.tsx` — 연도/유형 섹션 제거, 도메인 bar 섹션 추가.
3. **T3** `RecommendedTasks.tsx` — axObjs 배너.
4. **T4** `PersonDetailPane.tsx`, `App.tsx` — props 전달.
5. **T5** build + bundle.

## Verification

```bash
cd "Interview/ax-interview-app" && pnpm exec tsc --noEmit && pnpm build
python inline-bundle.py
```

UI 수동:
| 검증 | 기대 |
|------|------|
| 설문 제출자 | 기존 3섹션 + Separator + 업무 도메인 bar |
| 설문 미제출자 (objectives≥1) | info 배지 + 업무 도메인 bar |
| objectives 0건 | "목표 데이터 없음" 단일 텍스트 |
| AX 키워드 목표 많은 사람 | WorkSummaryCard 에는 AX 섹션 없음. RecommendedTasks 상단에 파란 배너로 최대 5건 표시 |
| AX 0건 사람 | 배너 자체 비표시 |
| 도메인 bar 정렬 | weight 합 내림차순. 0건 도메인 비표시 |
| 미매칭 목표 | "기타 운영" 카테고리로 집계 |

### 분류 품질 점검

수동 20건 샘플:
- "비용 절감(CR)" → 보고·거버넌스 (감사/정책 키워드 없음 → etc 로 빠질 수 있음, 품질 저하 시 keywords 튜닝)
- "경영간부 인원정보 자동화" → 인사기획·HR IT ('경영간부' 매칭)
- "신입사원 채용 및 온보딩" → 채용·온보딩
- "교육 수료관리 DB 자동화" → 교육·인재개발
- "GHR 다국가 대시보드" → 글로벌·해외 HR
분류 정확도 <70% 면 keywords 보강(2차 배포).

---

## Execution (본 plan 승인 직후)

본 통합 plan 을 archive 에 **두 개 파일로 분할 배치**:

```bash
# Part B → plan-roi-admin-move-v1.0.md (긴급)
cp "C:/Users/Pulmuone/.claude/plans/c-users-pulmuone-onedrive-claude-interv-idempotent-swing.md" \
   "C:/Users/Pulmuone/OneDrive - 풀무원/!Claude/Interview/archive/plan-roi-admin-move-v1.0.md"
# Edit: Meta + Part A 섹션 제거, Part B 만 남김

# Part A → plan-work-summary-objectives-v2.1.md (후속)
cp "C:/Users/Pulmuone/.claude/plans/c-users-pulmuone-onedrive-claude-interv-idempotent-swing.md" \
   "C:/Users/Pulmuone/OneDrive - 풀무원/!Claude/Interview/archive/plan-work-summary-objectives-v2.1.md"
# Edit: Meta + Part B 섹션 제거, Part A 만 남김
```

v2.0 원본 (`plan-work-summary-objectives-v2.0.md`) 은 사용자 손주석 보존 차원에서 **그대로 유지**.

구현은 **Part B 먼저, Part A 는 사용자 추가 지시 시** 진행.

## 범위 밖

- weight null 비율 통계 재확인 (v2.0 탐색 중 세 번째 agent 미완 — 필요 시 구현 단계 T1 에서 품질 점검).
- 가중치 슬라이더(Phase 3) 및 Supabase 이관(Phase 4) 은 본 plan 범위 외.
- `description` 필드 파싱 (seed 에 미포함) — 분류 정확도 부족 시 05_build_seed.py 재실행 후 추가.
