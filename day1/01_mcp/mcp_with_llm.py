"""
MCP + LLM 연동 예제

MCP 서버의 도구를 LLM의 function calling과 연동하는 완전한 워크플로우를 보여줍니다.

전체 흐름:
1. MCP 서버에 연결하여 사용 가능한 도구 목록을 가져옴
2. MCP 도구 스키마를 OpenAI function calling 형식으로 변환
3. 사용자 질문 + 도구 정보를 LLM에 전송
4. LLM이 반환한 tool_calls를 파싱하여 MCP 도구 실행
5. 도구 실행 결과를 다시 LLM에 전송
6. LLM이 최종 답변 생성

실행 방법:
    python mcp_with_llm.py

의존성:
    pip install mcp openai httpx
"""

import asyncio
import json
import os
import sys

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def mcp_tools_to_openai_format(mcp_tools) -> list[dict]:
    """MCP 도구 스키마를 OpenAI function calling 형식으로 변환합니다.

    MCP의 도구 정의는 자체 스키마를 사용하지만, OpenAI API는
    별도의 function calling 형식을 요구합니다. 이 함수가 변환을 담당합니다.

    Args:
        mcp_tools: MCP 서버에서 가져온 도구 목록

    Returns:
        OpenAI function calling 형식의 도구 정의 리스트
    """
    openai_tools = []
    for tool in mcp_tools:
        # OpenAI의 function calling 형식으로 변환
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                # inputSchema: MCP 도구의 JSON Schema (이미 OpenAI 호환 형식)
                "parameters": tool.inputSchema
                if tool.inputSchema
                else {"type": "object", "properties": {}},
            },
        }
        openai_tools.append(openai_tool)
    return openai_tools


async def run_mcp_with_llm():
    """MCP + LLM 연동 메인 함수"""

    # OpenAI 클라이언트 생성 (사내 게이트웨이 사용)
    client = get_openai_client()

    # ──────────────────────────────────────────
    # 1단계: MCP 서버에 연결
    # ──────────────────────────────────────────
    server_script = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
    )

    print("[1단계] MCP 서버에 연결 중...")

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("  -> MCP 서버 연결 완료!")

            # ──────────────────────────────────
            # 2단계: MCP 도구 목록 가져와서 OpenAI 형식으로 변환
            # ──────────────────────────────────
            print("\n[2단계] MCP 도구를 OpenAI function calling 형식으로 변환...")
            tools_result = await session.list_tools()
            openai_tools = mcp_tools_to_openai_format(tools_result.tools)

            print(f"  -> 변환된 도구 {len(openai_tools)}개:")
            for t in openai_tools:
                print(f"     - {t['function']['name']}: {t['function']['description'][:50]}...")

            # ──────────────────────────────────
            # 3단계: 사용자 질문 + 도구 정보를 LLM에 전송
            # ──────────────────────────────────
            user_query = "서울 날씨 알려주고 3+5 계산해줘"
            print(f"\n[3단계] 사용자 질문: '{user_query}'")
            print("  -> LLM에 질문 + 도구 정보 전송 중...")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "당신은 유능한 AI 어시스턴트입니다. "
                        "사용자의 요청을 처리하기 위해 제공된 도구를 적극 활용하세요. "
                        "여러 작업이 요청되면 가능한 모든 도구를 호출하세요."
                    ),
                },
                {"role": "user", "content": user_query},
            ]

            # 첫 번째 LLM 호출: 도구 호출 여부 결정
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages,
                tools=openai_tools,  # MCP에서 가져온 도구 정보
                tool_choice="auto",  # LLM이 자동으로 도구 호출 판단
            )

            assistant_message = response.choices[0].message

            # ──────────────────────────────────
            # 4단계: LLM의 tool_calls 처리
            # ──────────────────────────────────
            if assistant_message.tool_calls:
                print(f"\n[4단계] LLM이 {len(assistant_message.tool_calls)}개 도구 호출을 요청했습니다:")

                # 어시스턴트 메시지(tool_calls 포함)를 대화 히스토리에 추가
                messages.append(assistant_message)

                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    print(f"\n  도구 호출: {func_name}({func_args})")

                    # ──────────────────────────
                    # 5단계: MCP 도구 실행
                    # ──────────────────────────
                    # LLM이 요청한 도구를 MCP 서버에서 실행
                    result = await session.call_tool(func_name, arguments=func_args)

                    # 도구 실행 결과를 텍스트로 추출
                    tool_result_text = ""
                    for content in result.content:
                        tool_result_text += content.text

                    print(f"  실행 결과: {tool_result_text}")

                    # 도구 결과를 대화 히스토리에 추가
                    # role: "tool"은 도구 실행 결과를 나타내는 특별한 역할
                    # tool_call_id: 어떤 tool_call에 대한 응답인지 매핑
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result_text,
                        }
                    )

                # ──────────────────────────────
                # 6단계: 도구 결과를 포함하여 LLM에 다시 전송
                # ──────────────────────────────
                print("\n[6단계] 도구 결과를 LLM에 전송하여 최종 답변 생성 중...")
                final_response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=messages,
                )
                final_answer = final_response.choices[0].message.content
            else:
                # 도구 호출 없이 직접 답변한 경우
                final_answer = assistant_message.content

            # ──────────────────────────────────
            # 최종 결과 출력
            # ──────────────────────────────────
            print("\n" + "=" * 60)
            print("  최종 답변")
            print("=" * 60)
            print(final_answer)
            print("=" * 60)

            # ──────────────────────────────────
            # 전체 흐름 요약 출력
            # ──────────────────────────────────
            print("\n[흐름 요약]")
            print("  사용자 질문 -> LLM (도구 필요 판단)")
            print("  -> MCP 도구 호출 (get_weather, add)")
            print("  -> 도구 결과 수집")
            print("  -> LLM (최종 답변 생성)")
            print("  -> 사용자에게 답변 전달")


if __name__ == "__main__":
    asyncio.run(run_mcp_with_llm())
