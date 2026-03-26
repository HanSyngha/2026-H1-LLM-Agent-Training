"""
Tool Calling 고급 패턴

기초를 넘어 실무에서 필요한 고급 Tool Calling 패턴을 다룹니다.

주요 내용:
1. 체인 호출 (한 도구의 결과를 다른 도구에 전달)
2. 에러 핸들링 (도구 실행 실패 시 처리)
3. 도구 결과 포맷팅 모범 사례
4. 스트리밍과 Tool Calling 조합
5. tool_choice="required" vs "auto" 동작 차이

실행 방법:
    python tool_calling_advanced.py

의존성:
    pip install openai httpx
"""

import json
import os
import sys
import traceback
from datetime import datetime

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ══════════════════════════════════════════════
# 도구(함수) 정의
# ══════════════════════════════════════════════

def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """환율 조회 (시뮬레이션)"""
    rates = {
        ("USD", "KRW"): 1350.50,
        ("EUR", "KRW"): 1480.20,
        ("JPY", "KRW"): 9.15,
        ("KRW", "USD"): 0.00074,
    }
    rate = rates.get((from_currency, to_currency))
    if rate is None:
        return {"error": f"{from_currency} → {to_currency} 환율 정보를 찾을 수 없습니다."}
    return {
        "from": from_currency,
        "to": to_currency,
        "rate": rate,
        "timestamp": datetime.now().isoformat(),
    }


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """
    통화 변환 (환율 조회 결과에 의존).

    체인 호출 시나리오: get_exchange_rate → convert_currency
    """
    rate_info = get_exchange_rate(from_currency, to_currency)
    if "error" in rate_info:
        return rate_info

    converted = amount * rate_info["rate"]
    return {
        "original_amount": amount,
        "from_currency": from_currency,
        "converted_amount": round(converted, 2),
        "to_currency": to_currency,
        "rate_used": rate_info["rate"],
    }


def get_product_price(product_id: str) -> dict:
    """상품 가격 조회 (시뮬레이션)"""
    products = {
        "PROD-001": {"name": "무선 이어폰", "price": 89000, "currency": "KRW"},
        "PROD-002": {"name": "스마트 워치", "price": 299000, "currency": "KRW"},
        "PROD-003": {"name": "노트북 거치대", "price": 45000, "currency": "KRW"},
    }
    product = products.get(product_id)
    if product is None:
        # 의도적으로 에러를 발생시키는 케이스
        return {"error": f"상품 ID '{product_id}'를 찾을 수 없습니다."}
    return {"product_id": product_id, **product}


def create_order(product_id: str, quantity: int, customer_name: str) -> dict:
    """주문 생성 (시뮬레이션)"""
    if quantity <= 0:
        return {"error": "수량은 1 이상이어야 합니다."}
    if quantity > 10:
        return {"error": "최대 주문 수량은 10개입니다."}

    return {
        "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "product_id": product_id,
        "quantity": quantity,
        "customer_name": customer_name,
        "status": "created",
        "created_at": datetime.now().isoformat(),
    }


def unstable_api_call(endpoint: str) -> dict:
    """
    불안정한 외부 API 호출 시뮬레이션.
    에러 핸들링 데모용으로 의도적으로 예외를 발생시킵니다.
    """
    # 특정 엔드포인트에서 의도적으로 에러 발생
    if "timeout" in endpoint.lower():
        raise TimeoutError(f"API 호출 시간 초과: {endpoint}")
    if "error" in endpoint.lower():
        raise ConnectionError(f"API 연결 실패: {endpoint}")

    return {"endpoint": endpoint, "status": "success", "data": "정상 응답"}


