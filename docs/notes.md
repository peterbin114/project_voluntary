# 진행 상황 기록

## 2026-11-10

- 저장소와 기존 급식 안내 문서를 확인했습니다. Arduino의 NEXT 입력을 서버에 전달하고 교실 TV에 순번을 표시하는 구조입니다.
- Arduino Uno R4 WiFi가 서버에 HTTP로 직접 연결하도록 스케치를 추가했습니다. 버튼 입력은 `POST /api/next`로 전달합니다.
- Python 서버에 급식 순서 상태와 `GET /api/state` API를 추가했습니다.
- 서버가 교실별 TV 페이지를 제공하고, 각 화면이 2초마다 상태를 조회해 현재/다음 순서와 연결 상태를 갱신하도록 연결했습니다.
- 서버 실행, Wi-Fi 설정, 버튼 배선, TV 접속 주소를 문서화했습니다.
- 변경 사항을 초안 [PR #1](https://github.com/peterbin114/project_voluntary/pull/1)에 올렸습니다.
- 실제 Uno R4 WiFi 보드와 TV 네트워크에서의 연결 검증, 실제 급식 순서로의 설정은 남아 있습니다.
