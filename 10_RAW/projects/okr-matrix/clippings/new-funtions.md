# 1.D&D fix v2.0
직전 task가 아니라 kr 내에서만 이동하도록 수정 된것으로 보인다
task 내에서도 자유롭게 이동되도록 수정
task 내 이동이 어떤 의미인지 명확하게 이해가 되지 않을경우 반드시 사용자에게 물어본 후 진행한다.

  ## 참고 파일
- 다음 파일을 참고하여 유사하게 개발을 진행한다. "C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\OKR\fix-plan\v1.12" 경로의 'phase-2-kr-movement.md'
- 신규 개발의 코드는 새로운 파일을 생성하여 관리한다.(이후 쉬운 유지관리를 위해서)

# 2.날짜 입력 기능 개선(급하진 않은 기능)
현재 수정 버튼을 눌러야 입력되는 날짜를 버튼 없이도 바로 입력 가능되는 내용을 검토한다

# 3. 현재 프론트앤드 완료 탭에 있는 ROW ROW DATA들을 DB에 저장 하고 화면에서는 clear하는 기능을 구현한다
- 해당 기능을 위해 웹브라우저 로컬스토리지에 저장된 데이터를 로컬 DB에 저장하고 화면에서는 clear하는 기능을 구현한다
 SQLite DB 추가

 ## 에이전트 추가
| 에이전트 | 역할 |
 | db-manager | SQLite DB CRUD 관리 | 

 ### agent.md feature
name: db-manager
description: mailing-agent SQLite DB(data/emails.db)의 CRUD를 담당하는 에이전트. 다른 에이전트가 DB 작업이 필요할 때 호출.
tools: Read, Write, Bash
model: sonnet
---

# DB Manager Agent

## 역할
`data/emails.db` SQLite 데이터베이스의 모든 읽기/쓰기 작업을 담당한다.

## DB 위치
```
data/emails.db
```
DB가 존재하지 않으면 `python src/database.py init` 실행을 사용자에게 안내한다.

## 허용 작업

### 자동 실행 (사용자 확인 불필요)
- SELECT 쿼리 (조회만)
- DB 파일 존재 여부 확인

### 사용자 확인 후 실행
- INSERT (새 레코드 추가)
- UPDATE (기존 레코드 수정)
- DELETE (레코드 삭제)


### 활성 사용자 조회 (draft-writer용)
```bash
python src/database.py get-user
```
반환 예시:
```json
{"id": 1, "name": "김지형", "team": "인사혁신팀", "email": "gian.kim@pulmuone.com"}
```
결과가 `null`이면 사용자에게 등록 안내:
```
등록된 사용자가 없습니다. 아래 명령어로 먼저 등록해주세요:
python src/database.py register-user --name 이름 --team 팀명
```

### 사용자 등록 (최초 1회, 이미 있으면 기존 id 반환)
```bash
python src/database.py register-user --name 김지형 --team 인사혁신팀 --email gian.kim@pulmuone.com
```

## 오류 처리
- DB 파일 없음: `python src/database.py init` 안내
- 테이블 없음: `python src/database.py init` 안내
- 쿼리 실패: 오류 내용과 함께 사용자에게 보고