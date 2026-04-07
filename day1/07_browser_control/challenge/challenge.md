# 브라우저 자동화 실습

> 타겟 웹페이지에서 상품 목록을 추출하세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `https://a2g.samsungds.net:70777` |
| 타겟 페이지 | `https://a2g.samsungds.net:70777/browser-target` |
| 정답 제출 | `POST https://a2g.samsungds.net:70777/challenges/browser/submit` |

## 과제

타겟 페이지를 Playwright 등으로 접근하여 상품 데이터(이름, 가격)를 추출하고 제출하세요.

### 제출 형식

```json
{
  "token": "<SSO access_token>",
  "answer": {
    "products": [
      {"name": "제품명", "price": 123000},
      ...
    ]
  }
}
```

### 성공 화면

```
🎉 홍길동님, 브라우저 자동화 통과!
5/5 상품 데이터 일치
```
