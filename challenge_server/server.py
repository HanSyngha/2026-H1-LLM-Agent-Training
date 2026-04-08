"""
통합 Challenge 서버

강사가 a2g.samsungds.net:47777에 띄워두면,
수강생이 SSO 토큰 + 정답을 제출하여 과제를 통과합니다.

실행: python server.py
주소: http://0.0.0.0:47777

인증: a2g.samsungds.net:8090 (OIDC 인증 서버)
"""

import json
import time
import os
from datetime import datetime
from pathlib import Path

import requests
import urllib3
import uuid
from urllib.parse import urlencode
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from challenges import CHALLENGES, validate_answer
from prompt_challenge import PROMPT_TEST_CASES, call_llm, validate_result

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
AUTH_SERVER = os.getenv("AUTH_SERVER", "https://12.81.222.45:9050")
DEV_MODE = os.getenv("DEV_MODE", "").lower() in ("1", "true", "yes")  # 로컬 테스트용 SSO 우회
AUTH_PUBLIC = os.getenv("AUTH_PUBLIC", "http://a2g.samsungds.net:8090")  # 브라우저가 접근하는 주소
CHALLENGE_HOST = os.getenv("CHALLENGE_HOST", "http://a2g.samsungds.net:47777")  # 콜백 URL용
PORT = int(os.getenv("CHALLENGE_PORT", "47777"))

# LLM 설정 — 여러 개 등록 가능, 과제별로 선택
llm_endpoints: dict[str, dict] = {}  # {id: {name, base_url, api_key, model}}

# 채점용 LLM (기존 호환)
llm_config = {
    "base_url": os.getenv("LLM_GATEWAY_URL", ""),
    "api_key": os.getenv("LLM_GATEWAY_API_KEY", ""),
    "model": os.getenv("LLM_MODEL", "gpt-4o"),
}

# 과제별 LLM 매핑 {challenge_id: llm_endpoint_id}
challenge_llm_map: dict[str, str] = {}

# 슬라이드 동기화 (강사가 넘기면 수강생도 따라감)
current_slide = {"slide": 1}

# 반응/질문 저장 (동시성 고려 — Lock 사용)
from threading import Lock
reactions_lock = Lock()
reactions_data: dict[int, dict[str, int]] = {}  # {slide_num: {type: count}}
questions_lock = Lock()
questions_data: list[dict] = []  # [{slide, user, text, timestamp}]

# 성공자 저장 (메모리 — 서버 재시작 시 초기화)
# {challenge_id: [{name, dept, email, timestamp}, ...]}
completions: dict[str, list[dict]] = {cid: [] for cid in CHALLENGES}

# 예시 답안 공개 상태 (메모리)
unlocked_answers: set[str] = set()


# ============================================
# LLM 채점 함수
# ============================================
def llm_evaluate(challenge_id: str, mission: dict, answer: dict) -> dict:
    """
    LLM에게 정답 평가를 요청합니다.
    하드코딩 검증 대신 LLM이 미션 조건에 맞는지 판단합니다.
    """
    if not llm_config["base_url"] or not llm_config["api_key"]:
        # LLM 미설정 시 기존 하드코딩 검증으로 폴백
        return validate_answer(challenge_id, answer)

    challenge = CHALLENGES.get(challenge_id)
    if not challenge:
        return {"passed": False, "message": f"알 수 없는 과제: {challenge_id}"}

    prompt = f"""당신은 교육 과제 채점관입니다.

## 과제 정보
- 과제명: {challenge['name']}
- 설명: {challenge['description']}
- 미션 데이터: {json.dumps(mission, ensure_ascii=False, default=str)[:2000]}
- 제출 스키마: {challenge['submit_schema']}

## 수강생 제출 답안
{json.dumps(answer, ensure_ascii=False, default=str)[:2000]}

## 채점 기준
1. 제출 형식이 스키마에 맞는지
2. 내용이 미션 요구사항을 충족하는지
3. 명백한 오류가 없는지

관대하게 채점하되, 명백히 틀린 것은 FAIL 처리하세요.

## 응답 형식 (반드시 이 JSON 형식으로만 응답)
{{"passed": true/false, "message": "한줄 요약", "details": ["세부 평가 1", "세부 평가 2"]}}"""

    try:
        resp = requests.post(
            f"{llm_config['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {llm_config['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": llm_config["model"],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )

        if resp.status_code != 200:
            # LLM 호출 실패 시 하드코딩 검증으로 폴백
            return validate_answer(challenge_id, answer)

        result = resp.json()
        content = result["choices"][0]["message"]["content"]
        evaluation = json.loads(content)

        return {
            "passed": evaluation.get("passed", False),
            "message": evaluation.get("message", "LLM 평가 완료"),
            "details": evaluation.get("details", []),
        }

    except Exception as e:
        # LLM 오류 시 하드코딩 검증으로 폴백
        return validate_answer(challenge_id, answer)


