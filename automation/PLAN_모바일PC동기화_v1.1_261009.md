---
type: plan
project: knowledge-management
date: 2026-10-09
status: active
source: self
topic: 옵시디언 모바일↔PC 동기화 — 다중 PC(집 PC + 노트북) 확장
version: v1.1
supersedes: "[[PLAN_모바일PC동기화_v1.0_260919]]"
tags:
  - knowledge-management
  - sync
  - automation
  - multi-device
---

# Plan — 모바일↔PC 동기화 v1.1 (집 PC + 휴대용 노트북)

> v1.0 은 "PC 1대" 를 전제로 했다. v1.1 은 **집 PC + 노트북 + Android** 3기기로 확장하는 Δ 만 다룬다.
> v1.0 의 Android 세팅(§4), 인박스 구조, 가드레일은 그대로 유효하다.

## Key Changes (Δ vs v1.0)
- PC↔노트북 vault 동기화는 **OneDrive 가 이미 해결** — 추가 도구 불필요. 새 문제는 "동기화"가 아니라 **"누가 쓰나(single writer)"**
- 자동화 실행 주체를 고정 PC 가 아니라 **Hub lease(임대권)** 로 결정 — 켜져 있는 쪽이 자동 승계
- Syncthing 토폴로지 2기기 → 3기기 메시 (폰·집PC·노트북)
- `.git` 이 OneDrive 안에 있는 위험을 명시하고 완화책 도입
- v1.0 §2.3 의 "기기 3대 이상 → Obsidian Sync 재검토" 조건은 **너무 거칠었다** → "모바일 기기 2대 이상" 으로 정정 (아래 §6)

---

## 1. 새로 생긴 제약

| # | 제약 | 결과 |
|---|---|---|
| D1 | 두 PC 모두 같은 `OneDrive - 풀무원` 계정 → vault 가 이미 양쪽에 동기화됨 | PC↔PC 는 별도 동기화 도구를 **추가하면 안 됨**(이중 동기화) |
| D2 | 두 PC 가 같은 날 `LOG.md`·`INDEX.md` 에 append | OneDrive **충돌 사본** 발생 (`LOG-DESKTOP-ABC123.md` 같은 파일) |
| D3 | `.git` 이 vault 루트 = OneDrive 안. 그리고 `/projects`·`/assets` 스킬은 `git mv`·`git add` 를 **자동 실행** | 두 PC 에서 git 쓰기가 섞이면 `.git/index` 충돌·저장소 손상 위험 |
| D4 | 노트북은 이동 중 수시로 꺼짐. 출장 중엔 집 PC 가 꺼져 있을 수 있음 | "항상 집 PC 가 hub" 로 고정하면 출장 중 ingest 가 멈춤 |
| D5 | `scripts/.morning_last_run` 마커가 OneDrive 로 공유됨 | 지금도 우연히 "오늘 누군가 돌렸다" 플래그로 동작 — 단, **어느 기기가** 돌렸는지 모름 |
| D6 | `.claude/settings.json` SessionStart 훅이 `C:\Users\Pulmuone\...` 절대경로 | 노트북의 Windows 사용자 폴더명이 다르면 훅이 조용히 실패 |
| D7 | OneDrive "파일 온디맨드" 기본값 = 클라우드 전용 자리표시자 | 기내·지하철 등 오프라인에서 노트북이 raw 를 못 읽음 |

## 2. 원칙 — "파일은 모두가, 자동 쓰기는 한 대만"

| 기기 | 상시 역할 | Hub 일 때 추가 역할 |
|---|---|---|
| Android | 캡처(inbox 쓰기), digest 읽기 | — |
| 집 PC | Obsidian 편집, Syncthing 중계 | intake · `/projects` · `/ingest` · daily_brief · digest · git 쓰기 |
| 노트북 | Obsidian 편집, Syncthing 중계 | (동일) |

**Hub 는 동시에 1대만.** Hub 가 아닌 PC 는 자동화를 전부 skip 하고, Syncthing 중계와 사람이 하는 편집만 한다.

