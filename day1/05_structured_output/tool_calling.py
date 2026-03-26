"""
Tool Calling / Function Calling 기초 예제

LLM에게 외부 도구(함수)를 사용할 수 있게 하는 Tool Calling의 전체 워크플로우를
단계별로 설명합니다.

전체 흐름:
1. 도구(함수)를 JSON Schema로 정의
2. 도구 정의와 함께 사용자 질문을 LLM에 전송
3. LLM이 어떤 도구를 어떤 인자로 호출할지 결정 (tool_calls 반환)
4. 우리가 실제로 도구(함수)를 실행
5. 도구 실행 결과를 LLM에 다시 전달
6. LLM이 결과를 바탕으로 최종 답변 생성

주요 내용:
- 도구 스키마 정의 방법
- 단일 도구 호출
- 병렬 도구 호출 (Parallel Tool Calls)
- tool_choice 옵션 ("auto", "required", "none", 특정 함수 지정)

실행 방법:
    python tool_calling.py

의존성:
    pip install openai httpx
"""

import json
import os
import sys
from datetime import datetime

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ══════════════════════════════════════════════
# 1단계: 도구(함수) 실제 구현
# ══════════════════════════════════════════════
# 실제 서비스에서는 DB 조회, API 호출, 계산 등을 수행합니다.
# 여기서는 시뮬레이션용 더미 함수를 사용합니다.

def get_weather(city: str, unit: str = "celsius") -> dict:
    """
    날씨 정보를 조회하는 함수 (시뮬레이션).

    실제 서비스에서는 기상청 API나 OpenWeatherMap 등을 호출합니다.

    Args:
        city: 도시 이름
        unit: 온도 단위 ("celsius" 또는 "fahrenheit")

    Returns:
        날씨 정보 딕셔너리
    """
    # 시뮬레이션 데이터
    weather_data = {
        "서울": {"temp": 12, "condition": "맑음", "humidity": 45},
        "부산": {"temp": 15, "condition": "흐림", "humidity": 62},
        "제주": {"temp": 18, "condition": "비", "humidity": 78},
        "뉴욕": {"temp": 8, "condition": "맑음", "humidity": 35},
    }

    data = weather_data.get(city, {"temp": 20, "condition": "정보 없음", "humidity": 50})
    temp = data["temp"]

    # 화씨 변환
    if unit == "fahrenheit":
        temp = temp * 9 / 5 + 32

    return {
        "city": city,
        "temperature": temp,
        "unit": unit,
        "condition": data["condition"],
        "humidity": data["humidity"],
        "timestamp": datetime.now().isoformat(),
    }


def search_database(query: str, category: str = "all", limit: int = 5) -> dict:
    """
    데이터베이스에서 정보를 검색하는 함수 (시뮬레이션).

    실제 서비스에서는 Elasticsearch, 벡터 DB 등을 사용합니다.

    Args:
        query: 검색 키워드
        category: 검색 카테고리 ("all", "products", "users", "orders")
        limit: 결과 최대 개수

    Returns:
        검색 결과 딕셔너리
    """
    # 시뮬레이션 데이터
    results = [
        {"id": 1, "name": f"{query} 관련 상품 A", "category": "products", "score": 0.95},
        {"id": 2, "name": f"{query} 관련 상품 B", "category": "products", "score": 0.87},
        {"id": 3, "name": f"{query} 관련 주문 #1234", "category": "orders", "score": 0.82},
    ]

    # 카테고리 필터링
    if category != "all":
        results = [r for r in results if r["category"] == category]

    return {
        "query": query,
        "category": category,
        "total_results": len(results[:limit]),
        "results": results[:limit],
    }


def calculate(expression: str) -> dict:
    """
    수학 계산을 수행하는 함수.

    보안 주의: 실제 서비스에서는 eval() 대신 안전한 수학 파서를 사용해야 합니다.

    Args:
        expression: 수학 수식 문자열

    Returns:
        계산 결과 딕셔너리
    """
    try:
        # 보안 주의: 프로덕션에서는 eval() 대신 ast.literal_eval() 또는
        # 전용 수학 라이브러리(sympy 등)를 사용하세요
        allowed_chars = set("0123456789+-*/().% ")
        if not all(c in allowed_chars for c in expression):
            return {"expression": expression, "error": "허용되지 않는 문자가 포함되어 있습니다."}

        result = eval(expression)
        return {
            "expression": expression,
            "result": result,
            "type": type(result).__name__,
        }
    except Exception as e:
        return {
            "expression": expression,
            "error": str(e),
        }


