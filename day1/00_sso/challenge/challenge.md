# SSO 실습

> 제공된 Streamlit 앱에 OIDC 로그인을 연동하세요.

## 시작

```bash
pip install streamlit requests PyJWT
streamlit run app.py --server.port 3000
```

http://localhost:3000 에 접속하면 로그인 버튼만 있는 빈 앱이 뜹니다.
바이브 코딩으로 이 앱에 OIDC 로그인을 연동하세요.

## 인증 서버 정보

| 항목 | 값 |
|------|---|
| 인증 서버 | `https://auth.example.com` |
| Authorize | `GET https://auth.example.com/oidc/authorize` |
| Token | `POST https://auth.example.com/oidc/token` |
| Client ID | `cli-default` |
| Client Secret | `""` (빈 문자열) |
| 프로토콜 | HTTP |

## 과제: OIDC 로그인

app.py를 수정하여 OIDC 로그인을 연동하세요.
`/userinfo` 호출 없이, `id_token` JWT 디코딩만으로 이름/부서를 표시하세요.
로그인 성공 시 앱 내 "Challenge 서버에 제출" 버튼을 눌러 제출하세요.

### 성공 화면

```
✅ OIDC 로그인 성공!
이름: 홍길동
부서: 개발팀
```

### 제출

앱 내 제출 버튼 클릭 → `POST http://challenge.example.com:47777/challenges/sso_oidc/submit`

---

## 막히면? 예시 답안 프롬프트

```
이 Streamlit 앱(app.py)에 OIDC 로그인을 연동해줘.

인증 서버: https://auth.example.com
Authorize: GET /oidc/authorize
Token: POST /oidc/token
client_id: cli-default
client_secret: 빈 문자열 (Basic Auth에서 password 비움)
redirect_uri: http://localhost:3000
scope: openid profile email
response_type: code
nonce: UUID로 생성 (필수! 없으면 id_token 안 옴)

token 응답에서 id_token을 PyJWT로 디코딩해서 이름/부서 추출해줘.
jwt.decode(id_token, options={"verify_signature": False})
claims의 name이 이름, dept가 부서야.
/userinfo 호출 하지 마.

로그인 성공하면 st.session_state.user에 저장하고
st.session_state.access_token에 토큰 저장하고
st.session_state.method에 "oidc" 저장해줘.
```
