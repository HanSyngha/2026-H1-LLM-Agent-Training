"""
Tool Use (Function Calling) 실습 — Streamlit 챗봇

실행: pip install streamlit requests PyJWT
     streamlit run app.py --server.port 3000
접속: http://localhost:3000

과제: 챗봇에 2개의 Tool을 연결하세요.
      1. get_secret_key  → 서버에서 시크릿 키 발급
      2. submit_secret_key → 시크릿 키 제출
      LLM이 두 Tool을 연속 호출하면 과제 통과!

      SSO 로그인 + LLM 연결 + Agentic Loop는 이미 구현되어 있습니다.
      TODO 부분만 채우면 됩니다!
"""

import json
import uuid
import urllib.parse

import jwt
import requests
import streamlit as st

st.set_page_config(page_title="Tool Use 실습", page_icon="🔧", layout="centered")

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
for key, default in [
    ("user", None), ("access_token", None),
    ("messages", []), ("challenge_passed", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================
# OIDC 콜백 처리 (구현 완료)
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
            id_token = token_data.get("id_token")
            if id_token:
                claims = jwt.decode(id_token, options={"verify_signature": False}, algorithms=["HS256"])
                st.session_state.user = {
                    "sub": claims.get("sub", ""),
                    "name": claims.get("name", ""),
                    "dept": claims.get("dept", ""),
                    "email": claims.get("email", ""),
                }
                st.session_state.access_token = token_data.get("access_token")
                st.query_params.clear()
                st.rerun()
    except Exception as e:
        st.error(f"로그인 처리 실패: {e}")

# 로그인 안 됨 → 자동 SSO 리다이렉트
if st.session_state.user is None:
    nonce = uuid.uuid4().hex[:8]
    state = uuid.uuid4().hex[:8]
    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI,
        "response_type": "code", "scope": SCOPE,
        "state": state, "nonce": nonce,
    })
    login_url = f"{AUTH_SERVER}/oidc/authorize?{params}"
    st.markdown(f'<meta http-equiv="refresh" content="0;url={login_url}">', unsafe_allow_html=True)
    st.info("SSO 로그인 페이지로 이동합니다...")
    st.stop()

# ============================================
# 로그인 완료
# ============================================
user = st.session_state.user
user_id = user.get("sub", "")
token = st.session_state.access_token


# =============================================
# TODO 1: tools 리스트를 정의하세요!
#
# OpenAI Function Calling 형식으로 2개의 tool을 정의합니다.
#
# Tool 1: get_secret_key
#   - 설명: "과제용 시크릿 키를 발급받습니다"
#   - 파라미터: 없음
#
# Tool 2: submit_secret_key
#   - 설명: "발급받은 시크릿 키를 제출합니다"
#   - 파라미터: secret_key (string, 필수)
#
# 형식:
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "...",
#             "description": "...",
#             "parameters": {
#                 "type": "object",
#                 "properties": { ... },
#                 "required": [ ... ],
#             },
#         },
#     },
# ]
# =============================================

tools = []  # ← 여기를 채우세요!


# =============================================
# TODO 2: execute_tool 함수를 구현하세요!
#
# Tool 이름과 인자를 받아서 실제 API를 호출합니다.
#
# get_secret_key:
#   GET http://a2g.samsungds.net:47777/challenges/tool_use/secret
#   query params: token=<SSO access_token>  (위의 token 변수)
#   응답 예시: {"secret_key": "KEY-A1B2C3...", "message": "..."}
#
# submit_secret_key:
#   POST http://a2g.samsungds.net:47777/challenges/tool_use/submit
#   body: {"token": "<SSO access_token>", "answer": {"secret_key": "발급받은키"}}
#   응답 예시: {"status": "SUCCESS", "message": "🎉 통과!"}
#
# 반환값: dict (API 응답 JSON)
# =============================================

def execute_tool(tool_name, arguments):
    return {"error": "TODO 2를 구현하세요!"}  # ← 이 함수를 채우세요!


# =============================================
# LLM 호출 함수 (구현 완료)
# =============================================
def call_llm(messages):
    """LLM Gateway에 요청을 보냅니다."""
    body = {
        "model": "default",
        "messages": messages,
        "max_tokens": 1024,
    }
    if tools:
        body["tools"] = tools

    resp = requests.post(
        f"{LLM_GATEWAY}/chat/completions",
        headers={
            "Content-Type": "application/json",
            "x-service-id": SERVICE_ID,
            "x-user-id": user_id,
        },
        json=body,
        timeout=60,
    )
    if resp.status_code != 200:
        return None, f"LLM 오류 (HTTP {resp.status_code}): {resp.text[:200]}"
    return resp.json(), None


# ============================================
# Agentic Loop (구현 완료)
# tool_calls가 있으면 실행하고 LLM에 피드백하여 재호출
# ============================================
def run_agentic_loop(messages):
    """LLM을 반복 호출하여 tool_calls를 처리합니다."""
    max_iterations = 5

    for _ in range(max_iterations):
        result, error = call_llm(messages)
        if error:
            return None, error

        msg = result["choices"][0]["message"]

        # tool_calls가 없으면 → 최종 텍스트 응답
        if not msg.get("tool_calls"):
            return msg.get("content", ""), None

        # tool_calls 처리: assistant 메시지 추가
        messages.append(msg)

        for tc in msg["tool_calls"]:
            fn_name = tc["function"]["name"]
            fn_args = json.loads(tc["function"]["arguments"]) if tc["function"].get("arguments") else {}

            # Tool 실행
            tool_result = execute_tool(fn_name, fn_args)

            # submit 성공 감지
            if fn_name == "submit_secret_key" and isinstance(tool_result, dict):
                if tool_result.get("status") == "SUCCESS":
                    st.session_state.challenge_passed = True

            # Tool 결과를 messages에 추가 → LLM이 다음 단계를 판단
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": json.dumps(tool_result, ensure_ascii=False),
            })

        # 루프 계속 → 다시 call_llm()

    return "⚠️ 최대 반복 횟수 초과", None


# ============================================
# 사이드바
# ============================================
with st.sidebar:
    st.success(f"✅ {user.get('name', user_id)}님 로그인됨")
    st.caption(f"User ID: {user_id}")
    st.markdown("---")
    st.markdown("### 과제: TODO 2개 채우기")
    st.markdown("""
    **TODO 1** — `tools` 리스트 정의
    **TODO 2** — `execute_tool()` 구현

    Agentic Loop는 구현 완료!
    Tool만 연결하면 LLM이 자동 호출합니다.
    """)
    if st.session_state.challenge_passed:
        st.success("🎉 과제 통과!")
    st.markdown("---")
    if st.button("🔓 로그아웃"):
        for key in ["user", "access_token", "messages", "challenge_passed"]:
            st.session_state[key] = None
        st.session_state.messages = []
        st.rerun()

# ============================================
# 챗봇 UI (구현 완료)
# ============================================
st.title("🔧 Tool Use 실습 챗봇")
st.caption("'과제 제출해줘'라고 입력하면 LLM이 Tool을 호출합니다.")
st.markdown("---")

for msg in st.session_state.messages:
    if msg["role"] in ("user", "assistant") and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("'과제 제출해줘'라고 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("LLM 처리 중..."):
            answer, error = run_agentic_loop(st.session_state.messages)

            if error:
                st.error(f"❌ {error}")
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {error}"})
            elif answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.session_state.challenge_passed:
        st.balloons()
        st.success("🎉 Tool Use 과제 통과! LLM이 두 개의 Tool을 연속 호출했습니다.")