# ── 도구 스키마 정의 ──
ADVANCED_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "두 통화 간의 현재 환율을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "원래 통화 코드 (예: USD, EUR, KRW)",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "변환할 통화 코드 (예: USD, EUR, KRW)",
                    },
                },
                "required": ["from_currency", "to_currency"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "convert_currency",
            "description": "특정 금액을 다른 통화로 변환합니다. 내부적으로 환율을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "변환할 금액",
                    },
                    "from_currency": {
                        "type": "string",
                        "description": "원래 통화 코드",
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "변환할 통화 코드",
                    },
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_price",
            "description": "상품 ID로 상품의 가격 정보를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "상품 ID (예: PROD-001)",
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "상품을 주문합니다. 상품 ID, 수량, 주문자 이름이 필요합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "주문할 상품 ID",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "주문 수량 (1~10)",
                    },
                    "customer_name": {
                        "type": "string",
                        "description": "주문자 이름",
                    },
                },
                "required": ["product_id", "quantity", "customer_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unstable_api_call",
            "description": "외부 API를 호출합니다. (에러 핸들링 데모용)",
            "parameters": {
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "호출할 API 엔드포인트 URL",
                    },
                },
                "required": ["endpoint"],
            },
        },
    },
]

# 함수 매핑
TOOL_FUNCTIONS = {
    "get_exchange_rate": get_exchange_rate,
    "convert_currency": convert_currency,
    "get_product_price": get_product_price,
    "create_order": create_order,
    "unstable_api_call": unstable_api_call,
}


# ══════════════════════════════════════════════
# 도구 실행 헬퍼 (에러 핸들링 포함)
# ══════════════════════════════════════════════

def execute_tool_call_safe(tool_call) -> str:
    """
    도구를 안전하게 실행하는 헬퍼 함수.

    실무에서 반드시 필요한 에러 핸들링 패턴:
    1. 알 수 없는 함수 이름 처리
    2. JSON 파싱 오류 처리
    3. 함수 실행 중 예외 처리
    4. 에러 발생 시에도 LLM에게 구조화된 에러 정보 전달
    """
    function_name = tool_call.function.name

    # ── 1. 함수 존재 여부 확인 ──
    if function_name not in TOOL_FUNCTIONS:
        error_result = {
            "error": True,
            "error_type": "unknown_function",
            "message": f"등록되지 않은 함수: {function_name}",
        }
        return json.dumps(error_result, ensure_ascii=False)

    # ── 2. 인자 파싱 ──
    try:
        function_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        error_result = {
            "error": True,
            "error_type": "invalid_arguments",
            "message": f"함수 인자 JSON 파싱 실패: {str(e)}",
            "raw_arguments": tool_call.function.arguments,
        }
        return json.dumps(error_result, ensure_ascii=False)

    # ── 3. 함수 실행 (예외 처리) ──
    try:
        print(f"  [실행] {function_name}({json.dumps(function_args, ensure_ascii=False)})")
        result = TOOL_FUNCTIONS[function_name](**function_args)
        result_str = json.dumps(result, ensure_ascii=False)
        print(f"  [결과] {result_str[:150]}")
        return result_str

    except TypeError as e:
        # 인자 타입/개수 불일치
        error_result = {
            "error": True,
            "error_type": "argument_error",
            "message": f"함수 인자 오류: {str(e)}",
            "function": function_name,
            "arguments": function_args,
        }
        print(f"  [에러] 인자 오류: {e}")
        return json.dumps(error_result, ensure_ascii=False)

    except (TimeoutError, ConnectionError) as e:
        # 네트워크/타임아웃 에러
        error_result = {
            "error": True,
            "error_type": "network_error",
            "message": str(e),
            "function": function_name,
            "suggestion": "잠시 후 다시 시도하거나 다른 방법을 사용해주세요.",
        }
        print(f"  [에러] 네트워크 오류: {e}")
        return json.dumps(error_result, ensure_ascii=False)

    except Exception as e:
        # 예상치 못한 모든 에러
        error_result = {
            "error": True,
            "error_type": "unexpected_error",
            "message": str(e),
            "function": function_name,
            "traceback": traceback.format_exc(),
        }
        print(f"  [에러] 예상치 못한 오류: {e}")
        return json.dumps(error_result, ensure_ascii=False)


