"""HTTP server for Arduino meal-sequence updates and live TV pages.

Run with: python server.py
Open http://SERVER_IP:8000/?classroom=1-2 on a TV browser.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Lock
from urllib.parse import parse_qs, urlsplit

from app import TV_CLASSROOM, class_name, render_page

HOST = "0.0.0.0"
PORT = 8000
MEAL_ORDER = ["2-3", "1-2", "3-1", "2-1", "1-3"]

_state_lock = Lock()
_position = -1


def current_state():
    with _state_lock:
        current = MEAL_ORDER[_position] if _position >= 0 else None
        next_position = (_position + 1) % len(MEAL_ORDER)
        return {
            "current_class": current,
            "next_class": MEAL_ORDER[next_position],
            "position": _position,
            "total": len(MEAL_ORDER),
        }


LIVE_UPDATE_SCRIPT = """
<script>
  const classroomCode = __CLASSROOM_CODE__;
  const connectionLabel = document.querySelector("#connection-label");
  const messageElement = document.querySelector(".message");
  const statusElement = document.querySelector(".status");
  const iconElement = document.querySelector(".status-symbol");
  const statusTextElement = statusElement.querySelector("span:last-child");
  const footerElement = document.querySelector("footer > span:first-child");

  function applyMealState(state) {
    let display;
    if (state.current_class === classroomCode) {
      display = {
        message: "지금 급식 시간!",
        status: "current",
        icon: "●",
        text: "급식실로 이동하세요.",
        footer: "차례를 지켜 안전하게 이동해주세요."
      };
    } else if (state.next_class === classroomCode) {
      display = {
        message: "다음 순서입니다",
        status: "next",
        icon: "⏱",
        text: "준비해주세요.",
        footer: "안전하게 이동하고 맛있게 식사하세요."
      };
    } else if (state.current_class === null) {
      display = {
        message: "급식 시작 전",
        status: "waiting",
        icon: "✓",
        text: "다음 순서: " + state.next_class.replace("-", "학년 ") + "반",
        footer: "안내가 바뀔 때까지 교실에서 기다려주세요."
      };
    } else {
      display = {
        message: "현재 대기 중",
        status: "waiting",
        icon: "✓",
        text: "현재 " + state.current_class.replace("-", "학년 ") + "반 급식 중",
        footer: "안내가 바뀔 때까지 교실에서 기다려주세요."
      };
    }

    messageElement.textContent = display.message;
    statusElement.className = "status " + display.status;
    iconElement.textContent = display.icon;
    statusTextElement.textContent = display.text;
    footerElement.textContent = display.footer;
  }

  async function refreshMealState() {
    try {
      const response = await fetch("/api/state", { cache: "no-store" });
      if (!response.ok) throw new Error("HTTP " + response.status);
      applyMealState(await response.json());
      connectionLabel.textContent = "서버 연결됨";
    } catch (error) {
      connectionLabel.textContent = "서버 연결 끊김";
    } finally {
      window.setTimeout(refreshMealState, 2000);
    }
  }

  refreshMealState();
</script>
"""


class MealApiHandler(BaseHTTPRequestHandler):
    def _send_bytes(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(status, "application/json; charset=utf-8", body)

    def do_GET(self):
        request = urlsplit(self.path)
        if request.path == "/api/state":
            self._send_json(200, current_state())
            return

        if request.path != "/":
            self._send_json(404, {"error": "not_found"})
            return

        query = parse_qs(request.query)
        classroom = query.get("classroom", [TV_CLASSROOM])[0]
        try:
            class_name(classroom)
            state = current_state()
            page = render_page(
                tv_classroom=classroom,
                current_class=state["current_class"],
                next_class=state["next_class"],
            )
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return

        page = page.replace("교실 안내 화면", '<span id="connection-label">서버 연결 중</span>')
        live_script = LIVE_UPDATE_SCRIPT.replace(
            "__CLASSROOM_CODE__", json.dumps(classroom, ensure_ascii=False)
        )
        page = page.replace("</body>", live_script + "\n</body>")
        self._send_bytes(200, "text/html; charset=utf-8", page.encode("utf-8"))

    def do_POST(self):
        global _position
        if self.path != "/api/next":
            self._send_json(404, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length < 1 or content_length > 1024:
                raise ValueError("invalid_content_length")
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return

        if not isinstance(payload, dict) or payload.get("event") != "next":
            self._send_json(400, {"error": "expected_event_next"})
            return

        with _state_lock:
            _position = (_position + 1) % len(MEAL_ORDER)
        self._send_json(200, current_state())

    def log_message(self, format_string, *args):
        print("%s - %s" % (self.address_string(), format_string % args))


if __name__ == "__main__":
    print(f"Meal server listening on http://{HOST}:{PORT}")
    print(f"Meal order: {', '.join(MEAL_ORDER)}")
    ThreadingHTTPServer((HOST, PORT), MealApiHandler).serve_forever()
