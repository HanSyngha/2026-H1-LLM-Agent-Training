# LLM Endpoint 연결 실습

> 사내 LLM Gateway에 연결하여 첫 번째 응답을 받아오세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `http://a2g.samsungds.net:47777` |
| 인증 서버 | `http://a2g.samsungds.net:8090` |
| LLM Gateway | `.env` 파일의 `LLM_GATEWAY_URL` 참고 |
| 미션 조회 | `GET http://a2g.samsungds.net:47777/challenges/endpoint/mission` |
| 정답 제출 | `POST http://a2g.samsungds.net:47777/challenges/endpoint/submit` |

## 과제

LLM Gateway에 연결하여 미션 질문에 대한 응답을 받아 제출하세요.

### 제출 형식

```json
{
  "token": "<SSO access_token>",
  "answer": {
    "response": "LLM이 응답한 전체 텍스트"
  }
}
```

### 성공 화면

```
🎉 홍길동님, LLM Endpoint 연결 통과!
LLM Gateway 연결 및 응답 확인 완료
```

---

## 막히면? 예시 답안 프롬프트

```
Python requests로 사내 LLM Gateway에 연결해서 질문에 답변 받는 코드를 만들어줘.

- LLM Gateway URL: .env의 LLM_GATEWAY_URL (OpenAI Compatible)
- 질문: "대한민국의 수도는 어디이며, 그 도시의 영문명을 알려주세요."
- 응답을 받아서 POST http://a2g.samsungds.net:47777/challenges/endpoint/submit 에 제출
- 제출 형식: {"token": "SSO토큰", "answer": {"response": "LLM 응답 텍스트"}}

OpenAI Compatible이니까 /v1/chat/completions 엔드포인트에
{"model": "모델명", "messages": [{"role": "user", "content": "질문"}]} 보내면 됨.
```