# ══════════════════════════════════════════════
# 대화 루프 헬퍼 (멀티턴 도구 호출 지원)
# ══════════════════════════════════════════════

def run_conversation(client, messages: list, tools: list, max_turns: int = 5) -> str:
    """
    LLM과의 대화 루프를 실행합니다.
    도구 호출이 더 이상 없을 때까지 반복합니다.

    체인 호출 지원:
    - LLM이 도구 A 호출 → 결과 전달 → LLM이 도구 B 호출 → ...
    - max_turns로 무한 루프 방지

    Args:
        client: OpenAI 클라이언트
        messages: 대화 이력
        tools: 도구 정의 목록
        max_turns: 최대 도구 호출 턴 수

    Returns:
        최종 텍스트 응답
    """
    for turn in range(max_turns):
        print(f"\n  --- 턴 {turn + 1}/{max_turns} ---")

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # 도구 호출이 없으면 최종 답변
        if not assistant_message.tool_calls:
            print(f"  → 최종 답변 생성 완료")
            return assistant_message.content

        # 도구 호출 처리
        print(f"  → {len(assistant_message.tool_calls)}개 도구 호출")
        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            result = execute_tool_call_safe(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    # max_turns 초과 시 마지막 LLM 호출
    print(f"\n  → 최대 턴 수 도달, 최종 답변 요청")
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


# ══════════════════════════════════════════════
# 예제 1: 체인 도구 호출
# ══════════════════════════════════════════════

def chained_tool_calls_example():
    """
    한 도구의 결과가 다음 도구 호출에 영향을 주는 체인 호출 예제.

    시나리오: 상품 가격 조회 → 달러로 변환 → 주문 생성
    LLM이 각 단계의 결과를 보고 다음에 어떤 도구를 호출할지 판단합니다.
    """
    print("=" * 60)
    print("예제 1: 체인 도구 호출 (결과 전달 패턴)")
    print("=" * 60)

    client = get_openai_client()

    user_question = (
        "PROD-001 상품의 가격을 달러로 환산하면 얼마인지 알려주고, "
        "홍길동 이름으로 2개 주문해줘."
    )
    print(f"\n[사용자 질문] {user_question}")
    print(f"[예상 체인] get_product_price → get_exchange_rate → create_order")

    messages = [
        {
            "role": "system",
            "content": (
                "당신은 쇼핑 도우미입니다. "
                "필요한 정보를 단계별로 도구를 사용하여 수집하세요. "
                "한 도구의 결과를 바탕으로 다음 도구를 호출할 수 있습니다."
            ),
        },
        {"role": "user", "content": user_question},
    ]

    # run_conversation이 체인 호출을 자동으로 처리
    final_answer = run_conversation(client, messages, ADVANCED_TOOLS)
    print(f"\n[최종 답변]\n{final_answer}")


# ══════════════════════════════════════════════
# 예제 2: 에러 핸들링
# ══════════════════════════════════════════════

def error_handling_example():
    """
    도구 실행 중 에러가 발생했을 때 LLM이 어떻게 대처하는지 보여줍니다.

    핵심 패턴:
    - 에러 정보를 구조화된 JSON으로 LLM에 전달
    - LLM이 에러를 이해하고 사용자에게 적절히 안내
    - 필요시 대안을 제시하거나 다른 도구를 시도
    """
    print("\n" + "=" * 60)
    print("예제 2: 에러 핸들링")
    print("=" * 60)

    client = get_openai_client()

    # ── 케이스 1: 존재하지 않는 상품 조회 ──
    print("\n[케이스 1] 존재하지 않는 상품 조회")
    messages = [
        {"role": "system", "content": "당신은 쇼핑 도우미입니다. 에러 발생 시 사용자에게 친절하게 안내하세요."},
        {"role": "user", "content": "PROD-999 상품 가격 알려줘"},
    ]
    answer = run_conversation(client, messages, ADVANCED_TOOLS)
    print(f"\n[답변] {answer}")

    # ── 케이스 2: 불안정한 API 호출 ──
    print(f"\n{'─' * 50}")
    print("[케이스 2] 외부 API 타임아웃 발생")
    messages = [
        {
            "role": "system",
            "content": (
                "당신은 시스템 관리자입니다. "
                "API 호출 에러가 발생하면 원인을 분석하고 대안을 제시하세요."
            ),
        },
        {"role": "user", "content": "timeout-api.example.com 엔드포인트를 호출해줘"},
    ]
    answer = run_conversation(client, messages, ADVANCED_TOOLS)
    print(f"\n[답변] {answer}")


# ══════════════════════════════════════════════
# 예제 3: 도구 결과 포맷팅 모범 사례
# ══════════════════════════════════════════════

def result_formatting_best_practices():
    """
    도구 결과를 LLM에 전달할 때의 포맷팅 모범 사례를 보여줍니다.

    모범 사례:
    1. JSON 형식으로 구조화하여 전달
    2. 에러와 성공을 명확히 구분
    3. 불필요하게 큰 데이터는 요약하여 전달
    4. 메타데이터(타임스탬프, 소스 등)를 포함
    """
    print("\n" + "=" * 60)
    print("예제 3: 도구 결과 포맷팅 모범 사례")
    print("=" * 60)

    # ── 나쁜 예: 비정형 텍스트로 전달 ──
    bad_result = "서울 날씨는 12도이고 맑습니다. 습도는 45%입니다."

    # ── 좋은 예: 구조화된 JSON으로 전달 ──
    good_result = json.dumps({
        "status": "success",
        "data": {
            "city": "서울",
            "temperature": 12,
            "unit": "celsius",
            "condition": "맑음",
            "humidity": 45,
        },
        "metadata": {
            "source": "weather_api",
            "timestamp": "2024-03-15T10:30:00",
            "cache_hit": False,
        },
    }, ensure_ascii=False, indent=2)

    # ── 에러 시 좋은 예 ──
    error_result = json.dumps({
        "status": "error",
        "error": {
            "type": "not_found",
            "message": "해당 도시의 날씨 정보를 찾을 수 없습니다.",
            "code": 404,
        },
        "suggestion": "도시 이름을 확인하고 다시 시도해주세요.",
    }, ensure_ascii=False, indent=2)

    # ── 대용량 데이터 시 좋은 예: 요약 포함 ──
    large_data_result = json.dumps({
        "status": "success",
        "summary": "총 1,523개의 검색 결과 중 상위 3개를 반환합니다.",
        "total_count": 1523,
        "returned_count": 3,
        "results": [
            {"id": 1, "name": "상품 A", "relevance": 0.98},
            {"id": 2, "name": "상품 B", "relevance": 0.95},
            {"id": 3, "name": "상품 C", "relevance": 0.91},
        ],
        "has_more": True,
        "next_page_token": "abc123",
    }, ensure_ascii=False, indent=2)

    print("\n[나쁜 예] 비정형 텍스트")
    print(f"  {bad_result}")
    print(f"  → LLM이 구조를 파악하기 어려움")

    print(f"\n[좋은 예] 구조화된 JSON")
    print(f"  {good_result}")
    print(f"  → 명확한 구조, 메타데이터 포함")

    print(f"\n[에러 시 좋은 예]")
    print(f"  {error_result}")
    print(f"  → 에러 타입, 메시지, 해결 제안 포함")

    print(f"\n[대용량 데이터 시 좋은 예]")
    print(f"  {large_data_result}")
    print(f"  → 요약 정보 + 페이지네이션 지원")


# ══════════════════════════════════════════════
# 예제 4: 스트리밍 + Tool Calling
# ══════════════════════════════════════════════

def streaming_with_tool_calls_example():
    """
    스트리밍 모드에서 Tool Calling을 처리하는 예제.

    스트리밍 시 도구 호출 처리가 복잡해지는 이유:
    - tool_calls가 청크(chunk)로 나뉘어 도착
    - 각 청크에서 function.name과 function.arguments를 조립해야 함
    - 도구 호출 완료 후 결과를 다시 전송해야 함
    """
    print("\n" + "=" * 60)
    print("예제 4: 스트리밍 + Tool Calling")
    print("=" * 60)

    client = get_openai_client()

    messages = [
        {"role": "system", "content": "당신은 도우미입니다. 도구를 사용하여 정보를 제공하세요."},
        {"role": "user", "content": "PROD-002 상품 가격을 달러로 환산해줘."},
    ]

    print(f"\n[스트리밍 시작]")

    # 스트리밍 요청
    stream = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        tools=ADVANCED_TOOLS,
        tool_choice="auto",
        stream=True,  # ★ 스트리밍 활성화
    )

    # ── 스트리밍 청크에서 도구 호출 정보 조립 ──
    # 스트리밍에서는 tool_calls가 조각(delta)으로 도착합니다
    collected_tool_calls = {}  # index → {id, name, arguments}
    collected_content = ""
    finish_reason = None

    for chunk in stream:
        delta = chunk.choices[0].delta
        finish_reason = chunk.choices[0].finish_reason

        # 텍스트 콘텐츠 수집 (도구 호출이 아닌 일반 응답)
        if delta.content:
            collected_content += delta.content
            print(delta.content, end="", flush=True)

        # tool_calls 청크 수집
        if delta.tool_calls:
            for tc_chunk in delta.tool_calls:
                idx = tc_chunk.index

                # 새로운 도구 호출 시작
                if idx not in collected_tool_calls:
                    collected_tool_calls[idx] = {
                        "id": tc_chunk.id or "",
                        "name": "",
                        "arguments": "",
                    }

                # ID 업데이트 (첫 청크에만 포함)
                if tc_chunk.id:
                    collected_tool_calls[idx]["id"] = tc_chunk.id

                # 함수 이름 조립
                if tc_chunk.function and tc_chunk.function.name:
                    collected_tool_calls[idx]["name"] += tc_chunk.function.name

                # 인자 문자열 조립 (여러 청크에 걸쳐 도착)
                if tc_chunk.function and tc_chunk.function.arguments:
                    collected_tool_calls[idx]["arguments"] += tc_chunk.function.arguments

    print()  # 줄바꿈

    # ── 도구 호출 처리 ──
    if collected_tool_calls:
        print(f"\n[스트리밍 완료] {len(collected_tool_calls)}개 도구 호출 감지")

        # 조립된 도구 호출 정보로 assistant 메시지 구성
        tool_calls_for_message = []
        for idx in sorted(collected_tool_calls.keys()):
            tc = collected_tool_calls[idx]
            print(f"  도구: {tc['name']}({tc['arguments']})")
            tool_calls_for_message.append({
                "id": tc["id"],
                "type": "function",
                "function": {
                    "name": tc["name"],
                    "arguments": tc["arguments"],
                },
            })

        # assistant 메시지를 대화 이력에 추가
        messages.append({
            "role": "assistant",
            "content": collected_content or None,
            "tool_calls": tool_calls_for_message,
        })

        # 각 도구 실행 및 결과 추가
        for tc_info in tool_calls_for_message:
            # 간단한 호출 객체 시뮬레이션
            class ToolCallProxy:
                """스트리밍에서 조립한 도구 호출 정보를 함수에 전달하기 위한 프록시"""
                def __init__(self, tc_dict):
                    self.id = tc_dict["id"]
                    self.function = type("Function", (), {
                        "name": tc_dict["function"]["name"],
                        "arguments": tc_dict["function"]["arguments"],
                    })()

            result = execute_tool_call_safe(ToolCallProxy(tc_info))
            messages.append({
                "role": "tool",
                "tool_call_id": tc_info["id"],
                "content": result,
            })

        # 최종 답변 (스트리밍)
        print(f"\n[최종 답변 (스트리밍)]")
        final_stream = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=ADVANCED_TOOLS,
            stream=True,
        )

        for chunk in final_stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()

    else:
        print(f"\n[직접 답변] {collected_content}")


