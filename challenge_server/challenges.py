"""
과제 정의 및 검증 로직

각 과제는:
- name: 과제명
- description: 한줄 설명
- mission: GET /challenges/{id}/mission으로 수강생에게 제공되는 데이터
- submit_schema: 제출 형식 설명
- validate(answer): 정답 검증 함수
"""


# ============================================
# 과제 1: 프롬프트 엔지니어링
# ============================================
PROMPT_MISSION = {
    "tasks": [
        {
            "id": "classify",
            "type": "감정 분류",
            "input": "이 제품 정말 괜찮은데 배송이 너무 느려서 다시는 안 살 것 같아요. 품질은 좋은데 서비스가 별로네요.",
            "expected_format": "긍정 / 부정 / 중립 / 혼합 중 하나",
        },
        {
            "id": "summarize",
            "type": "요약",
            "input": (
                "인공지능(AI) 기술이 제조업에 미치는 영향이 날로 커지고 있습니다. "
                "특히 반도체 공정에서는 불량 검출, 수율 예측, 설비 예지보전 등에 AI가 활발히 적용되고 있습니다. "
                "기존에 엔지니어가 수동으로 분석하던 공정 데이터를 AI가 자동으로 분석하여 이상 징후를 조기에 감지할 수 있게 되었습니다. "
                "이에 따라 불량률이 평균 30% 감소하고, 설비 가동률은 15% 향상되었다는 보고가 있습니다. "
                "다만 AI 모델의 정확도는 학습 데이터의 품질에 크게 좌우되므로, 데이터 관리 체계 구축이 선행되어야 합니다. "
                "또한 현장 엔지니어와 AI 시스템 간의 협업 방식을 정립하는 것도 중요한 과제입니다."
            ),
            "expected_format": "3문장 이내 요약",
        },
        {
            "id": "extract",
            "type": "정보 추출",
            "input": (
                "안녕하세요, 다음 주 화요일 (4월 15일) 오후 2시에 본관 3층 대회의실에서 "
                "AI 전략 회의를 진행할 예정입니다. 참석자는 김부장, 이과장, 박대리입니다. "
                "회의 자료는 전날까지 공유 부탁드립니다."
            ),
            "expected_format": '{"date": "...", "time": "...", "location": "...", "attendees": [...]}',
        },
    ]
}


def validate_prompt(answer: dict) -> dict:
    """프롬프트 과제 검증"""
    results = []

    # Task 1: 감정 분류
    classify = answer.get("classify", "").strip()
    if classify in ["혼합", "mixed"]:
        results.append({"task": "classify", "passed": True, "message": "감정 분류 정확합니다"})
    else:
        results.append({"task": "classify", "passed": False,
                        "message": f"'{classify}'는 정확하지 않습니다. 긍정과 부정이 섞여있는 리뷰입니다"})

    # Task 2: 요약
    summary = answer.get("summarize", "").strip()
    sentences = [s.strip() for s in summary.replace(".", ".\n").split("\n") if s.strip()]
    has_key = any(kw in summary for kw in ["반도체", "AI", "불량", "수율", "데이터"])
    if len(sentences) <= 3 and has_key and len(summary) > 20:
        results.append({"task": "summarize", "passed": True, "message": "요약이 적절합니다"})
    else:
        msg = []
        if len(sentences) > 3:
            msg.append(f"3문장 이내여야 합니다 (현재 {len(sentences)}문장)")
        if not has_key:
            msg.append("핵심 키워드(반도체, AI, 불량 등)가 포함되어야 합니다")
        results.append({"task": "summarize", "passed": False, "message": ", ".join(msg)})

    # Task 3: 정보 추출
    extract = answer.get("extract", {})
    if isinstance(extract, str):
        try:
            import json
            extract = json.loads(extract)
        except Exception:
            results.append({"task": "extract", "passed": False, "message": "JSON 형식이 아닙니다"})
            passed = sum(1 for r in results if r["passed"])
            return {
                "passed": passed == 3,
                "message": f"{passed}/3 미션 통과",
                "details": results,
            }

    extract_ok = True
    extract_msgs = []
    if "date" not in extract or "15" not in str(extract.get("date", "")):
        extract_ok = False
        extract_msgs.append("date에 '4월 15일'이 포함되어야 합니다")
    if "time" not in extract or "2" not in str(extract.get("time", "")):
        extract_ok = False
        extract_msgs.append("time에 '오후 2시'가 포함되어야 합니다")
    if "location" not in extract or "대회의실" not in str(extract.get("location", "")):
        extract_ok = False
        extract_msgs.append("location에 '대회의실'이 포함되어야 합니다")
    if "attendees" not in extract or not isinstance(extract.get("attendees"), list):
        extract_ok = False
        extract_msgs.append("attendees는 배열이어야 합니다")

    if extract_ok:
        results.append({"task": "extract", "passed": True, "message": "정보 추출 정확합니다"})
    else:
        results.append({"task": "extract", "passed": False, "message": ", ".join(extract_msgs)})

    passed = sum(1 for r in results if r["passed"])
    return {
        "passed": passed == 3,
        "message": f"{passed}/3 미션 통과",
        "details": results,
    }


