# SSO 실습

> AI를 적극 활용하세요. 강의에서 배운 내용을 AI에게 정확히 설명할 수 있어야 합니다.

## 서버 정보

| 항목 | 값 |
|------|---|
| 인증 서버 | `https://a2g.samsungds.net:8090` |
| Discovery | `https://a2g.samsungds.net:8090/.well-known/openid-configuration` |
| Client ID | `cli-default` |
| Client Secret | 없음 (빈 문자열) |

---

## 과제 1: OAuth2로 로그인하기

`http://localhost:<포트>` 에서 SSO 로그인 후, **본인의 이름과 부서**가 브라우저에 표시되면 성공입니다.

### 성공 화면

```
✅ OAuth2 로그인 성공!

사번: hong.gildong
이름: 홍길동
부서: 개발팀
이메일: hong.gildong@samsung.com

방식: access_token으로 /userinfo API를 호출
```

---

## 과제 2: OIDC로 로그인하기

과제 1과 같은 결과를, **`/userinfo` API를 호출하지 않고** 달성하세요.

### 성공 화면

```
✅ OIDC 로그인 성공!

사번: hong.gildong
이름: 홍길동
부서: 개발팀

방식: id_token JWT 디코딩 — /userinfo 호출 없음
nonce 검증: ✅ 일치
```
