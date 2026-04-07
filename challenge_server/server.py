"""
통합 Challenge 서버

강사가 a2g.samsungds.net:70777에 띄워두면,
수강생이 SSO 토큰 + 정답을 제출하여 과제를 통과합니다.

실행: python server.py
주소: http://0.0.0.0:70777

인증: a2g.samsungds.net:8090 (OIDC 인증 서버)
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path

import requests
import urllib3
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from challenges import CHALLENGES, validate_answer

urllib3.disable_warnings()

app = FastAPI(title="LLM Agent 교육 Challenge Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 설정
# ============================================
AUTH_SERVER = os.getenv("AUTH_SERVER", "https://a2g.samsungds.net:8090")
PORT = int(os.getenv("CHALLENGE_PORT", "70777"))

# 성공자 저장 (메모리 — 서버 재시작 시 초기화)
# {challenge_id: [{name, dept, email, timestamp}, ...]}
completions: dict[str, list[dict]] = {cid: [] for cid in CHALLENGES}


# ============================================
# 토큰으로 사용자 정보 확인 (인증 서버에 위임)
# ============================================
def get_user_from_token(token: str) -> dict | None:
    """
    인증 서버의 /oidc/userinfo에 토큰을 보내서 사용자 정보를 확인합니다.
    Challenge 서버는 토큰을 직접 디코딩하지 않습니다.
    """
    try:
        resp = requests.get(
            f"{AUTH_SERVER}/oidc/userinfo",
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


# ============================================
# 대시보드 (메인 페이지)
# ============================================
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """성공자 대시보드 — 실시간 업데이트"""
    dashboard_html = Path(__file__).parent / "dashboard.html"
    if dashboard_html.exists():
        return HTMLResponse(dashboard_html.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>dashboard.html not found</h1>")


# ============================================
# 과제 목록
# ============================================
@app.get("/challenges")
async def list_challenges():
    """전체 과제 목록과 현재 통과자 수를 반환합니다."""
    result = []
    for cid, info in CHALLENGES.items():
        result.append({
            "id": cid,
            "name": info["name"],
            "description": info["description"],
            "completions": len(completions.get(cid, [])),
        })
    return result


# ============================================
# 과제 미션 조회
# ============================================
@app.get("/challenges/{challenge_id}/mission")
async def get_mission(challenge_id: str):
    """과제의 미션 데이터를 반환합니다."""
    if challenge_id not in CHALLENGES:
        raise HTTPException(404, f"과제 '{challenge_id}'를 찾을 수 없습니다")

    challenge = CHALLENGES[challenge_id]
    return {
        "id": challenge_id,
        "name": challenge["name"],
        "description": challenge["description"],
        "mission": challenge["mission"],
        "submit_schema": challenge["submit_schema"],
    }


# ============================================
# 정답 제출
# ============================================
@app.post("/challenges/{challenge_id}/submit")
async def submit_answer(challenge_id: str, request: Request):
    """
    정답을 제출합니다.

    요청 형식:
    {
        "token": "<access_token>",
        "answer": { ... }
    }

    1. 토큰을 인증 서버에 보내서 사용자 확인
    2. 정답 스키마 및 내용 검증
    3. 통과 시 성공자 등록
    """
    if challenge_id not in CHALLENGES:
        raise HTTPException(404, f"과제 '{challenge_id}'를 찾을 수 없습니다")

    body = await request.json()
    token = body.get("token")
    answer = body.get("answer")

    if not token:
        return JSONResponse(
            {"status": "FAIL", "message": "token이 없습니다. SSO 로그인 후 access_token을 포함해주세요."},
            status_code=401,
        )

    if not answer:
        return JSONResponse(
            {"status": "FAIL", "message": "answer가 없습니다."},
            status_code=400,
        )

    # 1. 인증 서버에서 사용자 정보 확인
    user = get_user_from_token(token)
    if not user:
        return JSONResponse(
            {"status": "FAIL", "message": "토큰이 유효하지 않습니다. SSO 로그인을 다시 하세요."},
            status_code=401,
        )

    user_name = user.get("name", "?")
    user_dept = user.get("dept", "?")
    user_email = user.get("email", "?")
    user_sub = user.get("sub", "?")

    # 2. 정답 검증
    result = validate_answer(challenge_id, answer)

    if not result["passed"]:
        return JSONResponse({
            "status": "FAIL",
            "user": user_name,
            "message": result["message"],
            "details": result.get("details", []),
        }, status_code=400)

    # 3. 성공자 등록 (중복 방지)
    already = any(c["sub"] == user_sub for c in completions[challenge_id])
    if not already:
        completions[challenge_id].append({
            "sub": user_sub,
            "name": user_name,
            "dept": user_dept,
            "email": user_email,
            "timestamp": datetime.now().isoformat(),
        })

    return {
        "status": "SUCCESS",
        "user": user_name,
        "dept": user_dept,
        "message": f"🎉 {user_name}님, {CHALLENGES[challenge_id]['name']} 통과!",
        "challenge": challenge_id,
        "details": result.get("details", []),
    }


# ============================================
# 성공자 현황 (대시보드 데이터)
# ============================================
@app.get("/completions")
async def get_completions():
    """전체 과제의 성공자 현황을 반환합니다."""
    return {
        "challenges": {
            cid: {
                "name": CHALLENGES[cid]["name"],
                "completions": completions[cid],
            }
            for cid in CHALLENGES
        },
        "updated_at": datetime.now().isoformat(),
    }


# ============================================
# 브라우저 과제 타겟 페이지
# ============================================
@app.get("/browser-target", response_class=HTMLResponse)
async def browser_target():
    """브라우저 자동화 과제에서 수강생이 스크래핑할 타겟 페이지입니다."""
    from challenges import BROWSER_TARGET_DATA

    rows = "".join(
        f"<tr><td>{p['name']}</td><td>{p['price']:,}원</td></tr>"
        for p in BROWSER_TARGET_DATA
    )
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>상품 목록</title>
    <style>
        body {{ font-family: sans-serif; padding: 2em; background: #f8fafc; }}
        h1 {{ color: #1e293b; margin-bottom: 1em; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 600px; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #1e293b; color: white; }}
        tr:hover td {{ background: #f1f5f9; }}
        .product-name {{ font-weight: 600; }}
    </style></head>
    <body>
        <h1>반도체 제품 목록</h1>
        <table>
            <thead><tr><th class="product-name">제품명</th><th>가격</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        <p style="margin-top:2em;color:#94a3b8;font-size:.85em">이 데이터를 추출하여 Challenge 서버에 제출하세요.</p>
    </body></html>
    """)


# ============================================
# 헬스체크
# ============================================
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "challenge-server",
        "port": PORT,
        "auth_server": AUTH_SERVER,
        "challenges": len(CHALLENGES),
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print(f"  LLM Agent 교육 Challenge 서버")
    print(f"  http://0.0.0.0:{PORT}")
    print(f"  인증 서버: {AUTH_SERVER}")
    print(f"  과제 수: {len(CHALLENGES)}개")
    print("=" * 60)
    for cid, info in CHALLENGES.items():
        print(f"  [{cid}] {info['name']}")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=PORT)
