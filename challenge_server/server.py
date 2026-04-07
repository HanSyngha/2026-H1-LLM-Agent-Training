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
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"  # 로컬 테스트용 SSO 우회
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

# 반응/질문 저장 (동시성 고려 — Lock 사용)
from threading import Lock
reactions_lock = Lock()
reactions_data: dict[int, dict[str, int]] = {}  # {slide_num: {type: count}}
questions_lock = Lock()
questions_data: list[dict] = []  # [{slide, user, text, timestamp}]

# 성공자 저장 (메모리 — 서버 재시작 시 초기화)
# {challenge_id: [{name, dept, email, timestamp}, ...]}
completions: dict[str, list[dict]] = {cid: [] for cid in CHALLENGES}


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
        return {"sub": "dev.user", "name": "개발자", "dept": "개발팀", "email": "dev@test.com"}
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
    """현재 로그인한 사용자 정보를 반환합니다."""
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


# ============================================
# 브라우저 과제: 데이터 API (JS에서 fetch)
# ============================================
@app.get("/api/wiki-data")
async def wiki_data():
    """JS에서 fetch하는 데이터 API — requests.get('/browser-target')으로는 빈 페이지만 보입니다."""
    from challenges import BROWSER_TARGET_DATA
    return BROWSER_TARGET_DATA


# ============================================
# 브라우저 과제 타겟 페이지 (JS 렌더링 — CDP 필수)
# ============================================
@app.get("/browser-target", response_class=HTMLResponse)
async def browser_target():
    """
    JavaScript로 데이터를 로드하는 wiki 페이지입니다.
    requests.get()으로는 빈 테이블만 보이고, CDP로 브라우저를 제어해야 데이터가 보입니다.
    """
    return HTMLResponse("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>반도체 제품 Wiki</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; padding: 2em; background: #f8fafc; max-width: 800px; margin: 0 auto; }
        h1 { color: #1e293b; margin-bottom: .5em; }
        .subtitle { color: #64748b; margin-bottom: 2em; }
        table { border-collapse: collapse; width: 100%; }
        th, td { padding: 14px 18px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #1e293b; color: white; font-weight: 600; }
        tr:hover td { background: #f1f5f9; }
        .product-name { font-weight: 600; color: #1e293b; }
        .price { color: #2563eb; font-weight: 600; font-family: monospace; }
        .loading { text-align: center; padding: 2em; color: #94a3b8; }
        .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: .75em;
                 background: #dbeafe; color: #1d4ed8; margin-left: .5em; }
        .note { margin-top: 2em; padding: 1em; background: #fefce8; border: 1px solid #fde68a;
                border-radius: 8px; font-size: .85em; color: #92400e; }
    </style></head>
    <body>
        <h1>반도체 제품 Wiki <span class="badge">JS Rendered</span></h1>
        <p class="subtitle">이 페이지의 데이터는 JavaScript로 로드됩니다.</p>
        <div id="content"><div class="loading">데이터 로드 중...</div></div>
        <div class="note">
            <strong>참고:</strong> 이 페이지는 JavaScript가 실행되어야 데이터가 표시됩니다.
            단순 HTTP 요청(requests.get)으로는 "데이터 로드 중..." 만 보입니다.
        </div>

        <script>
        // 페이지 로드 후 API에서 데이터를 가져와 테이블을 생성합니다.
        // CDP로 브라우저를 제어해야만 이 JavaScript가 실행됩니다.
        (async function() {
            try {
                const resp = await fetch('/api/wiki-data');
                const products = await resp.json();

                let html = '<table><thead><tr><th>제품명</th><th>가격</th></tr></thead><tbody>';
                products.forEach(p => {
                    html += `<tr><td class="product-name">${p.name}</td><td class="price">${p.price.toLocaleString()}원</td></tr>`;
                });
                html += '</tbody></table>';
                html += `<p style="margin-top:1em;color:#64748b;font-size:.85em">총 ${products.length}개 제품 | 마지막 업데이트: ${new Date().toLocaleString('ko-KR')}</p>`;

                document.getElementById('content').innerHTML = html;
            } catch (e) {
                document.getElementById('content').innerHTML = '<p style="color:red">데이터 로드 실패: ' + e.message + '</p>';
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

    if not token:
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


@app.post("/settings/challenge-llm")
async def set_challenge_llm(request: Request):
    """과제에 LLM 연결"""
    body = await request.json()
    challenge_id = body.get("challenge_id", "")
    llm_id = body.get("llm_id", "")
    challenge_llm_map[challenge_id] = llm_id
    return {"status": "ok", "message": f"과제 '{challenge_id}'에 LLM '{llm_id}' 연결됨"}


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
