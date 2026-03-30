"""
Mock SSO 서버 (강의 데모용)

실제 A2A Agent Platform의 Mock SSO를 간소화한 버전입니다.
FastAPI로 구현한 SSO 서버로, 실제 SSO 동작을 시뮬레이션합니다.

실행: python sso_mock_server.py
접속: http://localhost:9999/mock-sso/login
"""

import json
import time
import uuid
from urllib.parse import urlencode, quote

import jwt  # PyJWT
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="Mock SSO Server")

# ============================================
# SSO 서버 설정
# ============================================
SSO_SECRET = "mock-sso-secret-key"  # 실제 환경에서는 RSA 키 사용
SSO_ISSUER = "mock-sso"
SSO_AUDIENCE = "our-platform"
TOKEN_EXPIRE_SECONDS = 3600  # 1시간

# ============================================
# 미리 정의된 사용자 목록
# ============================================
# 실제 SSO에서는 LDAP/AD에서 인물 정보를 조회합니다.
# 여기서는 데모용으로 하드코딩합니다.
MOCK_USERS = {
    "user1": {
        "loginid": "hong.gildong",
        "username": "홍길동",
        "mail": "hong.gildong@company.com",
        "deptid": "dev_team",
        "deptname": "개발팀",
        "deptname_en": "Dev Team",
        "role": "ADMIN",
    },
    "user2": {
        "loginid": "kim.cheolsu",
        "username": "김철수",
        "mail": "kim.cheolsu@company.com",
        "deptid": "ai_team",
        "deptname": "AI팀",
        "deptname_en": "AI Team",
        "role": "USER",
    },
    "user3": {
        "loginid": "lee.younghee",
        "username": "이영희",
        "mail": "lee.younghee@company.com",
        "deptid": "data_team",
        "deptname": "데이터팀",
        "deptname_en": "Data Team",
        "role": "USER",
    },
}


def create_id_token(user_data: dict) -> str:
    """
    사용자 정보를 담은 JWT ID 토큰을 생성합니다.

    핵심: 이 토큰 하나에 모든 인물 정보가 들어갑니다.
    클라이언트는 이 토큰만 디코딩하면 별도의 API 호출 없이
    사용자 정보를 모두 얻을 수 있습니다.
    """
    now = int(time.time())
    payload = {
        # 사용자 정보 (사내 SSO 고유 필드)
        "loginid": user_data["loginid"],
        "username": user_data["username"],  # 한글 이름
        "mail": user_data["mail"],
        "deptid": user_data["deptid"],
        "deptname": user_data["deptname"],
        "deptname_en": user_data["deptname_en"],
        "role": user_data.get("role", "USER"),
        # 표준 JWT 클레임
        "iat": now,
        "exp": now + TOKEN_EXPIRE_SECONDS,
        "iss": SSO_ISSUER,
        "aud": SSO_AUDIENCE,
    }

    # HS256으로 서명 (실제 환경에서는 RS256 + 인증서)
    token = jwt.encode(payload, SSO_SECRET, algorithm="HS256")
    return token


@app.get("/mock-sso/login", response_class=HTMLResponse)
async def login_page(redirect_uri: str = "", state: str = ""):
    """
    SSO 로그인 페이지

    실제 SSO에서는 ID/PW 입력 폼이지만,
    데모에서는 사용자 선택 카드를 보여줍니다.
    """
    user_cards = ""
    for key, user in MOCK_USERS.items():
        params = urlencode({
            "redirect_uri": redirect_uri,
            "user": key,
            "state": state,
        })
        user_cards += f"""
        <a href="/mock-sso/do-login?{params}" class="card">
            <div class="name">{user['username']}</div>
            <div class="id">{user['loginid']}</div>
            <div class="dept">{user['deptname']} ({user['role']})</div>
        </a>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Mock SSO Login</title>
        <style>
            body {{ font-family: sans-serif; background: #f0f4f8; display: flex;
                   justify-content: center; align-items: center; min-height: 100vh; }}
            .container {{ text-align: center; }}
            h1 {{ color: #1e293b; margin-bottom: 0.5em; }}
            p {{ color: #64748b; margin-bottom: 2em; }}
            .cards {{ display: flex; gap: 1em; flex-wrap: wrap; justify-content: center; }}
            .card {{ background: white; border-radius: 12px; padding: 1.5em 2em;
                     text-decoration: none; color: inherit; box-shadow: 0 2px 8px rgba(0,0,0,.08);
                     transition: transform 0.2s, box-shadow 0.2s; min-width: 200px; }}
            .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,.12); }}
            .name {{ font-size: 1.3em; font-weight: 700; color: #1e293b; }}
            .id {{ color: #2563eb; margin: 0.3em 0; }}
            .dept {{ color: #64748b; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SSO 로그인 (데모)</h1>
            <p>사용자를 선택하세요</p>
            <div class="cards">{user_cards}</div>
            <p style="margin-top:2em;font-size:0.8em;color:#94a3b8">
                redirect_uri: {redirect_uri}
            </p>
        </div>
    </body>
    </html>
    """


@app.get("/mock-sso/do-login", response_class=HTMLResponse)
async def do_login(redirect_uri: str, user: str, state: str = ""):
    """
    SSO 로그인 처리 + form_post 방식으로 id_token 전달

    핵심 포인트:
    1. 사용자 정보를 JWT로 만들고
    2. hidden form에 담아서
    3. redirect_uri로 POST (form_post)

    form_post 방식을 쓰는 이유:
    - URL에 토큰이 노출되지 않음 (query string이 아님)
    - 브라우저 히스토리에 토큰이 남지 않음
    - GET redirect보다 안전함
    """
    user_data = MOCK_USERS.get(user)
    if not user_data:
        return HTMLResponse("<h1>사용자를 찾을 수 없습니다</h1>", status_code=404)

    # JWT ID 토큰 생성 (모든 인물 정보 포함)
    id_token = create_id_token(user_data)

    # form_post: hidden form으로 id_token을 POST 전송
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>SSO 처리 중...</title></head>
    <body>
        <p>로그인 처리 중입니다...</p>

        <!-- form_post 방식: hidden form이 자동으로 POST 됨 -->
        <form id="ssoForm" method="POST" action="{redirect_uri}">
            <input type="hidden" name="id_token" value="{id_token}">
            <input type="hidden" name="code" value="mock-auth-code-{uuid.uuid4().hex[:8]}">
            <input type="hidden" name="state" value="{state}">
        </form>

        <script>
            // 페이지 로드 즉시 form 제출
            document.getElementById('ssoForm').submit();
        </script>
    </body>
    </html>
    """


@app.get("/mock-sso/verify")
async def verify_token(token: str):
    """토큰 검증 엔드포인트 (디버깅용)"""
    try:
        payload = jwt.decode(token, SSO_SECRET, algorithms=["HS256"])
        return JSONResponse({"valid": True, "payload": payload})
    except jwt.ExpiredSignatureError:
        return JSONResponse({"valid": False, "error": "토큰 만료"}, status_code=401)
    except jwt.InvalidTokenError as e:
        return JSONResponse({"valid": False, "error": str(e)}, status_code=401)


@app.get("/mock-sso/users")
async def list_users():
    """등록된 사용자 목록 (디버깅용)"""
    return MOCK_USERS


@app.get("/health")
async def health():
    return {"status": "ok", "service": "mock-sso"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print(" Mock SSO 서버를 시작합니다")
    print(" http://localhost:9999/mock-sso/login")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=9999)
