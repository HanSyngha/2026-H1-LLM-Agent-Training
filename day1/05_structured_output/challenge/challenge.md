# Structured Output 실습

> 뉴스 기사를 분석하여 구조화된 JSON으로 추출하세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `https://a2g.samsungds.net:47777` |
| 미션 조회 | `GET https://a2g.samsungds.net:47777/challenges/structured/mission` |
| 정답 제출 | `POST https://a2g.samsungds.net:47777/challenges/structured/submit` |

## 과제

미션에서 제공하는 뉴스 기사를 LLM의 Structured Output 기능으로 분석하여 제출하세요.

### 제출 형식

```json
{
  "token": "<SSO access_token>",
  "answer": {
    "title": "기사 제목",
    "category": "기술/경제/정치/사회/스포츠",
    "sentiment": "긍정/부정/중립",
    "keywords": ["키워드1", "키워드2", "키워드3"],
    "summary": "2문장 이내 요약"
  }
}
```

### 성공 화면

```
🎉 홍길동님, Structured Output 통과!
5/5 필드 검증 통과
```

---

## 막히면? 예시 답안 프롬프트

```
Python으로 LLM의 Structured Output 기능을 사용해서 뉴스 기사를 분석하는 코드를 만들어줘.

1. GET https://a2g.samsungds.net:47777/challenges/structured/mission 에서 뉴스 기사 받기
2. LLM에게 response_format으로 JSON Schema를 지정해서 분석 요청
   필요한 필드: title, category(기술/경제/정치/사회/스포츠), sentiment(긍정/부정/중립), keywords(3~5개 배열), summary(2문장)
3. POST https://a2g.samsungds.net:47777/challenges/structured/submit 에 제출
   형식: {"token": "SSO토큰", "answer": {title, category, sentiment, keywords, summary}}

OpenAI Compatible의 response_format: {"type": "json_object"} 사용.
```