### 2.1 Hub lease (임대권) 메커니즘
파일: `scripts/.hub_lease` (gitignore 대상, OneDrive 로 공유)
```json
{"host": "HOME-PC", "acquired": "2026-10-09T07:30:12", "expires": "2026-10-09T10:30:12"}
```

| 규칙 | 값 |
|---|---|
| TTL | **3시간** |
| Heartbeat | Hub 인 PC 는 **매시간** lease 갱신(`hub.py heartbeat`) |
| 획득 조건 | lease 없음 / 만료됨 / 내 것 |
| 다른 기기가 유효 보유 | 자동화 전부 **skip** (exit 0, "standby" 로그) |
| 강제 인계 | `python scripts\hub.py claim --force` (사람이 직접) |
| 반납 | `python scripts\hub.py release` (출장 전 집 PC 에서) |

**동작 시나리오**

| 상황 | 결과 |
|---|---|
| 평일, 둘 다 켜짐 | 먼저 lease 를 잡은 쪽(보통 집 PC 07:30)이 hub. 노트북 08:30 실행은 standby |
| 출장, 집 PC 꺼짐 | 집 PC heartbeat 끊김 → 최대 3시간 후 노트북의 다음 실행(로그온/정시)에서 **자동 승계** |
| 출장 복귀, 집 PC 다시 켬 | 노트북 lease 가 살아 있으면 집 PC 는 standby. 노트북이 3시간 이상 꺼지면 집 PC 가 자동 회수 — **깜빡임(flapping) 없음** |
| 출장 직전 확실히 넘기고 싶음 | 집 PC 에서 `hub.py release` → 노트북 즉시 승계 |
| 노트북에서 대화형 `/ingest` 를 지금 당장 하고 싶음 | `hub.py claim --force` 후 실행. 집 PC 는 다음 heartbeat 에서 standby 로 전환 |

**스케줄 엇갈리기(BINDING)**: 집 PC 07:30, 노트북 08:30. OneDrive 가 lease 파일을 전파할 시간(보통 수 초~수 분)을 확보해 동시 획득을 막는다.

### 2.2 남는 위험과 감지
lease 는 OneDrive 전파에 의존하므로 **OneDrive 가 일시중지된 노트북**(데이터 절약 모드 등)에서는 split-brain 이 생길 수 있다. 이건 막는 게 아니라 **감지**한다:
- `daily_brief.py` lint 에 **OneDrive 충돌 사본 탐지** 추가: vault 전체(+`.git/`)에서 `-<COMPUTERNAME>` 접미 파일 패턴 검색 → DAILY.md 상단 경고
- `hub.py claim` 은 OneDrive 클라이언트가 실행 중이 아니면 거부(`OneDrive.exe` 프로세스 확인)

## 3. Git — OneDrive 안의 `.git` 다루기

솔직한 평가: **OneDrive 로 `.git` 을 두 PC 가 공유하는 것은 원래 권장되지 않는다.** lease 로 "동시에 쓰지 않음" 은 보장하지만, 완전한 해결은 아니다. 단계적으로 줄인다.

| 단계 | 조치 | 효과 |
|---|---|---|
| 즉시 | 두 PC 모두 `setx GIT_OPTIONAL_LOCKS 0` | Claude Code 가 자동으로 부르는 `git status` 가 `.git/index` 를 갱신하지 않음 → non-hub 의 읽기 동작이 `.git` 을 건드리지 않음 |
| 즉시 | git **쓰기**(commit / pull / merge / checkout / `git mv` / `git add`)는 **hub 에서만** | lease 와 같은 규칙으로 단일 작성자 보장 |
| 즉시 | `hub.py claim` 시 `.git` 아래 충돌 사본이 있으면 claim 거부 | 손상된 상태에서 쓰기 시작 방지 |
| v1.2 | `/projects`·`/assets` 스킬의 `git mv` → 일반 이동으로 교체 | `10_RAW/` 가 `.gitignore` 대상이라 git 추적 이득이 없음. 바꾸면 **일상 자동화가 git 을 아예 안 건드림** → git 은 인프라 수정할 때만 사용 |

