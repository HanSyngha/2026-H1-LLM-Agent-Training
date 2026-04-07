# SSO 실습

> 제공된 Streamlit 앱에 SSO 로그인을 연동하세요.

## 시작

```bash
pip install streamlit requests PyJWT
streamlit run app.py --server.port 3000
```

http://localhost:3000 에 접속하면 로그인 버튼만 있는 빈 앱이 뜹니다.
바이브 코딩으로 이 앱에 SSO 로그인을 연동하세요.

## 인증 서버 정보

| 항목 | 값 |
|------|---|
| 인증 서버 | `http://a2g.samsungds.net:8090` |
| Authorize | `GET http://a2g.samsungds.net:8090/oidc/authorize` |
| Token | `POST http://a2g.samsungds.net:8090/oidc/token` |
| UserInfo | `GET http://a2g.samsungds.net:8090/oidc/userinfo` |
| Client ID | `cli-default` |
| Client Secret | `""` (빈 문자열) |
| 프로토콜 | HTTP (nginx가 내부에서 HTTPS 처리) |

---

## 과제 1: OAuth2

app.py를 수정하여 OAuth2 로그인을 연동하세요.
로그인 성공 시 본인의 **이름(한글)**과 **부서(한글)**가 화면에 표시되면 성공입니다.

### 성공 화면

```
✅ 로그인 성공!
이름: 홍길동
부서: 개발팀
```

### 제출

```
POST https://a2g.samsungds.net:47777/challenges/sso_oauth2/submit
{"token": "access_token", "answer": {"name": "홍길동", "dept": "개발팀"}}
```

---

## 과제 2: OIDC

같은 앱에서 `/userinfo` 호출 없이, `id_token` JWT 디코딩만으로 이름/부서를 표시하세요.

### 제출

```
POST https://a2g.samsungds.net:47777/challenges/sso_oidc/submit
{"token": "access_token", "answer": {"name": "홍길동", "dept": "개발팀", "method": "oidc"}}
```

---

## 막히면? 예시 답안 프롬프트

### 과제 1 (OAuth2)

```
이 Streamlit 앱(app.py)에 OAuth2 로그인을 연동해줘.

인증 서버: http://a2g.samsungds.net:8090
Authorize: GET /oidc/authorize
Token: POST /oidc/token
UserInfo: GET /oidc/userinfo
client_id: cli-default
client_secret: 빈 문자열 (Basic Auth에서 password 비움)
redirect_uri: http://localhost:3000
scope: openid
response_type: code
SSL: verify=False

로그인 성공하면 st.session_state.user에 이름/부서 저장하고 화면에 표시해줘.
access_token도 st.session_state.access_token에 저장해줘.
```

### 과제 2 (OIDC)

```
이 Streamlit 앱에 OIDC 로그인을 연동해줘.

OAuth2와 같은 서버인데 다른 점:
- scope를 "openid profile email"로 변경
- authorize에 nonce 파라미터 추가 (UUID, 필수 — 없으면 id_token 안 옴)
- token 응답에서 id_token 필드를 PyJWT로 디코딩
  jwt.decode(id_token, options={"verify_signature": False})
- /userinfo 호출 하지 마. claims의 name, dept 사용

나머지는 OAuth2와 동일 (client_id, SSL 등)
```
