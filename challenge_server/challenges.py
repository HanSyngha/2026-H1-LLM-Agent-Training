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
    "question": "대한민국의 수도는 어디이며, 그 도시의 영문명을 알려주세요.",
    "hint": ".env의 LLM_GATEWAY_URL과 LLM_MODEL을 사용하세요",
}


def validate_endpoint(answer: dict) -> dict:
    response_text = str(answer.get("response", "")).strip()
    has_seoul_kr = "서울" in response_text
    has_seoul_en = "Seoul" in response_text or "seoul" in response_text

    if has_seoul_kr and has_seoul_en:
        return {"passed": True, "message": "LLM Gateway 연결 및 응답 확인 완료",
                "details": [{"passed": True, "message": f"응답: {response_text[:100]}"}]}
    else:
        msgs = []
        if not has_seoul_kr:
            msgs.append("'서울'이 포함되어야 합니다")
        if not has_seoul_en:
            msgs.append("'Seoul'이 포함되어야 합니다")
        return {"passed": False, "message": ", ".join(msgs), "details": []}


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
# 과제 5: 브라우저 자동화
# ============================================
BROWSER_MISSION = {
    "target_url": "https://a2g.samsungds.net:70777/browser-target",
    "description": "위 URL의 페이지에서 상품 목록(이름, 가격)을 추출하세요.",
}

# 브라우저 과제 타겟 페이지 데이터
BROWSER_TARGET_DATA = [
    {"name": "AI 가속기 Mach-1", "price": 1250000},
    {"name": "HBM3E 16GB", "price": 89000},
    {"name": "DDR5 32GB", "price": 45000},
    {"name": "SSD 990 PRO 2TB", "price": 189000},
    {"name": "CXL 메모리 모듈", "price": 320000},
]


def validate_browser(answer: dict) -> dict:
    products = answer.get("products", [])
    if not isinstance(products, list):
        return {"passed": False, "message": "products는 배열이어야 합니다", "details": []}

    details = []
    for expected in BROWSER_TARGET_DATA:
        def match_product(p, exp):
            try:
                name_ok = exp["name"] in str(p.get("name", ""))
                price_raw = str(p.get("price", "0")).replace(",", "").replace("원", "").strip()
                price_ok = abs(int(price_raw) - exp["price"]) < 100
                return name_ok and price_ok
            except (ValueError, TypeError):
                return False
        found = any(match_product(p, expected) for p in products)
        details.append({
            "product": expected["name"],
            "passed": found,
            "message": "발견" if found else "미발견",
        })

    passed = sum(1 for d in details if d["passed"])
    return {"passed": passed >= 4, "message": f"{passed}/5 상품 데이터 일치", "details": details}


# ============================================
# 과제 6: Agentic Loop
# ============================================
AGENT_LOOP_MISSION = {
    "question": "서울의 현재 기온은 섭씨 몇 도이며, 이를 화씨로 변환하면 몇 도인가요? 최종 답을 '섭씨: X°C, 화씨: Y°F' 형식으로 알려주세요.",
    "tools": {
        "get_weather": {
            "description": "도시의 현재 날씨를 조회합니다",
            "endpoint": "LLM의 tool_calls로 처리 (외부 API 아님)",
            "mock_response": "서울: 맑음, 22°C",
        },
        "calculate": {
            "description": "수학 계산을 수행합니다",
            "endpoint": "LLM의 tool_calls로 처리",
            "example": "calculate('22 * 9 / 5 + 32') → 71.6",
        },
    },
    "note": "requests로 LLM API를 직접 호출하여 Agent Loop를 구현하세요. 프레임워크 사용 금지.",
}


def validate_agent_loop(answer: dict) -> dict:
    response = str(answer.get("response", ""))

    has_celsius = any(c in response for c in ["°C", "섭씨", "℃"])
    has_fahrenheit = any(f in response for f in ["°F", "화씨", "℉"])
    has_number = any(char.isdigit() for char in response)

    details = [
        {"check": "섭씨 포함", "passed": has_celsius, "message": "섭씨 값이 있습니다" if has_celsius else "섭씨 값이 없습니다"},
        {"check": "화씨 포함", "passed": has_fahrenheit, "message": "화씨 값이 있습니다" if has_fahrenheit else "화씨 값이 없습니다"},
        {"check": "숫자 포함", "passed": has_number, "message": "숫자가 있습니다" if has_number else "숫자가 없습니다"},
    ]

    passed = all(d["passed"] for d in details)
    return {"passed": passed, "message": "Agent Loop 응답 검증 통과" if passed else "응답 형식을 확인하세요", "details": details}


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
# 과제 정의 레지스트리
# ============================================
CHALLENGES = {
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
    "structured": {
        "name": "Structured Output",
        "description": "뉴스 기사를 분석하여 구조화된 JSON으로 추출하세요.",
        "mission": STRUCTURED_MISSION,
        "submit_schema": '{"title": "...", "category": "...", "sentiment": "...", "keywords": [...], "summary": "..."}',
        "validate": validate_structured,
    },
    "mcp": {
        "name": "MCP Tool 호출",
        "description": "MCP 서버에 연결하여 3가지 도구를 호출하세요.",
        "mission": MCP_MISSION,
        "submit_schema": '{"results": ["결과1", "결과2", "결과3"]}',
        "validate": validate_mcp,
    },
    "browser": {
        "name": "브라우저 자동화",
        "description": "타겟 웹페이지에서 상품 목록을 추출하세요.",
        "mission": BROWSER_MISSION,
        "submit_schema": '{"products": [{"name": "...", "price": 123}, ...]}',
        "validate": validate_browser,
    },
    "agent_loop": {
        "name": "Agentic Loop",
        "description": "requests로 Agent Loop를 구현하여 복합 질문에 답하세요.",
        "mission": AGENT_LOOP_MISSION,
        "submit_schema": '{"response": "섭씨: X°C, 화씨: Y°F"}',
        "validate": validate_agent_loop,
    },
    "final": {
        "name": "종합 실습",
        "description": "검색 → 추출 → Excel 저장 전체 파이프라인을 자동화하세요.",
        "mission": FINAL_MISSION,
        "submit_schema": '{"items": [{"title": "...", "link": "..."}, ...]}',
        "validate": validate_final,
    },
}


def validate_answer(challenge_id: str, answer: dict) -> dict:
    """과제별 검증 함수를 호출합니다."""
    challenge = CHALLENGES.get(challenge_id)
    if not challenge:
        return {"passed": False, "message": f"알 수 없는 과제: {challenge_id}"}
    return challenge["validate"](answer)
