# 종합 실습

> 브라우저 검색 → 데이터 추출 → 정리하여 제출하는 전체 파이프라인을 자동화하세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `http://challenge.example.com:47777` |
| 미션 조회 | `GET http://challenge.example.com:47777/challenges/final/mission` |
| 정답 제출 | `POST http://challenge.example.com:47777/challenges/final/submit` |

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

---

## 막히면? 예시 답안 프롬프트

```
브라우저로 검색하고 결과를 추출하는 Agent를 만들어줘.

1. GET http://challenge.example.com:47777/challenges/final/mission 에서 검색 키워드 확인
2. Chrome CDP로 네이버/구글에서 키워드 검색
3. 검색 결과 상위 5개의 제목과 링크 추출
4. POST http://challenge.example.com:47777/challenges/final/submit 에 제출
   형식: {"token": "SSO토큰", "answer": {"items": [{"title": "...", "link": "https://..."}]}}

CDP로 검색 → 결과 페이지 대기 → DOM에서 제목/링크 추출.
requests만으로는 JS 렌더링이 안 되니 반드시 브라우저 사용.
```
