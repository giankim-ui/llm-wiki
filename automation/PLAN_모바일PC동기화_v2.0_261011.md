---
type: plan
project: knowledge-management
date: 2026-10-11
status: active
source: self
topic: 3기기(집 PC · 노트북 · Android) 통합 동기화 — 로컬 + Google Drive 구조
version: v2.0
supersedes: "[[PLAN_모바일PC동기화_v1.1_261009]]"
tags:
  - knowledge-management
  - sync
  - automation
  - multi-device
---

# Plan — 3기기 통합 동기화 v2.0

## Key Changes (Δ vs v1.1)
- 전제 정정: 세 기기 모두 **OneDrive 미사용**, 로컬 + Google Drive 구조. v1.1 의 "PC끼리는 OneDrive가 맞춰 준다" 는 전제가 무너짐
- PC끼리 실시간 동기화 = **Syncthing** 으로 통일 (Android 인박스용으로 이미 설치하는 같은 도구)
- Google Drive = 실시간 동기화에서 빼고 **매일 일방향 백업** 전용으로 역할 변경
- `.git` 은 동기화 제외 → **집 PC 한 대만 git** 보유. 일상 자동화에서 git 제거가 선행조건이 됨
- Hub lease 는 유지하되, 승계 전 안전확인을 "OneDrive 실행 여부" → **Syncthing REST API 로 동기화 완료 확인** 으로 교체
- 두 PC 의 vault 경로를 **`C:\Vault\20-Obsidian` 으로 통일** + 훅·명령의 절대경로를 상대경로로 교체(이번 커밋에 반영)

**가정**: `.claude/settings.json` 등에 있던 `C:\Users\Pulmuone\OneDrive - 풀무원\...` 경로는 이 3기기 체계와 무관한 이전 경로로 본다. 회사 PC 도 같은 vault 를 써야 한다면 이 플랜에 4번째 기기로 추가 검토가 필요하다.

---

## 1. 왜 Google Drive 대신 Syncthing 으로 PC끼리 동기화하나

| 항목 | Google Drive for desktop | Syncthing |
|---|---|---|
| 일부 폴더·파일 제외 | **불가** — `.git`, `workspace.json` 까지 전부 동기화 | `.stignore` 로 가능 |
| `.git` 안전성 | 동기화 중 git 저장소 손상 사례가 많음 | 제외하면 문제 자체가 없음 |
| "동기화 끝났나" 를 스크립트로 확인 | **방법 없음** | REST API (`/rest/db/status`) 로 확인 가능 → hub 승계 전 안전확인에 필수 |
| 충돌 사본 이름 | 일정하지 않음 | `*.sync-conflict-YYYYMMDD-HHMMSS-<기기>.*` 고정 → 자동 탐지 쉬움 |
| 실수 복구 | 웹에서 파일별 버전 기록 | 로컬 버전 보관 (`.stversions`, 30일) |
| 상대 기기가 꺼져 있을 때 | 클라우드 경유로 나중에 받음 | **두 기기가 동시에 켜져야 전달** |
| 클라우드 백업 | 기본 제공 | 없음 |
| Android 에서 vault 폴더로 열기 | 불가 (Drive 앱이 로컬 폴더를 안 만듦) | 가능 (Syncthing-Fork) |

**결론**: 매일 LLM 이 `LOG.md`·`INDEX.md`·`synthesis.md` 를 쓰는 vault 에는 **제외 패턴 + 동기화 완료 확인 + 고정된 충돌 이름** 이 필요하다. 셋 다 Syncthing 에만 있다. Syncthing 의 약점 두 가지(동시 온라인 필요, 클라우드 백업 없음)는 각각 hub 규칙(§4)과 Google Drive 백업(§5)으로 메운다.

> 동시 온라인 약점이 실제로 의미하는 것: 출장 중 노트북에서 쓴 내용은 귀가해서 집 PC 와 노트북이 둘 다 켜졌을 때 넘어간다. 출장 중에는 노트북이 hub 라서 쓰기 충돌은 없다. 내용이 사라지지 않고 늦게 도착할 뿐이다.

## 2. 최종 구조

```
                    Android (Syncthing-Fork)
          km-inbox (보내기·받기) / km-digest (받기만)
              ╱                              ╲
   집 PC ══════════ km-vault (보내기·받기) ══════════ 노트북
   C:\Vault\20-Obsidian                     C:\Vault\20-Obsidian   ← 경로 동일
   C:\KM-Sync\{inbox,digest}               C:\KM-Sync\{inbox,digest}
   .git 있음 (git 전용 PC)                  .git 없음
        │
        └─(hub 가) 매일 23:00 vault zip → Google Drive\KM-Backup\  (일방향, 30개 보관)
```