> v1.2 까지 가면 D3 위험이 "인프라 코드 수정하는 날 1대에서만 git" 수준으로 줄어든다. 이게 근본 해결이다.

## 4. Syncthing — 3기기 메시

```
        Android (inbox: S&R / digest: Receive Only)
          ╱                     ╲
   집 PC ─────────────────────── 노트북
 (inbox: S&R, digest: S&R)   (inbox: S&R, digest: S&R)
 C:\KM-Sync\  ← 두 PC 모두 OneDrive 바깥
```

- 폰은 **켜져 있는 PC 아무 데로나** 보낸다. 둘 다 켜져 있으면 둘 다 받는다
- intake 는 **hub 만** 실행 → hub 가 파일을 vault 로 옮기면(=KM-Sync 에서 삭제) 그 삭제가 Syncthing 으로 폰·다른 PC 에 전파 → 중복 이관 없음
- digest 는 hub 만 생성. v1.0 에서 PC 를 Send Only 로 했던 것을 **두 PC 모두 Send & Receive** 로 변경(hub 가 바뀔 수 있으므로). 폰은 계속 Receive Only
- **이동 중 팁**: 폰 핫스팟에 노트북을 붙이면 같은 LAN 이 되어 릴레이 없이 직결된다(가장 빠르고 회사망 차단 영향 없음)
- 노트북은 `Global Discovery` + `Relaying` **ON** (호텔·카페 와이파이 대비)

## 5. 노트북 세팅 — 스텝별 (약 40분)

### Step N-1. OneDrive
1. 같은 `OneDrive - 풀무원` 계정 로그인, 동기화 완료 대기
2. 탐색기에서 `20-Obsidian` 폴더 우클릭 → **"항상 이 장치에 유지"** (D7 해결 — 오프라인에서도 raw 읽기 가능)
3. 집 PC 도 동일하게 "항상 이 장치에 유지" 확인

### Step N-2. 경로 확인 (D6)
```bat
echo %USERPROFILE%
```
- `C:\Users\Pulmuone` 이면 → 그대로 OK
- 다르면 → SessionStart 훅을 경로 비의존형으로 바꿔야 함:
  ```json
  "command": "python \"$CLAUDE_PROJECT_DIR/scripts/daily_brief.py\""
  ```
  **집 PC 에서 먼저 바꿔 Claude Code 시작 시 DAILY 출력이 나오는지 확인 후** 커밋(이 파일도 OneDrive 로 노트북에 전달됨). 확인 전에는 바꾸지 않는다.
- ⚠ `.claude/settings.local.json` 도 vault 안 → OneDrive 로 **공유된다**. 기기별 설정은 반드시 `%USERPROFILE%\.claude\settings.json`(사용자 레벨)에 둘 것

### Step N-3. 런타임
1. Python(집 PC 와 같은 메이저 버전), Claude Code CLI 설치 → `claude` 로그인
2. `setx GIT_OPTIONAL_LOCKS 0` (§3) → 터미널 재시작
3. vault 루트에서 `python scripts\daily_brief.py --no-lint` 가 돌아가는지 확인

### Step N-4. Syncthing
1. SyncTrayzor 설치, `C:\KM-Sync\{inbox,digest,_trash}` 생성 (OneDrive **밖**)
2. 장치 추가: 폰 ↔ 노트북, 집 PC ↔ 노트북 (QR 또는 장치 ID)
   - 편의: 집 PC 를 **Introducer** 로 지정하면 집 PC 가 아는 장치(폰)가 노트북에 자동 소개됨
3. `km-inbox`, `km-digest` 공유 수락 → 경로 `C:\KM-Sync\inbox`, `C:\KM-Sync\digest`, 둘 다 Send & Receive
4. 설정 → Connections: Global Discovery ON, Relaying ON
5. 폰 Syncthing-Fork 에서 노트북 장치 승인 + 두 폴더에 노트북 공유 체크

### Step N-5. 스케줄러 (hub gate 경유)
| 작업 | 트리거 | 명령 |
|---|---|---|
| `KM-Daily` | 평일 08:30 **+ 로그온 시** (노트북은 로그온 트리거가 핵심) | `automation\km-daily.cmd` (첫 줄에서 `hub.py gate` — hub 아니면 즉시 종료) |
| `KM-Heartbeat` | 매 1시간 | `python scripts\hub.py heartbeat` (hub 일 때만 갱신, 아니면 no-op) |