# ============================================
# LLM 설정 API
# ============================================
# /settings → React SPA에서 처리


@app.post("/settings/update")
async def update_settings(request: Request):
    """LLM 설정을 업데이트하고 연결을 테스트합니다."""
    body = await request.json()

    new_url = body.get("base_url", "").strip()
    new_key = body.get("api_key", "").strip()
    new_model = body.get("model", "gpt-4o").strip()

    if not new_url:
        llm_config["base_url"] = ""
        llm_config["api_key"] = ""
        return {"status": "ok", "message": "LLM 설정 제거됨 — 하드코딩 검증 모드로 전환"}

    # 연결 테스트
    try:
        resp = requests.post(
            f"{new_url}/chat/completions",
            headers={"Authorization": f"Bearer {new_key}", "Content-Type": "application/json"},
            json={"model": new_model, "messages": [{"role": "user", "content": "test"}], "max_tokens": 5},
        )
        if resp.status_code == 200:
            llm_config["base_url"] = new_url
            llm_config["api_key"] = new_key
            llm_config["model"] = new_model
            return {"status": "ok", "message": f"LLM 연결 성공 — 모델: {new_model}"}
        else:
            return {"status": "error", "message": f"LLM 응답 오류: HTTP {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "message": f"LLM 연결 실패: {str(e)}"}


# ============================================
# 토큰으로 사용자 정보 확인 (인증 서버에 위임)
# ============================================
def get_user_from_token(token: str) -> dict | None:
    """
    인증 서버의 /oidc/userinfo에 토큰을 보내서 사용자 정보를 확인합니다.
    DEV_MODE=true이면 토큰 검증 없이 더미 사용자 반환.
    """
    if DEV_MODE:
        return {"sub": "syngha.han", "name": "한승하", "dept": "S/W혁신팀", "email": "syngha.han@samsung.com"}
    url = f"{AUTH_SERVER}/oidc/userinfo"
    print(f"[AUTH] 토큰 검증 요청: {url}")
    print(f"[AUTH] 토큰 앞 30자: {token[:30]}...")
    try:
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            verify=False,
            timeout=10,
            proxies={"http": None, "https": None},
        )
        print(f"[AUTH] 응답: HTTP {resp.status_code}")
        print(f"[AUTH] 응답 본문: {resp.text[:200]}")
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        print(f"[AUTH] 에러: {type(e).__name__}: {e}")
        return None


# ============================================
# SSO 로그인 (Challenge 서버 자체 로그인)
# ============================================
@app.get("/auth/login")
async def auth_login(request: Request, redirect: str = "/"):
    """SSO 로그인 시작 — OIDC authorize로 리다이렉트합니다."""
    state = uuid.uuid4().hex
    params = urlencode({
        "client_id": "cli-default",
        "redirect_uri": f"{CHALLENGE_HOST}/auth/callback",
        "response_type": "code",
        "scope": "openid profile email",
        "state": state,
        "nonce": uuid.uuid4().hex,
    })
    # state에 redirect 경로 저장 (쿠키)
    response = RedirectResponse(url=f"{AUTH_PUBLIC}/oidc/authorize?{params}")
    response.set_cookie("auth_redirect", redirect, max_age=600, httponly=True)
    response.set_cookie("auth_state", state, max_age=600, httponly=True)
    return response


