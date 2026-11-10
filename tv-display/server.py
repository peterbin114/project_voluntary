"""Minimal HTTP API for Arduino meal-sequence updates.

Run with: python server.py
The server listens on all network interfaces at port 8000.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Lock

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


class MealApiHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/api/state":
            self._send_json(404, {"error": "not_found"})
            return
        self._send_json(200, current_state())

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
    print(f"Meal API listening on http://{HOST}:{PORT}")
    print(f"Meal order: {', '.join(MEAL_ORDER)}")
    ThreadingHTTPServer((HOST, PORT), MealApiHandler).serve_forever()
