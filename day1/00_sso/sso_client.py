"""
SSO 클라이언트 (백엔드 서비스) 예제

SSO 서버에서 받은 id_token을 처리하고,
자체 access_token을 발급하는 백엔드 서비스입니다.

실제 A2A Agent Platform의 user-service 인증 로직을 기반으로 합니다.

실행 순서:
1. sso_mock_server.py 먼저 실행 (포트 9999)
2. 이 파일 실행 (포트 8000)
3. 브라우저에서 http://localhost:8000 접속
"""

import time
import json

import jwt  # PyJWT
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

app = FastAPI(title="SSO Client Service")

# ============================================
# 설정
# ============================================
SSO_BASE_URL = "http://localhost:9999"
OUR_CALLBACK_URL = "http://localhost:8000/callback"
CLIENT_BASE_URL = "http://localhost:8000"

# 자체 JWT 설정 (SSO 토큰과 별개)
OUR_JWT_SECRET = "our-service-secret-key"
OUR_TOKEN_EXPIRE_HOURS = 12

# SSO 서버의 시크릿 (실제 환경에서는 인증서의 public key 사용)
SSO_SECRET = "mock-sso-secret-key"


# ============================================
# 1단계: 로그인 시작 → SSO URL 생성
# ============================================
@app.get("/", response_class=HTMLResponse)
async def home():
    """홈 페이지 — 로그인 버튼"""
    return """
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>SSO 데모</title>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center;
               align-items: center; min-height: 100vh; background: #f8fafc; }
        .btn { background: #2563eb; color: white; border: none; padding: 16px 32px;
               border-radius: 8px; font-size: 1.1em; cursor: pointer; text-decoration: none; }
        .btn:hover { background: #1d4ed8; }
    </style></head>
    <body>
        <div style="text-align:center">
            <h1>SSO 로그인 데모</h1>
            <p style="color:#64748b;margin:1em 0 2em">사내 SSO 연동 예시</p>
            <a href="/login" class="btn">SSO 로그인</a>
        </div>
    </body></html>
    """


@app.get("/login")
async def initiate_login():
    """
    로그인 시작: SSO 로그인 URL을 생성하고 리다이렉트합니다.

    실제 구현에서는:
    - client_id, nonce, state 등의 파라미터를 추가
    - redirect_uri는 우리 서비스의 callback URL
    """
    # SSO 로그인 URL 구성
    sso_login_url = (
        f"{SSO_BASE_URL}/mock-sso/login"
        f"?redirect_uri={OUR_CALLBACK_URL}"
        f"&state=random-state-for-csrf-protection"
    )

    # 사용자를 SSO 로그인 페이지로 리다이렉트
    return RedirectResponse(url=sso_login_url)


