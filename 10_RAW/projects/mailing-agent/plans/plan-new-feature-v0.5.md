# plan-new-feature-v0.5
> 기준 문서: `research-new-feature-v1.2.md`
> 작성일: 2026-04-15
> 수정: Item 4 표 기능을 Item 1에 통합 (저장 시 자동 변환)

---

## 전체 의존성 그래프

```
[병렬 착수 가능]
  Item 3 ─── 독립 (draft.md, draft-writer.md 수정만)
  Item 2 ─── 독립 (database.py → CLAUDE.md → draft-writer.md)

[Item 3, 2 완료 후]
  Item 1+4 Phase 1 → Phase 2 → Phase 3
  (표 변환 기능을 임시보관함 저장에 통합)
```

## 개발 우선순위

| 순위 | Item | 핵심 작업 | 선행 조건 |
|------|------|----------|----------|
| 1 | Item 3 | draft.md 수정 | 없음 |
| 2 | Item 2 | DB 테이블 추가 | 없음 |
| 3 | **Item 1+4** | outlook_bridge.py 신규 생성 (표 변환 포함) | pywin32, markdown 패키지 설치 |

> Item 4는 별도 작업 없이 Item 1 구현 시 함께 완료됨.

---

## Item 3: /draft 질문 단순화 (1순위)

### 수정 파일
| 파일 | 경로 |
|------|------|
| draft.md | `.claude/commands/draft.md` |
| draft-writer.md | `.claude/agents/draft-writer.md` |

### Step 3-1: 메일 유형 자동 추론 (Step 1 제거)

**`draft.md`**
- "Step 1: 메일 유형 확인" 블록 전체 삭제
- 이후 Step 번호 전체 재정렬 (기존 Step 2~5 → Step 1~4)

**`draft-writer.md`**
- 유형 추론 규칙 추가 (키워드 매핑):

  | 키워드 | 추론 유형 |
  |--------|----------|
  | 결재, 승인, 품의 | 결재 요청 |
  | 보고, 공유, 알려드립니다 | 업무 보고 |
  | 협조, 지원, 요청 | 협조 요청 |
  | 문의, 여쭤, 확인 | 자료/정보 문의 |
  | 감사, 수고 | 감사/인사 |
  | (해당 없음) | 기타 |

- 초안 본문 최상단에 의무 출력:
  ```
  [추론 메일 유형: {유형명}]
  ```
  불명확 시: `[추론 메일 유형: 기타 - 확인 권장]`

### Step 3-2: 입력 필드 6개 → 3개 간소화

**`draft.md`** Step 2 블록을 아래로 교체:
```
다음 정보를 입력해주세요. (해당 없는 항목은 'n' 입력)

목적 및 수신자: (예: 담당님께 Claude Team Plan 구매 사전 결재)
주요 내용 및 기한: (핵심 사실/수치를 입력, 기한이 있다면 함께 기재)
참고 메일: (data/emails/파일명.eml - 없으면 'n')
```

삭제 필드: `참조`, `첨부파일`, `기한/일정` (독립 필드), `수신자` (독립 필드)

**`draft-writer.md`** 에 첨부파일 감지 보존 규칙 추가:
> 사용자 입력 텍스트에 '첨부', '파일', '붙임' 키워드가 있으면
> 검토 포인트에 "첨부 파일 확인 필요" 항목을 자동 추가한다.

### Step 3-3: 안내 문구 변경

**`draft.md`**
- `(모르는 항목은 Enter로 건너뛰기)` → 삭제
- 각 선택 항목 뒤에 `(없으면 'n' 입력)` 추가

**`draft-writer.md`**
- 'n' 처리 규칙 추가: "필드 값이 'n'이면 해당 항목 null 처리 후 다음 질문으로 진행"

### 테스트 기준
- `/draft` 실행 시 유형 선택 프롬프트 미출력, 3개 필드만 노출 확인
- "결재" 포함 입력 → 초안 상단 `[추론 메일 유형: 결재 요청]` 출력 확인
- 주요 내용에 "첨부" 포함 시 검토 포인트에 첨부파일 항목 자동 추가 확인
- 참고 메일에 'n' 입력 시 참고 메일 없이 정상 생성 확인

---

## Item 2: 최초 사용자 등록 (2순위)

### 수정 파일
| 파일 | 경로 | 변경 성격 |
|------|------|----------|
| database.py | `src/database.py` | users 테이블 + 함수 추가 |
| CLAUDE.md | `CLAUDE.md` | 하드코딩 제거 |
| draft-writer.md | `.claude/agents/draft-writer.md` | 동적 이름 조회 추가 |
| db-manager.md | `.claude/agents/db-manager.md` | users 쿼리 패턴 추가 |

### Step 2-1: users 테이블 스키마 추가

**`src/database.py`** 의 `SCHEMA_SQL`에 추가:
```sql
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    name       TEXT    NOT NULL,
    team       TEXT,
    email      TEXT,
    is_active  INTEGER NOT NULL DEFAULT 1
);
```

### Step 2-2: 함수 및 CLI 서브커맨드 추가

**`src/database.py`**에 추가:

| 함수/커맨드 | 동작 |
|------------|------|
| `register_user(name, team, email)` | name+team 중복 시 기존 id 반환, 없으면 INSERT |
| `get_active_user()` | is_active=1 최신 레코드 반환, 없으면 None |
| CLI: `register-user --name --team --email` | 등록 실행 |
| CLI: `get-user` | JSON 출력 |

### Step 2-3: CLAUDE.md 하드코딩 제거

| 위치 | 기존 | 변경 |
|------|------|------|
| 프로젝트 목적 2행 | `사용자(김지형, 인사혁신팀) 맞춤형` | `사용자 맞춤형 (활성 사용자: data/emails.db > users 테이블)` |
| 맺음말 규칙 | `감사합니다. 김지형 드림` | `감사합니다. {users.name} 드림` |

