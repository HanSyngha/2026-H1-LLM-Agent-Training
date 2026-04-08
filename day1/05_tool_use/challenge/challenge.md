# Tool Use (Function Calling) 실습

> LLM에 Tool을 연결하고, 시크릿 키를 받아 제출하세요.

## 실행 방법

```bash
pip install streamlit requests PyJWT
streamlit run app.py --server.port 3000
```

## 과제 흐름

```
사용자: "과제 제출해줘"
  ↓
LLM: get_secret_key 호출 (Tool Call #1)
  ↓
서버: {"secret_key": "KEY-A1B2C3..."} 반환
  ↓  (결과를 LLM에게 피드백)
LLM: submit_secret_key 호출 (Tool Call #2)
  ↓
서버: "과제 통과!" 반환
  ↓
챗봇: 성공 메시지 출력
```

## TODO (2개만 채우면 됩니다)

### TODO 1: tools 리스트 정의

OpenAI Function Calling 형식으로 2개 tool을 정의하세요.

| Tool | 설명 | 파라미터 |
|------|------|----------|
| `get_secret_key` | 시크릿 키 발급 | 없음 |
| `submit_secret_key` | 시크릿 키 제출 | `secret_key` (string) |

### TODO 2: Agentic Loop 구현

LLM 응답에 `tool_calls`가 있으면:
1. `execute_tool()`로 실행
2. 결과를 messages에 추가
3. 다시 `call_llm()` 호출
4. `tool_calls`가 없을 때까지 반복

## 서버 API

| Endpoint | 설명 |
|----------|------|
| `GET /challenges/tool_use/secret?token=SSO토큰` | 시크릿 키 발급 |
| `POST /challenges/tool_use/submit` | 시크릿 키로 과제 제출 |

---

## 막히면? 바이브 코딩 프롬프트

```
app.py의 TODO 1과 TODO 2를 채워줘.

TODO 1: OpenAI Function Calling 형식으로 tools 리스트를 만들어.
- get_secret_key: 파라미터 없음
- submit_secret_key: secret_key (string) 파라미터

TODO 2: Agentic Loop를 구현해.
- call_llm() 호출 후 응답에 tool_calls가 있으면
- execute_tool()로 실행하고 결과를 messages에 추가
- 다시 call_llm() 호출, tool_calls 없을 때까지 반복
```
