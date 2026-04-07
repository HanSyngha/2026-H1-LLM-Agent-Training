"""
SSO 실습용 Streamlit 앱 (기본 템플릿)

실행: streamlit run app.py --server.port 3000
접속: http://localhost:3000

과제: 이 앱에 OAuth2 / OIDC 로그인을 연동하세요.
"""

import streamlit as st

st.set_page_config(page_title="SSO 실습", page_icon="🔐", layout="centered")

st.title("🔐 SSO 로그인 실습")
st.markdown("---")

# ============================================
# 현재 상태: 로그인 안 됨
# ============================================
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.warning("로그인이 필요합니다.")
    st.markdown("""
    ### 과제
    이 앱에 **OAuth2 또는 OIDC 로그인**을 연동하세요.

    로그인 성공 시 본인의 **이름**과 **부서**가 아래에 표시되어야 합니다.
    """)

    # TODO: 여기에 OAuth2/OIDC 로그인 버튼을 추가하세요
    st.button("🔑 SSO 로그인", disabled=True, help="바이브 코딩으로 이 버튼에 SSO 로그인을 연결하세요")

else:
    # ============================================
    # 로그인 성공 화면
    # ============================================
    user = st.session_state.user
    st.success(f"✅ 로그인 성공!")
    st.markdown(f"""
    | 항목 | 값 |
    |------|---|
    | **이름** | {user.get('name', '?')} |
    | **부서** | {user.get('dept', '?')} |
    | **이메일** | {user.get('email', '?')} |
    | **사번** | {user.get('sub', '?')} |
    """)

    # Challenge 서버 제출 버튼
    st.markdown("---")
    st.markdown("### Challenge 서버 제출")

    token = st.session_state.get("access_token", "")
    if st.button("🎯 과제 제출"):
        if token:
            import requests
            resp = requests.post(
                "https://a2g.samsungds.net:47777/challenges/sso_oauth2/submit",
                json={
                    "token": token,
                    "answer": {
                        "name": user.get("name", ""),
                        "dept": user.get("dept", ""),
                    }
                },
                verify=False,
            )
            if resp.status_code == 200:
                result = resp.json()
                st.balloons()
                st.success(result.get("message", "통과!"))
            else:
                st.error(f"실패: {resp.json().get('message', resp.text)}")
        else:
            st.error("access_token이 없습니다. SSO 로그인을 먼저 완료하세요.")
