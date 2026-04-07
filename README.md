# visualize_json

`json-path` 인자로 전달한 JSON 파일을 읽어서 LLM 모델 3개의 답변을 그대로 보여주는 Flask 웹앱입니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py /path/to/data.json
```

브라우저에서 `http://127.0.0.1:5000`으로 접속하면 JSON 내용이 화면에 렌더링됩니다.
