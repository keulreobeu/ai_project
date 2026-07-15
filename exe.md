# 로컬 실행 순서 (백엔드 + 프론트엔드 연결 확인)

이 문서는 VSCode에서 이 프로젝트 폴더(`ai_project`)를 열었을 때, 백엔드(FastAPI, 8001번 포트)와
프론트엔드(Vue3+Vite, 5173번 포트)를 각각 띄우고 두 서버가 정상적으로 연결되는지 확인하는
절차를 처음부터 끝까지 그대로 따라 할 수 있게 정리한 것이다.

터미널은 **2개**가 필요하다 (백엔드용 1개, 프론트엔드용 1개). 아래 명령어는 VSCode 기본 터미널인
**PowerShell** 기준으로 작성했다. (Git Bash를 쓰는 경우 3-2절 하단의 참고를 보면 된다.)

---

## 0. 사전 준비 (최초 1회만)

- VSCode에서 `File > Open Folder...` (또는 `파일 > 폴더 열기...`)로 `ai_project` 폴더 전체를 연다.
  - `backend`나 `frontend` 하위 폴더가 아니라 **`ai_project` 루트 폴더**를 열어야 한다.
- Python 3.11, Node.js 18+ 이 설치되어 있는지 확인한다.
  ```powershell
  python --version
  node --version
  npm --version
  ```
  버전이 출력되지 않으면 Python/Node.js를 먼저 설치한 뒤 VSCode를 재시작한다.

---

## 1. VSCode에서 터미널 여는 법

1. VSCode 상단 메뉴에서 **Terminal(터미널) → New Terminal(새 터미널)** 을 클릭한다.
   - 단축키: `` Ctrl + ` `` (백틱 키, ESC 아래에 있는 키)
2. 화면 하단에 터미널 패널이 열리고, 기본적으로 프로젝트 루트(`ai_project`)에서 시작된다.
   - 프롬프트가 `PS C:\Users\SSAFY\Documents\ai_project>` 형태로 보이면 PowerShell이 맞다.
3. **터미널을 하나 더 연다** (백엔드/프론트엔드를 동시에 띄워야 하므로):
   - 터미널 패널 오른쪽 위의 `+` 아이콘을 클릭 (새 터미널 추가), 또는
   - 단축키 `` Ctrl + Shift + ` `` 를 한 번 더 누른다.
   - 터미널 패널 오른쪽 위의 `⊞`(분할) 아이콘을 누르면 화면을 좌우로 나눠 두 터미널을 동시에 볼 수 있어 편하다.

이제 **터미널 1(백엔드용)**, **터미널 2(프론트엔드용)** 두 개가 준비된 상태다.

---

## 2. 터미널 1 — 백엔드(FastAPI) 실행

터미널 목록에서 첫 번째 탭을 클릭해 선택한 뒤 아래를 순서대로 입력한다.

```powershell
cd backend
```

### 2-1. 의존성 설치 (최초 1회, 또는 requirements.txt가 바뀌었을 때만)

```powershell
pip install -r requirements.txt
```

### 2-2. OpenAI API 키 설정 (챗봇 기능을 테스트하려면 필요)

챗봇(`/api/chat`)을 테스트하지 않고 축제 목록/상세만 확인할 거라면 이 단계는 건너뛰어도 된다.
챗봇까지 확인하려면, **현재 열린 터미널 세션에서만 유효한** 환경변수로 키를 설정한다.

```powershell
$env:OPENAI_API_KEY = "sk-여기에-실제-키-입력"
```

> 이 명령은 터미널을 닫으면 사라진다(정상). 코드나 `.env` 파일에 실제 키 값을 직접 적어 커밋하지
> 않도록 주의한다.

### 2-3. 서버 실행

```powershell
python run_server.py
```

아래와 비슷한 로그가 뜨면 정상이다.

```text
INFO:     Started server process [....]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

이 터미널은 **그대로 켜둔 채** 다음 단계로 넘어간다 (서버를 계속 실행 중인 상태를 유지해야 함).
종료하고 싶을 때는 이 터미널에서 `Ctrl + C`.

---

## 3. 터미널 2 — 프론트엔드(Vue3/Vite) 실행

터미널 목록에서 두 번째 탭(또는 분할된 오른쪽 화면)을 클릭해 선택한 뒤 진행한다.

```powershell
cd frontend
```

### 3-1. 의존성 설치 (최초 1회, 또는 package.json이 바뀌었을 때만)

```powershell
npm install
```

### 3-2. 개발 서버 실행

```powershell
npm run dev
```

아래와 비슷한 로그가 뜨면 정상이다.

```text
  VITE v5.4.21  ready in 466 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://xxx.xxx.xxx.xxx:5173/
