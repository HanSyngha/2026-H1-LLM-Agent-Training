"""
SSO 실습용 Streamlit 앱

실행: streamlit run app.py --server.port 3000
접속: http://localhost:3000

과제: 이 앱에 OIDC 로그인을 연동하세요.
"""

import streamlit as st
import requests
import json

st.set_page_config(page_title="SSO 실습", page_icon="🔐", layout="centered")

# ============================================
# 세션 상태 초기화
# ============================================
if "user" not in st.session_state:
    st.session_state.user = None          # 로그인한 사용자 정보 (dict)
if "access_token" not in st.session_state:
    st.session_state.access_token = None  # SSO access_token
if "method" not in st.session_state:
    st.session_state.method = None        # "oidc"

CHALLENGE_SERVER = "http://a2g.samsungds.net:47777"

st.title("🔐 SSO 로그인 실습")
st.markdown("---")

# ============================================
# 로그인 안 된 상태
# ============================================
if st.session_state.user is None:
    st.warning("로그인이 필요합니다.")
    st.info("바이브 코딩으로 아래 로그인 버튼에 OIDC 로그인을 연동하세요.")

    # TODO: 바이브 코딩으로 이 버튼에 OIDC 로그인을 연결하세요
    st.button("🔑 SSO 로그인 (OIDC)", disabled=True, help="바이브 코딩으로 이 버튼에 OIDC 로그인을 연결하세요")

    st.markdown("---")
    st.markdown("### 로그인 정보 (비어있음)")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("이름", value="", disabled=True)
        st.text_input("이메일", value="", disabled=True)
    with col2:
        st.text_input("부서", value="", disabled=True)
        st.text_input("사번", value="", disabled=True)

    st.markdown("---")
    st.button("🎯 Challenge 서버에 제출", disabled=True, help="로그인 먼저 완료하세요")

# ============================================
# 로그인 성공 상태
# ============================================
else:
    user = st.session_state.user

    st.success("✅ OIDC 로그인 성공!")

    st.markdown("### 로그인 정보")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("이름", value=user.get("name", ""), disabled=True)
        st.text_input("이메일", value=user.get("email", ""), disabled=True)
    with col2:
        st.text_input("부서", value=user.get("dept", ""), disabled=True)
        st.text_input("사번", value=user.get("sub", ""), disabled=True)

    # ============================================
    # Challenge 서버 제출
    # ============================================
    st.markdown("---")
    st.markdown("### Challenge 서버 제출")

    submit_data = {
        "token": st.session_state.access_token or "",
        "answer": {
            "name": user.get("name", ""),
            "dept": user.get("dept", ""),
            "method": "oidc",
        }
    }

    st.code(json.dumps(submit_data, ensure_ascii=False, indent=2), language="json")

    if st.button("🎯 Challenge 서버에 제출"):
        if not st.session_state.access_token:
            st.error("access_token이 없습니다.")
        else:
            try:
                resp = requests.post(
                    f"{CHALLENGE_SERVER}/challenges/sso_oidc/submit",
                    json=submit_data,
                    timeout=10,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    st.balloons()
                    st.success(f"🎉 {result.get('message', '통과!')}")
                else:
                    error = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"message": resp.text}
                    st.error(f"❌ 실패: {error.get('message', resp.text)}")
            except Exception as e:
                st.error(f"❌ 연결 실패: {e}")

    # 로그아웃
    if st.button("🔓 로그아웃"):
        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.method = None
        st.rerun()
