# Security Guide — API Key & Git 보안 관리

**작성일**: 2026-05-03  
**작업 디렉토리**: `C:\Users\nayut\!claudeProject`

---

## 발견된 보안 이슈

| 파일 | 노출된 키 | git 추적 여부 | 조치 |
|------|-----------|--------------|------|
| `.claude/settings.local.json` | `OPENDART_API_KEY` (권한 문자열 내 평문) | ✅ 추적 중 → 제거 완료 | `git rm --cached` + `.gitignore` |
| `S-anlyz/.claude/settings.local.json` | `SEC_API_KEY` | 미추적 (안전) | `.gitignore`로 보호 |
| `S-anlyz-kr/.claude/settings.local.json` | `DART_API_KEY` | 미추적 (안전) | `.gitignore`로 보호 |
| `S-anlyz-jp/.claude/settings.local.json` | `EDINET_API_KEY` | 미추적 (안전) | `.gitignore`로 보호 |

---

## 적용된 조치

### 1. git 추적 제거
```bash
git rm --cached .claude/settings.local.json
```
- 파일 자체는 로컬에 유지
- 이후 커밋부터 git이 이 파일을 무시

### 2. .gitignore 생성
**경로**: `C:\Users\nayut\!claudeProject\.gitignore`

```gitignore
# API keys & local settings
**/.claude/settings.local.json

# Node
node_modules/
dist/
.cache/

# Python
__pycache__/
*.pyc

# OS
.DS_Store
Thumbs.db

# Env files
.env
.env.local
*.env
```

### 3. 커밋
```
[master f945a2d] add .gitignore, untrack settings.local.json
 2 files changed, 20 insertions(+), 31 deletions(-)
 delete mode 100644 .claude/settings.local.json
 create mode 100644 .gitignore
```

---

## 위험도 평가

| 상황 | 위험도 |
|------|--------|
| 로컬 커밋만 존재 (GitHub 미업로드) | ✅ 낮음 |
| GitHub 등 원격에 push된 경우 | ❌ 높음 — 히스토리 조회 가능 |

**현재 상태**: 로컬 전용 커밋. 외부 노출 없음.

---

## GitHub Push 전 체크리스트

나중에 이 저장소를 GitHub에 올릴 경우:

- [ ] 과거 커밋에 키가 남아 있으므로 **BFG Repo Cleaner** 또는 **git filter-repo**로 히스토리 정리
- [ ] 또는 노출된 키를 모두 **revoke & regenerate** (가장 간단)
- [ ] push 후 GitHub Secret Scanning 경고 확인

---

## BFG Repo Cleaner 사용법 (필요 시)

### 사전 요건
- Java 설치 필요
- [공식 다운로드](https://rtyley.github.io/bfg-repo-cleaner/) — `bfg-x.x.x.jar`

### 방법 1 — 특정 파일을 히스토리에서 완전 삭제
```bash
git clone --mirror <repo-url> repo.git
java -jar bfg.jar --delete-files settings.local.json repo.git
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

### 방법 2 — 특정 문자열(키 값)을 `***REMOVED***`로 치환
```bash
# 삭제할 키 값 목록 파일 생성
echo "43eaec615dab2ef2ddfcd3eea3212f62544050e9" > passwords.txt
echo "c4bee0d5ceba586113c5efd5834595365762dbdc18e79948b66be763034b9941" >> passwords.txt

java -jar bfg.jar --replace-text passwords.txt repo.git
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

### 주의사항
- bare clone(`--mirror`)에서 실행
- `git push --force` 후 팀원 전원 re-clone 필요
- GitHub의 경우 branch protection 규칙 일시 해제 필요할 수 있음

---

## 재발 방지 원칙

1. **API 키는 `settings.local.json`의 `env` 섹션에만 저장** — 권한 문자열(permissions.allow)에 키 값 직접 삽입 금지
2. **`.gitignore` 먼저** — 새 프로젝트 시작 시 `settings.local.json` 패턴 즉시 등록
3. **키 로테이션 주기** — 실수로 노출 의심 시 즉시 해당 서비스에서 키 재발급
