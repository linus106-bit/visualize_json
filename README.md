# visualize_json

JSON 데이터로 LLM 모델별 답변을 비교하는 간단한 Flask 웹앱입니다.

## JSON 입력 방법

다음 두 가지 중 하나로 입력할 수 있습니다.

1. **붙여넣기**: 화면의 큰 텍스트 박스에 JSON 배열 데이터를 그대로 붙여넣기
2. **파일 업로드**: `jsonFile` 선택 버튼으로 `.json` 파일 선택 (선택 시 텍스트 박스에 자동 채움)

이후 `데이터 확인` 버튼을 누르면 세션별 비교 화면이 열립니다.
(`데이터 확인`은 브라우저 내에서 바로 검증/렌더링하므로 서버 API 호출 문제와 무관하게 동작합니다.)

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://127.0.0.1:5000` 접속 후 JSON을 입력해 확인하세요.

## 실행 인자(args)

`app.py` 실행 시 JSON 파일 경로를 인자로 줄 수 있습니다.

```bash
python app.py --json-path ./sample.json
```

- `--json-path`: 시작할 때 textarea에 미리 채울 JSON 파일 경로
- `--host`: 기본값 `127.0.0.1`
- `--port`: 기본값 `5000`
- `--debug`: 지정하면 Flask 디버그 모드 활성화
