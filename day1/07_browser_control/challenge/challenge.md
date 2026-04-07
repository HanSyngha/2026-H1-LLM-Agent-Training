# 브라우저 자동화 실습 (Windows CDP)

> 타겟 페이지는 JavaScript로 렌더링됩니다. `requests.get()`으로는 데이터를 가져올 수 없습니다.
> Chrome CDP를 사용하여 데이터를 추출하세요.

## 서버 정보

| 항목 | 값 |
|------|---|
| Challenge 서버 | `https://a2g.samsungds.net:70777` |
| 타겟 페이지 | `https://a2g.samsungds.net:70777/browser-target` |
| 정답 제출 | `POST https://a2g.samsungds.net:70777/challenges/browser/submit` |

## 과제

타겟 페이지에서 상품 목록(이름, 가격)을 추출하고 제출하세요.

**주의**: 이 페이지는 JavaScript가 실행되어야 데이터가 표시됩니다.
Chrome을 `--remote-debugging-port` 옵션으로 실행하고, CDP로 접근해야 합니다.

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

---

## 막히면? 예시 답안 프롬프트

```
Chrome CDP로 웹페이지에서 상품 데이터를 추출하는 Python 코드를 만들어줘.

1. Chrome을 --remote-debugging-port=9222 옵션으로 실행
   (Windows: chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome)
2. CDP WebSocket으로 연결
3. https://a2g.samsungds.net:70777/browser-target 페이지로 이동
4. 이 페이지는 JavaScript로 데이터를 렌더링하므로 JS 실행 대기 필요
5. 테이블에서 제품명과 가격 추출
6. POST https://a2g.samsungds.net:70777/challenges/browser/submit 에 제출
   형식: {"token": "SSO토큰", "answer": {"products": [{"name": "...", "price": 123000}]}}

CDP 명령: Page.navigate, Runtime.evaluate 등 사용.
가격은 숫자만 (쉼표, '원' 제거).
```
