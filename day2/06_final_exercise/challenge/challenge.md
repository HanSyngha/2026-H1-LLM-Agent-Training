# 종합 실습

> 브라우저 검색 → 데이터 추출 → 정리하여 제출하는 전체 파이프라인을 자동화하세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `https://a2g.samsungds.net:70777` |
| 미션 조회 | `GET https://a2g.samsungds.net:70777/challenges/final/mission` |
| 정답 제출 | `POST https://a2g.samsungds.net:70777/challenges/final/submit` |

## 과제

미션에서 지정한 키워드로 검색하여 상위 결과의 제목과 링크를 추출하고 제출하세요.

### 제출 형식

```json
{
  "token": "<SSO access_token>",
  "answer": {
    "items": [
      {"title": "기사 제목", "link": "https://..."},
      ...
    ]
  }
}
```

### 성공 화면

```
🎉 홍길동님, 종합 실습 통과!
5개 항목 검증 통과
```