# ============================================
# 과제 2: LLM Endpoint 연결
# ============================================
ENDPOINT_MISSION = {
    "description": "SSO 로그인 후 사내 LLM Gateway에 연결하여 챗봇을 완성하세요.",
    "gateway_url": "http://a2g.samsungds.net:8090/v1",
    "service_id": "test-service",
    "headers": {
        "x-service-id": "test-service (미리 세팅됨)",
        "x-user-id": "<SSO 로그인한 user ID>",
    },
    "hint": "app.py에 SSO 로그인을 연동하면 챗봇이 동작하고, LLM 응답 시 자동 제출됩니다.",
}


def validate_endpoint(answer: dict) -> dict:
    response_text = str(answer.get("response", "")).strip()

    if len(response_text) < 2:
        return {"passed": False, "message": "LLM 응답이 비어있습니다.", "details": []}

    return {"passed": True, "message": "LLM Gateway 연결 및 응답 확인 완료!",
            "details": [{"passed": True, "message": f"응답: {response_text[:100]}"}]}


# ============================================
# 과제 3: Structured Output
# ============================================
STRUCTURED_MISSION = {
    "article": (
        "[속보] 삼성전자, 차세대 AI 반도체 'Mach-1' 양산 개시\n\n"
        "삼성전자가 자체 개발한 AI 가속기 'Mach-1'의 양산을 시작했다고 15일 밝혔다. "
        "Mach-1은 기존 제품 대비 전력 효율이 2배 향상되었으며, "
        "주요 글로벌 클라우드 업체들과 공급 계약을 체결한 것으로 알려졌다. "
        "업계에서는 이번 양산이 삼성전자의 비메모리 사업 경쟁력을 크게 높일 것으로 전망하고 있다. "
        "다만 일부 전문가들은 TSMC와의 기술 격차가 여전하다는 점을 지적했다."
    ),
    "required_schema": {
        "title": "string (기사 제목)",
        "category": "string (기술/경제/정치/사회/스포츠 중 하나)",
        "sentiment": "string (긍정/부정/중립 중 하나)",
        "keywords": "string[] (3~5개 키워드)",
        "summary": "string (2문장 이내 요약)",
    },
}


def validate_structured(answer: dict) -> dict:
    details = []
    fields = ["title", "category", "sentiment", "keywords", "summary"]

    for field in fields:
        if field not in answer:
            details.append({"field": field, "passed": False, "message": f"'{field}' 필드가 없습니다"})
            continue

        value = answer[field]

        if field == "category":
            valid = value in ["기술", "경제", "정치", "사회", "스포츠"]
            details.append({"field": field, "passed": valid,
                            "message": f"'{value}'" + ("" if valid else " — 허용값: 기술/경제/정치/사회/스포츠")})
        elif field == "sentiment":
            valid = value in ["긍정", "부정", "중립"]
            details.append({"field": field, "passed": valid,
                            "message": f"'{value}'" + ("" if valid else " — 허용값: 긍정/부정/중립")})
        elif field == "keywords":
            valid = isinstance(value, list) and 3 <= len(value) <= 5
            details.append({"field": field, "passed": valid,
                            "message": f"{len(value) if isinstance(value, list) else 0}개" +
                                       ("" if valid else " — 3~5개 필요")})
        elif field == "summary":
            sentences = [s for s in str(value).split(".") if s.strip()]
            valid = len(sentences) <= 2 and len(str(value)) > 10
            details.append({"field": field, "passed": valid,
                            "message": f"{len(sentences)}문장" + ("" if valid else " — 2문장 이내 필요")})
        else:
            valid = isinstance(value, str) and len(value) > 0
            details.append({"field": field, "passed": valid, "message": f"'{value[:30]}'"})

    passed = sum(1 for d in details if d["passed"])
    return {
        "passed": passed == 5,
        "message": f"{passed}/5 필드 검증 통과",
        "details": details,
    }