### Step 2-4: draft-writer.md 동적 이름 조회

1단계 컨텍스트 로딩 최상단에 추가:
```
0. 활성 사용자 조회:
   python src/database.py get-user
   → 반환값의 name을 맺음말 및 서명에 사용
   → 결과 없을 시 안내:
     "등록된 사용자가 없습니다.
      python src/database.py register-user --name 이름 --team 팀명"
```

### 테스트 기준
- `python src/database.py init` → users 테이블 생성 확인
  (`sqlite3 data/emails.db ".schema users"`)
- `register-user --name 김지형 --team 인사혁신팀` 실행 → id 반환
- 동일 인자 재실행 → 기존 id 반환 (중복 삽입 없음)
- `get-user` 실행 → JSON 반환
- `/draft` 초안 맺음말이 DB 이름으로 출력되는지 확인
- CLAUDE.md 내 "김지형" 하드코딩 잔재 없음 확인

---

## Item 1+4: 아웃룩 임시보관함 자동 저장 + 표 자동 변환 통합 (3순위)

### 통합 개요

**사용자 경험 (변경 후):**
```
1. /draft 로 초안 생성 (표 포함 가능)
2. "Outlook 임시보관함에 저장할까요? (y/n)"
3. y 입력
4. → 마크다운 전체가 HTML로 자동 변환 (표 포함)
5. → Outlook 임시보관함에 저장 완료
6. Outlook 열면 표가 반듯하게 들어간 메일 초안이 대기 중
```

별도 명령어 불필요. 저장 시 표 변환이 자동으로 함께 처리됨.

### 파일
| 파일 | 경로 | 변경 성격 |
|------|------|----------|
| outlook_bridge.py | `src/outlook_bridge.py` | **신규 생성** |
| draft-writer.md | `.claude/agents/draft-writer.md` | Outlook 저장 옵션 추가 |
| settings.local.json | `.claude/settings.local.json` | Bash 권한 추가 |

### Phase 1: 환경 구성 확인

필요 패키지 확인:
```bash
python -c "import win32com.client; print('pywin32 OK')"
python -c "import markdown; print('markdown OK')"
```
없을 시:
```bash
pip install pywin32 markdown
python Scripts/pywin32_postinstall.py -install
```

### Phase 2: outlook_bridge.py 구현

**핵심 로직 — 마크다운 → HTML 변환 후 HTMLBody로 저장:**
```python
import markdown, win32com.client

def save_to_drafts(subject, md_body, to_addr):
    # 1. 마크다운 전체(표 포함)를 HTML로 변환
    html_body = markdown.markdown(md_body, extensions=['tables', 'nl2br'])

    # 2. Outlook COM 연결
    outlook = win32com.client.GetActiveObject("Outlook.Application")

    # 3. 임시보관함에 저장
    mail = outlook.CreateItem(0)        # olMailItem
    mail.Subject = subject
    mail.HTMLBody = html_body           # 표 서식 유지
    mail.To = to_addr
    mail.Save()                         # Drafts 폴더 자동 저장
```

Outlook 미실행 시 오류 처리:
```python
# GetActiveObject 실패 → "Outlook이 실행되어 있지 않습니다." 출력 후 종료
```

CLI 인터페이스:
```bash
python src/outlook_bridge.py save-draft \
  --subject "제목" \
  --body-file "data/drafts/파일명.md" \
  --to "수신자@도메인"
```

### Phase 3: draft-writer.md 연동

초안 출력(마지막 단계) 이후에 추가:
```
[Outlook 저장 옵션]
"Outlook 임시보관함에 바로 저장할까요? (y/n)"

y 입력 시:
  python src/outlook_bridge.py save-draft \
    --subject "{추천 제목}" \
    --body-file "{저장된 초안 경로}" \
    --to "{수신자 이메일 또는 공란}"

완료 시: "Outlook 임시보관함에 저장했습니다. 표 서식이 자동 적용되었습니다."
실패 시: "Outlook 연결 실패. 초안 파일을 직접 참고하세요: {경로}"
```

**`.claude/settings.local.json`** allow 배열에 추가:
```json
"Bash(python src/outlook_bridge.py *)"
```

### 테스트 기준
- Outlook 실행 중 `save-draft` → 임시보관함에 항목 생성 확인
- 저장된 메일을 Outlook에서 열었을 때 **표가 반듯하게 보이는지** 확인
- 표 없는 일반 초안도 정상 저장 확인 (표 없으면 그냥 텍스트로 저장)
- Outlook 미실행 상태에서 실행 → "Outlook이 실행되어 있지 않습니다" 메시지 확인 (크래시 없음)
- 한글 포함 표 저장 시 깨짐 없음 확인

---

## 파일별 변경 범위 요약

| 파일 | 관련 Item | 변경 성격 |
|------|----------|----------|
| `.claude/commands/draft.md` | 3 | Step 1 삭제, 필드 3개로 축소, 문구 교체 |
| `.claude/agents/draft-writer.md` | 3, 2, 1+4 | 유형 추론 / 동적 이름 / Outlook 저장(표 포함) |
| `src/database.py` | 2 | users 테이블, register/get 함수, CLI 서브커맨드 |
| `CLAUDE.md` | 2 | 하드코딩 개인정보 → 동적 참조로 교체 |
| `.claude/agents/db-manager.md` | 2 | users 쿼리 패턴 추가 |
| `src/outlook_bridge.py` | 1+4 | **신규 생성** (임시보관함 저장 + 표 자동 변환 통합) |
| `.claude/settings.local.json` | 1+4 | outlook_bridge.py Bash 권한 추가 |
