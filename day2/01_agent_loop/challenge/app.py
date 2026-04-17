"""
Agentic Loop 실습 — API 미로 탈출 챗봇

실행: pip install streamlit requests PyJWT
     streamlit run app.py --server.port 3000
접속: http://localhost:3000

과제: Agentic Loop(while 루프)를 구현하세요.
      LLM이 Tool을 호출하면 실행하고 결과를 피드백하여 재호출을 유도합니다.
      API 미로: start → 3개 스텝 순서대로 → end → completion_code 획득!

      SSO, LLM 연결, tools, execute_tool 모두 구현 완료.
      TODO: agentic loop (while 루프) 하나만 채우면 됩니다!
"""

import json
import uuid
import urllib.parse

import jwt
import requests
import streamlit as st

st.set_page_config(page_title="Agentic Loop 실습", page_icon="🔄", layout="centered")

# ============================================
# 서버 정보
# ============================================
CHALLENGE_SERVER = "http://challenge.example.com:47777"
AUTH_SERVER = "https://auth.example.com"
LLM_GATEWAY = "https://llm-gateway.example.com/v1"
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
    ("completion_code", None),
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


# ============================================
# Tool 정의 (구현 완료) — API 미로용 4개 tool
# ============================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "maze_start",
            "description": "API 미로를 시작합니다. 3개의 스텝 순서가 안내됩니다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "maze_step",
            "description": "미로의 특정 스텝을 호출합니다. 순서대로 호출해야 하며, 틀리면 초기화됩니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "step_number": {"type": "integer", "description": "호출할 스텝 번호 (1~10)"},
                },
                "required": ["step_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "maze_end",
            "description": "미로를 종료하고 completion_code를 받습니다. 3개 스텝을 모두 완료한 후 호출하세요.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


# ============================================
# Tool 실행 함수 (구현 완료)
# ============================================
def execute_tool(tool_name, arguments):
    """Tool 이름과 인자를 받아 실제 API를 호출합니다."""
    if tool_name == "maze_start":
        resp = requests.get(
            f"{CHALLENGE_SERVER}/challenges/agent_loop/start",
            params={"token": token},
            timeout=10,
        )
        return resp.json()

    elif tool_name == "maze_step":
        step_num = arguments.get("step_number", 0)
        resp = requests.get(
            f"{CHALLENGE_SERVER}/challenges/agent_loop/step/{step_num}",
            params={"token": token},
            timeout=10,
        )
        return resp.json()

    elif tool_name == "maze_end":
        resp = requests.get(
            f"{CHALLENGE_SERVER}/challenges/agent_loop/end",
            params={"token": token},
            timeout=10,
        )
        result = resp.json()
        # completion_code 저장
        if result.get("completion_code"):
            st.session_state.completion_code = result["completion_code"]
        return result

    return {"error": f"알 수 없는 tool: {tool_name}"}


# ============================================
# System Prompt (구현 완료)
# ============================================
SYSTEM_PROMPT = """당신은 API 미로를 풀어주는 에이전트입니다.

사용자가 미로 풀기를 요청하면:
1. maze_start를 호출하여 3개 스텝의 순서를 확인합니다.
2. 안내된 순서대로 maze_step을 호출합니다 (순서를 틀리면 초기화!).
3. 3개 스텝을 모두 완료하면 maze_end를 호출하여 completion_code를 받습니다.
4. 결과를 사용자에게 알려줍니다.

반드시 start가 알려준 순서를 정확히 따르세요."""


# ============================================
# LLM 호출 함수 (구현 완료)
# ============================================
def call_llm(messages):
    """LLM Gateway에 요청을 보냅니다."""
    all_messages = messages
    if not any(m.get("role") == "system" for m in messages):
        all_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    body = {
        "model": "testmodel",
        "messages": all_messages,
        "max_tokens": 1024,
        "tools": tools,
        "tool_choice": "auto",
    }

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


# =============================================
# TODO: Agentic Loop를 구현하세요!
#
# call_llm()을 호출하고, 응답에 tool_calls가 있으면
# execute_tool()로 실행 → 결과를 messages에 추가 → 다시 call_llm()
# tool_calls가 없을 때까지 반복합니다.
#
# 구현 가이드:
# 1. while 루프 (최대 10회 반복)
# 2. result, error = call_llm(messages) 호출
# 3. error면 return None, error
# 4. msg = result["choices"][0]["message"]
# 5. msg에 tool_calls가 없으면 → return msg.get("content"), None
# 6. tool_calls가 있으면:
#    a. messages.append(msg)  # assistant의 tool_calls 메시지
#    b. 각 tool_call에 대해:
#       - fn_name = tc["function"]["name"]
#       - fn_args = json.loads(tc["function"]["arguments"]) if tc["function"].get("arguments") else {}
#       - tool_result = execute_tool(fn_name, fn_args)
#       - messages.append({"role": "tool", "tool_call_id": tc["id"],
#                          "content": json.dumps(tool_result, ensure_ascii=False)})
#    c. 루프 계속 (다시 call_llm)
# =============================================

def run_agentic_loop(messages):
    """LLM을 반복 호출하여 tool_calls를 처리합니다."""

    # TODO를 구현하기 전에는 에러 반환
    return None, "❌ run_agentic_loop()가 구현되지 않았습니다. TODO를 채워주세요!"


# ============================================
# 사이드바
# ============================================
with st.sidebar:
    st.success(f"✅ {user.get('name', user_id)}님 로그인됨")
    st.caption(f"User ID: {user_id}")
    st.markdown("---")
    st.markdown("### 과제: Agentic Loop 구현")
    st.markdown("""
    **TODO** — `run_agentic_loop()` 함수에
    while 루프를 구현하세요.

    `call_llm()`, `execute_tool()`,
    `tools`, `SYSTEM_PROMPT` 모두 완료!
    **루프만 짜면 됩니다.**
    """)
    if st.session_state.completion_code:
        st.success(f"🔑 {st.session_state.completion_code}")
    if st.session_state.challenge_passed:
        st.success("🎉 과제 통과!")
    st.markdown("---")
    if st.button("🔓 로그아웃"):
        for key in ["user", "access_token", "messages", "challenge_passed", "completion_code"]:
            st.session_state[key] = None
        st.session_state.messages = []
        st.rerun()

# ============================================
# 챗봇 UI (구현 완료)
# ============================================
st.title("🔄 Agentic Loop — API 미로 탈출")
st.caption("'미로 풀어줘'라고 입력하면 에이전트가 API를 순서대로 호출합니다.")
st.markdown("---")

for msg in st.session_state.messages:
    if msg["role"] in ("user", "assistant") and msg.get("content"):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("'미로 풀어줘'라고 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("에이전트 동작 중..."):
            answer, error = run_agentic_loop(st.session_state.messages)
            if error:
                st.error(f"❌ {error}")
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {error}"})
            elif answer:
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

    # completion_code가 있으면 자동 제출
    if st.session_state.completion_code and not st.session_state.challenge_passed:
        try:
            submit_resp = requests.post(
                f"{CHALLENGE_SERVER}/challenges/agent_loop/submit",
                json={
                    "token": token,
                    "answer": {"completion_code": st.session_state.completion_code},
                },
                timeout=10,
            )
            if submit_resp.status_code == 200:
                result = submit_resp.json()
                if result.get("status") == "SUCCESS":
                    st.session_state.challenge_passed = True
                    st.balloons()
                    st.success(f"🎉 {result.get('message', 'Agentic Loop 과제 통과!')}")
        except Exception:
            pass