# ══════════════════════════════════════════════
# 2단계: 도구를 JSON Schema로 정의
# ══════════════════════════════════════════════
# LLM에게 어떤 도구가 있는지, 각 파라미터는 무엇인지 알려줍니다.
# 이 스키마가 LLM이 도구를 이해하는 유일한 방법입니다.

# ── 도구 스키마 정의 ──
# OpenAI의 tools 파라미터에 전달할 JSON Schema 형식
TOOLS = [
    {
        # type: "function"은 이 도구가 함수 호출임을 의미합니다
        "type": "function",
        "function": {
            # name: LLM이 이 도구를 호출할 때 사용하는 식별자
            # 영문, 숫자, 밑줄만 사용 가능 (최대 64자)
            "name": "get_weather",

            # description: LLM이 이 도구를 언제 사용해야 하는지 판단하는 핵심 정보
            # 명확하고 구체적으로 작성해야 합니다
            "description": (
                "특정 도시의 현재 날씨 정보를 조회합니다. "
                "기온, 날씨 상태, 습도 등을 반환합니다."
            ),

            # parameters: JSON Schema 형식으로 파라미터 정의
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        # 각 파라미터의 description도 LLM의 인자 결정에 영향
                        "description": "날씨를 조회할 도시 이름 (예: 서울, 부산, 뉴욕)",
                    },
                    "unit": {
                        "type": "string",
                        # enum으로 가능한 값을 제한
                        "enum": ["celsius", "fahrenheit"],
                        "description": "온도 단위. 기본값은 celsius(섭씨)",
                    },
                },
                # required: 필수 파라미터 목록
                # 여기에 없는 파라미터는 LLM이 생략할 수 있음
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": (
                "내부 데이터베이스에서 상품, 주문, 사용자 정보를 검색합니다. "
                "키워드 기반 검색을 지원하며 카테고리 필터링이 가능합니다."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색 키워드",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["all", "products", "users", "orders"],
                        "description": "검색 카테고리. 기본값은 'all' (전체 검색)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "반환할 최대 결과 수. 기본값은 5",
                        "minimum": 1,
                        "maximum": 50,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "수학 계산을 수행합니다. "
                "사칙연산, 괄호, 소수점 등을 지원합니다. "
                "예: '(100 + 200) * 0.1', '15 / 4'"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "계산할 수학 수식 (예: '100 * 1.1 + 50')",
                    },
                },
                "required": ["expression"],
            },
        },
    },
]

# ── 함수 이름 → 실제 함수 매핑 ──
# LLM이 반환한 함수 이름으로 실제 함수를 찾기 위한 딕셔너리
TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "search_database": search_database,
    "calculate": calculate,
}


# ══════════════════════════════════════════════
# 3단계: 도구 호출 실행 헬퍼
# ══════════════════════════════════════════════

def execute_tool_call(tool_call) -> str:
    """
    LLM이 반환한 tool_call 객체를 파싱하여 실제 함수를 실행합니다.

    tool_call 객체의 구조:
    - tool_call.id: 도구 호출 고유 ID (응답 시 매칭에 사용)
    - tool_call.type: "function" (현재는 function만 지원)
    - tool_call.function.name: 호출할 함수 이름
    - tool_call.function.arguments: JSON 문자열로 된 함수 인자

    Args:
        tool_call: LLM 응답의 tool_calls 항목

    Returns:
        함수 실행 결과 (JSON 문자열)
    """
    function_name = tool_call.function.name
    # arguments는 JSON 문자열이므로 파싱이 필요합니다
    function_args = json.loads(tool_call.function.arguments)

    print(f"  [도구 실행] {function_name}({json.dumps(function_args, ensure_ascii=False)})")

    # 등록된 함수에서 찾아 실행
    if function_name in TOOL_FUNCTIONS:
        result = TOOL_FUNCTIONS[function_name](**function_args)
    else:
        result = {"error": f"알 수 없는 함수: {function_name}"}

    result_str = json.dumps(result, ensure_ascii=False)
    print(f"  [도구 결과] {result_str[:200]}...")
    return result_str


# ══════════════════════════════════════════════
# 예제 1: 단일 도구 호출 (전체 흐름)
# ══════════════════════════════════════════════

