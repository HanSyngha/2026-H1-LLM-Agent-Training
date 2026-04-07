# LLM Endpoint 연결 실습

> 사내 LLM Gateway에 연결하여 첫 번째 응답을 받아오세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `https://a2g.samsungds.net:70777` |
| 인증 서버 | `https://a2g.samsungds.net:8090` |
| LLM Gateway | `.env` 파일의 `LLM_GATEWAY_URL` 참고 |
| 미션 조회 | `GET https://a2g.samsungds.net:70777/challenges/endpoint/mission` |
| 정답 제출 | `POST https://a2g.samsungds.net:70777/challenges/endpoint/submit` |

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