@app.get("/auth/callback")
async def auth_callback(request: Request, code: str = "", state: str = ""):
    """SSO 콜백 — code를 token으로 교환하고 쿠키에 저장합니다."""
    if not code:
        return HTMLResponse("<h1>code가 없습니다</h1>", status_code=400)

    # token 교환
    try:
        resp = requests.post(
            f"{AUTH_SERVER}/oidc/token",
            auth=("cli-default", ""),
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{CHALLENGE_HOST}/auth/callback",
            },
            verify=False,
            timeout=10,
            proxies={"http": None, "https": None},
        )
        if resp.status_code != 200:
            return HTMLResponse(f"<h1>토큰 교환 실패: {resp.status_code}</h1><pre>{resp.text}</pre>", status_code=400)

        token_data = resp.json()
        access_token = token_data.get("access_token", "")
    except Exception as e:
        return HTMLResponse(f"<h1>토큰 교환 에러: {e}</h1>", status_code=500)

    # 원래 페이지로 리다이렉트 + 토큰 쿠키 설정
    redirect = request.cookies.get("auth_redirect", "/")
    response = RedirectResponse(url=redirect)
    response.set_cookie("challenge_token", access_token, max_age=43200, httponly=True)  # 12시간
    response.delete_cookie("auth_redirect")
    response.delete_cookie("auth_state")
    return response


@app.get("/auth/me")
async def auth_me(request: Request):
    """현재 로그인한 사용자 정보를 반환합니다. DEV_MODE면 로그인 없이 더미 사용자."""
    if DEV_MODE:
        return {"logged_in": True, "user": {"sub": "syngha.han", "name": "한승하", "dept": "S/W혁신팀", "email": "syngha.han@samsung.com"}, "token": "dev-token"}
    token = request.cookies.get("challenge_token", "")
    if not token:
        return JSONResponse({"logged_in": False}, status_code=401)
    user = get_user_from_token(token)
    if not user:
        return JSONResponse({"logged_in": False, "error": "토큰 만료"}, status_code=401)
    return {"logged_in": True, "user": user, "token": token}


@app.get("/auth/logout")
async def auth_logout():
    """로그아웃 — 쿠키 삭제"""
    response = RedirectResponse(url="/")
    response.delete_cookie("challenge_token")
    return response


# ============================================
# 대시보드 (메인 페이지)
# ============================================
# / → React SPA에서 처리


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
# Tool Use 과제 — 시크릿 키 발급
# ============================================
@app.get("/challenges/tool_use/secret")
async def tool_use_get_secret(request: Request):
    """Tool Use 과제용 시크릿 키를 발급합니다."""
    from challenges import generate_tool_use_secret

    token = request.query_params.get("token", "") or request.cookies.get("challenge_token", "")
    if not token and not DEV_MODE:
        return JSONResponse({"error": "token이 필요합니다."}, status_code=401)

    user = get_user_from_token(token)
    if not user:
        return JSONResponse({"error": "유효하지 않은 토큰입니다."}, status_code=401)

    secret = generate_tool_use_secret(user["sub"])
    return {"secret_key": secret, "message": "이 키를 submit_secret_key 도구로 제출하세요."}


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

    print(f"[SUBMIT] 과제: {challenge_id}")
    print(f"[SUBMIT] 토큰 존재: {bool(token)}, 답변 존재: {bool(answer)}")
    if token:
        print(f"[SUBMIT] 토큰 앞 30자: {token[:30]}...")

    if not answer:
        return JSONResponse(
            {"status": "FAIL", "message": "answer가 없습니다."},
            status_code=400,
        )

    # 1. 인증 서버에서 사용자 정보 확인
    # token이 body에 없으면 cookie에서 시도
    if not token:
        token = request.cookies.get("challenge_token", "")

    user = get_user_from_token(token) if token else None

    if not user:
        return JSONResponse(
            {"status": "FAIL", "message": "token이 없거나 유효하지 않습니다. SSO 로그인 후 다시 시도하세요."},
            status_code=401,
        )

    user_name = user.get("name", "?")
    user_dept = user.get("dept", "?")
    user_email = user.get("email", "?")
    user_sub = user.get("sub", "?")

    # tool_use 과제: user_sub 주입 (시크릿 키 검증용)
    if challenge_id == "tool_use":
        answer["_user_sub"] = user_sub

    # 2. 정답 검증 (LLM 설정 시 LLM 채점, 미설정 시 하드코딩 검증)
    challenge = CHALLENGES[challenge_id]
    result = llm_evaluate(challenge_id, challenge["mission"], answer)

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


