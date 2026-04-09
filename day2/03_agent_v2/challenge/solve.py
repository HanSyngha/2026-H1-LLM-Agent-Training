"""
Agent 설계 과제 — LLM + Agentic Loop로 미로를 풀어주세요!

실행: python solve.py

⚠️ 중요: 이 과제는 반드시 LLM을 사용한 Agentic Loop로 풀어야 합니다.
         API를 직접 순서대로 호출하는 방식(for문, 하드코딩)은 금지입니다!
         LLM이 다음에 무엇을 할지 판단하고, tool을 호출하고,
         결과를 보고 다음 행동을 결정하는 loop를 구현하세요.

=== 구현해야 하는 것 ===
1. call_llm(messages) — LLM Gateway에 요청
2. Agentic Loop — LLM 호출 → tool_calls 처리 → 결과 피드백 → 반복
3. Completion 판단 — LLM이 모든 작업 완료를 판단하여 종료
4. History 관리 — messages에 대화 기록 누적
5. 에러 처리 — 작업 실패 시 LLM이 재시도 판단

=== 성공 시 ===
completion_code를 강의 슬라이드에 입력하면 통과!
"""

import requests
import json

# ============================================
# 서버 정보
# ============================================
CHALLENGE_SERVER = "http://a2g.samsungds.net:47777"
LLM_GATEWAY = "http://a2g.samsungds.net:8090/v1"
SERVICE_ID = "test-service"
MODEL = "testmodel"

# ============================================
# 본인 정보 입력
# ============================================
TOKEN = ""   # SSO access_token
USER_ID = "" # SSO user ID

# ============================================
# Tool 정의 (제공됨)
# ============================================
tools = [
    {"type": "function", "function": {
        "name": "start_maze",
        "description": "에이전트 미로를 시작합니다. 어떤 작업들이 있는지 안내받습니다.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
    {"type": "function", "function": {
        "name": "run_task",
        "description": "특정 작업을 실행합니다. 실패할 수 있으며 재시도가 필요합니다.",
        "parameters": {"type": "object", "properties": {
            "task_id": {"type": "string", "description": "실행할 작업 ID"},
        }, "required": ["task_id"]},
    }},
    {"type": "function", "function": {
        "name": "finish_maze",
        "description": "모든 작업 완료 후 호출합니다. completion_code가 반환됩니다.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }},
]

# ============================================
# Tool 실행 함수 (제공됨)
# ============================================
def execute_tool(tool_name, arguments):
    if tool_name == "start_maze":
        return requests.get(f"{CHALLENGE_SERVER}/challenges/agent_v2/start", params={"token": TOKEN}).json()
    elif tool_name == "run_task":
        return requests.get(f"{CHALLENGE_SERVER}/challenges/agent_v2/task/{arguments['task_id']}", params={"token": TOKEN}).json()
    elif tool_name == "finish_maze":
        return requests.get(f"{CHALLENGE_SERVER}/challenges/agent_v2/end", params={"token": TOKEN}).json()
    return {"error": f"unknown tool: {tool_name}"}

# ============================================
# System Prompt (제공됨)
# ============================================
SYSTEM_PROMPT = """당신은 API 미로를 푸는 에이전트입니다.
start_maze로 시작하여, 안내에 따라 작업을 실행하고, 모든 작업이 완료되면 finish_maze를 호출하세요.
작업이 실패하면 재시도하세요. 절대 중간에 멈추지 마세요."""

# ============================================
# ⚠️ 아래를 구현하세요!
#
# 절대 API를 직접 순서대로 호출하지 마세요 (for문 금지!)
# LLM이 tool_calls로 판단 → execute_tool 실행 → 결과를 LLM에 피드백
# 이 과정을 반복하는 while loop를 만드세요.
#
# 필요한 것:
# 1. call_llm(messages): POST LLM_GATEWAY/chat/completions
#    headers: Content-Type, x-service-id(SERVICE_ID), x-user-id(USER_ID)
#    body: model(MODEL), messages, tools, max_tokens
#
# 2. messages = [system prompt, user 메시지] 로 시작
#
# 3. while loop:
#    - call_llm(messages)
#    - response의 tool_calls 확인
#    - 있으면: execute_tool() 후 결과를 messages에 추가, 반복
#    - 없으면: LLM의 최종 텍스트 응답 출력, 종료
# ============================================

print("🔄 이 스크립트를 바이브 코딩으로 완성하세요!")
print("⚠️ for문으로 직접 호출 금지 — LLM Agentic Loop 필수!")
