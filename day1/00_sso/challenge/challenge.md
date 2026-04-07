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

---

## 막히면? 예시 답안 프롬프트

> 아래는 AI에게 이렇게 말하면 된다는 참고용입니다. 본인 상황에 맞게 수정하세요.

### 과제 1 (OAuth2)

```
Python FastAPI로 OAuth2 Authorization Code Flow 클라이언트를 만들어줘.

- 인증 서버: https://a2g.samsungds.net:8090
- Discovery URL: https://a2g.samsungds.net:8090/.well-known/openid-configuration
- client_id: cli-default
- client_secret: 빈 문자열 (없음)
- redirect_uri: http://localhost:3000/callback
- scope: openid

주의사항:
- SSL 인증서가 사내 자체 인증서라서 verify=False 필요
- client_secret이 빈 문자열이니 Basic Auth에서 password를 비워둬야 함
- /login 접속 시 authorize URL로 리다이렉트
- /callback에서 code 받아서 /oidc/token으로 교환
- access_token으로 /oidc/userinfo 호출해서 이름/부서 표시
```

### 과제 2 (OIDC)

```
위 코드를 수정해서 OIDC 방식으로 바꿔줘.

- scope를 "openid profile email"로 변경
- authorize 요청에 nonce 파라미터 추가 (UUID로 생성)
- token 응답에서 id_token 필드를 JWT 디코딩
- /userinfo 호출 없이 id_token의 claims에서 이름/부서 추출
- nonce가 없으면 id_token이 안 오니까 반드시 포함

PyJWT로 디코딩할 때 verify_signature=False로 해줘.
```