@app.post("/completions/reset")
async def reset_completions(request: Request):
    """대시보드 초기화 — 강사(syngha.han)만 가능."""
    body = await request.json()
    token = body.get("token", "") or request.cookies.get("challenge_token", "")
    user = get_user_from_token(token)
    if not user or user.get("sub") != "syngha.han":
        return JSONResponse({"error": "강사만 초기화할 수 있습니다."}, status_code=403)

    for cid in completions:
        completions[cid] = []

    # tool_use 시크릿도 초기화
    from challenges import _tool_use_secrets
    _tool_use_secrets.clear()

    # 답안 공개 상태도 초기화
    unlocked_answers.clear()

    return {"status": "OK", "message": "모든 과제 성공 기록이 초기화되었습니다."}


# ============================================
# 예시 답안 공개/잠금 (강사 전용)
# ============================================
@app.get("/answers/status")
async def answers_status():
    """공개된 답안 목록 반환."""
    return {"unlocked": list(unlocked_answers)}


@app.post("/answers/toggle")
async def answers_toggle(request: Request):
    """답안 공개/잠금 토글 — 강사(syngha.han)만 가능."""
    body = await request.json()
    token = body.get("token", "") or request.cookies.get("challenge_token", "")
    user = get_user_from_token(token)
    if not user or user.get("sub") != "syngha.han":
        return JSONResponse({"error": "강사만 변경할 수 있습니다."}, status_code=403)

    answer_id = body.get("id", "")
    if answer_id in unlocked_answers:
        unlocked_answers.discard(answer_id)
        return {"id": answer_id, "unlocked": False}
    else:
        unlocked_answers.add(answer_id)
        return {"id": answer_id, "unlocked": True}


# ============================================
# Agentic Loop 과제 — API 미로
# ============================================
@app.get("/challenges/agent_loop/start")
async def agent_loop_start_api(request: Request):
    """미로 시작 — 랜덤 3개 스텝 순서 생성."""
    from challenges import agent_loop_start
    token = request.query_params.get("token", "") or request.cookies.get("challenge_token", "")
    if not token and not DEV_MODE:
        return JSONResponse({"error": "token이 필요합니다."}, status_code=401)
    user = get_user_from_token(token)
    if not user:
        return JSONResponse({"error": "유효하지 않은 토큰입니다."}, status_code=401)
    return agent_loop_start(user["sub"])


@app.get("/challenges/agent_loop/step/{step_num}")
async def agent_loop_step_api(step_num: int, request: Request):
    """스텝 호출 — 순서 맞으면 진행, 틀리면 초기화."""
    from challenges import agent_loop_call_step
    token = request.query_params.get("token", "") or request.cookies.get("challenge_token", "")
    if not token and not DEV_MODE:
        return JSONResponse({"error": "token이 필요합니다."}, status_code=401)
    user = get_user_from_token(token)
    if not user:
        return JSONResponse({"error": "유효하지 않은 토큰입니다."}, status_code=401)
    if step_num < 1 or step_num > 10:
        return JSONResponse({"error": "step은 1~10 사이여야 합니다."}, status_code=400)
    return agent_loop_call_step(user["sub"], step_num)


@app.get("/challenges/agent_loop/end")
async def agent_loop_end_api(request: Request):
    """미로 완료 — 3개 다 순서대로 했으면 completion_code 반환."""
    from challenges import agent_loop_end
    token = request.query_params.get("token", "") or request.cookies.get("challenge_token", "")
    if not token and not DEV_MODE:
        return JSONResponse({"error": "token이 필요합니다."}, status_code=401)
    user = get_user_from_token(token)
    if not user:
        return JSONResponse({"error": "유효하지 않은 토큰입니다."}, status_code=401)
    return agent_loop_end(user["sub"])


# ============================================
# 브라우저 과제: 비밀 키 API (JS에서 fetch)
# ============================================
@app.get("/api/browser-secret")
async def browser_secret_api():
    """JS에서 fetch하는 비밀 키 API — curl로는 직접 호출 가능하지만, 페이지에서 추출하는 것이 과제."""
    from challenges import BROWSER_SECRET_KEY
    return {"key": BROWSER_SECRET_KEY}


