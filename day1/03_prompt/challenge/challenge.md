# 프롬프트 엔지니어링 실습

> AI를 적극 활용하세요. 강의에서 배운 프롬프트 설계 원칙을 AI에게 정확히 전달해야 합니다.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `http://a2g.samsungds.net:47777` |
| 인증 서버 | `http://a2g.samsungds.net:8090` |
| 미션 조회 | `GET http://a2g.samsungds.net:47777/challenges/prompt/mission` |
| 정답 제출 | `POST http://a2g.samsungds.net:47777/challenges/prompt/submit` |

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

---

## 막히면? 예시 답안 프롬프트

```
사내 LLM Gateway에 연결하는 Python 스크립트를 만들어줘.

1. GET http://a2g.samsungds.net:47777/challenges/prompt/mission 으로 미션 조회
2. 미션에 3개 task가 있는데:
   - classify: 리뷰 감정 분류 (긍정/부정/중립/혼합)
   - summarize: 기술 문서 3문장 요약
   - extract: 이메일에서 날짜/시간/장소/참석자 JSON 추출
3. 각 task의 input을 LLM에게 보내서 결과 받기
4. POST http://a2g.samsungds.net:47777/challenges/prompt/submit 에 제출
   형식: {"token": "SSO토큰", "answer": {"classify": "...", "summarize": "...", "extract": {...}}}

LLM Gateway URL과 API Key는 .env 파일 참고.
```
