from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from flask import Flask, render_template

app = Flask(__name__)

SESSIONS: list[dict[str, Any]] = []


def load_sessions(json_path: Path) -> list[dict[str, Any]]:
    with json_path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)

    if not isinstance(raw_data, list):
        raise ValueError("최상위 JSON 형식은 배열(list)이어야 합니다.")

    for index, session in enumerate(raw_data, start=1):
        if not isinstance(session, dict):
            raise ValueError(f"{index}번째 항목은 객체(object)여야 합니다.")

        models = session.get("models")
        if not isinstance(models, list):
            raise ValueError(f"{index}번째 항목의 models는 배열(list)이어야 합니다.")
        if len(models) != 3:
            raise ValueError(f"{index}번째 항목의 models는 정확히 3개여야 합니다.")

    return raw_data


@app.route("/")
def index() -> str:
    return render_template("index.html", sessions=SESSIONS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JSON 파일을 읽어 LLM 답변 비교 화면을 제공합니다.")
    parser.add_argument("json_path", help="비교할 JSON 파일 경로")
    parser.add_argument("--host", default="127.0.0.1", help="Flask 서버 호스트")
    parser.add_argument("--port", default=5000, type=int, help="Flask 서버 포트")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    json_path = Path(args.json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {json_path}")

    SESSIONS = load_sessions(json_path)
    app.run(host=args.host, port=args.port, debug=True)
