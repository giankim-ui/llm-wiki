---
type: plan
project: knowledge-management
date: 2026-09-19
status: active
source: self
topic: 옵시디언 모바일↔PC 최적 동기화
version: v1.0
tags:
  - knowledge-management
  - sync
  - automation
  - mobile
mirrors_raw: "[[옵시디언 모바일 pc 최적 동기화방안-260916]]"
---

# Plan — 옵시디언 모바일↔PC 동기화 + llm-wiki 자동화 v1.0

## 0. 목표 (사용자 원문)

1. 모바일에서 떠오른 투자 아이디어를 모바일 Gemini로 딥리서치
2. 그 결과를 옵시디언 **RAW**에 넣기
3. 모바일 → PC 동기화
4. PC에서 RAW 확정
5. n8n(또는 .cmd 스케줄러)으로 매일 자동 llm-wiki 관리
6. 모바일↔PC 양방향 동기화

## 1. 현황 제약 (이 설계를 규정하는 4가지)

| # | 제약 | 결과 |
|---|---|---|
| C1 | vault 실체 = `C:\Users\Pulmuone\OneDrive - 풀무원\20-Obsidian` (**회사 OneDrive**) | 회사 데이터가 섞여 있음 → 외부 클라우드/공개 저장소로 vault 전체를 올리면 안 됨 |
| C2 | OneDrive Android 앱은 **로컬 동기화 폴더를 제공하지 않음** | Obsidian 모바일이 OneDrive vault를 직접 열 수 없음. "OneDrive로 양방향" 은 애초에 성립 불가 |
| C3 | `.gitignore` 가 `10_RAW/`·`20_WIKI/`·루트 `*.md` 제외 (git = 인프라 전용) | vault 내용을 GitHub로 동기화하려면 보안 정책 재검토 필요 → **채택하지 않음** |
| C4 | 자동화는 이미 `morning-routine.cmd` → `morning_gate.py` → `claude "/projects → /ingest"` 로 하루 1회 동작 | n8n은 **이 체인을 대체**하는 게 아니라 **트리거만 교체** |

> C2 때문에 "모바일에서 전체 vault를 그대로 편집" 은 유료 Obsidian Sync 말고는 안전한 길이 없다.
> 따라서 v1.0은 **전체 vault 양방향을 포기하고, 역할을 분리**한다.

## 2. 아키텍처 결정

### 2.1 권장안 — 인박스 분리형 (Syncthing + 미니 vault)

```
[Android]
 Gemini 딥리서치 결과
        │ 공유(Share) →
 Obsidian 모바일 "KM-Inbox" 미니 vault   ← 수십 KB, 회사기밀 없음
        │
   Syncthing-Fork (P2P, 로컬망/릴레이)
        │
[Windows PC]
 C:\KM-Sync\inbox\            ← OneDrive **바깥** 착지 폴더 (이중동기화 차단)
        │ scripts/inbox_intake.py (이동 + frontmatter 정규화)
        ▼
 OneDrive\20-Obsidian\10_RAW\inbox\<slug>\  ← 여기서부터 기존 vault 규칙 적용
        │ n8n Schedule → claude -p "/projects → /ingest"
        ▼
 20_WIKI/... + INDEX.md + LOG.md + DAILY.md
        │ scripts/mobile_digest.py (읽기 전용 내보내기)
        ▼
 C:\KM-Sync\digest\  → Syncthing → Android "KM-Inbox" vault 안 digest/ 폴더
```

