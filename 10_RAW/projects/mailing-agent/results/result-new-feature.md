# result-new-feature
> 작성일: 2026-04-15
> 기준 계획: `plan-new-feature-v0.5.md`

---

## 전체 구현 현황

| Item | 내용 | 상태 |
|------|------|------|
| Item 3 | /draft 질문 단순화 | 완료 |
| Item 2 | 최초 사용자 등록 | 완료 |
| Item 1+4 | 아웃룩 임시보관함 저장 + 표 자동 변환 | 구현 완료 / 테스트 보류 |

---

## Item 3: /draft 질문 단순화 — 완료

### 변경 파일
- `.claude/commands/draft.md`
- `.claude/agents/draft-writer.md`

### 주요 변경 내용

**`draft.md`**
- Step 1 (메일 유형 수동 선택 6개) 완전 제거
- 입력 필드 6개 → 3개로 간소화
  ```
  목적 및 수신자: (예: 담당님께 Claude Team Plan 구매 사전 결재)
  주요 내용 및 기한: (핵심 사실/수치, 기한이 있다면 함께 기재)
  참고 메일: (data/emails/파일명.eml - 없으면 'n')
  ```
- `(모르는 항목은 Enter로 건너뛰기)` 문구 삭제 → `(없으면 'n' 입력)` 으로 교체
- 전체 Step 수: 5단계 → 3단계

**`draft-writer.md`**
- **0단계 추가**: `python src/database.py get-user` 로 활성 사용자 동적 조회
- **1단계 추가**: 키워드 기반 메일 유형 자동 추론 (6개 유형 매핑)
- 초안 상단에 `[추론 메일 유형: {유형명}]` 자동 출력
- 맺음말 하드코딩 `김지형 드림` → `{users.name} 드림` 동적 처리
- 첨부/파일/붙임 키워드 감지 시 검토 포인트 자동 추가
- 필드 값 'n' 입력 시 null 처리 규칙 명시
- **6단계 추가**: Outlook 임시보관함 저장 옵션 (y/n)

### 테스트 결과 (claude -p)
- draft.md 3개 필드, 'n' 입력, Step 3개 구조: **PASS**
- draft-writer.md 5개 항목 (사용자 조회, 유형 추론, 동적 이름, 첨부 감지, Outlook 저장): **5/5 PASS**

---

## Item 2: 최초 사용자 등록 — 완료

### 변경 파일
- `src/database.py`
- `CLAUDE.md`
- `.claude/agents/draft-writer.md`
- `.claude/agents/db-manager.md`

### 주요 변경 내용

**`src/database.py`**
- `users` 테이블 스키마 추가:
  ```sql
  CREATE TABLE IF NOT EXISTS users (
      id, created_at, name, team, email, is_active
  );
  ```
- `register_user(name, team, email)` 함수 추가 — 중복 시 기존 id 반환
- `get_active_user()` 함수 추가 — is_active=1 최신 사용자 반환
- CLI 서브커맨드 추가:
  - `python src/database.py register-user --name --team --email`
  - `python src/database.py get-user`

**`CLAUDE.md`**
- `사용자(김지형, 인사혁신팀)` 하드코딩 제거 → DB 동적 참조로 교체
- 맺음말 `감사합니다. 김지형 드림` → `감사합니다. {users.name} 드림`

**`db-manager.md`**
- `get-user`, `register-user` 쿼리 패턴 및 응답 예시 추가

### 현재 등록된 사용자
```json
{"id": 1, "name": "김지형", "team": "인사혁신팀", "email": "gian.kim@pulmuone.com"}
```

### 테스트 결과
- DB 사용자 조회: **PASS**
- 중복 등록 방어 (동일 id 반환): **PASS**

---

## Item 1+4: 아웃룩 임시보관함 저장 + 표 자동 변환 — 구현 완료 / 실환경 테스트 보류

### 신규 파일
- `src/outlook_bridge.py`

### 설치된 패키지
- `pywin32==311`
- `markdown==3.10.2`

### 주요 기능

**마크다운 → HTML 자동 변환 (표 포함)**
```python
_md_to_html(md_text)
# markdown 패키지로 변환, 표 border-collapse 스타일 포함
# Outlook 호환 HTML 출력
```

**Outlook 임시보관함 저장**
```python
save_to_drafts(subject, body_file, to_addr)
# COM Automation (win32com) 방식
# mail.HTMLBody = html → 표 서식 그대로 저장
```

**CLI 사용법**
```bash
# 연결 확인
python src/outlook_bridge.py check

# 저장
python src/outlook_bridge.py save-draft \
  --subject "메일 제목" \
  --body-file "data/drafts/파일명.md" \
  --to "수신자@도메인"
```

### 테스트 결과
- 마크다운 → HTML 변환 (표, UTF-8, 한글 깨짐): **5/5 PASS**
- Outlook 미실행 시 오류 처리 (False 반환 + 메시지): **PASS**
- Outlook 연결 None 처리: **PASS**

### 실환경 테스트 보류 사유
현재 `olk.exe` (New Outlook) 실행 중.
COM Automation은 `OUTLOOK.EXE` (Classic Outlook) 전용으로 New Outlook에서는 작동하지 않음.

**해결 방향 (미결):**

| 방법 | 조건 | 코드 변경 |
|------|------|----------|
| Classic Outlook으로 전환 | Outlook 토글로 전환 가능 여부 확인 필요 | 불필요 |
| Microsoft Graph API 방식 전환 | Azure AD 앱 등록 또는 IT 부서 협조 | 필요 |

---

## 미결 사항

| # | 내용 | 비고 |
|---|------|------|
| 1 | Item 1+4 실환경 테스트 | Classic Outlook 전환 또는 Graph API 방향 결정 후 진행 |
| 2 | New Outlook 대응 방안 확정 | IT 정책 확인 필요 |
