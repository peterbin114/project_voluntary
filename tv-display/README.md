# TV 화면과 실시간 서버

Python 표준 라이브러리만 사용합니다. Arduino와 TV 브라우저가 같은 서버에 연결해 급식 순번을 공유합니다.

## 실시간 화면 실행

1. `server.py`의 `MEAL_ORDER`를 실제 급식 순서로 수정합니다.
2. 이 폴더에서 서버를 실행합니다.

```bash
python server.py
```

서버 노트북의 사설 IP 주소와 포트 8000을 사용해 TV 브라우저에서 엽니다. 교실 코드를 쿼리 값으로 지정합니다.

```text
http://SERVER_IP:8000/?classroom=1-2
```

예를 들어 `http://192.168.0.25:8000/?classroom=1-2`입니다. 각 TV는 주소의 `classroom` 값만 다르게 설정합니다. 브라우저 페이지는 2초마다 서버 상태를 확인하고 현재/다음 순서와 연결 상태를 갱신합니다.

Arduino Uno R4 WiFi 설정과 버튼 배선은 `docs/arduino-wifi-communication.md`를 참고하세요. 서버를 실행하는 노트북에서 TCP 8000 포트 연결을 허용해야 할 수 있습니다.

## API

- `GET /api/state`: 현재 반과 다음 반 상태를 JSON으로 반환합니다.
- `POST /api/next`: Arduino가 호출해 다음 급식 순서로 진행합니다.

서버 상태는 메모리에 저장되므로 서버가 재시작되면 초기화됩니다. 예시 순번을 조정하려면 서버를 시작하기 전에 `MEAL_ORDER`를 바꾸세요.

## 정적 화면 미리보기

서버 없이 디자인만 확인하려면 다음 명령을 실행하고 생성된 `index.html`을 브라우저에서 엽니다.

```bash
python app.py
```

정적 미리보기는 고정된 예시 상태를 사용합니다. 실시간 TV 화면은 반드시 `python server.py`로 제공해야 합니다.
