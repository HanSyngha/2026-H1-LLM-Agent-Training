"""
MCP 실습 정답: 나만의 MCP 서버 + 클라이언트 + LLM 연동

FastMCP를 사용하여 커스텀 도구 3개, 리소스 1개, 프롬프트 1개를 구현하고,
LLM과 연동하여 자연어로 도구를 호출하는 완전한 예제입니다.

실행 방법:
    python exercise_solution.py

의존성:
    pip install mcp openai httpx
"""

import asyncio
import json
import os
import sys

# 공통 설정 로드
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

from mcp.server.fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# 1. MCP 서버 정의
# ============================================================
# FastMCP 인스턴스를 생성합니다.
mcp = FastMCP("my-custom-server")


# --- 도구 1: 환율 변환 ---
@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """통화를 변환합니다. 원화(KRW), 달러(USD), 엔화(JPY), 유로(EUR)를 지원합니다.

    Args:
        amount: 변환할 금액
        from_currency: 원래 통화 코드 (예: KRW, USD, JPY, EUR)
        to_currency: 변환할 통화 코드 (예: KRW, USD, JPY, EUR)
    """
    # 더미 환율 데이터 (1 USD 기준)
    rates = {"USD": 1.0, "KRW": 1350.0, "JPY": 155.0, "EUR": 0.92}
    from_c = from_currency.upper()
    to_c = to_currency.upper()

    if from_c not in rates or to_c not in rates:
        return {"error": f"지원하지 않는 통화입니다. 지원 통화: {list(rates.keys())}"}

    # 원래 통화 -> USD -> 목표 통화
    usd_amount = amount / rates[from_c]
    converted = usd_amount * rates[to_c]

    return {
        "original": f"{amount:,.2f} {from_c}",
        "converted": f"{converted:,.2f} {to_c}",
        "rate": f"1 {from_c} = {rates[to_c] / rates[from_c]:.4f} {to_c}",
    }


# --- 도구 2: 문서 검색 ---
@mcp.tool()
def search_document(query: str) -> dict:
    """사내 문서에서 키워드로 검색합니다.

    회사 규정, 기술 문서, FAQ 등을 검색할 수 있습니다.

    Args:
        query: 검색할 키워드 또는 질문
    """
    # 더미 문서 데이터베이스
    documents = [
        {"id": 1, "title": "연차 사용 규정", "content": "연차 휴가는 입사 첫해 15일이며, 매년 1일씩 가산됩니다. 최대 25일까지 부여됩니다."},
        {"id": 2, "title": "재택근무 가이드", "content": "주 2일까지 재택근무가 가능하며, 코어타임(10시~16시)에는 반드시 연락이 가능해야 합니다."},
        {"id": 3, "title": "코드 리뷰 규칙", "content": "모든 PR은 최소 1명의 리뷰어 승인이 필요합니다. 리뷰는 24시간 이내에 완료해야 합니다."},
        {"id": 4, "title": "배포 프로세스", "content": "배포는 develop → staging → production 순서로 진행됩니다. production 배포는 팀장 승인이 필요합니다."},
        {"id": 5, "title": "보안 정책", "content": "사내 코드는 외부 공개가 금지됩니다. 외부 라이브러리 사용 시 보안팀 검토가 필요합니다."},
    ]

    # 간단한 키워드 매칭 검색
    results = []
    for doc in documents:
        if query.lower() in doc["title"].lower() or query.lower() in doc["content"].lower():
            results.append(doc)

    if not results:
        return {"message": f"'{query}'에 대한 검색 결과가 없습니다.", "count": 0}

    return {"results": results, "count": len(results)}


# --- 도구 3: 알림 전송 ---
@mcp.tool()
def send_notification(recipient: str, message: str, priority: str = "normal") -> dict:
    """팀원에게 알림 메시지를 전송합니다.

    Args:
        recipient: 수신자 이름 또는 이메일
        message: 전송할 메시지 내용
        priority: 우선순위 (low, normal, high, urgent)
    """
    # 더미 전송 (실제로는 메시지 큐나 이메일 API 사용)
    valid_priorities = ["low", "normal", "high", "urgent"]
    if priority not in valid_priorities:
        return {"error": f"잘못된 우선순위입니다. 허용값: {valid_priorities}"}

    return {
        "status": "sent",
        "recipient": recipient,
        "message": message,
        "priority": priority,
        "timestamp": "2026-03-31T10:00:00",
        "notification_id": "NOTIF-20260331-001",
    }


# --- 리소스: 시스템 설정 ---
@mcp.resource("config://system")
def get_system_config() -> str:
    """현재 시스템 설정 정보를 반환합니다.

    서버의 설정값, 지원 기능, 제한 사항 등을 포함합니다.
    """
    config = {
        "server_name": "My Custom MCP Server",
        "version": "1.0.0",
        "supported_currencies": ["KRW", "USD", "JPY", "EUR"],
        "max_search_results": 10,
        "notification_channels": ["email", "slack", "teams"],
        "features": {
            "currency_conversion": True,
            "document_search": True,
            "notifications": True,
        },
    }
    return json.dumps(config, ensure_ascii=False, indent=2)