| Folder ID | 참여 기기 | PC 경로 | 폰 경로 | 폴더 타입 | 버전 보관 |
|---|---|---|---|---|---|
| `km-vault` | 집 PC, 노트북 | `C:\Vault\20-Obsidian` | (참여 안 함) | 양쪽 Send & Receive | Staggered 30일 |
| `km-inbox` | 3기기 | `C:\KM-Sync\inbox` | `Documents/KM-Inbox/inbox` | 전부 Send & Receive | Trash Can 7일 |
| `km-digest` | 3기기 | `C:\KM-Sync\digest` | `Documents/KM-Inbox/digest` | PC: Send & Receive / 폰: Receive Only | 없음 |

**폴더 중첩 금지 (BINDING)**: `C:\KM-Sync` 는 `C:\Vault` 안에 두지 않는다. Syncthing 폴더가 다른 Syncthing 폴더 안에 있으면 같은 파일을 두 폴더가 동시에 다룬다.

**경로 통일 이유**: 작업 스케줄러 명령, n8n 노드, 문서 속 경로가 두 PC 에서 똑같아진다. 사용자 폴더 이름(`C:\Users\<이름>`)이 PC 마다 달라도 상관없다.

## 3. 동기화 제외 (`.stglobalignore`)

레포 루트에 `.stglobalignore` 를 커밋했다(이번 커밋). 이 파일은 vault 와 함께 동기화되므로 제외 규칙이 두 PC 에서 항상 같다. 각 PC 에서 할 일은 vault 루트에 `.stignore` 파일을 만들고 아래 한 줄만 넣는 것이다(`.stignore` 자체는 동기화되지 않는다):

```
#include .stglobalignore
```

제외 대상: `.git`, `.obsidian/workspace*.json`, `.obsidian/cache`, `.trash`, `.claude/settings.local.json`, 파이썬 캐시.
**제외하면 안 되는 것**: `scripts/.hub_lease`, `scripts/.morning_last_run` — 두 PC 가 공유해야 하는 상태 파일이다.

## 4. 역할 규칙

### 4.1 Git — 집 PC 전용
- `.git` 은 동기화에서 빠지므로 **노트북에는 git 저장소가 없다**. 정상이다
- 인프라(`scripts/`, `.claude/`, `CLAUDE.md`, `automation/`)를 바꿀 때는 집 PC 에서 `git pull`/커밋 → Syncthing 이 노트북에 파일을 넘긴다
- **선행조건(필수)**: `/projects`·`/assets` 스킬의 `git mv`·`git add` 를 일반 이동으로 바꾼다. 안 바꾸면 노트북이 hub 일 때 아침 자동화가 git 명령에서 실패한다. (별도 작업 카드 "Fix /ingest auto-scan relying on gitignored 10_RAW" 가 이 범위를 포함)

### 4.2 Hub lease — v1.1 유지, 안전확인만 교체
"자동 쓰기는 한 대만" 원칙과 `scripts/.hub_lease`(만료 3시간, 매시간 갱신, 출장 시 자동 승계, `claim --force`/`release`)는 v1.1 §2.1 그대로다.

바뀌는 부분 — **승계(claim) 전 안전확인**:

| 상황 | 판정 |
|---|---|
| 상대 PC 연결됨 (`GET /rest/system/connections`) | `km-vault` 가 `idle` 이고 받을 파일 0개(`GET /rest/db/status?folder=km-vault` → `state=="idle"`, `needTotalItems==0`)가 될 때까지 최대 10분 대기 → 그 뒤 lease 판단 |
| 상대 PC 미연결 | Syncthing 시작 후 **10분 유예** 뒤 claim (그동안 연결 안 되면 꺼져 있다고 판단) |
| `.sync-conflict-` 파일이 `LOG.md`·`INDEX.md`·`scripts/.hub_lease` 에 있음 | claim 거부 → DAILY.md 상단 경고 |

10분 유예가 필요한 이유: 출장에서 돌아와 집 PC 를 켜면, 노트북이 갖고 있던 최신 lease 가 아직 안 넘어온 상태에서 집 PC 가 자기 옛 lease(만료됨)만 보고 hub 를 잡을 수 있다. 연결·동기화 완료를 확인하면 이 경쟁이 없어진다.

API 키: Syncthing 화면 → 설정 → API 키를 복사해 PC 마다 `setx SYNCTHING_API_KEY <키>` 로 저장한다. **vault 안에 저장하지 않는다.**

### 4.3 남는 위험
집 PC 와 노트북이 둘 다 켜져 있는데 서로 연결이 안 되는 경우(다른 네트워크 + 릴레이 차단)에는 둘 다 hub 가 될 수 있다. 막지 못하고 **감지**한다: `daily_brief.py` 가 `*.sync-conflict-*` 파일을 찾아 DAILY.md 상단에 경고한다. Syncthing 버전 보관(30일)으로 복구한다.

