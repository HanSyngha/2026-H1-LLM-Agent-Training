# Agentic Loop 실습

> requests만 사용하여 Agent Loop를 구현하고, 복합 질문에 답하세요. 프레임워크 사용 금지.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `http://challenge.example.com:47777` |
| LLM Gateway | `.env` 파일의 `LLM_GATEWAY_URL` 참고 |
| 미션 조회 | `GET http://challenge.example.com:47777/challenges/agent_loop/mission` |
| 정답 제출 | `POST http://challenge.example.com:47777/challenges/agent_loop/submit` |

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

---

## 막히면? 예시 답안 프롬프트

```
Python requests만 사용해서 Agent Loop를 구현해줘. 프레임워크 쓰지 마.

1. GET http://challenge.example.com:47777/challenges/agent_loop/mission 에서 미션 확인
2. LLM Gateway에 tool_calls를 지원하는 도구 정의:
   - get_weather(city): 도시 날씨 조회
   - calculate(expression): 수학 계산
3. Agent Loop 구현:
   - 사용자 질문 + tools를 LLM에 전송
   - 응답에 tool_calls가 있으면 → 도구 실행 → 결과를 messages에 추가 → 다시 LLM 호출
   - tool_calls가 없으면 최종 답변
4. 최종 답변을 POST http://challenge.example.com:47777/challenges/agent_loop/submit 에 제출
   형식: {"token": "SSO토큰", "answer": {"response": "섭씨: X°C, 화씨: Y°F"}}

OpenAI Compatible /v1/chat/completions 에 tools 파라미터로 도구 정의.
응답의 choices[0].message.tool_calls 파싱.
```
