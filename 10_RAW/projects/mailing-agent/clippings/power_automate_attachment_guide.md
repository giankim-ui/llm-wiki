# Power Automate로 Outlook 첨부파일을 SharePoint 폴더에 자동 저장하기

## 1. 목표
Outlook 메일이 도착하면 첨부파일을 Power Automate로 받아서, SharePoint 문서 라이브러리의 특정 폴더에 자동 저장한다.

### 대상 폴더
- SharePoint 사이트: `https://pmoo365.sharepoint.com/sites/Smartmeeting`
- 문서 라이브러리: `Shared Documents`
- 저장 폴더: `!Claude/Smartmeeting - 문서/10_HR_IN_Meeting_DB/10_Raw`

> 참고: 로컬 경로처럼 보이는 `C:\Users\Pulmuone\OneDrive - 풀무원\...` 경로는 실제로는 OneDrive/SharePoint 동기화 결과로 보이는 경로이며, Power Automate에서는 SharePoint에 직접 저장하는 방식이 적절하다.

---

## 2. 전체 권장 구조
1. Outlook 메일 수신
2. 첨부파일이 있는 메일만 처리
3. 첨부파일 내용을 가져오기
4. SharePoint에 파일 저장
5. 필요 시 메일을 읽음 처리하거나 처리 완료 폴더로 이동

---

## 3. 기본 흐름 구성

### 3-1. 트리거
- **When a new email arrives (V3)**

권장 설정:
- **Folder**: Inbox 또는 원하는 하위 폴더
- **Only with Attachments**: Yes
- **Include Attachments**: Yes
- 필요 시 **From**, **Subject Filter** 추가

---

### 3-2. 첨부파일 반복
- **Apply to each**
- 대상: 트리거의 **Attachments**

메일에 첨부파일이 여러 개일 수 있으므로 반복문을 사용한다.

---

### 3-3. 첨부파일 내용 가져오기
- **Get attachment (V2)** 또는 **Get attachment content (V2)**

입력값:
- **Message Id**: 트리거의 `Message Id`
- **Attachment Id**: 현재 반복 중인 첨부파일의 `Attachment Id`

#### 중요한 개념
- **Message Id** = 메일 1건의 ID
- **Attachment Id** = 해당 메일 안의 첨부파일 ID

---

## 4. `Message Id`는 어디서 확인하나?
`Get attachment (V2)`의 **Message Id**는 직접 찾는 값이 아니라, **트리거인 `When a new email arrives (V3)`의 동적 콘텐츠**에서 가져온다.

### 확인 방법
1. `Get attachment (V2)` 추가
2. **Message Id** 입력칸 클릭
3. 동적 콘텐츠에서 **Message Id** 선택

### 안 보일 때 확인할 점
- 트리거가 `When a new email arrives (V3)`인지 확인
- 동적 콘텐츠 검색창에서 `message` 또는 `id` 검색
- `Apply to each` 안에서도 Message Id는 트리거 값 사용

---

## 5. SharePoint에 파일 저장
- **SharePoint → Create file**

### 입력 예시
- **Site Address**: `https://pmoo365.sharepoint.com/sites/Smartmeeting`
- **Folder Path**: `/Shared Documents/!Claude/Smartmeeting - 문서/10_HR_IN_Meeting_DB/10_Raw`
- **File Name**: 아래의 파일명 규칙 사용
- **File Content**: `Get attachment content` 결과

---

## 6. 파일명 규칙

### 6-1. 기본 형식
원하는 파일명 형식:

```text
yyyymmdd_##_인사혁신팀_정기미팅.txt
```

예:

```text
20260401_01_인사혁신팀_정기미팅.txt
```

---

### 6-2. 숫자 변수가 이미 있을 때 파일명 expression
`varSeq`가 `1`, `2`, `3` 같은 숫자라고 가정하면:

```powerautomate
concat(
  formatDateTime(convertTimeZone(utcNow(),'UTC','Korea Standard Time'),'yyyyMMdd'),
  '_',
  padLeft(string(variables('varSeq')), 2, '0'),
  '_인사혁신팀_정기미팅.txt'
)
```

이 expression은 다음처럼 동작한다.
- `varSeq = 1` → `20260401_01_인사혁신팀_정기미팅.txt`
- `varSeq = 2` → `20260401_02_인사혁신팀_정기미팅.txt`

---

## 7. `varSeq` 흐름 추가
`varSeq`는 같은 날짜에 생성된 기존 파일 개수를 기준으로 자동 계산한다.

### 전체 흐름
1. 오늘 날짜 문자열 만들기
2. SharePoint 폴더의 기존 파일 목록 가져오기
3. 오늘 날짜로 시작하는 파일만 필터링
4. 개수 + 1을 `varSeq`로 설정
5. `Create file`에서 파일명에 반영

---

