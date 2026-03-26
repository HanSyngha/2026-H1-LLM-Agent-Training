"""
Windows 앱 제어 도구

pywinauto를 사용한 Windows GUI 자동화 도구입니다.
WSL에서는 직접 실행이 불가능하므로, Windows에서 실행해야 합니다.

=== Windows 앱 제어 방법 ===

1. pywinauto: Windows GUI 자동화
   - 창 찾기, 버튼 클릭, 텍스트 입력 등
   - Win32 API / UIA (UI Automation) 백엔드 지원
   - pip install pywinauto

2. win32com: COM 자동화
   - Office 앱 (Excel, Word, PowerPoint) 직접 제어
   - 셀 편집, 매크로 실행, 프레젠테이션 생성 등
   - pip install pywin32

3. CDP (Chrome DevTools Protocol): Electron 앱 제어
   - VS Code, Slack, Teams 등 Electron 기반 앱
   - --remote-debugging-port로 CDP 포트 열기
   - WebSocket으로 명령 전송

=== WSL 호환성 ===
pywinauto와 win32com은 Windows에서만 동작합니다.
WSL에서는:
- PowerShell을 통한 간접 제어가 가능합니다
- CDP를 통한 Electron 앱 제어는 가능합니다 (네트워크 통신)
"""

import sys
import os
import json
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# pywinauto 설치 여부 확인
try:
    import pywinauto
    from pywinauto import Application, Desktop
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False

# WSL 환경 감지
IS_WSL = "microsoft" in os.uname().release.lower() if hasattr(os, "uname") else False


# ============================================================
# Windows 앱 제어 도구 (pywinauto 기반)
# ============================================================