두 작업 모두 "예약 시간이 지난 후 가능한 한 빨리 시작" 체크. 집 PC 는 `KM-Daily` 07:30.

### Step N-6. `morning-routine.cmd` 동작 변경
`morning_gate.py` 가 마커 대신 lease 를 본다:
- 내가 hub(또는 획득 성공) + 오늘 미실행 → 기존대로 `/projects → /ingest` 자동 실행
- 다른 기기가 hub → `claude` 만 열고 첫 줄에 `[STANDBY] hub=HOME-PC (만료 09:30). 쓰기 작업 전 hub.py claim` 안내

### Step N-7. 수용 테스트
1. 폰에서 `inbox/test-261009.md` 생성 → 두 PC `C:\KM-Sync\inbox` 에 모두 도착
2. 집 PC 에서 `hub.py status` = HOME-PC 확인 → `km-daily.cmd` 수동 실행 → 파일이 vault 로 이동 + 폰·노트북의 inbox 에서도 사라짐
3. 노트북에서 `km-daily.cmd` 실행 → `standby` 로 즉시 종료되는지
4. 집 PC `hub.py release` → 노트북 `km-daily.cmd` → 승계 확인
5. 다음 날 vault 전체에서 충돌 사본 0건 확인

## 6. Obsidian Sync 재검토 (v1.0 §2.3 정정)

v1.0 은 "기기 3대 이상" 이면 유료 전환을 재검토한다고 했다. 노트북이 추가되어 조건이 형식상 충족됐지만, **결론은 그대로 Syncthing 인박스 분리형 유지**다.
- 늘어난 기기는 **PC** 이고, PC↔PC 는 OneDrive 가 이미 담당한다
- Obsidian Sync 를 넣으면 두 PC 에서 OneDrive 와 이중 동기화가 생겨 오히려 D2 가 악화된다(쓰려면 vault 를 OneDrive 밖으로 옮겨야 함)

**정정된 전환 조건**: ① 모바일 기기 2대 이상(태블릿 추가 등) ② 모바일에서 `20_WIKI/` 편집이 주 1회 이상 ③ 회사 보안SW 가 Syncthing 차단 — 중 하나.

## 7. 구현 대상 (v1.0 §11 에 추가)

| # | 파일 | 내용 |
|---|---|---|
| 1 | `scripts/hub.py` (신규) | `status / claim [--force] / release / heartbeat / gate` · OneDrive 실행 확인 · `.git` 충돌 사본 시 claim 거부 |
| 2 | `scripts/morning_gate.py` | 마커 → lease 기반 판정, standby 안내 |
| 3 | `scripts/daily_brief.py` | OneDrive 충돌 사본 탐지 lint |
| 4 | `automation/km-daily.cmd` | 첫 단계 `hub.py gate` |
| 5 | `.gitignore` | `scripts/.hub_lease` 추가 |
| 6 | `scripts/test_hub.py` | 획득/만료/강제/동시 시나리오 TDD |
| 7 | (v1.2) `.claude/projects.md`, `.claude/assets.md` | `git mv` → 일반 이동 |

## 8. 실행 체크리스트 (노트북 추가분)
- [ ] N-1 OneDrive 로그인 + 두 PC 모두 "항상 이 장치에 유지"
- [ ] N-2 `%USERPROFILE%` 확인 (다르면 훅 경로 수정 — 집 PC 에서 검증 후)
- [ ] N-3 Python · Claude Code · `GIT_OPTIONAL_LOCKS=0`
- [ ] N-4 Syncthing 3기기 메시 + 노트북 Relay ON
- [ ] N-5 `KM-Daily`(08:30+로그온) · `KM-Heartbeat`(매시)
- [ ] N-6 morning_gate lease 연동
- [ ] N-7 수용 테스트 5항목 통과
- [ ] 1주 운영 후 충돌 사본 0건

## Raw Coords Read
none
