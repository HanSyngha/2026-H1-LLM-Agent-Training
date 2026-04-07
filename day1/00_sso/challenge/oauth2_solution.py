"""
과제 1 정답: OAuth2 Authorization Code Flow

브라우저에서 http://localhost:3000 접속 → SSO 로그인 → 이름/부서 표시

실행: python oauth2_solution.py
"""

import uuid
import urllib.parse

import jwt
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# ============================================
# 설정 — 수강생에게 제공되는 정보
# ============================================
AUTH_SERVER = "https://a2g.samsungds.net:8090"
CLIENT_ID = "cli-default"
CLIENT_SECRET = ""  # cli-default는 secret 없음
REDIRECT_URI = "http://localhost:3000/callback"
SCOPE = "openid"


# ============================================
# Step 1: /login → 인증 서버로 리다이렉트
# ============================================
@app.get("/")
async def home():
    """로그인 버튼이 있는 홈 페이지입니다."""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>OAuth2 실습</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center;
               align-items: center; min-height: 100vh; background: #f8fafc; }
        .btn { background: #2563eb; color: white; border: none; padding: 16px 32px;
               border-radius: 8px; font-size: 1.1em; cursor: pointer; text-decoration: none; }
    </style></head>
    <body>
        <div style="text-align:center">
            <h1>OAuth2 실습</h1>
            <p style="color:#64748b;margin:1em 0 2em">Authorization Code Flow</p>
            <a href="/login" class="btn">SSO 로그인</a>
        </div>
    </body></html>
    """)


@app.get("/login")
async def login():
    """인증 서버의 authorize 엔드포인트로 리다이렉트합니다."""
    # state: CSRF 방어용 랜덤 값
    state = uuid.uuid4().hex

    # authorize URL 구성
    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
    })

    authorize_url = f"{AUTH_SERVER}/oidc/authorize?{params}"
    return RedirectResponse(url=authorize_url)


# ============================================
# Step 2: /callback → code 수신 + token 교환
# ============================================
@app.get("/callback")
async def callback(code: str = "", state: str = ""):
    """
    인증 서버가 redirect해서 돌아오는 엔드포인트입니다.
    code를 받아서 access_token으로 교환합니다.
    """
    if not code:
        return HTMLResponse("<h1>code가 없습니다. 로그인을 다시 시도하세요.</h1>", status_code=400)

    # ============================================
    # Step 3: code → access_token 교환
    # ============================================
    token_response = requests.post(
        f"{AUTH_SERVER}/oidc/token",
        auth=(CLIENT_ID, CLIENT_SECRET),  # Basic Auth (password 비어있음)
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        verify=False,  # 사내 SSL 인증서 이슈
    )

    if token_response.status_code != 200:
        return HTMLResponse(
            f"<h1>토큰 교환 실패</h1><pre>{token_response.text}</pre>",
            status_code=400,
        )

    token_data = token_response.json()
    access_token = token_data["access_token"]

    # ============================================
    # Step 4: access_token으로 사용자 정보 조회
    # ============================================
    userinfo_response = requests.get(
        f"{AUTH_SERVER}/oidc/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        verify=False,
    )

    if userinfo_response.status_code != 200:
        return HTMLResponse(
            f"<h1>사용자 정보 조회 실패</h1><pre>{userinfo_response.text}</pre>",
            status_code=400,
        )

    user = userinfo_response.json()

    # ============================================
    # Step 5: 성공 화면 — 이름/부서 표시
    # ============================================
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>로그인 성공!</title>
    <style>
        body {{ font-family: sans-serif; display: flex; justify-content: center;
               align-items: center; min-height: 100vh; background: #f0fdf4; }}
        .card {{ background: white; border-radius: 16px; padding: 3em; text-align: center;
                 box-shadow: 0 4px 24px rgba(0,0,0,.08); max-width: 500px; }}
        .check {{ font-size: 4em; margin-bottom: .3em; }}
        h1 {{ color: #059669; margin-bottom: .5em; }}
        .field {{ margin: .6em 0; font-size: 1.1em; }}
        .label {{ color: #64748b; }}
        .value {{ color: #1e293b; font-weight: 700; }}
        .badge {{ display: inline-block; padding: 4px 16px; border-radius: 20px;
                  background: #dbeafe; color: #1d4ed8; font-size: .85em; font-weight: 600;
                  margin-top: 1em; }}
        .method {{ margin-top: 1.5em; padding: 1em; background: #f8fafc; border-radius: 8px;
                   font-size: .85em; color: #475569; }}
    </style></head>
    <body>
        <div class="card">
            <div class="check">✅</div>
            <h1>OAuth2 로그인 성공!</h1>
            <div class="field"><span class="label">사번: </span><span class="value">{user.get('sub', '?')}</span></div>
            <div class="field"><span class="label">이름: </span><span class="value">{user.get('name', '?')}</span></div>
            <div class="field"><span class="label">부서: </span><span class="value">{user.get('dept', '?')}</span></div>
            <div class="field"><span class="label">이메일: </span><span class="value">{user.get('email', '?')}</span></div>
            <div class="badge">OAuth2 Authorization Code Flow</div>
            <div class="method">
                <strong>방식:</strong> access_token으로 /userinfo API를 호출하여 정보를 가져왔습니다.<br>
                <strong>요청 횟수:</strong> authorize → token → userinfo (총 3단계)
            </div>
        </div>
    </body></html>
    """)


if __name__ == "__main__":
    import uvicorn
    import urllib3
    urllib3.disable_warnings()  # SSL 경고 무시

    print("=" * 50)
    print(" OAuth2 실습 서버")
    print(" http://localhost:3000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=3000)
