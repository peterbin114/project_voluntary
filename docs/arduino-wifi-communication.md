# Arduino Uno R4 WiFi, 서버, TV 실시간 통신

Arduino와 TV 브라우저는 노트북에서 실행하는 Python 서버에 Wi-Fi로 연결합니다.

```text
NEXT 버튼 → Arduino Uno R4 WiFi → HTTP POST /api/next
TV 브라우저 ← 2초마다 HTTP GET /api/state ← Python 서버
```

## 서버 실행

1. 노트북과 Arduino, TV를 같은 네트워크에 연결합니다.
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

## TV 브라우저 설정

TV 브라우저에서 서버 주소와 해당 교실 코드를 엽니다.

```text
http://192.168.0.25:8000/?classroom=1-2
```

다른 교실 화면은 `classroom=1-2` 부분을 해당 교실 코드로 바꿉니다. 페이지가 2초마다 상태를 가져와 현재 순서, 다음 순서, 대기 메시지와 서버 연결 상태를 갱신합니다.

## Arduino 설정과 업로드

1. Arduino IDE에서 Arduino Uno R4 WiFi 보드를 선택합니다.
2. `arduino/uno-r4-wifi-meal-button/uno-r4-wifi-meal-button.ino`에서 Wi-Fi 이름과 비밀번호를 입력합니다.
3. `BUTTON_PIN`은 기본 D2입니다. 버튼 한쪽을 D2, 다른 쪽을 GND에 연결합니다. 내부 풀업 저항을 사용하므로 외부 저항은 필요하지 않습니다.
4. `API_SERVER`를 서버 노트북의 사설 IPv4 주소로 바꿉니다.
5. 스케치를 업로드하고 시리얼 모니터를 115200 baud로 엽니다.
6. 버튼을 누르면 서버가 HTTP 200으로 응답하고, TV 화면은 다음 상태 조회에서 변경됩니다.

Arduino와 서버, TV가 서로 통신 가능한 같은 네트워크에 있어야 합니다. 학교 네트워크에서 기기 간 통신을 제한하는 경우 네트워크 관리자 설정이 필요할 수 있습니다.

## HTTP API

- `GET /api/state`: 현재 반, 다음 반, 순번을 JSON으로 반환합니다.
- `POST /api/next`: `{"event":"next","device_id":"uno-r4-wifi"}`를 보내 순번을 진행합니다.

서버의 순번은 메모리에만 보관되므로 서버를 재시작하면 초기 상태로 돌아갑니다.