**왜 이 안인가**
- C2 회피: 모바일이 여는 건 OneDrive가 아니라 Syncthing이 만든 **로컬 폴더**
- C1 준수: 모바일에 나가는 건 *내가 모바일에서 쓴 것* + *내가 고른 요약* 뿐. 회사 원본은 PC에 잔류
- C3 준수: GitHub 정책 변경 불필요
- 이중 동기화 충돌 차단: Syncthing 착지 폴더를 OneDrive 밖(`C:\KM-Sync\`)에 둠 — OneDrive와 Syncthing이 **같은 파일을 동시에 건드리지 않음**
- 비용 0원

**양방향의 정의(중요)**: 쓰기 양방향이 아니라 **쓰기는 모바일→PC 단방향, 읽기는 PC→모바일 단방향**의 조합이다. 같은 파일을 양쪽에서 동시에 편집하지 않으므로 충돌 파일(`sync-conflict`)이 구조적으로 발생하지 않는다. 실무에서 필요한 건 대부분 이것이다.

### 2.2 대안 비교

| 방식 | 비용 | 진짜 양방향 | 회사정책 리스크 | 충돌 위험 | 판정 |
|---|---|---|---|---|---|
| **Syncthing 인박스 분리형** | 0 | 부분(역할분리) | 낮음(P2P, 외부 클라우드 미경유) | 매우 낮음 | **채택** |
| Obsidian Sync | 약 $4~5/월 | 완전 | 중(vault 전체가 외부 서버 경유, E2EE지만 회사데이터) | 낮음 | 전체 양방향이 꼭 필요해지면 전환 |
| Git(obsidian-git) | 0 | 완전 | **높음** — `10_RAW` 에 인사위/PMO 자료 존재, private라도 사외 호스팅 | 중(모바일 머지 실패 잦음) | 기각 |
| OneDrive 앱 직결 | 0 | — | — | — | **불가**(C2) |
| Syncthing으로 vault 전체 | 0 | 완전 | 중(PC 방화벽/보안SW 승인 필요) | **높음**(OneDrive와 이중 동기화) | 기각 |

### 2.3 전환 조건 (v2 트리거)
아래 중 하나라도 발생하면 Obsidian Sync 유료 전환을 재검토한다.
- 모바일에서 `20_WIKI/` 를 **편집**해야 하는 일이 주 1회 이상
- 기기가 3대 이상으로 늘어남
- Syncthing이 회사 보안SW에 차단됨

---

## 3. Phase 1 — PC 준비 (30분)

### Step 1-1. 착지 폴더 생성 (OneDrive 바깥)
```bat
mkdir C:\KM-Sync\inbox
mkdir C:\KM-Sync\digest
mkdir C:\KM-Sync\_trash
```
`C:\KM-Sync` 는 **절대 OneDrive 안에 두지 않는다**. 이게 이 설계의 핵심 가드레일이다.

### Step 1-2. Syncthing 설치
- https://syncthing.net/downloads/ → Windows (SyncTrayzor 권장: 트레이 상주 + 자동시작)
- 설치 후 브라우저 GUI `http://127.0.0.1:8384` 자동 오픈
- **Actions → Settings → GUI** 에서 사용자명/비번 설정 (로컬 GUI 보호)
- **Settings → Connections**: `Enable NAT traversal` ON, `Global Discovery` 는 회사망 정책에 따라 — LAN에서만 쓸 거면 OFF 가능(집/회사 왔다갔다 하면 ON 권장)

### Step 1-3. 공유 폴더 2개 등록
| Folder ID | 경로 | Folder Type |
|---|---|---|
| `km-inbox` | `C:\KM-Sync\inbox` | **Send & Receive** |
| `km-digest` | `C:\KM-Sync\digest` | **Send Only** ← PC가 발신만 |

`km-digest` 를 Send Only로 두면 모바일에서 실수로 요약본을 수정해도 PC 원본이 오염되지 않는다.

### Step 1-4. 방화벽
Windows Defender 방화벽에서 Syncthing의 **TCP/UDP 22000**, **UDP 21027(로컬 디스커버리)** 인바운드 허용. 회사 보안SW(예: 백신/EDR)가 차단하면 → 2.3 전환 조건 발동.

---

## 4. Phase 2 — Android 세팅 (스텝별 상세, 40분)

### Step 2-1. Syncthing-Fork 설치
- Play 스토어 → **"Syncthing-Fork"** (Catfriend1 배포). 공식 `Syncthing` 앱은 유지보수 중단 상태라 Fork를 쓴다.
- 최초 실행 → 저장소 권한 허용
- **Settings → Run conditions**: `Run on mobile data` OFF(원하면), `Run on battery` ON, `Always run in background` ON
- **배터리 최적화 제외** 필수: 설정 → 앱 → Syncthing-Fork → 배터리 → **제한 없음**. 이걸 안 하면 도즈 모드에서 동기화가 몇 시간씩 밀린다.

### Step 2-2. 기기 페어링
1. 폰 Syncthing-Fork → **Devices → + → QR 스캔**
2. PC Syncthing GUI → **Actions → Show ID** (QR 표시) → 폰으로 스캔
3. PC GUI에 "새 기기 승인?" 알림 → **Add Device** → 이름 `android-phone` → Save
4. 폰에도 승인 알림 → 수락
5. 양쪽 Devices 탭에 상대 기기가 **Connected** 로 뜰 때까지 대기(같은 Wi-Fi면 수 초)

### Step 2-3. 폴더 페어링
1. PC GUI → `km-inbox` 폴더 → **Edit → Sharing 탭 → `android-phone` 체크 → Save**
2. 폰에 "폴더 공유 요청" 알림 → 수락 → 로컬 경로를 다음으로 지정:
   `/storage/emulated/0/Documents/KM-Inbox/inbox`
3. `km-digest` 도 동일하게 공유 → 폰 경로 `/storage/emulated/0/Documents/KM-Inbox/digest`
   - 폰 쪽 폴더 타입은 **Receive Only** 로 설정
4. 폰에서 폴더 상태가 `Up to Date` 가 되는지 확인

> Android 11+ 에서 `/storage/emulated/0/Documents/...` 아래는 앱이 자유롭게 쓸 수 있다. `Android/data/` 아래는 피할 것(Obsidian이 못 읽음).

### Step 2-4. Obsidian 모바일 — 미니 vault 열기
1. Obsidian 모바일 설치 → 첫 화면 **"Open folder as vault"**
2. 폴더 선택기에서 `Documents/KM-Inbox` 선택 → vault 이름 `KM-Inbox`
   - 이 안에 `inbox/`(쓰기) 와 `digest/`(읽기) 가 하위 폴더로 보인다
3. Settings → Files & Links
   - `Default location for new notes` → **In the folder specified below** → `inbox`
   - `Default location for new attachments` → `inbox/_attachments`
4. Settings → Editor → `Show frontmatter` ON

### Step 2-5. 캡처 템플릿 (frontmatter 자동)
1. Settings → Core plugins → **Templates** ON
2. Settings → Templates → Template folder: `_tpl`
3. `_tpl/idea.md` 파일을 vault에 생성(모바일에서 직접 작성해도 되고, PC `C:\KM-Sync\inbox\_tpl\idea.md` 에 만들면 동기화된다):

```markdown
---
type: chat-extract
source: gemini-mobile
status: draft
date: {{date:YYYY-MM-DD}}
captured_at: {{time:HH:mm}}
axis: asset
slug:
ticker:
tags:
  - mobile-capture
  - deep-research
---

# {{title}}

## 아이디어 한 줄

## Gemini 딥리서치 원문

## 다음 액션
- [ ] PC에서 축/슬러그 확정
- [ ] /ingest
```

4. Settings → Hotkeys(또는 모바일 툴바) → `Insert template` 을 **모바일 툴바에 고정**

> `axis`/`slug` 는 모바일에서 비워둬도 된다. Step 3의 intake 스크립트가 비어 있으면 `inbox/_unsorted/` 로 보내고, PC에서 확정한다.

### Step 2-6. Gemini → Obsidian 캡처 플로우 (실사용 동선)
**A안 — 공유 시트 (가장 빠름, 2탭)**
1. Gemini 앱에서 딥리서치 답변 → 답변 하단 **공유/내보내기 → 공유 → Obsidian**
2. Obsidian 공유 대상 선택창 → vault `KM-Inbox`, 폴더 `inbox`, **Create new note**
3. 제목을 `아이디어-<종목/주제>-260919` 형식으로 수정 → 저장
4. 노트 맨 위에서 `Insert template` → `idea` 실행 → frontmatter 삽입 → `ticker`/`slug` 만 채움

**B안 — 긴 리포트일 때**
1. Gemini 딥리서치 → **Google Docs로 내보내기** → Docs 앱에서 전체 복사
2. Obsidian `KM-Inbox` → 새 노트 → 템플릿 삽입 → `## Gemini 딥리서치 원문` 아래 붙여넣기

**파일명 규칙(BINDING)**: `<종류>-<주제>-<YYMMDD>.md`
- 예: `idea-한화에어로스페이스-260919.md`, `research-방산수출사이클-260919.md`
- 스키마의 ctime 기준 LOG 정렬과 맞물리므로 날짜 6자리를 **반드시** 붙인다.

### Step 2-7. 동기화 확인 (수용 테스트)
1. 폰에서 `inbox/test-260919.md` 생성 → 30초 내 PC `C:\KM-Sync\inbox\test-260919.md` 등장 확인
2. PC `C:\KM-Sync\digest\hello.md` 생성 → 폰 Obsidian `digest/hello.md` 등장 확인
3. 확인 후 테스트 파일 삭제

---

## 5. Phase 3 — 인박스 인테이크 (PC측 수문)

### Step 3-1. `scripts/inbox_intake.py` (신규, 이번 플랜의 구현 대상)
역할:
1. `C:\KM-Sync\inbox\*.md` 스캔 (`_tpl/`, `_attachments/` 제외)
2. frontmatter 검증·보정
   - 없으면 생성 / `tags` 는 **블록 시퀀스**로 강제(CLAUDE.md Rule 8)
   - 숫자로 시작하는 태그 금지 규칙 적용
3. 라우팅
   - `axis: asset` + `ticker` 있음 → `10_RAW/assets/<CATEGORY>-<ticker>/`
   - `axis: project` + `slug` 있음 → `10_RAW/projects/<slug>/`
   - 판별 불가 → `10_RAW/inbox/_unsorted/`
4. **이동(move)** — 복사 아님. `C:\KM-Sync\inbox` 는 항상 비워져 다음 캡처를 받는다
5. 원본 mtime 보존, 충돌 시 `-2` suffix
6. `LOG/synthesis 기록 없음` — 기록은 `/ingest` 단계 책임 (CLAUDE.md LOG-02 준수)

> Rule 9(INGEST ORDER) 충족: wiki 생성 전에 raw가 `10_RAW/` 에 먼저 안착한다.
> Rule 1 충돌 없음: 기존 raw 편집이 아니라 **신규 파일 이관**이라 허용 범위.

### Step 3-2. 드라이런
```bat
python scripts\inbox_intake.py --dry-run
```
라우팅 결과만 출력. 실제 이동 없음.

---

## 6. Phase 4 — 매일 자동화 (n8n, .cmd 폴백)

### Step 4-1. 파이프라인 정의
```
07:30  inbox_intake.py        (수문 열기: KM-Sync → 10_RAW)
07:31  claude -p "/projects"  (archive 이관/분류)
07:35  claude -p "/ingest"    (wiki 생성·갱신 + LOG per-file)
07:45  daily_brief.py         (DAILY.md 갱신, --skip-if-today 금지)
07:46  mobile_digest.py       (DAILY.md + 신규 wiki 요약 → C:\KM-Sync\digest)
```

### Step 4-2. n8n 노드 구성
| 노드 | 타입 | 설정 |
|---|---|---|
| 1 | Schedule Trigger | Cron `30 7 * * 1-5` |
| 2 | Execute Command | `python C:\...\20-Obsidian\scripts\inbox_intake.py` |
| 3 | IF | exit code 0 아니면 5번으로 |
| 4 | Execute Command | `claude -p "/projects 실행 후 이어서 /ingest 실행"` (cwd = vault root) |
| 5 | Execute Command | `python ...\scripts\daily_brief.py` |
| 6 | Execute Command | `python ...\scripts\mobile_digest.py` |
| 7 | Error Trigger | 실패 시 알림(메일/텔레그램) |

주의사항:
- n8n을 **Docker**로 돌리면 Windows 호스트 경로와 `claude` CLI에 접근 못 한다 → 반드시 **n8n Desktop 또는 `npx n8n` 을 호스트에서** 실행
- `claude -p` 는 비대화 모드. 현행 `morning_gate.py` 의 대화형 실행과 **택일** — 둘 다 켜면 하루 두 번 ingest가 돌아 LOG가 중복된다
- 실행 계정은 OneDrive 폴더 접근 권한이 있는 **로그인 사용자 계정**이어야 함

### Step 4-3. 폴백 — Windows 작업 스케줄러
n8n이 회사 PC에 못 올라가거나 불안정하면 즉시 폴백:
1. `automation/km-daily.cmd` (Phase 4에서 작성) — 위 5단계를 순차 실행 + `logs/km-daily-YYYYMMDD.log` 기록
2. `schtasks` 등록:
```bat
schtasks /Create /TN "KM-Daily" /TR "\"C:\Users\Pulmuone\OneDrive - 풀무원\20-Obsidian\automation\km-daily.cmd\"" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 07:30 /RL LIMITED /F
```
3. 부팅 직후 놓친 경우 대비: 작업 속성 → **"예약 시간이 지난 후 가능한 한 빨리 작업 시작"** 체크

> 판단 기준: **폴백이 기본, n8n이 업그레이드**. 먼저 .cmd로 돌려 안정화한 뒤 n8n으로 옮기는 순서를 권장한다. n8n의 실익은 실패 알림/조건 분기/향후 외부 API 연동이다.

---

## 7. Phase 5 — 역방향(PC → 모바일) 읽기 동기화

### Step 5-1. `scripts/mobile_digest.py` (신규)
`C:\KM-Sync\digest\` 에 다음만 내보낸다 (**회사 민감정보 필터 필수**):
- `DAILY.md` 전문
- 최근 7일 내 갱신된 `20_WIKI/assets/<ID>/synthesis.md` 의 **마지막 Δ 블록**
- `20_WIKI/assets/assets-INDEX.md` 의 watchlist 표

제외 규칙(BINDING): `10_RAW/` 전체, `projects/` 축 중 회사 업무 슬러그(인사위·PMO·HR 등)는 **allowlist 방식**으로만 내보낸다. 즉 "빼는 목록"이 아니라 "내보낼 슬러그 목록"을 명시한다.

### Step 5-2. 모바일에서 읽기
Obsidian `KM-Inbox` vault → `digest/` 폴더. Receive Only라 수정해도 PC로 안 넘어간다(수정분은 다음 동기화에 덮어써짐 — 의도된 동작).

---

## 8. 가드레일 (사고 예방)

| 위험 | 방지책 |
|---|---|
| OneDrive ↔ Syncthing 이중 동기화 충돌 | 착지 폴더를 OneDrive **밖**(`C:\KM-Sync`)에 고정. 어떤 경우에도 OneDrive 하위를 Syncthing 폴더로 등록하지 않는다 |
| 회사 자료 사외 유출 | Syncthing은 P2P(외부 서버 미보관). digest는 **allowlist** 내보내기. GitHub는 인프라 전용 유지(.gitignore 변경 금지) |
| 모바일 노트 frontmatter 깨짐 | intake 스크립트가 Rule 5/8 강제 보정. 태그는 블록 시퀀스, 숫자 시작 금지 |
| LOG 중복/오염 | intake·digest 스크립트는 LOG를 **쓰지 않는다**. 기록은 `/ingest` 단일 지점 (LOG-02) |
| ingest 이중 실행 | `morning_gate.py` 마커와 n8n 중 **하나만** 활성. 전환 시 다른 쪽 비활성화 |
| 폰 배터리 최적화로 동기화 지연 | Syncthing-Fork 배터리 제한 해제(Step 2-1) |
| 파일명 날짜 누락 → LOG 정렬 깨짐 | 파일명 `-YYMMDD` 강제, intake가 없으면 ctime으로 자동 부여 |

## 9. 실행 체크리스트

- [ ] P1-1 `C:\KM-Sync\{inbox,digest}` 생성
- [ ] P1-2 SyncTrayzor 설치 + GUI 인증 설정
- [ ] P1-3 폴더 2개 등록(`km-inbox` S&R / `km-digest` Send Only)
- [ ] P1-4 방화벽 22000 TCP/UDP, 21027 UDP 허용
- [ ] P2-1 Syncthing-Fork 설치 + 배터리 제한 해제
- [ ] P2-2 QR 페어링 → 양쪽 Connected
- [ ] P2-3 폴더 2개 수락(digest는 Receive Only)
- [ ] P2-4 Obsidian 모바일 `KM-Inbox` vault 오픈 + 기본 폴더 `inbox`
- [ ] P2-5 `_tpl/idea.md` 템플릿 + 툴바 버튼
- [ ] P2-6 Gemini 공유 → Obsidian 1회 성공
- [ ] P2-7 양방향 수용 테스트 통과
- [ ] P3-1 `scripts/inbox_intake.py` 구현
- [ ] P3-2 `--dry-run` 검증
- [ ] P4-3 `automation/km-daily.cmd` + schtasks 등록 (**먼저**)
- [ ] P4-2 n8n 전환 (안정화 후)
- [ ] P5-1 `scripts/mobile_digest.py` 구현 + allowlist 확정
- [ ] 1주 운영 후 `sync-conflict` 파일 0건 확인

## 10. 롤백

| 단계 | 롤백 |
|---|---|
| Syncthing 문제 | 폴더 Pause → PC는 기존 OneDrive 단독 운영으로 즉시 복귀(변경 없음) |
| intake 오라우팅 | `C:\KM-Sync\_trash` 로 이동한 원본 7일 보관 → 수동 복구 |
| n8n 불안정 | 작업 스케줄러 `.cmd` 로 폴백 (P4-3이 항상 살아있게 유지) |
| 전체 폐기 | `C:\KM-Sync` 삭제 + 폰 앱 제거. vault 자체는 손대지 않았으므로 원상복구 |

## 11. 다음 세션 작업 (구현 대상)

1. `scripts/inbox_intake.py` — 라우팅 + frontmatter 정규화 + `--dry-run`
2. `scripts/mobile_digest.py` — allowlist 기반 내보내기
3. `automation/km-daily.cmd` + `schtasks` 등록 스크립트
4. `automation/n8n/km-daily.workflow.json` — 임포트용 워크플로우
5. `scripts/test_inbox_intake.py` — 라우팅 테이블 TDD

## Raw Coords Read
none (사용자 원문 노트 직접 수신)