def single_tool_call_example():
    """
    단일 도구 호출의 전체 흐름을 보여주는 예제.

    흐름도:
    사용자 → [질문] → LLM → [tool_calls] → 우리 코드 → [함수 실행]
                                                    ↓
    사용자 ← [최종 답변] ← LLM ← [tool 결과 전달] ←┘
    """
    print("=" * 60)
    print("예제 1: 단일 도구 호출 (전체 흐름)")
    print("=" * 60)

    client = get_openai_client()
    user_question = "서울 날씨 어때?"

    print(f"\n[사용자 질문] {user_question}")

    # ── Step 1: 사용자 질문 + 도구 정의를 LLM에 전송 ──
    print(f"\n[Step 1] LLM에게 질문과 도구 목록 전달")
    messages = [
        {
            "role": "system",
            "content": "당신은 친절한 도우미입니다. 필요한 경우 제공된 도구를 사용하세요.",
        },
        {"role": "user", "content": user_question},
    ]

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        tools=TOOLS,           # ★ 도구 정의 전달
        tool_choice="auto",    # ★ LLM이 도구 사용 여부를 자동 판단
    )

    assistant_message = response.choices[0].message

    # ── Step 2: LLM 응답 확인 ──
    # LLM이 도구를 호출하기로 결정했는지 확인합니다
    print(f"\n[Step 2] LLM 응답 분석")
    print(f"  finish_reason: {response.choices[0].finish_reason}")
    # finish_reason이 "tool_calls"이면 도구 호출이 필요하다는 의미

    if assistant_message.tool_calls:
        print(f"  도구 호출 수: {len(assistant_message.tool_calls)}")

        # ── Step 3: LLM의 응답(tool_calls 포함)을 대화 이력에 추가 ──
        # 중요: assistant 메시지를 그대로 대화 이력에 추가해야 합니다
        messages.append(assistant_message)

        # ── Step 4: 각 도구 호출 실행 및 결과 전달 ──
        print(f"\n[Step 3-4] 도구 실행 및 결과 전달")
        for tool_call in assistant_message.tool_calls:
            # 도구 실행
            result = execute_tool_call(tool_call)

            # 도구 결과를 대화 이력에 추가
            # role: "tool"과 tool_call_id로 어떤 호출의 결과인지 매칭
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,  # ★ 반드시 tool_call의 id와 매칭
                "content": result,
            })

        # ── Step 5: 도구 결과를 포함하여 LLM에 다시 요청 ──
        print(f"\n[Step 5] 도구 결과를 포함하여 LLM에 최종 답변 요청")
        final_response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=TOOLS,
        )

        final_answer = final_response.choices[0].message.content
        print(f"\n[최종 답변] {final_answer}")

    else:
        # 도구 호출 없이 직접 답변한 경우
        print(f"  LLM이 도구 없이 직접 답변했습니다.")
        print(f"\n[최종 답변] {assistant_message.content}")


# ══════════════════════════════════════════════
# 예제 2: 병렬 도구 호출 (Parallel Tool Calls)
# ══════════════════════════════════════════════

def parallel_tool_calls_example():
    """
    LLM이 여러 도구를 동시에 호출하는 예제.

    LLM이 질문에 답하기 위해 여러 정보가 필요하다고 판단하면,
    한 번의 응답에서 여러 tool_calls를 반환합니다.
    이를 병렬로 실행하여 효율성을 높일 수 있습니다.
    """
    print("\n" + "=" * 60)
    print("예제 2: 병렬 도구 호출 (Parallel Tool Calls)")
    print("=" * 60)

    client = get_openai_client()

    # 여러 도구가 필요한 질문
    user_question = (
        "서울과 부산의 날씨를 비교해주고, "
        "여행 관련 상품도 검색해줘. "
        "그리고 서울-부산 KTX 왕복 요금 59,800원의 부가세(10%)도 계산해줘."
    )
    print(f"\n[사용자 질문] {user_question}")

    messages = [
        {
            "role": "system",
            "content": "당신은 여행 계획 도우미입니다. 필요한 정보를 도구를 사용하여 수집하세요.",
        },
        {"role": "user", "content": user_question},
    ]

    # 첫 번째 LLM 호출
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    if assistant_message.tool_calls:
        print(f"\n[LLM 응답] {len(assistant_message.tool_calls)}개의 도구 호출 요청")

        # assistant 메시지를 대화 이력에 추가
        messages.append(assistant_message)

        # 모든 도구 호출 실행 (실제 서비스에서는 asyncio로 병렬 실행 가능)
        for i, tool_call in enumerate(assistant_message.tool_calls, 1):
            print(f"\n  --- 도구 호출 {i}/{len(assistant_message.tool_calls)} ---")
            result = execute_tool_call(tool_call)

            # 각 도구의 결과를 개별적으로 대화 이력에 추가
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        # 모든 도구 결과를 포함하여 최종 답변 요청
        print(f"\n[최종 답변 요청]")
        final_response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=TOOLS,
        )

        print(f"\n[최종 답변]\n{final_response.choices[0].message.content}")
    else:
        print(f"\n[직접 답변] {assistant_message.content}")


