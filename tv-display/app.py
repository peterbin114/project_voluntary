"""HTML rendering for the cafeteria TV display.

Run app.py to generate a static preview, or run server.py to serve live data.
"""
from datetime import date
from html import escape
from pathlib import Path

# Static preview defaults. Live values are passed by server.py.
TV_CLASSROOM = "1-2"
CURRENT_CLASS = "2-3"
NEXT_CLASS = "1-2"

WEEKDAYS_KO = ("월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일")


def class_name(class_code):
    """Convert a code such as '1-2' to a Korean classroom label."""
    if class_code is None:
        return "급식 시작 전"
    parts = class_code.split("-", maxsplit=1)
    if len(parts) != 2 or not all(part.isdecimal() for part in parts):
        raise ValueError("교실 코드는 학년-반 형식이어야 합니다 (예: 1-2).")
    grade, room = (int(part) for part in parts)
    if grade < 1 or room < 1:
        raise ValueError("학년과 반은 1 이상의 숫자여야 합니다.")
    return f"{grade}학년 {room}반"


def display_data(tv_classroom, current_class, next_class):
    """Choose the text and color for a classroom's current state."""
    if tv_classroom == current_class:
        return {
            "message": "지금 급식 시간!",
            "status_class": "current",
            "icon": "●",
            "status_text": "급식실로 이동하세요.",
            "footer": "차례를 지켜 안전하게 이동해주세요.",
        }

    if tv_classroom == next_class:
        return {
            "message": "다음 순서입니다",
            "status_class": "next",
            "icon": "⏱",
            "status_text": "준비해주세요.",
            "footer": "안전하게 이동하고 맛있게 식사하세요.",
        }

    if current_class is None:
        return {
            "message": "급식 시작 전",
            "status_class": "waiting",
            "icon": "✓",
            "status_text": f"다음 순서: {class_name(next_class)}",
            "footer": "안내가 바뀔 때까지 교실에서 기다려주세요.",
        }

    return {
        "message": "현재 대기 중",
        "status_class": "waiting",
        "icon": "✓",
        "status_text": f"현재 {class_name(current_class)} 급식 중",
        "footer": "안내가 바뀔 때까지 교실에서 기다려주세요.",
    }


def render_page(tv_classroom=TV_CLASSROOM, current_class=CURRENT_CLASS, next_class=NEXT_CLASS):
    """Fill the HTML design template with the supplied state."""
    folder = Path(__file__).resolve().parent
    template = (folder / "template.html").read_text(encoding="utf-8")
    today = date.today()
    date_label = f"{today.year}년 {today.month}월 {today.day}일 {WEEKDAYS_KO[today.weekday()]}"
    data = display_data(tv_classroom, current_class, next_class)

    values = {
        "DATE": date_label,
        "MESSAGE": data["message"],
        "ROOM": class_name(tv_classroom),
        "STATUS_CLASS": data["status_class"],
        "ICON": data["icon"],
        "STATUS_TEXT": data["status_text"],
        "FOOTER": data["footer"],
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", escape(value))

    return template


def main():
    output = Path(__file__).resolve().with_name("index.html")
    output.write_text(render_page(), encoding="utf-8")
    print(f"TV 화면 파일을 생성했습니다: {output}")


if __name__ == "__main__":
    main()