# ============================================
# 과제 4: MCP
# ============================================
MCP_MISSION = {
    "description": "MCP 서버(day1/01_mcp/mcp_server.py)에 연결하여 아래 3가지 도구를 호출하세요.",
    "tasks": [
        {"tool": "add", "args": {"a": 157, "b": 289}, "expected": 446},
        {"tool": "get_weather", "args": {"city": "서울"}, "expected_contains": "맑음"},
        {"tool": "search_employee", "args": {"name": "김"}, "expected_contains": "김"},
    ],
    "note": "MCP 서버는 수강생이 직접 실행하세요: python day1/01_mcp/mcp_server.py",
}


def validate_mcp(answer: dict) -> dict:
    details = []
    results = answer.get("results", [])

    if not isinstance(results, list) or len(results) < 3:
        return {"passed": False, "message": f"results 배열에 3개 결과가 필요합니다 (현재 {len(results) if isinstance(results, list) else 0}개)",
                "details": []}

    tasks = MCP_MISSION["tasks"]
    for i, task in enumerate(tasks):
        if i >= len(results):
            details.append({"tool": task["tool"], "passed": False, "message": "결과 없음"})
            continue

        result_str = str(results[i])
        if "expected" in task:
            ok = str(task["expected"]) in result_str
        else:
            ok = task["expected_contains"] in result_str

        details.append({
            "tool": task["tool"],
            "passed": ok,
            "message": f"결과: {result_str[:50]}" + ("" if ok else f" — '{task.get('expected_contains', task.get('expected'))}' 포함 필요"),
        })

    passed = sum(1 for d in details if d["passed"])
    return {"passed": passed == 3, "message": f"{passed}/3 도구 호출 성공", "details": details}


# ============================================
# 과제 5: 브라우저 자동화 (CDP로 비밀 키 추출)
# ============================================
BROWSER_SECRET_KEY = "BROWSER-CDP-2026-SAMSUNG"

BROWSER_MISSION = {
    "target_url": "http://a2g.samsungds.net:47777/browser-target",
    "description": "위 URL에 접속하면 비밀 키가 표시됩니다. 단, JavaScript로 렌더링되므로 curl/requests로는 보이지 않습니다. CDP 또는 Playwright로 브라우저를 제어하여 비밀 키를 추출하세요.",
    "hint": "requests.get()으로는 '로딩 중...'만 보입니다. 브라우저 자동화가 필요합니다.",
}


def validate_browser(answer: dict) -> dict:
    secret = str(answer.get("secret_key", "")).strip()
    if secret == BROWSER_SECRET_KEY:
        return {"passed": True, "message": "브라우저 자동화 과제 통과! CDP로 비밀 키를 추출했습니다.",
                "details": [{"passed": True, "message": f"키 일치: {secret}"}]}
    return {"passed": False, "message": f"비밀 키가 일치하지 않습니다.",
            "details": [{"passed": False, "message": f"제출: '{secret[:20]}...' — http://a2g.samsungds.net:47777/browser-target 페이지를 브라우저로 열어 확인하세요."}]}


# ============================================
# 과제 6: Agentic Loop — API 미로
# ============================================
import random as _random

# 유저별 세션: {user_sub: {"sequence": [3,7,1], "progress": 0}}
_agent_loop_sessions = {}

AGENT_LOOP_STEPS = {
    1: {"name": "인증 서버 확인", "data": "AUTH_TOKEN_VALID"},
    2: {"name": "사용자 프로필 조회", "data": "PROFILE_LOADED"},
    3: {"name": "권한 검증", "data": "PERMISSION_GRANTED"},
    4: {"name": "데이터베이스 연결", "data": "DB_CONNECTED"},
    5: {"name": "캐시 조회", "data": "CACHE_HIT"},
    6: {"name": "외부 API 호출", "data": "EXTERNAL_OK"},
    7: {"name": "로그 기록", "data": "LOG_WRITTEN"},
    8: {"name": "알림 전송", "data": "NOTIFICATION_SENT"},
    9: {"name": "파일 시스템 접근", "data": "FILE_ACCESSED"},
    10: {"name": "보안 스캔", "data": "SECURITY_CLEAR"},
}