```

> **Git Bash를 쓰는 경우**: `$env:OPENAI_API_KEY = "..."` 대신 `export OPENAI_API_KEY="..."` 를 쓰는 것 외에는
> 나머지 `cd`, `pip install`, `python run_server.py`, `npm install`, `npm run dev` 명령어는 동일하게 쓰면 된다.

이 터미널도 **그대로 켜둔 채** 다음 단계로 넘어간다.

---

## 4. 브라우저에서 연결 확인

1. 아무 브라우저(Chrome 등)를 열고 주소창에 `http://localhost:5173` 을 입력해 접속한다.
2. **축제 목록 화면이 뜨는지 확인**한다 — 이미지/제목이 있는 카드 목록이 보이면, 프론트엔드가
   백엔드의 `/api/festivals`를 정상적으로 호출해 데이터를 받아온 것이다(= 두 서버가 잘 연결됨).
   - 목록이 비어 있거나 "데이터를 불러오지 못했습니다" 라고 뜨면 6절(문제 해결)을 참고한다.
3. 축제 카드의 **"자세히 보기"** 를 눌러 상세 페이지로 이동해본다 — 주변 장소 목록까지 뜨면 정상.
4. 화면 오른쪽 아래의 **💬(챗봇 버튼)** 을 눌러 채팅창을 연다.
   - "이번 주말 축제 추천해줘" 처럼 입력하고 전송 → 축제 후보가 답변과 함께 버튼(칩) 형태로 뜨는지 확인
   - 후보 하나를 클릭 → "주변에 또 어떤 시설이 궁금하세요?" 라는 후속 질문과 카테고리 버튼이 뜨는지 확인
   - 카테고리(예: 숙박) 버튼 클릭 → 거리순으로 정렬된 결과가 답변과 함께 리스트로 뜨는지 확인
   - 2-2절에서 `OPENAI_API_KEY`를 설정하지 않았다면, 이 단계에서는 "답변을 가져오지 못했어요"
     라는 메시지가 뜨는 것이 **정상**이다(챗봇 자체가 아니라 키 미설정 때문).

여기까지 정상적으로 보이면 백엔드-프론트엔드 연결 확인이 끝난 것이다.

---

## 5. (선택) 터미널에서 curl로 빠르게 확인하기

브라우저를 열지 않고 터미널만으로도 백엔드가 살아있는지 빠르게 확인할 수 있다.
**터미널 1, 2와 별개로 새 터미널(세 번째)** 을 하나 열어서 실행한다.

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/health"
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/festivals" | Select-Object -First 3
```

`{"status":"ok"}` 와 축제 목록 JSON이 각각 출력되면 백엔드는 정상 동작 중이다.
프론트엔드 경유 확인은 포트만 5173으로 바꿔서 동일하게 호출해보면 된다(Vite가 `/api`를 8001로
프록시하므로 결과가 같아야 한다).

```powershell
Invoke-RestMethod -Uri "http://localhost:5173/api/health"
```

---

## 6. 문제 해결 (자주 발생하는 상황)

**"포트가 이미 사용 중입니다" / 서버가 안 켜짐**
이전에 띄운 서버가 안 꺼지고 남아있는 경우다. 아래로 포트를 점유한 프로세스를 찾아 종료한다.

```powershell
Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
# 위 명령 결과에 나온 OwningProcess 번호(PID)를 아래에 넣어서 종료
Stop-Process -Id <PID번호> -Force
```
5173 포트도 같은 방식으로 확인/종료하면 된다.

**프론트엔드 화면에 "데이터를 불러오지 못했습니다"가 뜸**
- 터미널 1(백엔드)이 여전히 켜져 있고 에러 없이 떠 있는지 먼저 확인한다.
- `frontend/vite.config.js`의 `server.proxy['/api']` 값이 `http://127.0.0.1:8001` 인지 확인한다(수정한 적 없다면 원래 이 값).

**챗봇이 항상 "답변을 가져오지 못했어요"라고 뜸**
- 터미널 1에서 `OPENAI_API_KEY`를 설정했는지 확인한다(2-2절). 설정 없이 실행했다면 이 동작이 정상이다.
- 키를 설정했는데도 안 되면, 터미널 1에 뜨는 에러 로그(백엔드 콘솔)를 확인한다 — 대부분 키 오타/만료 문제다.

**`pip install`이나 `npm install`이 느리거나 실패함**
- 사내망/방화벽 문제일 수 있다. 네트워크 연결 후 재시도한다.

---

## 참고: 이건 "개발 모드" 확인 절차다

위 방법은 5173(프론트)/8001(백엔드) **두 개의 포트를 분리해서 띄우는 개발용 실행 방법**이다.
배포용으로 하나의 포트(8001)만으로 프론트+백엔드를 함께 서빙하는 방법은 `README.md`의
"Single-port production build" 절을 참고한다.
