# 프롬프트 엔지니어링 실습

> AI를 적극 활용하세요. 강의에서 배운 프롬프트 설계 원칙을 AI에게 정확히 전달해야 합니다.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `https://a2g.samsungds.net:70777` |
| 인증 서버 | `https://a2g.samsungds.net:8090` |
| 미션 조회 | `GET https://a2g.samsungds.net:70777/challenges/prompt/mission` |
| 정답 제출 | `POST https://a2g.samsungds.net:70777/challenges/prompt/submit` |

## 과제

미션 3개(감정 분류, 요약, 정보 추출)를 LLM으로 해결하고 결과를 제출하세요.

### 제출 형식

```json
{
  "token": "<SSO access_token>",
  "answer": {
    "classify": "긍정 / 부정 / 중립 / 혼합",
    "summarize": "3문장 이내 요약",
    "extract": {"date": "...", "time": "...", "location": "...", "attendees": [...]}
  }
}
```

### 성공 화면

```
🎉 홍길동님, 프롬프트 엔지니어링 통과!
3/3 미션 통과
```