def agent_loop_start(user_sub: str) -> dict:
    """미로 시작 — 랜덤 3개 스텝 순서 생성"""
    seq = sorted(_random.sample(range(1, 11), 3), key=lambda _: _random.random())
    _agent_loop_sessions[user_sub] = {"sequence": seq, "progress": 0, "collected": []}
    return {
        "message": "미로가 시작되었습니다! 아래 3개의 API를 순서대로 호출하세요.",
        "sequence": [
            {"order": i + 1, "step": s, "name": AGENT_LOOP_STEPS[s]["name"]}
            for i, s in enumerate(seq)
        ],
        "warning": "순서를 틀리면 처음부터 다시 시작합니다!",
    }


def agent_loop_call_step(user_sub: str, step_num: int) -> dict:
    """스텝 호출 — 순서 맞으면 진행, 틀리면 초기화"""
    session = _agent_loop_sessions.get(user_sub)
    if not session:
        return {"error": True, "message": "먼저 start를 호출하세요."}

    expected = session["sequence"][session["progress"]]
    if step_num != expected:
        # 틀림 → 초기화
        old_seq = session["sequence"]
        _agent_loop_sessions.pop(user_sub, None)
        return {
            "error": True,
            "message": f"순서가 틀렸습니다! step{expected}을 호출해야 하는데 step{step_num}을 호출했습니다. 세션이 초기화됩니다.",
            "expected": expected,
            "got": step_num,
            "hint": "start부터 다시 시작하세요.",
        }

    # 맞음 → 진행
    step_info = AGENT_LOOP_STEPS[step_num]
    session["progress"] += 1
    session["collected"].append(step_info["data"])

    remaining = session["sequence"][session["progress"]:]
    return {
        "success": True,
        "step": step_num,
        "name": step_info["name"],
        "code": step_info["data"],
        "progress": f"{session['progress']}/{len(session['sequence'])}",
        "next": f"step{remaining[0]}" if remaining else "end를 호출하세요!",
        "message": f"step{step_num} 통과! {'다음: step' + str(remaining[0]) if remaining else '모든 스텝 완료! end를 호출하세요.'}",
    }


def agent_loop_end(user_sub: str) -> dict:
    """미로 완료 확인"""
    session = _agent_loop_sessions.get(user_sub)
    if not session:
        return {"error": True, "message": "먼저 start를 호출하세요."}

    if session["progress"] < len(session["sequence"]):
        done = session["progress"]
        total = len(session["sequence"])
        return {
            "error": True,
            "message": f"아직 {total - done}개 스텝이 남았습니다. ({done}/{total} 완료)",
        }

    # 성공!
    code = "-".join(session["collected"])
    _agent_loop_sessions.pop(user_sub, None)
    return {
        "success": True,
        "message": "미로 탈출 성공!",
        "completion_code": code,
    }


AGENT_LOOP_MISSION = {
    "description": "Agentic Loop를 구현하여 API 미로를 탈출하세요.",
    "apis": {
        "start": "GET /challenges/agent_loop/start — 미로 시작, 3개 스텝 순서 안내",
        "step": "GET /challenges/agent_loop/step/{n} — n번 스텝 호출 (순서 틀리면 초기화!)",
        "end": "GET /challenges/agent_loop/end — 3개 완료 후 종료, completion_code 획득",
    },
    "flow": "start → step(순서대로 3개) → end → completion_code를 슬라이드에 입력",
}


def validate_agent_loop(answer: dict) -> dict:
    code = str(answer.get("completion_code", "")).strip()
    if not code:
        return {"passed": False, "message": "completion_code가 없습니다.", "details": []}

    # completion_code는 3개의 스텝 데이터를 -로 연결한 것
    parts = code.split("-")
    valid_codes = [s["data"] for s in AGENT_LOOP_STEPS.values()]
    if len(parts) == 3 and all(p in valid_codes for p in parts):
        return {
            "passed": True,
            "message": "Agentic Loop 과제 통과! API 미로를 성공적으로 탈출했습니다.",
            "details": [{"step": i + 1, "passed": True, "code": p} for i, p in enumerate(parts)],
        }

    return {"passed": False, "message": "유효하지 않은 completion_code입니다.", "details": []}