# ══════════════════════════════════════════════
# 예제 5: tool_choice 동작 차이 비교
# ══════════════════════════════════════════════

def tool_choice_comparison():
    """
    tool_choice="required"와 "auto"의 동작 차이를 실험적으로 비교합니다.

    핵심 차이:
    - "auto": LLM이 도구가 필요한지 스스로 판단
      → 도구 없이 답할 수 있으면 도구 호출 안 함
    - "required": LLM이 반드시 하나 이상의 도구를 호출
      → 도구가 필요 없는 질문에도 강제로 도구 호출

    사용 시나리오:
    - "auto": 일반적인 챗봇 (도구는 필요할 때만)
    - "required": 데이터 수집 파이프라인 (항상 도구 사용)
    - "none": 도구 없이 LLM의 지식만으로 답변 (디버깅용)
    - 특정 함수: 특정 작업을 반드시 수행해야 할 때
    """
    print("\n" + "=" * 60)
    print("예제 5: tool_choice 동작 차이 비교")
    print("=" * 60)

    client = get_openai_client()

    # 테스트 시나리오
    test_cases = [
        {
            "question": "PROD-001 가격 알려줘",
            "description": "도구가 필요한 질문",
        },
        {
            "question": "오늘 기분이 좋아!",
            "description": "도구가 필요 없는 질문",
        },
    ]

    choices_to_test = ["auto", "required", "none"]

    for case in test_cases:
        print(f"\n{'━' * 50}")
        print(f"테스트: {case['description']}")
        print(f"질문: \"{case['question']}\"")
        print(f"{'━' * 50}")

        for choice in choices_to_test:
            messages = [
                {"role": "system", "content": "당신은 쇼핑 도우미입니다."},
                {"role": "user", "content": case["question"]},
            ]

            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                tools=ADVANCED_TOOLS,
                tool_choice=choice,
            )

            msg = response.choices[0].message
            finish = response.choices[0].finish_reason

            print(f"\n  [tool_choice='{choice}']")
            print(f"    finish_reason: {finish}")

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    args_preview = tc.function.arguments[:60]
                    print(f"    도구 호출: {tc.function.name}({args_preview})")
            else:
                content_preview = (msg.content or "")[:80]
                print(f"    텍스트 응답: {content_preview}")

    # ── 비교 정리 ──
    print(f"\n{'━' * 50}")
    print("[정리]")
    print("  'auto'     : 도구 필요 시에만 호출 → 일반 챗봇에 적합")
    print("  'required' : 항상 도구 호출 → 데이터 파이프라인, 작업 자동화에 적합")
    print("  'none'     : 도구 호출 금지 → 디버깅, 도구 없는 답변 비교에 유용")
    print("  특정 함수  : 해당 함수만 호출 → 특정 작업 강제 실행에 유용")


# ══════════════════════════════════════════════
# 메인 실행
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("📌 Tool Calling 고급 패턴")
    print("실무에서 필요한 체인 호출, 에러 처리, 스트리밍 패턴을 다룹니다.\n")

    # 예제 1: 체인 도구 호출
    chained_tool_calls_example()

    # 예제 2: 에러 핸들링
    error_handling_example()

    # 예제 3: 결과 포맷팅 모범 사례
    result_formatting_best_practices()

    # 예제 4: 스트리밍 + Tool Calling
    streaming_with_tool_calls_example()

    # 예제 5: tool_choice 비교
    tool_choice_comparison()

    print("\n" + "=" * 60)
    print("모든 예제 완료!")
    print("exercise.md에서 실습 과제를 확인하세요.")
    print("=" * 60)
