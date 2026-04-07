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
AUTH_SERVER = os.getenv("AUTH_SERVER", "http://a2g.samsungds.net:8090")
PORT = int(os.getenv("CHALLENGE_PORT", "47777"))

# LLM 설정 (설정 페이지에서 변경 가능)
llm_config = {
    "base_url": os.getenv("LLM_GATEWAY_URL", ""),
    "api_key": os.getenv("LLM_GATEWAY_API_KEY", ""),
    "model": os.getenv("LLM_MODEL", "gpt-4o"),
}

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
            verify=False,
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
@app.get("/settings", response_class=HTMLResponse)
async def settings_page():
    """LLM 설정 페이지입니다."""
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Challenge Server 설정</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0;
               display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 2em; }}
        .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 2.5em;
                 max-width: 550px; width: 100%; }}
        h1 {{ font-size: 1.5em; margin-bottom: .5em; color: #f1f5f9; }}
        p {{ color: #64748b; margin-bottom: 1.5em; font-size: .9em; }}
        label {{ display: block; font-size: .85em; color: #94a3b8; margin-bottom: .3em; margin-top: 1em; }}
        input {{ width: 100%; padding: 10px 14px; background: #0f172a; border: 1px solid #334155;
                 border-radius: 8px; color: #e2e8f0; font-size: .95em; font-family: monospace; }}
        input:focus {{ border-color: #6366f1; outline: none; }}
        .btn {{ width: 100%; padding: 12px; background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white; border: none; border-radius: 8px; font-size: 1em; font-weight: 600;
                cursor: pointer; margin-top: 1.5em; }}
        .btn:hover {{ filter: brightness(1.1); }}
        .status {{ margin-top: 1em; padding: 10px; border-radius: 8px; font-size: .85em; display: none; }}
        .ok {{ background: rgba(16,185,129,.15); color: #34d399; border: 1px solid rgba(16,185,129,.3); }}
        .err {{ background: rgba(239,68,68,.15); color: #f87171; border: 1px solid rgba(239,68,68,.3); }}
        .current {{ margin-top: 1em; padding: 10px; background: #0f172a; border-radius: 8px; font-size: .8em;
                    color: #64748b; font-family: monospace; }}
    </style></head>
    <body>
    <div class="card">
        <h1>Challenge Server 설정</h1>
        <p>채점에 사용할 LLM (OpenAI Compatible) 엔드포인트를 설정하세요.</p>

        <label>LLM Base URL</label>
        <input id="url" type="text" placeholder="http://your-gateway:port/v1" value="{llm_config['base_url']}">

        <label>API Key</label>
        <input id="key" type="password" placeholder="sk-..." value="{llm_config['api_key']}">

        <label>Model</label>
        <input id="model" type="text" placeholder="gpt-4o" value="{llm_config['model']}">

        <button class="btn" onclick="save()">저장 및 테스트</button>

        <div class="status" id="status"></div>
        <div class="current">
            현재 상태: LLM {'연결됨 ✅' if llm_config['base_url'] else '미설정 ⚠️ (하드코딩 검증 모드)'}
        </div>
    </div>
    <script>
    async function save() {{
        const s = document.getElementById('status');
        s.style.display = 'block';
        s.className = 'status';
        s.textContent = '저장 중...';

        try {{
            const resp = await fetch('/settings/update', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    base_url: document.getElementById('url').value,
                    api_key: document.getElementById('key').value,
                    model: document.getElementById('model').value,
                }})
            }});
            const data = await resp.json();
            if (data.status === 'ok') {{
                s.className = 'status ok';
                s.textContent = '✅ ' + data.message;
            }} else {{
                s.className = 'status err';
                s.textContent = '❌ ' + data.message;
            }}
        }} catch (e) {{
            s.className = 'status err';
            s.textContent = '❌ 요청 실패: ' + e.message;
        }}
    }}
    </script>
    </body></html>
    """)


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
            verify=False, timeout=15,
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
