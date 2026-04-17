# MCP Tool 호출 실습

> MCP 서버에 연결하여 3가지 도구를 호출하세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `http://challenge.example.com:47777` |
| MCP 서버 | 수강생이 직접 실행: `python day1/01_mcp/mcp_server.py` |
| 미션 조회 | `GET http://challenge.example.com:47777/challenges/mcp/mission` |
| 정답 제출 | `POST http://challenge.example.com:47777/challenges/mcp/submit` |

## 과제

MCP 서버를 실행하고, 클라이언트 + LLM을 연동하여 3개 도구 호출 결과를 제출하세요.

### 제출 형식

```json
{
  "token": "<SSO access_token>",
  "answer": {
    "results": ["add 결과", "get_weather 결과", "search_employee 결과"]
  }
}
```

### 성공 화면

```
🎉 홍길동님, MCP Tool 호출 통과!
3/3 도구 호출 성공
```

---

## 막히면? 예시 답안 프롬프트

```
FastMCP 클라이언트로 MCP 서버에 연결하는 Python 코드를 만들어줘.

1. 먼저 python day1/01_mcp/mcp_server.py 로 MCP 서버 실행 (별도 터미널)
2. FastMCP Client로 서버에 연결
3. 3개 도구 호출:
   - add(a=157, b=289)
   - get_weather(city="서울")
   - search_employee(name="김")
4. 결과를 POST http://challenge.example.com:47777/challenges/mcp/submit 에 제출
   형식: {"token": "SSO토큰", "answer": {"results": ["결과1", "결과2", "결과3"]}}

FastMCP 사용법: from fastmcp import Client
async with Client("mcp_server.py") as client:
    result = await client.call_tool("add", {"a": 157, "b": 289})
```