## 5. Google Drive — 백업 전용

- vault 는 Google Drive 동기화 폴더 **밖**(`C:\Vault`)에 둔다
- hub 가 매일 23:00 `automation\km-backup.cmd` 실행:
  ```bat
  tar -a -c -f "%GDRIVE_BACKUP%\vault-%DATE6%.zip" --exclude=.stversions -C C:\Vault 20-Obsidian
  ```
  - `GDRIVE_BACKUP` = PC 별 Google Drive 경로 (예: `G:\내 드라이브\KM-Backup`), `setx` 로 저장
  - 30개 넘으면 오래된 것부터 삭제
  - 집 PC 가 hub 일 때 만든 zip 에는 `.git` 도 들어간다
- 출장 중에는 노트북이 hub → 노트북이 백업한다. 그래서 **노트북에도 Google Drive for desktop 이 있어야 한다**
- 복구: zip 을 받아 `C:\Vault\20-Obsidian_restore` 에 풀고 필요한 파일만 옮긴다 (Syncthing 이 켜진 상태에서 폴더째 덮어쓰지 않는다)

## 6. 이관 절차 — 기존 vault → `C:\Vault\20-Obsidian` (약 30분)

> 순서가 중요하다. 한 PC 의 최신본을 기준으로 삼고 다른 PC 는 **빈 폴더로 받는다**. 두 PC 의 사본을 동시에 Syncthing 에 넣으면 충돌 사본이 쏟아진다.

### M-1. 기준 PC 정하기
최신 vault 를 가진 PC(보통 집 PC)를 기준으로 정한다. 노트북에만 있는 최근 수정분이 있으면 먼저 기준 PC 로 옮긴다.

### M-2. 기준 PC: 복사
1. Obsidian, Claude Code 종료
2. 현재 vault 가 Google Drive 안에 있다면 Drive 동기화 완료(트레이 아이콘 "최신 상태") 확인
3. vault 를 `C:\Vault\20-Obsidian` 으로 **복사** (이동하지 않는다)
4. 기존 위치 폴더는 이름을 `20-Obsidian_OLD-261011` 로 바꿔 2주 보관 → 이상 없으면 삭제
5. `C:\Vault\20-Obsidian` 에서 `git status` → 정상이면 OK

### M-3. 기준 PC: Obsidian·Claude Code 확인
1. Obsidian → 다른 보관소 열기 → `C:\Vault\20-Obsidian`
2. 그 폴더에서 `claude` 실행 → 시작할 때 DAILY 브리프가 출력되는지 확인 (SessionStart 훅이 상대경로로 바뀌었으므로 **vault 루트에서 실행해야 한다**. `morning-routine.cmd` 는 이미 루트로 이동 후 실행하므로 그대로 동작)

### M-4. 기준 PC: Syncthing
1. Syncthing(Windows 는 SyncTrayzor 권장) 설치
2. `C:\Vault\20-Obsidian\.stignore` 생성 → 내용 `#include .stglobalignore`
3. 폴더 추가: ID `km-vault`, 경로 `C:\Vault\20-Obsidian`, 버전 관리 = Staggered, 최대 보관 30일
4. `C:\KM-Sync\{inbox,digest,_trash}` 생성 → `km-inbox`, `km-digest` 폴더 추가 (v1.0 §3 과 같음)

### M-5. 노트북: 빈 폴더로 받기
1. `C:\Vault\20-Obsidian` 을 **빈 폴더로** 생성. 노트북에 옛 vault 사본이 있으면 다른 이름으로 치워 둔다
2. 같은 폴더에 `.stignore` 먼저 생성(`#include .stglobalignore`)
3. Syncthing 설치 → 집 PC 와 장치 연결(QR 또는 장치 ID)
4. `km-vault` 공유 수락 → 경로 `C:\Vault\20-Obsidian`, **폴더 타입 = Receive Only** 로 받는다
5. 초기 동기화가 100% 되면 폴더 타입을 **Send & Receive** 로 바꾼다
   (첫 동기화 동안 노트북이 실수로 내보내는 일을 막는 안전장치)
6. `km-inbox`, `km-digest` 도 수락 → `C:\KM-Sync\inbox`, `C:\KM-Sync\digest`
7. 설정 → 연결: 전역 검색 ON, 릴레이 ON (출장지 와이파이 대비)