# ============================================
# 과제 7: 종합 실습
# ============================================
FINAL_MISSION = {
    "description": "브라우저로 검색하여 결과를 추출하고, Excel 파일로 저장한 뒤, 파일 내용을 제출하세요.",
    "search_query": "2026 AI 반도체 트렌드",
    "required_fields": ["title", "link"],
    "min_items": 3,
}


def validate_final(answer: dict) -> dict:
    items = answer.get("items", [])

    if not isinstance(items, list):
        return {"passed": False, "message": "items는 배열이어야 합니다", "details": []}

    if len(items) < FINAL_MISSION["min_items"]:
        return {"passed": False,
                "message": f"최소 {FINAL_MISSION['min_items']}개 항목 필요 (현재 {len(items)}개)",
                "details": []}

    details = []
    valid_count = 0
    for i, item in enumerate(items[:5]):
        has_title = "title" in item and len(str(item["title"])) > 3
        has_link = "link" in item and ("http" in str(item.get("link", "")) or "www" in str(item.get("link", "")))
        ok = has_title and has_link
        if ok:
            valid_count += 1
        details.append({
            "item": i + 1,
            "passed": ok,
            "title": str(item.get("title", "?"))[:40],
            "has_link": has_link,
        })

    return {
        "passed": valid_count >= FINAL_MISSION["min_items"],
        "message": f"{valid_count}개 항목 검증 통과",
        "details": details,
    }


# ============================================
# 과제 8: Index Explore
# ============================================
INDEX_EXPLORE_KEYWORDS = {
    "q1": ["12단", "1.18TB/s"],
    "q2": ["3.5조"],
    "q3": ["오버레이", "38%"],
}


def validate_index_explore(answer: dict) -> dict:
    details = []
    for qid, keywords in INDEX_EXPLORE_KEYWORDS.items():
        ans = str(answer.get(qid, "")).replace(" ", "")
        passed = all(kw.replace(" ", "") in ans for kw in keywords)
        details.append({
            "question": qid,
            "passed": passed,
            "message": f"{'통과' if passed else '키워드 누락'}: {', '.join(keywords)}",
        })
    count = sum(1 for d in details if d["passed"])
    return {
        "passed": count == len(INDEX_EXPLORE_KEYWORDS),
        "message": f"{count}/{len(INDEX_EXPLORE_KEYWORDS)} 질문 통과",
        "details": details,
    }


# ============================================
# 과제 0-1: SSO OAuth2
# ============================================
SSO_OAUTH2_MISSION = {
    "description": "OAuth2 Authorization Code Flow로 로그인하여 본인의 이름과 부서를 제출하세요.",
}


def validate_sso_oauth2(answer: dict) -> dict:
    name = str(answer.get("name", "")).strip()
    dept = str(answer.get("dept", "")).strip()

    details = []
    if not name or len(name) < 2:
        details.append({"field": "name", "passed": False, "message": "이름이 없거나 너무 짧습니다"})
    else:
        details.append({"field": "name", "passed": True, "message": f"이름: {name}"})

    if not dept or len(dept) < 2:
        details.append({"field": "dept", "passed": False, "message": "부서명이 없거나 너무 짧습니다"})
    else:
        details.append({"field": "dept", "passed": True, "message": f"부서: {dept}"})

    passed = all(d["passed"] for d in details)
    return {"passed": passed, "message": f"OAuth2 로그인 {'성공' if passed else '실패'} — {name}, {dept}", "details": details}


# ============================================
# 과제 0-2: SSO OIDC
# ============================================
SSO_OIDC_MISSION = {
    "description": "OIDC로 로그인하여 id_token에서 직접 이름과 부서를 추출하여 제출하세요. /userinfo를 호출하지 마세요.",
}


def validate_sso_oidc(answer: dict) -> dict:
    name = str(answer.get("name", "")).strip()
    dept = str(answer.get("dept", "")).strip()
    method = str(answer.get("method", "")).strip().lower()

    details = []
    if not name or len(name) < 2:
        details.append({"field": "name", "passed": False, "message": "이름이 없거나 너무 짧습니다"})
    else:
        details.append({"field": "name", "passed": True, "message": f"이름: {name}"})

    if not dept or len(dept) < 2:
        details.append({"field": "dept", "passed": False, "message": "부서명이 없거나 너무 짧습니다"})
    else:
        details.append({"field": "dept", "passed": True, "message": f"부서: {dept}"})

    if method != "oidc":
        details.append({"field": "method", "passed": False, "message": f"method가 'oidc'여야 합니다 (현재: '{method}')"})
    else:
        details.append({"field": "method", "passed": True, "message": "OIDC 방식 확인"})

    passed = all(d["passed"] for d in details)
    return {"passed": passed, "message": f"OIDC 로그인 {'성공' if passed else '실패'} — {name}, {dept}", "details": details}


