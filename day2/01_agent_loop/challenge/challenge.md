# Agentic Loop 실습

> requests만 사용하여 Agent Loop를 구현하고, 복합 질문에 답하세요. 프레임워크 사용 금지.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `https://a2g.samsungds.net:70777` |
| LLM Gateway | `.env` 파일의 `LLM_GATEWAY_URL` 참고 |
| 미션 조회 | `GET https://a2g.samsungds.net:70777/challenges/agent_loop/mission` |
| 정답 제출 | `POST https://a2g.samsungds.net:70777/challenges/agent_loop/submit` |

## 과제

미션의 복합 질문을 Agent Loop (LLM + Tool Calling 반복)로 해결하고 최종 답을 제출하세요.

### 제출 형식

```json
{
  "token": "<SSO access_token>",
  "answer": {
    "response": "섭씨: X°C, 화씨: Y°F"
  }
}
```

### 성공 화면

```
🎉 홍길동님, Agentic Loop 통과!
Agent Loop 응답 검증 통과
```