# ══════════════════════════════════════════════
# 예제 3: tool_choice 옵션 비교
# ══════════════════════════════════════════════

def tool_choice_options_example():
    """
    tool_choice 파라미터의 다양한 옵션을 비교합니다.

    옵션:
    1. "auto"     - LLM이 도구 사용 여부를 자동 판단 (기본값)
    2. "required" - LLM이 반드시 하나 이상의 도구를 호출해야 함
    3. "none"     - 도구를 호출하지 않고 텍스트로만 응답
    4. 특정 함수  - 지정한 특정 함수를 반드시 호출
    """
    print("\n" + "=" * 60)
    print("예제 3: tool_choice 옵션 비교")
    print("=" * 60)

    client = get_openai_client()

    # 도구가 필요한 질문과 필요 없는 질문을 각각 테스트
    questions = [
        "서울 날씨 알려줘",  # 도구가 필요한 질문
        "안녕하세요!",       # 도구가 필요 없는 질문
    ]

    for question in questions:
        print(f"\n{'─' * 50}")
        print(f"질문: \"{question}\"")
        print(f"{'─' * 50}")

        base_messages = [
            {"role": "system", "content": "당신은 친절한 도우미입니다."},
            {"role": "user", "content": question},
        ]

        # ── 옵션 1: tool_choice="auto" ──
        print(f"\n  [tool_choice='auto'] LLM이 자동 판단")
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=base_messages,
            tools=TOOLS,
            tool_choice="auto",  # 기본값
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            tool_names = [tc.function.name for tc in msg.tool_calls]
            print(f"    → 도구 호출: {tool_names}")
        else:
            content_preview = (msg.content or "")[:80]
            print(f"    → 텍스트 응답: {content_preview}...")

        # ── 옵션 2: tool_choice="required" ──
        print(f"\n  [tool_choice='required'] 도구 호출 강제")
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=base_messages,
            tools=TOOLS,
            tool_choice="required",  # 반드시 도구 호출
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            tool_names = [tc.function.name for tc in msg.tool_calls]
            print(f"    → 도구 호출: {tool_names}")
        else:
            print(f"    → (도구 호출 없음 - 예상치 못한 결과)")

        # ── 옵션 3: tool_choice="none" ──
        print(f"\n  [tool_choice='none'] 도구 호출 금지")
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=base_messages,
            tools=TOOLS,
            tool_choice="none",  # 도구 호출 금지
        )
        msg = resp.choices[0].message
        content_preview = (msg.content or "")[:80]
        print(f"    → 텍스트 응답: {content_preview}...")

        # ── 옵션 4: 특정 함수 지정 ──
        print(f"\n  [tool_choice=특정 함수] get_weather 강제 호출")
        resp = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=base_messages,
            tools=TOOLS,
            # 특정 함수를 반드시 호출하도록 지정
            tool_choice={
                "type": "function",
                "function": {"name": "get_weather"},
            },
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"    → {tc.function.name}({tc.function.arguments})")


# ══════════════════════════════════════════════
# 메인 실행
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("📌 Tool Calling / Function Calling 기초 예제")
    print("LLM에게 외부 도구를 사용하게 하는 방법을 알아봅니다.\n")

    # 예제 1: 단일 도구 호출 전체 흐름
    single_tool_call_example()

    # 예제 2: 병렬 도구 호출
    parallel_tool_calls_example()

    # 예제 3: tool_choice 옵션 비교
    tool_choice_options_example()

    print("\n" + "=" * 60)
    print("다음 단계: tool_calling_advanced.py에서 체인 호출,")
    print("에러 처리, 스트리밍 등 고급 패턴을 알아보세요.")
    print("=" * 60)
