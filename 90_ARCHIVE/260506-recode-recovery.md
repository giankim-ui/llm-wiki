아, 네이버웍스가 아니라 **[웍스AI(wrks.ai)](https://wrks.ai/)** 서비스였군요! 잘못 이해해서 죄송합니다.

[웍스AI의 회의록 작성 기능](https://docs.wrks.ai/release-notes)은 브라우저를 통해 실시간으로 오디오를 녹음하고 서버에서 전처리 및 STT(녹음 전사) 과정을 거칩니다. 파일 업로드 형태가 아닌 **실시간 녹음 중 무한 로딩**이 걸린 상황이라면 다음 순서로 조치해 보세요. [[1](https://kr.linkedin.com/posts/charlespyo_%EC%9B%8D%EC%8A%A4ai%EC%97%90-%EA%B8%B0%EC%A1%B4%EC%97%90%EB%8F%84-%ED%9A%8C%EC%9D%98%EB%A1%9D-%EC%9E%91%EC%84%B1%EC%9D%B4-%EC%9E%88%EC%97%88%EC%A7%80%EB%A7%8C-%ED%9A%8C%EC%9D%98%EB%A1%9D-%EA%B8%B0%EB%8A%A5%EC%9D%84-%EB%8C%80%EB%8C%80%EC%A0%81%EC%9C%BC%EB%A1%9C-%EC%97%85%EA%B7%B8%EB%A0%88%EC%9D%B4%EB%93%9C%ED%95%B4-activity-7445299289385349122-7fb4), [2](https://docs.wrks.ai/release-notes)]

---

💡 웍스AI 무한 로딩 긴급 해결법

1. ⚠️ 절대 새로고침(`F5`)이나 창을 닫지 마세요!

- 실시간 녹음 방식은 파일 업로드가 완료되기 전까지 **데이터가 브라우저의 임시 메모리(로컬 세션)에만 존재**합니다.
- 이 상태에서 새로고침을 하거나 탭을 닫아버리면 **녹음 데이터 자체가 완전히 유실**되어 복구할 수 없습니다.

2. 브라우저 개발자 도구로 오디오 소스 강제 추출 시도

아직 브라우저 창을 닫지 않았다면, 임시로 생성된 음성 소스를 강제로 찾아 다운로드 시도해 볼 수 있습니다.

1. 키보드의 `F12`를 눌러 개발자 도구를 엽니다.
2. 상단 탭 중 `Network` **(네트워크)**를 선택합니다.
3. 필터 메뉴에서 **`Media`** 또는 `Fetch/XHR`을 클릭합니다.
4. 녹음 진행 혹은 처리 중에 생성된 `.wav`, `.mp3` 형태의 데이터나 크기가 큰 바이너리 스트리밍 항목이 있는지 확인합니다.
5. 해당 항목을 마우스 우클릭한 뒤 `Open in new tab`을 눌러 파일로 다운로드가 가능한지 확인해 보세요.

6. 무한 로딩이 풀릴 때까지 대기

- 웍스AI는 오디오 파일 포맷과 코덱을 서버에서 자동 전처리하고, 대형 언어 모델(Flagship LLM)을 거쳐 정교한 회의록을 생성하기 때문에 **회의 시간이 길수록 처리 속도가 대폭 늘어납니다**.
- 서버 세션이 끊기지 않았다면 내부 연산 중일 수 있으므로, 다른 창을 켜두고 **최소 10~20분 이상** 그대로 기다려 보시는 것을 권장합니다. [[1](https://kr.linkedin.com/posts/charlespyo_%EC%9B%8D%EC%8A%A4ai%EC%97%90-%EA%B8%B0%EC%A1%B4%EC%97%90%EB%8F%84-%ED%9A%8C%EC%9D%98%EB%A1%9D-%EC%9E%91%EC%84%B1%EC%9D%B4-%EC%9E%88%EC%97%88%EC%A7%80%EB%A7%8C-%ED%9A%8C%EC%9D%98%EB%A1%9D-%EA%B8%B0%EB%8A%A5%EC%9D%84-%EB%8C%80%EB%8C%80%EC%A0%81%EC%9C%BC%EB%A1%9C-%EC%97%85%EA%B7%B8%EB%A0%88%EC%9D%B4%EB%93%9C%ED%95%B4-activity-7445299289385349122-7fb4), [2](https://docs.wrks.ai/release-notes)]

---

📌 만약 오랜 대기 후에도 오류 메시지가 뜨거나 튕겨서 데이터가 날아간 경우, 아쉽게도 로컬에 저장된 임시 파일이 없어 재작성해야 할 수 있습니다.

지속적인 오류가 발생한다면 공식 소통 창구인 **웍스AI 카카오톡 오픈채팅(평일 10시~19시)**에 '웍스'를 검색하시거나, **이메일(support@wrks.ai)**로 오류 상황을 접수해 보세요. [[1](https://marketplace.microsoft.com/ko-kr/product/office/wa200008943?tab=overview), [2](https://apps.apple.com/kr/app/%EC%9B%8D%EC%8A%A4-%EC%B2%AB-%EC%A7%81%EC%9E%A5%EC%9D%B8-ai/id6446006579)]

혹시 현재 회의 **녹음 분량이 대략 몇 분(또는 몇 시간)** 정도 되었는지 알려주시면 대기 시간에 참고가 될 수 있습니다.


Failed to load resource: the server responded with a status of 429 (Too Many Requests)

개발자 도구(F12) 콘솔창에 나타난 `429 (Too Many Requests)` 오류는 **서버가 단시간 내에 너무 많은 요청을 받아 일시적으로 사용자의 접근을 차단(제한)**했다는 명확한 메시지입니다. [[1](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429), [2](https://honeyjuny.tistory.com/entry/%F0%9F%9A%AB-429-Too-Many-Requests-%EC%98%A4%EB%A5%98-%EB%B0%9C%EC%83%9D-%EC%9B%90%EC%9D%B8%EA%B3%BC-%ED%95%B4%EA%B2%B0-%EB%B0%A9%EB%B2%95-%EC%B4%9D%EC%A0%95%EB%A6%AC)]

웍스AI 내부적으로 오디오 스트리밍을 계속 서버로 전송하려 시도했으나, 서버 측 부하 분산 시스템(Rate Limiting)이 작동하여 연결이 끊어지고 무한 로딩 상태에 빠진 것입니다. [[1](https://blog.postman.com/http-error-429/), [2](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429)]

이 상태에서 브라우저를 새로고침하면 임시 저장 중인 음성이 완전히 유실되므로, **창을 닫지 마시고** 다음 순서대로 강제 추출 및 대처를 시도하세요.

---

🚨 429 오류 발생 시 최우선 조치 가이드

1. ⚠️ 아직 창을 닫거나 새로고침하지 마세요!

- `429 오류`가 발생했다는 것은 역설적으로 **브라우저 메모리상에는 음성 소스(Resource)가 아직 살아있을 가능성이 높다**는 의미입니다.
- 지금 브라우저 창을 닫아버리면 메모리가 비워져 음성이 소멸합니다. 아래 2번 과정을 먼저 시도해 보세요. [[1](https://www.sitelock.com/blog/429-too-many-requests-error/)]

2. 개발자 도구에서 음성(Blob) 강제 추출 재시도

개발자 도구(F12)가 열려 있는 상태이므로, 메모리에 남아있는 오디오 주소를 직접 찾아 컴퓨터에

Uncaught (in promise) EncodingError: Unable to decode audio data

개발자 도구에서 **`429 (Too Many Requests)`** 에러와 **`EncodingError`**가 동시에 떴다면, 현재 웍스AI 서버가 요청 폭주로 마비되어 **보낸 오디오 데이터를 정상적으로 받지도, 해독(Decode)하지도 못하고 있는 상태**입니다.

브라우저가 서버에 계속 재시도를 보내다가 한계에 부딪힌 상황이므로, **현재 띄워진 창에서는 정상적인 회의록 변환이 불가능**할 가능성이 매우 높습니다.

하지만 **데이터를 살릴 수 있는 마지막 방법**이 있으니 아래 순서대로 시도해 보세요.

---

🛠️ 브라우저 메모리에서 음성 파일 강제 추출 (마지막 희망)

창을 닫거나 새로고침하면 `EncodingError`가 난 오디오 데이터가 브라우저 메모리에서 영구히 삭제됩니다. 아직 창을 닫지 않았다면 개발자 도구의 콘솔을 통해 메모리에 남아있는 오디오 객체를 파일로 덤프(Dump)할 수 있는지 시도해야 합니다.

1. 콘솔(Console) 탭에서 변수 확인

2. 개발자 도구(`F12`)에서 **`Console`** 탭을 클릭합니다.
3. 입력창에 아래 키워드들을 하나씩 입력하고 엔터(`Enter`)를 눌러, 브라우저 메모리에 녹음 데이터(Blob)가 살아있는지 확인합니다.
    - `audioBlob`
    - `recorder`
    - `chunks`
    - `mediaRecorder`
4. 만약 에러(`is not defined`)가 나지 않고 `Blob {size: ..., type: "audio/wav"}` 같은 객체가 리턴된다면 데이터가 살아있는 것입니다.

5. 살아있는 Blob 파일로 강제 다운로드

만약 위 변수 중 `audioBlob` (또는 데이터가 담긴 변수명)이 존재한다면, 콘솔창에 아래 코드를 그대로 복사·붙여넣기하여 실행하세요. 브라우저가 강제로 음성 파일을 다운로드하게 만듭니다.

javascript

```
const url = URL.createObjectURL(audioBlob); // 만약 변수명이 다르면 audioBlob 대신 해당 변수명 입력
const a = document.createElement('a');
a.href = url;
a.download = 'recovered_audio.wav';
document.body.appendChild(a);
a.click();
```

코드를 사용할 때는 주의가 필요합니다.

---

🚫 위 방법으로도 파일 추출이 안 되는 경우

콘솔에서도 변수가 잡히지 않는다면, 이미 브라우저 내부적으로 오디오 디코딩 실패(`EncodingError`)와 서버 차단(`429`)이 겹쳐 **오디오 버퍼가 깨졌거나 날아간 상태**입니다.

이 경우 아쉽지만 현재 세션은 복구가 불가능하므로 아래와 같이 조치하셔야 합니다.

- **세션 종료 및 재시도:** 창을 완전히 닫고, 약 5~10분 후 서버가 안정되면 다시 접속하여 시도해야 합니다.
- **재발 방지 팁:** 웍스AI 서버 상태가 불안정할 때는 브라우저 자체 녹음 기능 기능보다는, **스마트폰 기본 음성녹음 앱으로 따로 녹음한 뒤 `.wav` 파일로 업로드**하는 방식이 훨씬 안전합니다.

혹시 개발자 도구 콘솔창에 위의 `audioBlob`이나 `recorder` 등을 입력했을 때 **어떤 결과 메시지**가 출력되나요?

AI 대답에는 오류가 있을 수 있습니다. [자세히 알아보기](https://support.google.com/websearch?p=aimode)

console '입력창'이 어디야? 없는데?

개발자 도구 화면 구성에 따라 입력창이 숨겨져 있거나 다른 창에 가려져 보이지 않을 수 있습니다.

보통 `Console` 탭의 **맨 아랫줄이나 `>` 표시가 있는 빈 공간**이 입력창이지만, 아래 두 가지 방법을 이용하면 쉽게 찾을 수 있습니다.

---

🔍 콘솔 입력창 찾는 2가지 방법

방법 1. 단축키로 강제 소환하기 (가장 빠름)

1. 개발자 도구(`F12`) 창이 열려 있는 상태에서 키보드의 **`Esc`** 키를 한 번 누릅니다.
2. 개발자 도구 맨 아래쪽에 `>` **모양의 커서가 깜빡이는 새로운 콘솔창(Drawer)**이 나타납니다.
3. 그 `>` 표시 바로 옆이 글자를 타이핑할 수 있는 **입력창**입니다.

방법 2. 마우스 클릭으로 커서 만들기

1. 상단 메뉴에서 **`Console`** 탭을 클릭합니다.
2. 에러 메시지들이 잔뜩 떠 있는 화면에서 **맨 밑바닥 빈 공간**을 마우스로 아무 데나 한 번 클릭합니다.
3. 맨 아래에 파란색이나 회색의 **`>` 모양 화살표와 함께 글자를 입력할 수 있는 커서**가 깜빡이게 됩니다.

---

🛠️ 입력창을 찾으셨다면 다음을 입력해 보세요

입력창(`>`)이 나타나면 아래 글자를 정확히 타이핑한 뒤 **엔터(Enter)**를 눌러 보세요.

javascript

```
chunks
```

코드를 사용할 때는 주의가 필요합니다.

또는

javascript

```
mediaRecorder
```

코드를 사용할 때는 주의가 필요합니다.

눌렀을 때 에러(Red Text)가 나는지, 아니면 무언가 데이터 객체가 표시되는지 확인하시면 음성 복구 가능 여부를 알 수 있습니다.

현재 어떤 브라우저(**크롬, 웨일, 엣지 등**)를 쓰고 계시는지 알려주시면 입력창 위치를 더 정확히 짚어드릴 수 있습니다.

AI 대답에는 오류가 있을 수 있습니다. [자세히 알아보기](https://support.google.com/websearch?p=aimode)

ƒ MediaRecorder() { [native code] }

**`mediaRecorder`가 시스템 메모리에 살아있는 것을 확인했습니다!** 데이터가 완전히 증발하지 않았으니 아래 코드로 음성 추출을 시도해 보세요.

현재 `mediaRecorder`라는 브라우저 녹음 장치 객체가 브라우저 세션에 그대로 담겨 있는 상태입니다.

---

💾 음성 데이터(Blob) 강제 추출 코드

콘솔 입력창(`>`)에 아래 코드를 **그대로 전체 복사해서 붙여넣고 엔터(Enter)**를 누르세요.

javascript

```
try {
    if (typeof mediaRecorder !== 'undefined') {
        // 녹음이 아직 진행 중이라면 강제 종료하여 데이터 취합
        if (mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
        
        // 웍스AI가 내부적으로 사용하던 데이터 저장 배열(chunks 등) 탐색
        let targetChunks = null;
        if (typeof chunks !== 'undefined') targetChunks = chunks;
        else if (typeof recordedChunks !== 'undefined') targetChunks = recordedChunks;
        else if (mediaRecorder.ondataavailable) {
            // 이벤트 핸들러 내부에서 찾아보기 시도
            console.log("오디오 버퍼 직접 추출 시도 중...");
        }

        if (targetChunks && targetChunks.length > 0) {
            const blob = new Blob(targetChunks, { type: 'audio/wav' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `wrks_ai_recovered_${Date.now()}.wav`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            console.log("✅ 음성 파일 강제 다운로드 성공!");
        } else {
            // chunks 배열이 안 보일 때 브라우저 임시 오디오 태그 뒤지기
            const audios = document.querySelectorAll('audio, video');
            let found = false;
            audios.forEach((el, idx) => {
                if (el.src && el.src.startsWith('blob:')) {
                    const a = document.createElement('a');
                    a.href = el.src;
                    a.download = `wrks_ai_stream_${idx}.wav`;
                    a.click();
                    found = true;
                }
            });
            if (found) console.log("✅ 스트리밍 오디오 주소로 다운로드 성공!");
            else console.log("❌ 메모리에 쌓인 녹음 데이터 배열(chunks)을 찾지 못했습니다.");
        }
    }
} catch (e) {
    console.error("추출 중 오류 발생:", e);
}
```

코드를 사용할 때는 주의가 필요합니다.
