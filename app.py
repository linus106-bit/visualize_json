from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
INITIAL_JSON_TEXT = ""


@dataclass
class ModelAnswer:
    name: str
    original: str
    korean: str


@dataclass
class SessionData:
    session_number: int
    question: str
    question_korean: str
    models: list[ModelAnswer]


def parse_sessions(raw_data: Any) -> list[SessionData]:
    if not isinstance(raw_data, list):
        raise ValueError("최상위 JSON 형식은 배열(list)이어야 합니다.")

    sessions: list[SessionData] = []
    for index, item in enumerate(raw_data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{index}번째 항목은 객체(object)여야 합니다.")

        session_number = item.get("sessionNumber")
        question = item.get("question")
        question_korean = item.get("questionKorean")
        models = item.get("models")

        if not isinstance(session_number, int):
            raise ValueError(f"{index}번째 sessionNumber는 정수여야 합니다.")
        if not isinstance(question, str):
            raise ValueError(f"{index}번째 question은 문자열이어야 합니다.")
        if not isinstance(question_korean, str):
            raise ValueError(f"{index}번째 questionKorean은 문자열이어야 합니다.")
        if not isinstance(models, list):
            raise ValueError(f"{index}번째 models는 배열(list)이어야 합니다.")

        parsed_models: list[ModelAnswer] = []
        for model_idx, model in enumerate(models, start=1):
            if not isinstance(model, dict):
                raise ValueError(f"{index}번째 세션의 {model_idx}번째 모델 데이터는 객체여야 합니다.")

            name = model.get("name")
            original = model.get("original")
            korean = model.get("korean")

            if not isinstance(name, str):
                raise ValueError(f"{index}번째 세션의 {model_idx}번째 model.name은 문자열이어야 합니다.")
            if not isinstance(original, str):
                raise ValueError(f"{index}번째 세션의 {model_idx}번째 model.original은 문자열이어야 합니다.")
            if not isinstance(korean, str):
                raise ValueError(f"{index}번째 세션의 {model_idx}번째 model.korean은 문자열이어야 합니다.")

            parsed_models.append(ModelAnswer(name=name, original=original, korean=korean))

        sessions.append(
            SessionData(
                session_number=session_number,
                question=question,
                question_korean=question_korean,
                models=parsed_models,
            )
        )

    sessions.sort(key=lambda s: s.session_number)
    return sessions


@app.route("/")
def index() -> str:
    return render_template_string(PAGE_TEMPLATE, initial_json_text=INITIAL_JSON_TEXT)


@app.post("/api/validate")
def validate_json():
    payload = request.get_json(silent=True) or {}
    raw_json_text = payload.get("jsonText", "")

    try:
        raw_data = json.loads(raw_json_text)
    except json.JSONDecodeError as exc:
        return jsonify({"ok": False, "error": f"JSON 파싱 오류: {exc}"}), 400

    try:
        sessions = parse_sessions(raw_data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    serialized = [
        {
            "sessionNumber": session.session_number,
            "question": session.question,
            "questionKorean": session.question_korean,
            "models": [
                {
                    "name": model.name,
                    "original": model.original,
                    "korean": model.korean,
                }
                for model in session.models
            ],
        }
        for session in sessions
    ]

    return jsonify({"ok": True, "sessions": serialized})


PAGE_TEMPLATE = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LLM 답변 비교기</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7fb;
      --card: #ffffff;
      --text: #1f2430;
      --muted: #5f6b7a;
      --accent: #3b82f6;
      --border: #d7deea;
    }
    body {
      margin: 0;
      padding: 24px;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    h1 { margin-top: 0; }
    .panel {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 16px;
    }
    textarea {
      width: 100%;
      min-height: 180px;
      box-sizing: border-box;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 13px;
      resize: vertical;
    }
    button {
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 14px;
      cursor: pointer;
    }
    button:disabled {
      opacity: 0.4;
      cursor: not-allowed;
    }
    .actions { display: flex; gap: 8px; margin-top: 10px; }
    .error { color: #b42318; font-weight: 600; margin-top: 8px; }
    .meta { color: var(--muted); margin: 0 0 10px 0; }
    .question { margin: 6px 0; }
    .model-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 12px;
      overflow-x: auto;
      align-items: stretch;
    }
    .model-card {
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      background: #fff;
      min-width: 240px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .model-name {
      font-size: 16px;
      font-weight: 700;
      margin: 0;
    }
    .label {
      font-size: 12px;
      color: var(--muted);
      margin: 0;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    .answer {
      white-space: pre-wrap;
      background: #f8fbff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px;
      margin: 0;
      flex: 1;
    }
    .nav {
      display: flex;
      gap: 8px;
      margin-top: 14px;
    }
  </style>
</head>
<body>
  <h1>LLM 답변 비교 웹페이지</h1>
  <div class="panel">
    <p class="meta">1) JSON 붙여넣기 또는 파일 선택 → 2) <strong>데이터 확인</strong> 버튼 클릭</p>
    <input id="jsonFile" type="file" accept="application/json,.json" />
    <textarea id="jsonInput" placeholder='[{"sessionNumber":1,"question":"질문","questionKorean":"한글질문","models":[{"name":"model1","original":"...","korean":"..."}]}]'>{{ initial_json_text }}</textarea>
    <div class="actions">
      <button id="validateBtn" type="button">데이터 확인</button>
      <button id="loadSampleBtn" type="button">샘플 채우기</button>
    </div>
    <div id="errorMessage" class="error"></div>
  </div>

  <div class="panel" id="viewer" hidden>
    <p class="meta" id="sessionMeta"></p>
    <p class="question" id="questionOriginal"></p>
    <p class="question" id="questionKorean"></p>
    <div class="model-grid" id="modelGrid"></div>
    <div class="nav">
      <button id="prevBtn" type="button">이전</button>
      <button id="nextBtn" type="button">다음</button>
    </div>
  </div>

  <script>
    const jsonInput = document.getElementById('jsonInput');
    const validateBtn = document.getElementById('validateBtn');
    const jsonFile = document.getElementById('jsonFile');
    const loadSampleBtn = document.getElementById('loadSampleBtn');
    const errorMessage = document.getElementById('errorMessage');

    const viewer = document.getElementById('viewer');
    const sessionMeta = document.getElementById('sessionMeta');
    const questionOriginal = document.getElementById('questionOriginal');
    const questionKorean = document.getElementById('questionKorean');
    const modelGrid = document.getElementById('modelGrid');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    let sessions = [];
    let currentIndex = 0;

    function renderSession() {
      if (!sessions.length) {
        viewer.hidden = true;
        return;
      }
      const session = sessions[currentIndex];

      viewer.hidden = false;
      sessionMeta.textContent = `세션 ${session.sessionNumber} (${currentIndex + 1}/${sessions.length})`;
      questionOriginal.textContent = `Q(EN): ${session.question}`;
      questionKorean.textContent = `Q(KO): ${session.questionKorean}`;

      modelGrid.innerHTML = '';
      session.models.forEach((model) => {
        const card = document.createElement('div');
        card.className = 'model-card';
        card.innerHTML = `
          <p class="model-name">${model.name}</p>
          <p class="label">Original</p>
          <p class="answer">${model.original}</p>
          <p class="label">Korean</p>
          <p class="answer">${model.korean}</p>
        `;
        modelGrid.appendChild(card);
      });

      prevBtn.disabled = currentIndex === 0;
      nextBtn.disabled = currentIndex === sessions.length - 1;
    }


    jsonFile.addEventListener('change', async (event) => {
      const file = event.target.files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        jsonInput.value = text;
      } catch (err) {
        errorMessage.textContent = `파일 읽기 실패: ${err.message}`;
      }
    });

    function normalizeAndValidateClient(rawData) {
      if (!Array.isArray(rawData)) {
        throw new Error('최상위 JSON 형식은 배열(list)이어야 합니다.');
      }

      const normalized = rawData.map((item, index) => {
        if (typeof item !== 'object' || item === null || Array.isArray(item)) {
          throw new Error(`${index + 1}번째 항목은 객체(object)여야 합니다.`);
        }
        const { sessionNumber, question, questionKorean, models } = item;
        if (!Number.isInteger(sessionNumber)) {
          throw new Error(`${index + 1}번째 sessionNumber는 정수여야 합니다.`);
        }
        if (typeof question !== 'string') {
          throw new Error(`${index + 1}번째 question은 문자열이어야 합니다.`);
        }
        if (typeof questionKorean !== 'string') {
          throw new Error(`${index + 1}번째 questionKorean은 문자열이어야 합니다.`);
        }
        if (!Array.isArray(models)) {
          throw new Error(`${index + 1}번째 models는 배열(list)이어야 합니다.`);
        }

        const normalizedModels = models.map((model, modelIndex) => {
          if (typeof model !== 'object' || model === null || Array.isArray(model)) {
            throw new Error(`${index + 1}번째 세션의 ${modelIndex + 1}번째 모델 데이터는 객체여야 합니다.`);
          }
          const { name, original, korean } = model;
          if (typeof name !== 'string') {
            throw new Error(`${index + 1}번째 세션의 ${modelIndex + 1}번째 model.name은 문자열이어야 합니다.`);
          }
          if (typeof original !== 'string') {
            throw new Error(`${index + 1}번째 세션의 ${modelIndex + 1}번째 model.original은 문자열이어야 합니다.`);
          }
          if (typeof korean !== 'string') {
            throw new Error(`${index + 1}번째 세션의 ${modelIndex + 1}번째 model.korean은 문자열이어야 합니다.`);
          }
          return { name, original, korean };
        });

        return { sessionNumber, question, questionKorean, models: normalizedModels };
      });

      normalized.sort((a, b) => a.sessionNumber - b.sessionNumber);
      return normalized;
    }

    function validateAndLoad() {
      errorMessage.textContent = '';
      viewer.hidden = true;

      let parsed;
      try {
        parsed = JSON.parse(jsonInput.value);
      } catch (err) {
        errorMessage.textContent = `JSON 파싱 오류: ${err.message}`;
        return;
      }

      try {
        sessions = normalizeAndValidateClient(parsed);
      } catch (err) {
        errorMessage.textContent = err.message;
        return;
      }

      currentIndex = 0;
      renderSession();
    }

    validateBtn.addEventListener('click', validateAndLoad);

    prevBtn.addEventListener('click', () => {
      if (currentIndex > 0) {
        currentIndex -= 1;
        renderSession();
      }
    });

    nextBtn.addEventListener('click', () => {
      if (currentIndex < sessions.length - 1) {
        currentIndex += 1;
        renderSession();
      }
    });

    loadSampleBtn.addEventListener('click', () => {
      jsonInput.value = JSON.stringify([
        {
          sessionNumber: 1,
          question: 'What is the capital of France?',
          questionKorean: '프랑스의 수도는 어디인가요?',
          models: [
            { name: 'model1', original: 'The capital is Paris.', korean: '수도는 파리입니다.' },
            { name: 'model2', original: 'France\'s capital city is Paris.', korean: '프랑스의 수도 도시는 파리입니다.' }
          ]
        },
        {
          sessionNumber: 2,
          question: 'Explain photosynthesis briefly.',
          questionKorean: '광합성을 간단히 설명해 주세요.',
          models: [
            { name: 'model1', original: 'Plants convert light into energy.', korean: '식물은 빛을 에너지로 전환합니다.' },
            { name: 'model2', original: 'Photosynthesis uses sunlight to make glucose.', korean: '광합성은 햇빛을 이용해 포도당을 만듭니다.' }
          ]
        }
      ], null, 2);
    });
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM 답변 비교용 Flask 웹앱")
    parser.add_argument(
        "--json-path",
        type=str,
        default="",
        help="시작 시 textarea에 미리 채울 JSON 파일 경로",
    )
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.json_path:
        path = Path(args.json_path).expanduser()
        INITIAL_JSON_TEXT = path.read_text(encoding="utf-8")

    app.run(host=args.host, port=args.port, debug=args.debug)