### M-6. 노트북: 실행 환경
1. Python(집 PC 와 같은 버전대), Claude Code 설치 → `claude` 로그인
2. `setx SYNCTHING_API_KEY <노트북 Syncthing 키>`, `setx GDRIVE_BACKUP "<노트북의 Google Drive 경로>\KM-Backup"`
3. Google Drive for desktop 로그인 (백업 대상 폴더만 쓰면 됨)
4. `C:\Vault\20-Obsidian` 에서 `python scripts\daily_brief.py --no-lint` 실행 확인
5. Obsidian → 보관소 열기 → `C:\Vault\20-Obsidian`

### M-7. Android
v1.0 §4 그대로. 추가로 할 일 하나: 폰 Syncthing-Fork 에서 **노트북 장치를 추가**하고 `km-inbox`·`km-digest` 를 노트북과도 공유한다. 집 PC 를 Introducer 로 지정하면 자동으로 소개된다.
이동 중 팁: 노트북을 폰 핫스팟에 연결하면 같은 네트워크가 되어 폰↔노트북이 바로 연결된다.

### M-8. 스케줄러 (두 PC 같은 명령, 시간만 다름)
| 작업 | 집 PC | 노트북 | 명령 |
|---|---|---|---|
| `KM-Daily` | 평일 07:30 | 평일 08:30 **+ 로그온 시** | `C:\Vault\20-Obsidian\automation\km-daily.cmd` |
| `KM-Heartbeat` | 매시간 | 매시간 | `python C:\Vault\20-Obsidian\scripts\hub.py heartbeat` |
| `KM-Backup` | 매일 23:00 | 매일 23:00 | `C:\Vault\20-Obsidian\automation\km-backup.cmd` |

세 작업 모두 첫 단계에서 `hub.py gate` 를 거친다 — hub 가 아닌 PC 에서는 바로 끝난다. "예약 시간을 놓치면 가능한 빨리 실행" 을 체크한다.

## 7. 수용 테스트
1. 집 PC 에서 `test-261011.md` 를 vault 에 생성 → 노트북에 도착 / 노트북에서 삭제 → 집 PC 에서도 삭제
2. 노트북 vault 에 `.git` 이 **없는지** 확인
3. 폰 `inbox/test-261011.md` → 두 PC `C:\KM-Sync\inbox` 에 도착 → hub 의 `km-daily.cmd` 가 vault 로 옮기고 → 폰·다른 PC inbox 에서 사라짐
4. 노트북 `km-daily.cmd` → `standby` 로 바로 끝나는지
5. 집 PC `hub.py release` → 노트북 `km-daily.cmd` → hub 승계
6. 집 PC Syncthing 중지 → 노트북에서 lease 만료 후 자동 승계 → 집 PC Syncthing 재시작 → 10분 유예 안에 standby 로 판정되는지
7. Google Drive `KM-Backup` 에 zip 생성 확인
8. 1주 운영 후 vault 전체에서 `*.sync-conflict-*` 0건

## 8. 구현 대상 (v1.1 §7 갱신)

| # | 파일 | 상태 |
|---|---|---|
| 1 | `.stglobalignore` | **이번 커밋** |
| 2 | `.claude/settings.json`, `.claude/commands/morning.md`, `CLAUDE.md` 절대경로 → 상대경로 | **이번 커밋** |
| 3 | `.gitignore` 에 `scripts/.hub_lease`, `.stversions/`, `.stignore` 추가 | **이번 커밋** |
| 4 | `.claude/projects.md`, `.claude/assets.md`, `.claude/commands/ingest.md` 에서 git 의존 제거 | 작업 카드 (선행조건) |
| 5 | `scripts/hub.py` — lease + Syncthing REST 안전확인 + 10분 유예 | 다음 |
| 6 | `scripts/morning_gate.py` — lease 기반 판정, standby 안내 | 다음 |
| 7 | `scripts/daily_brief.py` — `*.sync-conflict-*` 탐지 | 다음 |
| 8 | `automation/km-daily.cmd`, `automation/km-backup.cmd` | 다음 |
| 9 | `scripts/inbox_intake.py`, `scripts/mobile_digest.py` (v1.0 §5·§7) | 다음 |
| 10 | `scripts/test_hub.py` | 다음 |

## 9. Google Drive 로 PC끼리 동기화를 계속하고 싶다면 (비권장)
가능은 하지만 세 가지를 감수해야 한다.
- `.git` 을 vault 밖으로 빼야 한다 (Drive 는 제외 기능이 없다). 인프라는 vault 밖 별도 clone 에서 관리하고 vault 로 복사하는 절차가 생긴다
- 동기화 완료를 확인할 방법이 없어 자동 승계를 못 한다 → **집 PC 고정 hub** + 출장 시 노트북에서 수동 `claim --force`
- 충돌 사본 이름이 일정하지 않아 자동 탐지가 어렵다

## Raw Coords Read
none
