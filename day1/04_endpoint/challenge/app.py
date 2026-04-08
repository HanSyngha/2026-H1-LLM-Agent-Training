"""
LLM Gateway 연결 실습 — Streamlit 챗봇

실행: pip install streamlit requests PyJWT
     streamlit run app.py --server.port 3000
접속: http://localhost:3000

과제: 사내 LLM Gateway에 requests로 요청을 보내서 응답을 받으세요.
      SSO 로그인은 자동으로 처리됩니다.
      TODO 부분만 채우면 됩니다!
"""

import uuid
import urllib.parse

import jwt
import requests
import streamlit as st

st.set_page_config(page_title="LLM 챗봇 실습", page_icon="🤖", layout="centered")

# ============================================
# 서버 정보
# ============================================
CHALLENGE_SERVER = "http://a2g.samsungds.net:47777"
AUTH_SERVER = "http://a2g.samsungds.net:8090"
LLM_GATEWAY = "http://a2g.samsungds.net:8090/v1"
SERVICE_ID = "test-service"

# OIDC 설정
CLIENT_ID = "cli-default"
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:3000"
SCOPE = "openid profile email"

# ============================================
# 세션 상태 초기화
# ============================================
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "challenge_passed" not in st.session_state:
    st.session_state.challenge_passed = False

# ============================================
# OIDC 콜백 처리
# ============================================
query_params = st.query_params
if "code" in query_params and st.session_state.user is None:
    code = query_params["code"]
    try:
        token_resp = requests.post(
            f"{AUTH_SERVER}/oidc/token",
            auth=(CLIENT_ID, CLIENT_SECRET),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )
        if token_resp.status_code == 200:
            token_data = token_resp.json()
            access_token = token_data.get("access_token")
            id_token = token_data.get("id_token")
            if id_token:
                claims = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["HS256"])
                st.session_state.user = {
                    "sub": claims.get("sub", ""),
                    "name": claims.get("name", ""),
                    "dept": claims.get("dept", ""),
                    "email": claims.get("email", ""),
                }
                st.session_state.access_token = access_token
                st.query_params.clear()
                st.rerun()
    except Exception as e:
        st.error(f"로그인 처리 실패: {e}")

# ============================================
# 로그인 안 됨 → 자동 SSO 리다이렉트
# ============================================
if st.session_state.user is None:
    nonce = uuid.uuid4().hex[:8]
    state = uuid.uuid4().hex[:8]
    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
        "nonce": nonce,
    })
    login_url = f"{AUTH_SERVER}/oidc/authorize?{params}"

    st.markdown(
        f'<meta http-equiv="refresh" content="0;url={login_url}">',
        unsafe_allow_html=True,
    )
    st.info("SSO 로그인 페이지로 이동합니다...")
    st.stop()

# ============================================
# 로그인 완료 → 챗봇 UI
# ============================================
user = st.session_state.user
user_id = user.get("sub", "")

# 사이드바
with st.sidebar:
    st.success(f"✅ {user.get('name', user_id)}님 로그인됨")
    st.caption(f"사번: {user_id}")
    st.caption(f"부서: {user.get('dept', '-')}")
    st.markdown("---")
    st.markdown("### Gateway 연결 정보")
    st.code(
        f"URL: {LLM_GATEWAY}/chat/completions\n"
        f"x-service-id: {SERVICE_ID}\n"
        f"x-user-id: {user_id}",
        language="text",
    )
    if st.session_state.challenge_passed:
        st.success("🎉 과제 자동 제출 완료!")
    st.markdown("---")
    if st.button("🔓 로그아웃"):
        for key in ["user", "access_token", "messages", "challenge_passed"]:
            st.session_state[key] = None
        st.session_state.messages = []
        st.rerun()

st.title("🤖 사내 LLM 챗봇")
st.markdown("---")

# 채팅 히스토리
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 채팅 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("LLM 응답 대기중..."):
            # =============================================
            # TODO: 여기를 채우세요!
            # requests.post()로 사내 LLM Gateway에 요청을 보내세요.
            #
            # URL:  http://a2g.samsungds.net:8090/v1/chat/completions
            # 헤더:
            #   Content-Type: application/json
            #   x-service-id: test-service  (위의 SERVICE_ID 변수)
            #   x-user-id:                  (위의 user_id 변수)
            # body (JSON):
            #   model: "default"
            #   messages: st.session_state.messages
            #   max_tokens: 1024
            # =============================================

            resp = None  # ← 이 줄을 requests.post(...)로 바꾸세요!

            # =============================================
            # 아래는 응답 처리 + 자동 과제 제출 (수정 불필요)
            # =============================================
            if resp is None:
                st.error("❌ resp가 None입니다. 위의 TODO를 채워주세요!")
                st.session_state.messages.append(
                    {"role": "assistant", "content": "❌ TODO를 채워주세요!"}
                )
            elif resp.status_code != 200:
                error_msg = f"❌ LLM 오류 (HTTP {resp.status_code}): {resp.text[:300]}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                # 성공!
                result = resp.json()
                answer = result["choices"][0]["message"]["content"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

                # === 자동 과제 제출 ===
                if not st.session_state.challenge_passed and st.session_state.access_token:
                    try:
                        submit_resp = requests.post(
                            f"{CHALLENGE_SERVER}/challenges/endpoint/submit",
                            json={
                                "token": st.session_state.access_token,
                                "answer": {"response": answer},
                            },
                            timeout=10,
                        )
                        if submit_resp.status_code == 200:
                            submit_result = submit_resp.json()
                            if submit_result.get("passed"):
                                st.session_state.challenge_passed = True
                                st.balloons()
                                st.success(
                                    f"🎉 {submit_result.get('message', 'Endpoint 과제 통과!')}"
                                )
                    except Exception:
                        pass