# ============================================
# 과제 3-1: Tool Use (Function Calling)
# ============================================
import secrets as _secrets

# 유저별 시크릿 키 저장소 (서버 메모리)
_tool_use_secrets = {}


def generate_tool_use_secret(user_sub: str) -> str:
    """유저별 시크릿 키 생성 및 저장"""
    key = f"KEY-{_secrets.token_hex(6).upper()}"
    _tool_use_secrets[user_sub] = key
    return key


def get_tool_use_secret(user_sub: str) -> str | None:
    """유저의 현재 시크릿 키 조회"""
    return _tool_use_secrets.get(user_sub)


TOOL_USE_MISSION = {
    "description": "LLM에 Tool(Function Calling)을 연결하여, secret key를 받아 제출하세요.",
    "tools": [
        {
            "name": "get_secret_key",
            "description": "과제용 시크릿 키를 발급받습니다.",
            "endpoint": "GET /challenges/tool_use/secret",
            "params": "token (SSO access_token)",
        },
        {
            "name": "submit_secret_key",
            "description": "발급받은 시크릿 키를 제출합니다.",
            "endpoint": "POST /challenges/tool_use/submit",
            "params": '{"token": "SSO토큰", "answer": {"secret_key": "발급받은키"}}',
        },
    ],
    "flow": "LLM이 get_secret_key 호출 → 키 수령 → submit_secret_key 호출 → 통과",
}


def validate_tool_use(answer: dict) -> dict:
    """시크릿 키 일치 검증 — user_sub는 서버에서 주입"""
    secret = str(answer.get("secret_key", "")).strip()
    user_sub = answer.get("_user_sub", "")  # 서버에서 주입

    if not secret:
        return {"passed": False, "message": "secret_key가 없습니다.", "details": []}

    expected = _tool_use_secrets.get(user_sub)
    if not expected:
        return {"passed": False, "message": "먼저 GET /challenges/tool_use/secret 으로 키를 발급받으세요.", "details": []}

    if secret != expected:
        return {"passed": False, "message": f"시크릿 키가 일치하지 않습니다. (제출: {secret[:10]}...)", "details": []}

    return {
        "passed": True,
        "message": "Tool Use 과제 통과! LLM이 두 개의 Tool을 연속 호출했습니다.",
        "details": [
            {"step": "get_secret_key", "passed": True, "message": "시크릿 키 발급 성공"},
            {"step": "submit_secret_key", "passed": True, "message": f"키 일치: {secret}"},
        ],
    }