# ============================================
# 브라우저 과제 타겟 페이지 (JS 렌더링 — CDP 필수)
# ============================================
@app.get("/browser-target", response_class=HTMLResponse)
async def browser_target():
    """
    JavaScript로 비밀 키를 로드하는 페이지입니다.
    requests.get()으로는 '로딩 중...'만 보이고, CDP/Playwright로 브라우저를 제어해야 키가 보입니다.
    """
    return HTMLResponse("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Browser Challenge</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0;
               display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .card { background: #1e293b; border-radius: 20px; padding: 48px 56px; text-align: center;
                box-shadow: 0 25px 60px rgba(0,0,0,.4); max-width: 560px; width: 90%; }
        h1 { font-size: 1.6em; margin-bottom: 8px; color: #f1f5f9; }
        .subtitle { color: #64748b; font-size: .9em; margin-bottom: 32px; }
        .loading { color: #94a3b8; font-size: 1.1em; padding: 20px; }
        .hint { margin-top: 20px; padding: 16px 20px; background: rgba(59,130,246,.08);
                border: 1px solid rgba(59,130,246,.2); border-radius: 12px;
                font-size: .82em; color: #93c5fd; line-height: 1.7; text-align: left; }
        .hint code { background: rgba(255,255,255,.08); padding: 1px 6px; border-radius: 4px;
                     font-family: monospace; color: #60a5fa; }
        .warning { margin-top: 16px; padding: 14px 18px; background: rgba(234,179,8,.1);
                   border: 1px solid rgba(234,179,8,.3); border-radius: 10px;
                   font-size: .82em; color: #fbbf24; }
        .badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: .7em;
                 background: rgba(59,130,246,.15); color: #60a5fa; margin-bottom: 16px;
                 letter-spacing: 1px; }
        .status { margin-top: 24px; padding: 12px; background: #0f172a; border-radius: 10px;
                  border: 1px solid #334155; }
        .status-label { font-size: .7em; color: #64748b; text-transform: uppercase;
                        letter-spacing: 2px; margin-bottom: 4px; }
        .status-value { font-family: monospace; font-size: .9em; color: #22c55e; }
    </style></head>
    <body>
        <div class="card">
            <div class="badge">JS RENDERED</div>
            <h1>Browser Challenge</h1>
            <p class="subtitle">이 페이지 어딘가에 비밀 키가 숨겨져 있습니다</p>
            <div id="content">
                <div class="loading">로딩 중...</div>
            </div>
        </div>

        <script>
        (async function() {
            await new Promise(r => setTimeout(r, 1200));
            try {
                const resp = await fetch('/api/browser-secret');
                const data = await resp.json();

                // 비밀 키는 화면에 보이지 않는 hidden 요소에 저장
                const hidden = document.createElement('div');
                hidden.id = 'secret-key';
                hidden.setAttribute('data-key', data.key);
                hidden.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;opacity:0;';
                hidden.textContent = data.key;
                document.body.appendChild(hidden);

                document.getElementById('content').innerHTML =
                    '<div class="status">' +
                    '<div class="status-label">Status</div>' +
                    '<div class="status-value">Secret loaded — hidden in DOM</div>' +
                    '</div>' +
                    '<div class="hint">' +
                    '<strong>힌트:</strong> 비밀 키는 이 페이지의 DOM 안에 숨겨져 있습니다.<br>' +
                    '눈에는 보이지 않지만 <code>document.querySelector</code>나<br>' +
                    '<code>Runtime.evaluate</code>로 찾을 수 있습니다.<br>' +
                    '요소 ID: <code>#secret-key</code>' +
                    '</div>' +
                    '<div class="warning">' +
                    'curl이나 requests.get()으로는 이 스크립트가 실행되지 않습니다.<br>' +
                    'CDP, Playwright, Selenium 등 브라우저 자동화가 필요합니다.' +
                    '</div>';
            } catch (e) {
                document.getElementById('content').innerHTML =
                    '<p style="color:#ef4444">로드 실패: ' + e.message + '</p>';
            }
        })();
        </script>
    </body></html>
    """)


# ============================================
# 프롬프트 과제 — 테스트 케이스 목록
# ============================================
@app.get("/challenges/prompt/cases")
async def prompt_cases():
    """프롬프트 과제의 테스트 케이스 목록을 반환합니다."""
    return [{
        "id": tc["id"],
        "title": tc["title"],
        "input": tc["input"],
        "expected_keys": list(tc["expected"].keys()),
        "expected": tc["expected"],
    } for tc in PROMPT_TEST_CASES]


# ============================================
# 프롬프트 과제 — 단일 테스트 실행
# ============================================
@app.post("/challenges/prompt/test")
async def prompt_test(request: Request):
    """수강생 프롬프트로 단일 테스트 케이스를 실행합니다."""
    body = await request.json()
    prompt = body.get("prompt", "")
    case_id = body.get("case_id")

    if not prompt:
        return JSONResponse({"error": "prompt가 없습니다."}, status_code=400)

    # 과제에 연결된 LLM 찾기
    llm_id = challenge_llm_map.get("prompt")
    llm = llm_endpoints.get(llm_id, llm_config) if llm_id else llm_config

    if not llm.get("base_url"):
        return JSONResponse({"error": "LLM이 설정되지 않았습니다. /settings에서 프롬프트 과제용 LLM을 등록해주세요."}, status_code=400)

    # 테스트 케이스 찾기
    tc = next((t for t in PROMPT_TEST_CASES if t["id"] == case_id), None)
    if not tc:
        return JSONResponse({"error": f"테스트 케이스 {case_id}를 찾을 수 없습니다."}, status_code=404)

    # LLM 호출
    result = call_llm(prompt, tc["input"], list(tc["expected"].keys()), llm)

    if "error" in result:
        return {"case_id": case_id, "pass": False, "error": result["error"], "raw": result.get("raw", "")}

    # 검증
    validation = validate_result(result["parsed"], tc["expected"])

    return {
        "case_id": case_id,
        "title": tc["title"],
        "pass": validation["pass"],
        "details": validation["details"],
        "actual": result["parsed"],
        "expected": tc["expected"],
    }


# ============================================
# 프롬프트 과제 — 전체 제출 (10개 모두 실행)
# ============================================
@app.post("/challenges/prompt/submit")
async def prompt_submit(request: Request):
    """수강생 프롬프트로 10개 전체 테스트. 모두 통과 시 성공 등록."""
    body = await request.json()
    token = body.get("token", "") or request.cookies.get("challenge_token", "")
    prompt = body.get("prompt", "")

    if not token and not DEV_MODE:
        return JSONResponse({"status": "FAIL", "message": "로그인이 필요합니다."}, status_code=401)
    if not prompt:
        return JSONResponse({"status": "FAIL", "message": "prompt가 없습니다."}, status_code=400)

    # 사용자 확인
    user = get_user_from_token(token)
    if not user:
        return JSONResponse({"status": "FAIL", "message": "토큰이 유효하지 않습니다."}, status_code=401)

    # LLM 설정
    llm_id = challenge_llm_map.get("prompt")
    llm = llm_endpoints.get(llm_id, llm_config) if llm_id else llm_config

    if not llm.get("base_url"):
        return JSONResponse({"status": "FAIL", "message": "LLM이 설정되지 않았습니다."}, status_code=400)

    # 10개 전부 실행
    results = []
    all_pass = True
    for tc in PROMPT_TEST_CASES:
        llm_result = call_llm(prompt, tc["input"], list(tc["expected"].keys()), llm)

        if "error" in llm_result:
            results.append({"case_id": tc["id"], "title": tc["title"], "pass": False, "error": llm_result["error"]})
            all_pass = False
            continue

        validation = validate_result(llm_result["parsed"], tc["expected"])
        results.append({
            "case_id": tc["id"],
            "title": tc["title"],
            "pass": validation["pass"],
            "details": validation["details"],
        })
        if not validation["pass"]:
            all_pass = False

    passed_count = sum(1 for r in results if r["pass"])
    user_name = user.get("name", "?")
    user_dept = user.get("dept", "?")
    user_sub = user.get("sub", "?")

    if all_pass:
        # 성공자 등록
        already = any(c["sub"] == user_sub for c in completions.get("prompt", []))
        if not already:
            if "prompt" not in completions:
                completions["prompt"] = []
            completions["prompt"].append({
                "sub": user_sub,
                "name": user_name,
                "dept": user_dept,
                "email": user.get("email", ""),
                "timestamp": datetime.now().isoformat(),
            })

    return {
        "status": "SUCCESS" if all_pass else "FAIL",
        "user": user_name,
        "message": f"🎉 {user_name}님, 프롬프트 엔지니어링 통과! {passed_count}/10" if all_pass else f"{passed_count}/10 통과 — 실패한 케이스를 확인하세요.",
        "passed": passed_count,
        "total": 10,
        "results": results,
    }


# ============================================
# 프롬프트 과제 UI 페이지
# ============================================
# /challenges/prompt → React SPA에서 처리 (로그인 체크는 React에서)


# ============================================
# LLM Endpoint 관리 API
# ============================================
@app.get("/settings/llm-endpoints")
async def list_llm_endpoints():
    return {"endpoints": llm_endpoints, "challenge_map": challenge_llm_map}


@app.post("/settings/llm-endpoints")
async def add_llm_endpoint(request: Request):
    body = await request.json()
    eid = body.get("id", "").strip()
    if not eid:
        import uuid
        eid = str(uuid.uuid4())[:8]

    llm_endpoints[eid] = {
        "name": body.get("name", eid),
        "base_url": body.get("base_url", ""),
        "api_key": body.get("api_key", ""),
        "model": body.get("model", ""),
    }

    # 연결 테스트
    try:
        resp = requests.post(
            f"{llm_endpoints[eid]['base_url']}/chat/completions",
            headers={"Authorization": f"Bearer {llm_endpoints[eid]['api_key']}", "Content-Type": "application/json"},
            json={"model": llm_endpoints[eid]["model"], "messages": [{"role": "user", "content": "test"}], "max_tokens": 5},
            verify=False, timeout=15, proxies={"http": None, "https": None},
        )
        ok = resp.status_code == 200
    except Exception:
        ok = False

    return {"status": "ok" if ok else "error", "id": eid, "message": f"{'연결 성공' if ok else '연결 실패'}: {llm_endpoints[eid]['name']}"}


@app.delete("/settings/llm-endpoints/{endpoint_id}")
async def delete_llm_endpoint(endpoint_id: str):
    if endpoint_id in llm_endpoints:
        del llm_endpoints[endpoint_id]
        # 매핑에서도 제거
        for k, v in list(challenge_llm_map.items()):
            if v == endpoint_id:
                del challenge_llm_map[k]
        return {"status": "ok", "message": f"'{endpoint_id}' 삭제됨"}
    return JSONResponse({"status": "error", "message": "없는 ID"}, status_code=404)


@app.post("/settings/challenge-llm")
async def set_challenge_llm(request: Request):
    """과제에 LLM 연결"""
    body = await request.json()
    challenge_id = body.get("challenge_id", "")
    llm_id = body.get("llm_id", "")
    challenge_llm_map[challenge_id] = llm_id
    return {"status": "ok", "message": f"과제 '{challenge_id}'에 LLM '{llm_id}' 연결됨"}


# ============================================
# 실습 코드 다운로드
# ============================================
@app.get("/downloads/{challenge_id}")
async def download_challenge(challenge_id: str):
    """과제별 실습 코드를 zip으로 다운로드합니다."""
    import zipfile
    import io

    # 과제별 디렉토리 매핑
    dirs = {
        "sso": "day1/00_sso/challenge",
        "prompt": "day1/03_prompt/challenge",
        "endpoint": "day1/04_endpoint/challenge",
        "tool_use": "day1/05_tool_use/challenge",
        "structured": "day1/05_structured_output",
        "browser": "day1/07_browser_control",
        "agent_loop": "day2/01_agent_loop/challenge",
        "index_explore": "day2/02_index_explore/challenge",
        "agent_loop": "day2/01_agent_loop",
        "final": "day2/06_final_exercise",
    }

    target = dirs.get(challenge_id)
    if not target:
        raise HTTPException(404, f"과제 '{challenge_id}' 코드를 찾을 수 없습니다")

    base = Path(__file__).parent / target
    if not base.exists():
        raise HTTPException(404, f"디렉토리 없음: {target}")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in base.rglob('*'):
            if f.is_file() and '__pycache__' not in str(f):
                zf.write(f, f.relative_to(base.parent))

    buf.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(buf, media_type='application/zip',
        headers={'Content-Disposition': f'attachment; filename={challenge_id}_code.zip'})


# ============================================
# 슬라이드 동기화 API
# ============================================
@app.get("/slides/current")
async def get_current_slide():
    return current_slide

@app.post("/slides/current")
async def set_current_slide(request: Request):
    body = await request.json()
    # 강사만 변경 가능 (syngha.han)
    token = request.cookies.get("challenge_token", "")
    if not DEV_MODE:
        user = get_user_from_token(token) if token else None
        if not user or user.get("sub") != "syngha.han":
            return JSONResponse({"error": "강사만 슬라이드를 변경할 수 있습니다."}, status_code=403)
    current_slide["slide"] = body.get("slide", 1)
    return current_slide


# ============================================
# 반응 API (동시성 — Lock 사용)
# ============================================
@app.post("/reactions")
async def add_reaction(request: Request):
    body = await request.json()
    slide = body.get("slide", 0)
    rtype = body.get("type", "")
    if not rtype:
        return JSONResponse({"error": "type 필요"}, status_code=400)
    with reactions_lock:
        if slide not in reactions_data:
            reactions_data[slide] = {}
        reactions_data[slide][rtype] = reactions_data[slide].get(rtype, 0) + 1
    return {"ok": True}


@app.get("/reactions")
async def get_reactions(slide: int = 0):
    with reactions_lock:
        return reactions_data.get(slide, {})


# ============================================
# 질문 API
# ============================================
@app.post("/questions")
async def add_question(request: Request):
    body = await request.json()
    slide = body.get("slide", 0)
    text = body.get("text", "").strip()
    if not text:
        return JSONResponse({"error": "text 필요"}, status_code=400)
    # 사용자 정보 (쿠키에서)
    token = request.cookies.get("challenge_token", "")
    user = get_user_from_token(token) if token else None
    with questions_lock:
        questions_data.append({
            "slide": slide,
            "user": user.get("name", "익명") if user else "익명",
            "text": text,
            "timestamp": datetime.now().isoformat(),
        })
    return {"ok": True}


@app.get("/questions")
async def get_questions(slide: int = 0):
    with questions_lock:
        if slide == 0:
            return questions_data[-50:]  # 최근 50개
        return [q for q in questions_data if q["slide"] == slide][-20:]


# ============================================
# 헬스체크 (SPA fallback보다 먼저 등록)
# ============================================
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "challenge-server",
        "port": PORT,
        "auth_server": AUTH_SERVER,
        "challenges": len(CHALLENGES),
        "llm_endpoints": len(llm_endpoints),
    }


# ============================================
# React 빌드 파일 서빙 (SPA fallback — 맨 마지막)
# ============================================
from fastapi.staticfiles import StaticFiles

_frontend_dist = Path(__file__).parent / "frontend" / "dist"
if _frontend_dist.exists():
    # 정적 파일 (JS, CSS, 이미지)
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="assets")

    # favicon 등 public 파일
    @app.get("/favicon.svg")
    async def favicon():
        f = _frontend_dist / "favicon.svg"
        if f.exists():
            from fastapi.responses import FileResponse
            return FileResponse(str(f))

    # SPA fallback — 모든 나머지 경로에서 index.html 반환
    @app.get("/", response_class=HTMLResponse)
    async def spa_root(request: Request):
        return HTMLResponse((_frontend_dist / "index.html").read_text(encoding="utf-8"))

    @app.get("/{path:path}", response_class=HTMLResponse)
    async def spa_fallback(path: str, request: Request):
        index = _frontend_dist / "index.html"
        if index.exists():
            return HTMLResponse(index.read_text(encoding="utf-8"))
        return HTMLResponse("<h1>Build not found</h1>")
else:
    # React 빌드가 없으면 기존 HTML fallback
    @app.get("/", response_class=HTMLResponse)
    async def legacy_dashboard():
        html = Path(__file__).parent / "dashboard.html"
        return HTMLResponse(html.read_text(encoding="utf-8") if html.exists() else "<h1>No frontend build</h1>")


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
