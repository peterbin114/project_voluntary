"""Python data layer for generating the static cafeteria TV display.

Edit the three example values below, then run: python app.py
No Arduino, server, or network communication is implemented.
"""

from datetime import date
from html import escape
from pathlib import Path

# 화면을 만들 때 사용할 예시 데이터입니다.
TV_CLASSROOM = "1-2"
CURRENT_CLASS = "2-3"
NEXT_CLASS = "1-2"

WEEKDAYS_KO = ("월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일")


def class_name(class_code):
    """Convert a code such as '1-2' to a Korean classroom label."""
    grade, room = (int(part) for part in class_code.split("-", maxsplit=1))
    return f"{grade}학년 {room}반"


def display_data():
    """Choose the text and color for this classroom's current state."""
    classroom = class_name(TV_CLASSROOM)

    if TV_CLASSROOM == CURRENT_CLASS:
        return {
            "message": "지금 급식 시간!",
            "status_class": "current",
            "icon": "●",
            "status_text": "급식실로 이동하세요.",
            "footer": "차례를 지켜 안전하게 이동해주세요.",
        }

    if TV_CLASSROOM == NEXT_CLASS:
        return {
            "message": "다음 순서입니다",
            "status_class": "next",
            "icon": "⏱",
            "status_text": "준비해주세요.",
            "footer": "안전하게 이동하고 맛있게 식사하세요.",
        }

    return {
        "message": "현재 대기 중",
        "status_class": "waiting",
        "icon": "✓",
        "status_text": f"현재 {class_name(CURRENT_CLASS)} 급식 중",
        "footer": "안내가 바뀔 때까지 교실에서 기다려주세요.",
    }


def render_page():
    """Fill the HTML design template with local example data."""
    folder = Path(__file__).resolve().parent
    template = (folder / "template.html").read_text(encoding="utf-8")
    today = date.today()
    date_label = f"{today.year}년 {today.month}월 {today.day}일 {WEEKDAYS_KO[today.weekday()]}"
    data = display_data()

    values = {
        "DATE": date_label,
        "MESSAGE": data["message"],
        "ROOM": class_name(TV_CLASSROOM),
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