# ============================================
# 2단계: SSO 콜백 처리 → id_token 수신
# ============================================
@app.post("/callback")
async def sso_callback(
    request: Request,
    id_token: str = Form(None),
    code: str = Form(None),
    state: str = Form(None),
):
    """
    SSO 콜백 엔드포인트

    SSO 서버가 form_post 방식으로 id_token을 POST합니다.
    이 엔드포인트에서 토큰을 검증하고 사용자 정보를 추출합니다.

    핵심: id_token 하나에 모든 정보가 들어있으므로
    추가 API 호출 없이 바로 사용자 정보를 얻습니다.
    """
    if not id_token:
        return HTMLResponse("<h1>id_token이 없습니다</h1>", status_code=400)

    # ============================================
    # 3단계: id_token 검증 및 사용자 정보 추출
    # ============================================
    try:
        # JWT 디코딩 (실제 환경에서는 RS256 + 인증서 public key 사용)
        user_info = jwt.decode(
            id_token,
            SSO_SECRET,
            algorithms=["HS256"],
            options={
                "verify_signature": True,  # 실제 환경에서는 반드시 True
                "verify_exp": True,
            },
        )
    except jwt.ExpiredSignatureError:
        return HTMLResponse("<h1>토큰이 만료되었습니다. 다시 로그인하세요.</h1>", status_code=401)
    except jwt.InvalidTokenError as e:
        return HTMLResponse(f"<h1>토큰 검증 실패: {e}</h1>", status_code=401)

    # ============================================
    # 사용자 정보 추출 (1회 요청으로 전부 획득!)
    # ============================================
    username = user_info.get("loginid")         # "hong.gildong"
    username_kr = user_info.get("username")     # "홍길동"
    email = user_info.get("mail")               # "hong.gildong@company.com"
    department_code = user_info.get("deptid")   # "dev_team"
    department_kr = user_info.get("deptname")   # "개발팀"
    department_en = user_info.get("deptname_en")# "Dev Team"

    print(f"[SSO] 로그인 성공: {username_kr} ({username}) - {department_kr}")

    # ============================================
    # 4단계: 자체 access_token 발급
    # ============================================
    # SSO id_token은 SSO 서버용이므로,
    # 우리 서비스용 access_token을 별도로 발급합니다.
    now = int(time.time())
    access_token = jwt.encode(
        {
            "sub": username,
            "role": user_info.get("role", "USER"),
            "department": department_code,
            "department_kr": department_kr,
            "department_en": department_en,
            "exp": now + (OUR_TOKEN_EXPIRE_HOURS * 3600),
            "iat": now,
        },
        OUR_JWT_SECRET,
        algorithm="HS256",
    )

    # ============================================
    # 5단계: 응답 (프론트엔드에 토큰 전달)
    # ============================================
    # 실제 서비스에서는 프론트엔드 콜백 페이지로 리다이렉트하고
    # 프론트엔드가 토큰을 localStorage에 저장합니다.
    # 여기서는 간단히 결과를 HTML로 보여줍니다.

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>로그인 성공</title>
    <style>
        body {{ font-family: sans-serif; background: #f8fafc; padding: 2em; }}
        .card {{ background: white; border-radius: 12px; padding: 2em;
                 max-width: 600px; margin: 2em auto; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
        h1 {{ color: #059669; }}
        .field {{ margin: 0.8em 0; }}
        .label {{ color: #64748b; font-size: 0.85em; }}
        .value {{ color: #1e293b; font-weight: 600; }}
        .token {{ background: #1e293b; color: #67e8f9; padding: 12px;
                  border-radius: 8px; font-family: monospace; font-size: 0.75em;
                  word-break: break-all; margin-top: 1em; }}
        .section-title {{ color: #2563eb; font-weight: 700; margin-top: 1.5em; }}
    </style></head>
    <body>
        <div class="card">
            <h1>로그인 성공!</h1>
            <p style="color:#64748b">SSO에서 받은 사용자 정보 (1회 요청으로 전부 획득)</p>

            <div class="section-title">사용자 정보</div>
            <div class="field"><span class="label">사번/ID: </span><span class="value">{username}</span></div>
            <div class="field"><span class="label">이름: </span><span class="value">{username_kr}</span></div>
            <div class="field"><span class="label">이메일: </span><span class="value">{email}</span></div>
            <div class="field"><span class="label">부서코드: </span><span class="value">{department_code}</span></div>
            <div class="field"><span class="label">부서명: </span><span class="value">{department_kr} ({department_en})</span></div>
            <div class="field"><span class="label">역할: </span><span class="value">{user_info.get('role')}</span></div>

            <div class="section-title">SSO id_token (원본)</div>
            <div class="token">{id_token}</div>

            <div class="section-title">자체 access_token (12시간 유효)</div>
            <div class="token">{access_token}</div>

            <p style="margin-top:1.5em;color:#94a3b8;font-size:0.85em">
                이 access_token을 이후 모든 API 요청의 Authorization 헤더에 포함합니다.<br>
                <code>Authorization: Bearer {access_token[:30]}...</code>
            </p>

            <div style="margin-top:2em;text-align:center">
                <a href="/protected" style="color:#2563eb;text-decoration:none;font-weight:600">
                    → 인증된 API 테스트하기 (토큰을 query로 전달)
                </a>
            </div>
        </div>
    </body></html>
    """)


# ============================================
# 인증이 필요한 API 엔드포인트 예시
# ============================================
@app.get("/api/me")
async def get_my_info(request: Request):
    """
    인증된 사용자 정보 조회

    Authorization: Bearer <access_token> 헤더로 토큰을 전달받아
    사용자 정보를 반환합니다.
    """
    # Authorization 헤더에서 토큰 추출
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            {"error": "Authorization 헤더가 없습니다"},
            status_code=401,
        )

    token = auth_header.replace("Bearer ", "")

    try:
        # 자체 토큰 검증
        payload = jwt.decode(token, OUR_JWT_SECRET, algorithms=["HS256"])
        return {
            "username": payload["sub"],
            "role": payload["role"],
            "department": payload["department"],
            "department_kr": payload["department_kr"],
            "message": "인증 성공! 이 정보는 SSO 토큰에서 추출된 것입니다.",
        }
    except jwt.ExpiredSignatureError:
        return JSONResponse({"error": "토큰 만료 — 재로그인 필요"}, status_code=401)
    except jwt.InvalidTokenError as e:
        return JSONResponse({"error": f"토큰 검증 실패: {e}"}, status_code=401)


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print(" SSO 클라이언트 서비스를 시작합니다")
    print(" http://localhost:8000")
    print()
    print(" ⚠ sso_mock_server.py가 먼저 실행 중이어야 합니다!")
    print("   python sso_mock_server.py  (포트 9999)")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