# --- 프롬프트: 업무 보고서 작성 ---
@mcp.prompt()
def report_prompt(topic: str, key_points: str) -> str:
    """업무 보고서 작성을 위한 프롬프트 템플릿입니다.

    주제와 핵심 내용을 입력하면 보고서 형식의 프롬프트를 생성합니다.

    Args:
        topic: 보고서 주제
        key_points: 핵심 내용 (쉼표로 구분)
    """
    return f"""다음 주제로 업무 보고서를 작성해주세요.

주제: {topic}
핵심 내용: {key_points}

보고서는 다음 형식으로 작성해주세요:
1. 개요 (1-2문장 요약)
2. 상세 내용 (핵심 내용별로 정리)
3. 향후 계획
4. 결론

한국어로 작성하시고, 간결하면서도 명확한 문체를 사용해주세요.
"""


# ============================================================
# 2. MCP + LLM 연동 실행
# ============================================================

def mcp_tools_to_openai_format(mcp_tools) -> list[dict]:
    """MCP 도구 스키마를 OpenAI function calling 형식으로 변환합니다."""
    openai_tools = []
    for tool in mcp_tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}},
            },
        }
        openai_tools.append(openai_tool)
    return openai_tools


async def run_mcp_with_llm():
    """MCP 서버를 실행하고, LLM과 연동하여 자연어로 도구를 호출합니다."""

    # OpenAI 클라이언트 생성
    client = get_openai_client()

    # MCP 서버에 연결 (현재 파일 자체가 서버 역할)
    server_script = os.path.abspath(__file__)
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script, "--server"],  # 서버 모드로 실행
    )

    print("[1단계] MCP 서버에 연결 중...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("  -> MCP 서버 연결 완료!")

            # 도구 목록을 가져와서 OpenAI 형식으로 변환합니다
            print("\n[2단계] MCP 도구를 OpenAI 형식으로 변환 중...")
            tools_result = await session.list_tools()
            openai_tools = mcp_tools_to_openai_format(tools_result.tools)
            print(f"  -> {len(openai_tools)}개 도구 변환 완료:")
            for t in openai_tools:
                print(f"     - {t['function']['name']}: {t['function']['description'][:60]}")

            # 리소스 조회합니다
            print("\n[3단계] MCP 리소스 조회 중...")
            resources = await session.list_resources()
            for r in resources.resources:
                print(f"  -> 리소스: {r.uri}")
                content = await session.read_resource(r.uri)
                print(f"     내용 미리보기: {str(content)[:100]}...")

            # 테스트 질문들입니다
            test_queries = [
                "100달러를 한국 원화로 환율 변환해줘",
                "재택근무 규정을 찾아줘",
                "김팀장에게 '내일 오전 회의 참석 부탁드립니다'라고 긴급 알림 보내줘",
            ]

            for query in test_queries:
                print(f"\n{'=' * 60}")
                print(f"  질문: {query}")
                print(f"{'=' * 60}")

                messages = [
                    {
                        "role": "system",
                        "content": (
                            "당신은 유능한 AI 어시스턴트입니다. "
                            "사용자의 요청을 처리하기 위해 제공된 도구를 적극 활용하세요. "
                            "한국어로 응답하세요."
                        ),
                    },
                    {"role": "user", "content": query},
                ]

                # LLM 호출 (도구 정보 포함)
                response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                )

                assistant_message = response.choices[0].message

                # 도구 호출이 있는 경우 MCP 서버에서 실행합니다
                if assistant_message.tool_calls:
                    print(f"  -> LLM이 {len(assistant_message.tool_calls)}개 도구 호출을 요청했습니다.")
                    messages.append(assistant_message)

                    for tool_call in assistant_message.tool_calls:
                        func_name = tool_call.function.name
                        func_args = json.loads(tool_call.function.arguments)
                        print(f"  도구 호출: {func_name}({func_args})")

                        # MCP 서버에서 도구를 실행합니다
                        result = await session.call_tool(func_name, arguments=func_args)
                        tool_result_text = ""
                        for content in result.content:
                            tool_result_text += content.text
                        print(f"  실행 결과: {tool_result_text[:200]}")

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result_text,
                        })

                    # 도구 결과를 포함하여 최종 답변을 생성합니다
                    final_response = client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=messages,
                    )
                    final_answer = final_response.choices[0].message.content
                else:
                    final_answer = assistant_message.content

                print(f"\n  최종 답변: {final_answer}")

    print(f"\n{'=' * 60}")
    print("  MCP + LLM 연동 완료!")
    print(f"{'=' * 60}")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    # 서버 모드: "--server" 인자가 있으면 MCP 서버로 실행합니다
    if "--server" in sys.argv:
        mcp.run(transport="stdio")
    else:
        # 클라이언트 모드: LLM과 연동하여 도구를 호출합니다
        print("=" * 60)
        print("  MCP 실습 정답: 커스텀 서버 + LLM 연동")
        print("=" * 60)
        asyncio.run(run_mcp_with_llm())
