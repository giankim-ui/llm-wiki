# 통합 프로젝트 리서치 고도화: Meeting Dashboard × OKR Matrix
> 작성일: 2026-04-20 | 대상 파일: `interg-m-o/plan/research.md`

---


### 비개발자용 Supabase 설정 단계별 가이드

#### Phase A: 계정 및 프로젝트 생성
```
1. 브라우저에서 https://supabase.com 접속
2. 우상단 "Start your project" 클릭
3. GitHub 계정으로 가입 (없으면 이메일 가입)
4. 로그인 후 "New project" 클릭
5. 설정값 입력:
   - Organization: Personal (기본값 그대로)
   - Project name: pulmuone-hr (또는 원하는 이름)
   - Database Password: 복잡한 비밀번호 → 반드시 메모장에 저장
   - Region: Northeast Asia (ap-northeast-1 / Tokyo) 선택
   - Pricing: Free tier
6. "Create new project" 클릭 → 1~2분 대기 (초록색 'Active' 표시 확인)
```

#### Phase B: DB 테이블 생성
```
7. 왼쪽 사이드바 아이콘 중 "SQL Editor" (코드 아이콘) 클릭
8. 화면 중앙 에디터에 위의 스키마 SQL 전체 붙여넣기
9. 우상단 "Run" (▶) 버튼 클릭
10. 하단에 "Success. No rows returned" 메시지 확인
11. 왼쪽 사이드바 "Table Editor"에서 7개 테이블 생성됐는지 확인
```

#### Phase C: API 키 발급
```
12. 왼쪽 사이드바 맨 아래 "Settings" (톱니바퀴) 클릭
13. "API" 메뉴 클릭
14. 아래 두 가지 값 복사해서 메모장에 저장:
    - Project URL: https://xxxxxxxxxxxx.supabase.co
    - anon public key: eyJhbGciOiJIUzI1NiIsInR5cCI6Ikp...
    (서비스 롤 키는 저장하지 말 것 — 보안 위험)
```

#### Phase D: 앱에 Supabase 연결 (각 앱별)
```html
<!-- meeting_dashboard.html <head>에 추가 (CDN) -->
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script>
  const SUPABASE_URL = 'https://xxxx.supabase.co';  // Phase C에서 복사한 값
  const SUPABASE_KEY = 'eyJhbGciOiJI...';           // Phase C에서 복사한 값
  const sb = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
</script>
```
> ⚠️ CDN 추가이므로 사용자 승인 필요 (Smartmeeting CLAUDE.md 규칙)

### localStorage → Supabase 마이그레이션 전략

사용자 결정: **기존 데이터 이전 (migrate)**

```
마이그레이션 절차:
1. 브라우저 개발자도구 Console에서 localStorage 데이터 추출
   → JSON.stringify(localStorage) 실행 → 결과를 텍스트 파일로 저장

2. 데이터 구조 파악 후 스키마에 맞게 매핑
   (실제 localStorage 키 이름은 아래 '추가 파일 읽기 필요' 항목 참고)

3. Supabase SQL Editor에서 직접 INSERT 또는
   마이그레이션 스크립트(JS) 실행

4. 이전 완료 후 localStorage 는 삭제하지 않고 보존
   (앱이 Supabase에서 읽기 성공하면 localStorage 무시하도록 코드 분기)
```