# ============================================
# 과제 정의 레지스트리
# ============================================
CHALLENGES = {
    "sso_oidc": {
        "name": "SSO OIDC 로그인",
        "description": "OIDC로 로그인, id_token에서 이름/부서를 추출하여 제출하세요.",
        "mission": SSO_OIDC_MISSION,
        "submit_schema": '{"name": "한글 이름", "dept": "한글 부서명", "method": "oidc"}',
        "validate": validate_sso_oidc,
    },
    "prompt": {
        "name": "프롬프트 엔지니어링",
        "description": "LLM에게 올바른 프롬프트를 작성하여 3가지 미션을 해결하세요.",
        "mission": PROMPT_MISSION,
        "submit_schema": '{"classify": "string", "summarize": "string", "extract": {}}',
        "validate": validate_prompt,
    },
    "endpoint": {
        "name": "LLM Endpoint 연결",
        "description": "사내 LLM Gateway에 연결하여 응답을 받아오세요.",
        "mission": ENDPOINT_MISSION,
        "submit_schema": '{"response": "string (LLM 응답 텍스트)"}',
        "validate": validate_endpoint,
    },
    "tool_use": {
        "name": "Tool Use (Function Calling)",
        "description": "LLM에 Tool을 연결하고, 시크릿 키를 받아 제출하세요.",
        "mission": TOOL_USE_MISSION,
        "submit_schema": '{"secret_key": "발급받은 시크릿 키"}',
        "validate": validate_tool_use,
    },
    "structured": {
        "name": "Structured Output",
        "description": "뉴스 기사를 분석하여 구조화된 JSON으로 추출하세요.",
        "mission": STRUCTURED_MISSION,
        "submit_schema": '{"title": "...", "category": "...", "sentiment": "...", "keywords": [...], "summary": "..."}',
        "validate": validate_structured,
    },
    "browser": {
        "name": "브라우저 자동화 (CDP)",
        "description": "JS 렌더링 페이지에서 비밀 키를 추출하세요.",
        "mission": BROWSER_MISSION,
        "submit_schema": '{"secret_key": "페이지에서 추출한 비밀 키"}',
        "validate": validate_browser,
    },
    "agent_loop": {
        "name": "Agentic Loop (API 미로)",
        "description": "Agentic Loop를 구현하여 API 미로를 탈출하세요.",
        "mission": AGENT_LOOP_MISSION,
        "submit_schema": '{"completion_code": "스텝 코드들을 -로 연결한 문자열"}',
        "validate": validate_agent_loop,
    },
    "index_explore": {
        "name": "Index Explore (.md 인덱스)",
        "description": "계층적 .md 인덱스를 만들어 AI가 문서를 탐색하게 하세요.",
        "mission": {"description": "raw 문서 10개를 .md 계층 구조로 정리하고, AI가 3개 질문에 답하면 통과"},
        "submit_schema": '{"q1": "답변1", "q2": "답변2", "q3": "답변3"}',
        "validate": validate_index_explore,
    },
    "agent_v2": {
        "name": "Agent 설계 (바이브 코딩)",
        "description": "바이브 코딩으로 에이전트를 처음부터 설계하세요.",
        "mission": {"description": "5개 API 작업을 순서대로 실행, 실패 시 재시도, completion_code 획득"},
        "submit_schema": '{"completion_code": "수집 데이터를 -로 연결한 문자열"}',
        "validate": lambda a: {
            "passed": bool(a.get("completion_code", "").count("-") >= 4),
            "message": "Agent 설계 과제 통과!" if a.get("completion_code", "").count("-") >= 4 else "completion_code가 올바르지 않습니다.",
            "details": [],
        },
    },
    "chat_extract": {
        "name": "채팅 정보 추출",
        "description": "팀 대화에서 일정/할일/결정사항을 빠짐없이 추출하세요.",
        "mission": {"description": "장문 채팅 기록에서 핵심 정보 5개 추출"},
        "submit_schema": '{"summary": "요약 텍스트"}',
        "validate": lambda a: {"passed": True, "message": "슬라이드에서 직접 테스트", "details": []},
    },
    "context": {
        "name": "Context Blindness (압축 프롬프트)",
        "description": "5000자 회의록을 500자로 압축하여 AI가 다음 행동을 예측하게 하세요.",
        "mission": {"description": "긴 문서를 압축하되 핵심을 보존하는 능력"},
        "submit_schema": '{"compressed": "압축된 텍스트"}',
        "validate": lambda a: {"passed": True, "message": "슬라이드에서 직접 테스트", "details": []},
    },
    "fewshot": {
        "name": "Few-shot 최적화",
        "description": "최소 예시로 분류 정확도 80% 이상을 달성하세요.",
        "mission": {"description": "고객 문의를 만족/불만/문의로 분류"},
        "submit_schema": '{"prompt": "시스템프롬프트", "examples": [...]}',
        "validate": lambda a: {"passed": True, "message": "슬라이드에서 직접 테스트", "details": []},
    },
    "defense": {
        "name": "System Prompt 방어전",
        "description": "5가지 공격에서 비밀번호를 지키세요.",
        "mission": {"description": "프롬프트 인젝션 방어"},
        "submit_schema": '{"prompt": "방어 시스템프롬프트"}',
        "validate": lambda a: {"passed": True, "message": "슬라이드에서 직접 테스트", "details": []},
    },
}


def validate_answer(challenge_id: str, answer: dict) -> dict:
    """과제별 검증 함수를 호출합니다."""
    challenge = CHALLENGES.get(challenge_id)
    if not challenge:
        return {"passed": False, "message": f"알 수 없는 과제: {challenge_id}"}
    return challenge["validate"](answer)
