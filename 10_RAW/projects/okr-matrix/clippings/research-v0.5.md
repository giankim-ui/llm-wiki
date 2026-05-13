# 1.목표
'meeting_dashboard' 내 헤더 인 라인에 신규 탭을 만들어(AX혁신 제언 우측) okr-martix-app을 탭으로 넣고자 해

## 'meeting_dashboard' 위치
"C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\Smartmeeting - 문서\10_HR_IN_Meeting_DB\meeting_dashboard.html"

## 'okr-martix-app' 정보
"C:\Users\Pulmuone\OneDrive - 풀무원\!Claude\OKR\claud.md"



#2.추가 기능

## 1.외부 DB 구축
1. 두 웹앱의 로컬 DB를 통합
2. 통합 스키마 토대 supabase에 db를 갖추기. (나는 supabase를 전혀 사용해 본적이 없어. 비개발자로 이에 맞춰 step별 상세한 안내가 필요해.)


## 2.TO-DO내 업무를 팀장이 OKR로 배분하기
- 사용자 추가기능(신설)하여 팀장 - 팀원A/B/C(추가가능) 의 구조를 만들기
- 팀장이 TO-DO 업무를 OKR로 배분할 수 있도록 함(업무는 2명 또는 3명이 함께 작업해야 할수도 있음)
- 팀장은 TASK 또는 initiative 묶음으로 업무를 줄 수 있음
- DB 연동으로 실시간 협업 성과 확인이 가능


## 3. OKRMatrix 내 반영
 이에 따라 OKRMatrix에서는 Task 세션 밑 현재 '진행중' '완료' 토글 을 수정하여 
-작업자 묶음 {'팀장' 팀원A/B/C(추가가능) }
-업무별 묶음 {TASK별 업무 담당자가 표기되게}



## 4. TASK 별 코맨트 기능
- 각 태스크 별로 팀장-팀원, 팀원-팀원 간 피드백을 줄 수 있고 해당 내역은 DB에 저장 하여 이후 360피드백에 활용/