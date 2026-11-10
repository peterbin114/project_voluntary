# Arduino Uno R4 WiFi와 서버 통신

Arduino는 Wi-Fi를 통해 노트북에서 실행하는 Python 서버에 HTTP 요청을 보냅니다.

```text
NEXT 버튼 → Arduino Uno R4 WiFi → 교내/가정 Wi-Fi → Python 서버
```

## 서버 실행

1. 노트북과 Arduino를 같은 네트워크에 연결합니다.
2. `tv-display/server.py`의 `MEAL_ORDER`를 실제 급식 순서로 수정합니다.
3. 노트북에서 `tv-display` 폴더로 이동해 실행합니다.

```bash
python server.py
```

서버는 포트 8000에서 실행됩니다. 노트북의 사설 IPv4 주소를 확인합니다. Arduino 스케치의 `API_SERVER` 값을 그 주소로 바꿉니다. 예를 들어 노트북 주소가 `192.168.0.25`라면:

```cpp
const IPAddress API_SERVER(192, 168, 0, 25);
```

운영체제 방화벽에서 같은 네트워크의 TCP 8000 연결을 허용해야 할 수 있습니다.

## Arduino 설정과 업로드

1. Arduino IDE에서 Arduino Uno R4 WiFi 보드를 선택합니다.
2. `arduino/uno-r4-wifi-meal-button/uno-r4-wifi-meal-button.ino`에서 Wi-Fi 이름과 비밀번호를 입력합니다.
3. `BUTTON_PIN`은 기본 D2입니다. 버튼 한쪽을 D2, 다른 쪽을 GND에 연결합니다. 내부 풀업 저항을 사용하므로 외부 저항은 필요하지 않습니다.
4. `API_SERVER`를 서버 노트북의 사설 IPv4 주소로 바꿉니다.
5. 스케치를 업로드하고 시리얼 모니터를 115200 baud로 엽니다.
6. 버튼을 누르면 서버가 HTTP 200으로 응답하고, 서버의 다음 순번이 한 단계 진행됩니다.

Wi-Fi 자격 증명과 서버 주소는 실제 환경에 맞게 설정해야 합니다. Arduino와 서버가 서로 통신 가능한 같은 네트워크에 있어야 합니다.

## HTTP API

- `GET /api/state`: 현재 반, 다음 반, 순번을 JSON으로 반환합니다.
- `POST /api/next`: `{"event":"next","device_id":"uno-r4-wifi"}`를 보내 순번을 진행합니다.

서버의 순번은 메모리에만 보관되므로 서버를 재시작하면 첫 순서 전 상태로 돌아갑니다. 이 API는 입력 통신 프로토타입이며 TV 화면 자동 갱신은 별도 연동 작업입니다.