### 7-1. 오늘 날짜 문자열 만들기
**Compose** 액션 추가

#### 액션 이름 예시
- `Compose_Today`

#### Expression
```powerautomate
formatDateTime(convertTimeZone(utcNow(),'UTC','Korea Standard Time'),'yyyyMMdd')
```

예시 결과:
- `20260401`
- `20260402`

---

### 7-2. 기존 파일 목록 가져오기
**SharePoint → Get files (properties only)** 추가

#### 설정 예시
- **Site Address**: `https://pmoo365.sharepoint.com/sites/Smartmeeting`
- **Library Name**: `Documents` 또는 `Shared Documents`
- **Folder**: `/Shared Documents/!Claude/Smartmeeting - 문서/10_HR_IN_Meeting_DB/10_Raw`

---

### 7-3. 오늘 날짜 파일만 필터링
**Filter array** 액션 추가

#### From
```powerautomate
body('Get_files_(properties_only)')?['value']
```

#### 조건 예시
`Name`을 기준으로 필터링:

```powerautomate
startsWith(item()?['Name'], concat(outputs('Compose_Today'),'_'))
```

만약 `Name`이 잘 안 되면 `FileLeafRef`로 바꿔서 시도한다.

```powerautomate
startsWith(item()?['FileLeafRef'], concat(outputs('Compose_Today'),'_'))
```

---

### 7-4. varSeq 계산하기
**Initialize variable** 또는 **Set variable** 사용

#### 변수 정보
- **Name**: `varSeq`
- **Type**: `Integer`
- **Value**: `0`

그 다음 **Set variable**에서 아래 expression 사용:

```powerautomate
add(length(body('Filter_array')), 1)
```

#### 의미
- 오늘 파일이 0개면 → `1`
- 오늘 파일이 1개면 → `2`
- 오늘 파일이 2개면 → `3`

---

## 8. `Create file`의 File Name expression
`varSeq`가 계산되면 `Create file`의 **File Name**에 아래 expression을 넣는다.

```powerautomate
concat(
  outputs('Compose_Today'),
  '_',
  padLeft(string(variables('varSeq')), 2, '0'),
  '_인사혁신팀_정기미팅.txt'
)
```

---

## 9. 예시 결과
### 예시 1
- 오늘 날짜: `20260401`
- 오늘 생성된 기존 파일 수: 0개
- `varSeq = 1`

결과 파일명:
```text
20260401_01_인사혁신팀_정기미팅.txt
```

### 예시 2
- 오늘 날짜: `20260401`
- 오늘 생성된 기존 파일 수: 1개
- `varSeq = 2`

결과 파일명:
```text
20260401_02_인사혁신팀_정기미팅.txt
```

---

## 10. 권장 액션 순서
1. **When a new email arrives (V3)**
2. **Apply to each** (Attachments)
3. **Get attachment content (V2)**
4. **Compose_Today**
5. **Get files (properties only)**
6. **Filter array**
7. **Initialize / Set variable: varSeq**
8. **SharePoint → Create file**

---

## 11. 주의할 점
### 11-1. 동시성 문제
같은 순간에 메일이 여러 개 들어오면 `varSeq`가 겹칠 수 있다.

대응 방법:
- 흐름의 **Concurrency control**을 끈다.
- 가능한 경우 저장 작업을 순차적으로 처리한다.

### 11-2. 파일명 중복
중복 파일명을 피하려면 날짜와 순번을 반드시 넣는 것이 좋다.

### 11-3. SharePoint 경로 확인
`Create file`에서 폴더가 보이지 않으면 다음을 확인한다.
- 사이트 주소가 정확한지
- 라이브러리명이 맞는지
- 폴더가 실제로 존재하는지

---

## 12. 한 줄 요약
**Outlook 첨부파일은 Power Automate에서 직접 로컬 경로로 저장하는 대신, SharePoint 문서 라이브러리에 저장하고, 날짜별 기존 파일 개수를 기준으로 `varSeq`를 계산해서 `yyyymmdd_##_인사혁신팀_정기미팅.txt` 형식으로 파일명을 만든다.**

---

## 13. 바로 붙여넣기용 주요 Expression 모음

### 한국시간 기준 오늘 날짜
```powerautomate
formatDateTime(convertTimeZone(utcNow(),'UTC','Korea Standard Time'),'yyyyMMdd')
```

### 오늘 날짜 기준 파일 개수 + 1
```powerautomate
add(length(body('Filter_array')), 1)
```

### 두 자리 순번
```powerautomate
padLeft(string(variables('varSeq')), 2, '0')
```

### 최종 파일명
```powerautomate
concat(
  formatDateTime(convertTimeZone(utcNow(),'UTC','Korea Standard Time'),'yyyyMMdd'),
  '_',
  padLeft(string(variables('varSeq')), 2, '0'),
  '_인사혁신팀_정기미팅.txt'
)
```