def get_running_apps() -> str:
    """
    현재 실행 중인 애플리케이션(창) 목록을 반환합니다.

    Returns:
        실행 중인 앱 목록 (창 제목, 프로세스 등)
    """
    # WSL에서는 PowerShell로 Windows 프로세스 조회
    if IS_WSL or not PYWINAUTO_AVAILABLE:
        try:
            result = subprocess.run(
                [
                    "powershell.exe", "-NoProfile", "-NonInteractive",
                    "-Command",
                    "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | "
                    "Select-Object ProcessName, MainWindowTitle, Id | "
                    "Format-Table -AutoSize | Out-String -Width 200"
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.stdout.strip():
                return f"=== 실행 중인 앱 (Windows) ===\n{result.stdout.strip()}"
            return "실행 중인 앱을 찾을 수 없습니다."
        except FileNotFoundError:
            return "오류: PowerShell을 사용할 수 없습니다."
        except Exception as e:
            return f"앱 목록 조회 오류: {e}"

    # Windows에서 pywinauto 사용
    try:
        desktop = Desktop(backend="uia")
        windows = desktop.windows()

        apps = []
        for w in windows:
            try:
                title = w.window_text()
                if title:
                    apps.append(f"  - {title}")
            except Exception:
                continue

        if not apps:
            return "실행 중인 앱을 찾을 수 없습니다."

        return f"=== 실행 중인 앱 ({len(apps)}개) ===\n" + "\n".join(apps)

    except Exception as e:
        return f"앱 목록 조회 오류: {e}"


def focus_window(title: str) -> str:
    """
    지정된 제목의 창을 전면으로 가져옵니다 (포커스).

    Args:
        title: 창 제목 (일부만 입력해도 됩니다)

    Returns:
        포커스 결과
    """
    if IS_WSL or not PYWINAUTO_AVAILABLE:
        try:
            # PowerShell로 창 활성화
            ps_script = f"""
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class WinAPI {{
                [DllImport("user32.dll")]
                public static extern bool SetForegroundWindow(IntPtr hWnd);
            }}
"@
            $proc = Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{title}*' }} | Select-Object -First 1
            if ($proc) {{
                [WinAPI]::SetForegroundWindow($proc.MainWindowHandle)
                Write-Output "창 활성화: $($proc.MainWindowTitle)"
            }} else {{
                Write-Output "창을 찾을 수 없습니다: {title}"
            }}
            """
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() or f"창 포커스 시도: {title}"
        except Exception as e:
            return f"창 포커스 오류: {e}"

    try:
        app = Application(backend="uia").connect(title_re=f".*{title}.*")
        window = app.top_window()
        window.set_focus()
        return f"창 포커스 완료: {window.window_text()}"
    except ElementNotFoundError:
        return f"창을 찾을 수 없습니다: '{title}'"
    except Exception as e:
        return f"창 포커스 오류: {e}"


def type_text(text: str) -> str:
    """
    현재 포커스된 창에 텍스트를 입력합니다.

    Args:
        text: 입력할 텍스트

    Returns:
        입력 결과

    주의: 현재 활성화된 창에 입력됩니다.
    먼저 focus_window()로 대상 창을 활성화하세요.
    """
    if IS_WSL or not PYWINAUTO_AVAILABLE:
        try:
            # PowerShell의 SendKeys를 사용
            # 특수문자 이스케이프 처리
            escaped = text.replace("'", "''")
            ps_script = f"""
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.SendKeys]::SendWait('{escaped}')
            """
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return f"텍스트 입력 완료: '{text[:50]}{'...' if len(text) > 50 else ''}'"
        except Exception as e:
            return f"텍스트 입력 오류: {e}"

    try:
        import pywinauto.keyboard as kb
        kb.send_keys(text, with_spaces=True)
        return f"텍스트 입력 완료: '{text[:50]}{'...' if len(text) > 50 else ''}'"
    except Exception as e:
        return f"텍스트 입력 오류: {e}"


def click_at(x: int, y: int) -> str:
    """
    화면의 특정 좌표를 클릭합니다.

    Args:
        x: X 좌표 (픽셀)
        y: Y 좌표 (픽셀)

    Returns:
        클릭 결과
    """
    if IS_WSL or not PYWINAUTO_AVAILABLE:
        try:
            ps_script = f"""
            Add-Type @"
            using System;
            using System.Runtime.InteropServices;
            public class MouseAPI {{
                [DllImport("user32.dll")]
                public static extern bool SetCursorPos(int X, int Y);
                [DllImport("user32.dll")]
                public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);
            }}
"@
            [MouseAPI]::SetCursorPos({x}, {y})
            Start-Sleep -Milliseconds 100
            [MouseAPI]::mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            [MouseAPI]::mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
            Write-Output "클릭 완료: ({x}, {y})"
            """
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() or f"클릭 시도: ({x}, {y})"
        except Exception as e:
            return f"클릭 오류: {e}"

    try:
        import pywinauto.mouse as mouse
        mouse.click(coords=(x, y))
        return f"클릭 완료: ({x}, {y})"
    except Exception as e:
        return f"클릭 오류: {e}"


# ============================================================
# Electron 앱 제어 (CDP)
# ============================================================

def connect_to_electron_app(port: int = 9222) -> str:
    """
    Electron 앱의 CDP(Chrome DevTools Protocol)에 연결합니다.

    === Electron 앱에서 CDP 활성화 방법 ===

    VS Code 예시:
        code --remote-debugging-port=9222

    일반 Electron 앱:
        app.exe --remote-debugging-port=9222

    또는 환경 변수:
        set ELECTRON_ENABLE_LOGGING=true
        set ELECTRON_ENABLE_STACK_DUMPING=true

    Args:
        port: CDP 디버깅 포트 (기본: 9222)

    Returns:
        연결 가능한 타겟 목록
    """
    import requests as req

    try:
        # CDP가 활성화되면 /json/list 엔드포인트에서 타겟 목록을 반환합니다
        url = f"http://localhost:{port}/json/list"
        response = req.get(url, timeout=5)
        targets = response.json()

        if not targets:
            return f"CDP 포트 {port}에 연결했지만 타겟이 없습니다."

        result = f"=== CDP 타겟 (포트: {port}) ===\n"
        for i, target in enumerate(targets):
            result += f"\n{i + 1}. {target.get('title', '(제목 없음)')}\n"
            result += f"   유형: {target.get('type', '알 수 없음')}\n"
            result += f"   URL: {target.get('url', '')}\n"
            result += f"   WebSocket: {target.get('webSocketDebuggerUrl', '')}\n"

        return result

    except req.ConnectionError:
        return (
            f"CDP 포트 {port}에 연결할 수 없습니다.\n"
            f"앱을 --remote-debugging-port={port} 옵션으로 실행했는지 확인하세요.\n"
            f"예: code --remote-debugging-port={port}"
        )
    except Exception as e:
        return f"CDP 연결 오류: {e}"


def execute_cdp_command(port: int, expression: str) -> str:
    """
    CDP를 통해 JavaScript를 실행합니다.

    Electron 앱(VS Code 등)의 DevTools Console에서
    JavaScript를 실행하는 것과 동일합니다.

    Args:
        port: CDP 포트
        expression: 실행할 JavaScript 표현식

    Returns:
        실행 결과
    """
    import requests as req

    try:
        # 먼저 타겟 목록에서 WebSocket URL 획득
        targets = req.get(f"http://localhost:{port}/json/list", timeout=5).json()
        if not targets:
            return "CDP 타겟이 없습니다."

        # 첫 번째 타겟 사용 (보통 메인 페이지)
        ws_url = targets[0].get("webSocketDebuggerUrl")
        if not ws_url:
            return "WebSocket URL을 찾을 수 없습니다."

        # WebSocket으로 Runtime.evaluate 명령 전송
        # (간단한 구현: requests로 CDP HTTP 엔드포인트 사용)
        # 참고: 완전한 구현은 websocket 라이브러리가 필요합니다
        result_url = f"http://localhost:{port}/json/evaluate"
        # HTTP 기반 evaluate는 일부 CDP 구현에서만 지원됩니다.
        # 여기서는 개념을 보여주기 위한 설명입니다.

        return (
            f"CDP JavaScript 실행 (개념 설명)\n"
            f"  타겟: {targets[0].get('title', '')}\n"
            f"  표현식: {expression}\n\n"
            f"실제 실행을 위해서는 websocket-client 라이브러리를 사용하세요:\n"
            f"  pip install websocket-client\n\n"
            f"예시 코드:\n"
            f"  import websocket, json\n"
            f"  ws = websocket.create_connection('{ws_url}')\n"
            f"  ws.send(json.dumps({{'id': 1, 'method': 'Runtime.evaluate', 'params': {{'expression': '{expression}'}}}}))\n"
            f"  result = json.loads(ws.recv())\n"
        )

    except Exception as e:
        return f"CDP 실행 오류: {e}"


# ============================================================
# OpenAI Tool Schema
# ============================================================

APP_CONTROL_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_running_apps",
            "description": "현재 실행 중인 Windows 애플리케이션(창) 목록을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "focus_window",
            "description": "지정된 제목의 창을 전면으로 가져옵니다 (활성화).",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "활성화할 창의 제목 (일부 문자열로도 검색 가능)",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "현재 활성화된 창에 텍스트를 입력합니다. 먼저 focus_window로 대상 창을 활성화하세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "입력할 텍스트",
                    },
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click_at",
            "description": "화면의 특정 좌표(x, y)를 마우스로 클릭합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X 좌표 (픽셀)",
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y 좌표 (픽셀)",
                    },
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "connect_to_electron_app",
            "description": "Electron 앱의 CDP(Chrome DevTools Protocol)에 연결하여 타겟 목록을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "port": {
                        "type": "integer",
                        "description": "CDP 디버깅 포트 (기본: 9222)",
                    },
                },
                "required": [],
            },
        },
    },
]

# 도구 이름 -> 함수 매핑
APP_CONTROL_TOOL_FUNCTIONS = {
    "get_running_apps": get_running_apps,
    "focus_window": focus_window,
    "type_text": type_text,
    "click_at": click_at,
    "connect_to_electron_app": connect_to_electron_app,
}


# ============================================================
# 테스트
# ============================================================

if __name__ == "__main__":
    print("=== 앱 제어 도구 테스트 ===\n")
    print(f"WSL 환경: {IS_WSL}")
    print(f"pywinauto 설치됨: {PYWINAUTO_AVAILABLE}")
    print()

    # 실행 중인 앱 목록
    print("[get_running_apps]")
    print(get_running_apps())
    print()

    # CDP 연결 테스트
    print("[connect_to_electron_app]")
    print(connect_to_electron_app(9222))
