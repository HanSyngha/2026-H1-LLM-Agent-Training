# LLM Gateway 연결 실습 — 사내 LLM 챗봇

> app.py의 TODO를 채워서 사내 LLM Gateway에 연결하세요.
> SSO 로그인은 자동으로 처리됩니다.

## 실행 방법

```bash
pip install streamlit requests PyJWT
streamlit run app.py --server.port 3000
```

## 서버 정보

| 항목 | 값 |
|------|---|
| LLM Gateway | `http://a2g.samsungds.net:8090/v1/chat/completions` |
| Service ID | `test-service` (코드에 세팅됨) |
| 인증 | SSO 자동 로그인 (user_id 자동 세팅) |

## 과제

`app.py`에서 `resp = None` 부분을 `requests.post(...)`로 바꾸세요.

### 필요한 정보

```python
resp = requests.post(
    "http://a2g.samsungds.net:8090/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "x-service-id": SERVICE_ID,     # "test-service"
        "x-user-id": user_id,           # SSO user ID (자동)
    },
    json={
        "model": "testmodel",
        "messages": st.session_state.messages,
        "max_tokens": 1024,
    },
)
```

### 성공 조건

LLM에서 200 응답이 오면 자동으로 과제가 제출됩니다.

---

## 막히면? 바이브 코딩 프롬프트

```
app.py의 TODO 부분을 채워줘.
requests.post로 LLM Gateway에 요청을 보내야 해.
URL, 헤더, body 정보는 TODO 주석에 다 적혀있어.
```
