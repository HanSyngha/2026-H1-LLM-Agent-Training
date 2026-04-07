# MCP Tool 호출 실습

> MCP 서버에 연결하여 3가지 도구를 호출하세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `https://a2g.samsungds.net:70777` |
| MCP 서버 | 수강생이 직접 실행: `python day1/01_mcp/mcp_server.py` |
| 미션 조회 | `GET https://a2g.samsungds.net:70777/challenges/mcp/mission` |
| 정답 제출 | `POST https://a2g.samsungds.net:70777/challenges/mcp/submit` |

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
