"""
과제 2 정답: OIDC (OpenID Connect) Flow

OAuth2와의 차이: id_token을 JWT 디코딩하면 /userinfo 호출 없이 사용자 정보를 얻습니다.

실행: python oidc_solution.py
"""

import uuid
import urllib.parse

import jwt
import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# ============================================
# 설정
# ============================================
AUTH_SERVER = "https://auth.example.com"
CLIENT_ID = "cli-default"
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:3000/callback"
SCOPE = "openid profile email"  # OAuth2보다 scope가 넓습니다

# nonce 저장 (실제 서비스에서는 세션/DB에 저장)
_nonce_store = {}


@app.get("/")
async def home():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>OIDC 실습</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center;
               align-items: center; min-height: 100vh; background: #f8fafc; }
        .btn { background: #7c3aed; color: white; border: none; padding: 16px 32px;
               border-radius: 8px; font-size: 1.1em; cursor: pointer; text-decoration: none; }
    </style></head>
    <body>
        <div style="text-align:center">
            <h1>OIDC 실습</h1>
            <p style="color:#64748b;margin:1em 0 2em">OpenID Connect Flow — id_token에서 직접 추출</p>
            <a href="/login" class="btn">SSO 로그인 (OIDC)</a>
        </div>
    </body></html>
    """)


# ============================================
# Step 1: /login → authorize (nonce 포함!)
# ============================================
@app.get("/login")
async def login():
    """
    OAuth2와의 차이점:
    1. scope에 'profile email' 추가
    2. nonce 파라미터 추가 (OIDC 필수)

    nonce가 있어야 인증 서버가 id_token을 발급합니다.
    """
    state = uuid.uuid4().hex
    nonce = uuid.uuid4().hex  # OIDC 핵심: nonce 생성

    # nonce 저장 (나중에 검증용)
    _nonce_store[state] = nonce

    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
        "nonce": nonce,  # OAuth2에는 없는 파라미터
    })

    authorize_url = f"{AUTH_SERVER}/oidc/authorize?{params}"
    return RedirectResponse(url=authorize_url)


# ============================================
# Step 2-3: callback → token 교환
# ============================================
@app.get("/callback")
async def callback(code: str = "", state: str = ""):
    if not code:
        return HTMLResponse("<h1>code가 없습니다.</h1>", status_code=400)

    # token 교환 (OAuth2와 동일)
    token_response = requests.post(
        f"{AUTH_SERVER}/oidc/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
    )

    if token_response.status_code != 200:
        return HTMLResponse(
            f"<h1>토큰 교환 실패</h1><pre>{token_response.text}</pre>",
            status_code=400,
        )

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    id_token = token_data.get("id_token")  # OIDC 핵심: id_token!

    if not id_token:
        return HTMLResponse("""
        <h1>id_token이 없습니다!</h1>
        <p>authorize 요청에 <code>nonce</code> 파라미터를 포함했는지 확인하세요.</p>
        <p>nonce가 없으면 인증 서버가 id_token을 발급하지 않습니다.</p>
        """, status_code=400)

    # ============================================
    # Step 4: id_token JWT 디코딩 (핵심!)
    # ============================================
    # /userinfo API를 호출하지 않고 토큰에서 직접 사용자 정보를 추출합니다.
    try:
        claims = jwt.decode(
            id_token,
            options={"verify_signature": False},  # 실습에서는 서명 검증 생략
            algorithms=["HS256"],
        )
    except Exception as e:
        return HTMLResponse(f"<h1>JWT 디코딩 실패: {e}</h1>", status_code=400)

    # nonce 검증 (Optional but recommended)
    saved_nonce = _nonce_store.get(state)
    token_nonce = claims.get("nonce")

    # ============================================
    # Step 5: 성공 화면 — OAuth2와 비교
    # ============================================
    # OAuth2와 달리 /userinfo를 호출하지 않았음을 강조합니다.
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>OIDC 로그인 성공!</title>
    <style>
        body {{ font-family: sans-serif; display: flex; justify-content: center;
               align-items: center; min-height: 100vh; background: #faf5ff; }}
        .card {{ background: white; border-radius: 16px; padding: 3em; text-align: center;
                 box-shadow: 0 4px 24px rgba(0,0,0,.08); max-width: 600px; }}
        .check {{ font-size: 4em; margin-bottom: .3em; }}
        h1 {{ color: #7c3aed; margin-bottom: .5em; }}
        .field {{ margin: .6em 0; font-size: 1.1em; }}
        .label {{ color: #64748b; }}
        .value {{ color: #1e293b; font-weight: 700; }}
        .badge {{ display: inline-block; padding: 4px 16px; border-radius: 20px;
                  background: #ede9fe; color: #6d28d9; font-size: .85em; font-weight: 600;
                  margin-top: 1em; }}
        .method {{ margin-top: 1.5em; padding: 1em; background: #f8fafc; border-radius: 8px;
                   font-size: .85em; color: #475569; text-align: left; }}
        .compare {{ margin-top: 1em; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
        .compare > div {{ padding: 12px; border-radius: 8px; font-size: .85em; }}
        .oauth {{ background: #dbeafe; color: #1d4ed8; }}
        .oidc {{ background: #ede9fe; color: #6d28d9; }}
        .token-box {{ background: #1e293b; color: #67e8f9; padding: 10px; border-radius: 8px;
                      font-family: monospace; font-size: .7em; word-break: break-all;
                      margin-top: .5em; max-height: 80px; overflow: auto; text-align: left; }}
        .nonce {{ font-size: .8em; color: #64748b; margin-top: .5em; }}
    </style></head>
    <body>
        <div class="card">
            <div class="check">✅</div>
            <h1>OIDC 로그인 성공!</h1>
            <p style="color:#475569">id_token에서 직접 추출 — /userinfo 호출 없음</p>

            <div class="field"><span class="label">사번: </span><span class="value">{claims.get('sub', '?')}</span></div>
            <div class="field"><span class="label">이름: </span><span class="value">{claims.get('name', '?')}</span></div>
            <div class="field"><span class="label">부서: </span><span class="value">{claims.get('dept', '?')}</span></div>
            <div class="field"><span class="label">이메일: </span><span class="value">{claims.get('email', '?')}</span></div>

            <div class="badge">OpenID Connect</div>

            <div class="compare">
                <div class="oauth">
                    <strong>OAuth2 방식</strong><br>
                    authorize → token → <strong>userinfo</strong><br>
                    (3단계, API 호출 필요)
                </div>
                <div class="oidc">
                    <strong>OIDC 방식</strong><br>
                    authorize → token (id_token 포함)<br>
                    (2단계, JWT 디코딩만)
                </div>
            </div>

            <div class="method">
                <strong>id_token (JWT):</strong>
                <div class="token-box">{id_token}</div>
                <div class="nonce">
                    nonce 검증: {('✅ 일치' if saved_nonce == token_nonce else '⚠️ 불일치 또는 미검증')}
                    (요청: {saved_nonce or 'N/A'}, 토큰: {token_nonce or 'N/A'})
                </div>
            </div>
        </div>
    </body></html>
    """)


if __name__ == "__main__":
    import uvicorn
    import urllib3
    urllib3.disable_warnings()

    print("=" * 50)
    print(" OIDC 실습 서버")
    print(" http://localhost:3000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=3000)
