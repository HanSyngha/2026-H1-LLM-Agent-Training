"""
Bash Tool 과제 — PowerShell/Subprocess Tool로 파일 해독

실행: python app.py
GUI 챗봇이 열립니다.

과제:
  encoded.txt에 숨겨진 비밀 코드를 찾으세요.
  mission.txt에 해독 방법이 적혀있습니다.
  LLM에게 subprocess tool을 주고, 명령어를 실행시켜 해독하세요.

  TODO: execute_command() 함수를 구현하세요!
        subprocess.run()으로 명령어를 실행하고 결과를 반환하면 됩니다.

  ⚠️ for문으로 직접 디코딩하지 마세요!
     LLM이 tool을 통해 명령어를 실행하여 해독해야 합니다.
"""

import json
import subprocess
import threading
import requests
import tkinter as tk
from tkinter import scrolledtext

# ============================================
# 서버 정보
# ============================================
CHALLENGE_SERVER = "http://challenge.example.com:47777"
LLM_GATEWAY = "https://llm-gateway.example.com/v1"
SERVICE_ID = "test-service"
MODEL = "testmodel"
USER_ID = ""  # 본인 SSO user ID 입력

# ============================================
# Tool 정의 (제공됨)
# ============================================
tools = [
    {"type": "function", "function": {
        "name": "run_command",
        "description": "로컬 명령어를 실행합니다. PowerShell, Python, 기본 명령어 모두 가능합니다.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "실행할 명령어 (예: dir, type file.txt, python -c 'code')"},
        }, "required": ["command"]},
    }},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "파일 내용을 읽습니다.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "읽을 파일 경로"},
        }, "required": ["path"]},
    }},
]

# ============================================
# TODO: execute_command 함수를 구현하세요!
#
# subprocess.run()으로 명령어를 실행하고
# stdout(표준 출력)을 문자열로 반환하세요.
#
# 힌트:
#   result = subprocess.run(command, shell=True,
#       capture_output=True, text=True, timeout=30)
#   return result.stdout or result.stderr
# ============================================
def execute_command(command):
    return "TODO: subprocess.run()으로 구현하세요!"


# ============================================
# TODO: read_file 함수도 구현하세요!
#
# 파일 경로를 받아서 내용을 읽어 반환하세요.
#
# 힌트:
#   with open(path, "r", encoding="utf-8") as f:
#       return f.read()
# ============================================
def read_file(path):
    return "TODO: open()으로 파일 읽기를 구현하세요!"


def execute_tool(tool_name, arguments):
    if tool_name == "run_command":
        return {"output": execute_command(arguments.get("command", ""))}
    elif tool_name == "read_file":
        return {"content": read_file(arguments.get("path", ""))}
    return {"error": f"unknown tool: {tool_name}"}

# ============================================
# System Prompt (제공됨)
# ============================================
SYSTEM_PROMPT = """당신은 파일 해독 에이전트입니다.
사용자가 파일 해독을 요청하면:
1. read_file로 mission.txt를 읽어 해독 방법을 확인하세요
2. run_command로 명령어를 실행하여 encoded.txt를 해독하세요
3. 해독 결과에서 비밀 코드를 추출하세요
4. 비밀 코드를 사용자에게 알려주세요

반드시 tool을 사용하여 해독하세요. 직접 추측하지 마세요."""

# ============================================
# LLM 호출 (제공됨)
# ============================================
def call_llm(messages):
    try:
        r = requests.post(f"{LLM_GATEWAY}/chat/completions",
            headers={"Content-Type": "application/json",
                     "x-service-id": SERVICE_ID, "x-user-id": USER_ID},
            json={"model": MODEL, "messages": messages, "tools": tools,
                  "tool_choice": "auto", "max_tokens": 1024},
            timeout=120)
        if r.status_code != 200:
            return None, f"LLM error {r.status_code}"
        return r.json(), None
    except Exception as e:
        return None, str(e)

# ============================================
# Agentic Loop (제공됨)
# ============================================
def run_agent(messages, log_fn):
    tool_called = False
    for i in range(15):
        result, error = call_llm(messages)
        if error:
            return f"❌ {error}"

        msg = result["choices"][0]["message"]
        if not msg.get("tool_calls"):
            if not tool_called:
                messages.append(msg)
                messages.append({"role": "user", "content": "tool을 사용하세요."})
                log_fn("⚠️ 재촉: tool 호출 필요")
                continue
            return msg.get("content", "")

        tool_called = True
        messages.append(msg)
        for tc in msg["tool_calls"]:
            fn = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"]) if tc["function"].get("arguments") else {}
            log_fn(f"🔧 {fn}: {json.dumps(args, ensure_ascii=False)[:60]}")
            tr = execute_tool(fn, args)
            log_fn(f"   → {json.dumps(tr, ensure_ascii=False)[:80]}")
            messages.append({"role": "tool", "tool_call_id": tc["id"],
                            "content": json.dumps(tr, ensure_ascii=False)})

    return "⚠️ 최대 반복 초과"

# ============================================
# GUI (제공됨)
# ============================================
class ChatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔧 Bash Tool 과제 — 파일 해독 에이전트")
        self.root.geometry("700x550")
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        self.chat = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Consolas", 10))
        self.chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        self.chat.config(state=tk.DISABLED)

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.entry = tk.Entry(frame, font=("Consolas", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.on_send)
        self.btn = tk.Button(frame, text="전송", command=self.on_send, width=8)
        self.btn.pack(side=tk.RIGHT, padx=(5, 0))

        self.log("시스템: encoded.txt에 숨겨진 비밀 코드를 찾으세요!")
        self.log("시스템: '해독해줘'라고 입력하세요.\n")

    def log(self, text):
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, text + "\n")
        self.chat.see(tk.END)
        self.chat.config(state=tk.DISABLED)

    def on_send(self, event=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.log(f"\n👤 {text}")
        self.messages.append({"role": "user", "content": text})
        self.btn.config(state=tk.DISABLED)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        answer = run_agent(self.messages, lambda t: self.root.after(0, self.log, t))
        self.root.after(0, self._done, answer)

    def _done(self, answer):
        self.log(f"\n🤖 {answer}")
        self.messages.append({"role": "assistant", "content": answer or ""})
        self.btn.config(state=tk.NORMAL)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    ChatApp().run()
