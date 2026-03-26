"""
CDP (Chrome DevTools Protocol) 직접 사용 예제

Chrome DevTools Protocol은 Chrome 브라우저의 내부 통신 프로토콜입니다.
Playwright, Puppeteer, Selenium 4+ 모두 내부적으로 CDP를 사용합니다.

=== CDP 아키텍처 ===
브라우저 ←→ WebSocket ←→ 클라이언트 (Python, Node.js 등)

CDP는 "도메인(Domain)" 단위로 기능이 분류됩니다:
- Page: 페이지 이동, 로딩, 스크린샷
- Runtime: JavaScript 실행
- DOM: DOM 트리 탐색, 조작
- Network: 네트워크 요청/응답 모니터링
- Input: 키보드/마우스 입력
- Target: 탭/iframe 관리
- Emulation: 디바이스 에뮬레이션

각 도메인은 다음 요소로 구성됩니다:
- Methods: 명령 실행 (예: Page.navigate)
- Events: 비동기 알림 (예: Page.loadEventFired)
- Types: 데이터 구조 (예: DOM.NodeId)

=== CDP vs Playwright ===
- Playwright: 고수준 API, 크로스 브라우저, auto-wait, 편리한 셀렉터
- CDP 직접 사용: 최대 성능, 세밀한 제어, Chrome 전용
- Browser Use 프로젝트: Playwright → raw CDP 전환 (성능 30% 향상)

=== Chrome 실행 (CDP 포트 열기) ===
Windows:
  chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\\temp\\chrome-debug

Mac/Linux:
  google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

WSL에서 Windows Chrome 사용:
  /mnt/c/Program\ Files/Google/Chrome/Application/chrome.exe \
    --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

=== 설치 ===
pip install websocket-client requests
"""

import sys
import os
import json
import time
import base64
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

# websocket-client: WebSocket 통신 라이브러리
# CDP는 WebSocket으로 명령을 주고받습니다
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("경고: websocket-client가 설치되지 않았습니다.")
    print("설치: pip install websocket-client")

import requests as http_requests  # requests와 이름 충돌 방지


# ============================================================
# CDP 디버깅 엔드포인트 탐색
# ============================================================

def get_cdp_targets(host: str = "localhost", port: int = 9222) -> list[dict]:
    """
    Chrome의 CDP 디버깅 대상(탭) 목록을 조회합니다.

    Chrome을 --remote-debugging-port로 실행하면
    HTTP 엔드포인트가 열립니다:
    - /json/list: 현재 열린 탭 목록
    - /json/version: 브라우저 버전 정보
    - /json/new?url=...: 새 탭 열기
    - /json/close/{id}: 탭 닫기

    Returns:
        탭 목록 (각 탭의 WebSocket URL 포함)
    """
    try:
        # /json/list 엔드포인트로 탭 목록 조회
        resp = http_requests.get(
            f"http://{host}:{port}/json/list",
            timeout=5,
        )
        targets = resp.json()

        print(f"[CDP] {len(targets)}개의 탭을 발견했습니다:")
        for i, target in enumerate(targets):
            print(f"  {i+1}. {target.get('title', '(제목 없음)')}")
            print(f"     URL: {target.get('url', '')}")
            print(f"     Type: {target.get('type', '')}")
            # webSocketDebuggerUrl: 이 탭에 CDP 명령을 보낼 WebSocket URL
            print(f"     WS: {target.get('webSocketDebuggerUrl', 'N/A')}")

        return targets

    except http_requests.ConnectionError:
        print(f"[CDP] Chrome에 연결할 수 없습니다 ({host}:{port})")
        print("Chrome을 다음 명령으로 실행하세요:")
        print(f'  chrome.exe --remote-debugging-port={port} --user-data-dir=C:\\\\temp\\\\chrome-debug')
        return []
    except Exception as e:
        print(f"[CDP] 대상 조회 오류: {e}")
        return []


def get_browser_version(host: str = "localhost", port: int = 9222) -> dict:
    """
    Chrome 브라우저 버전 정보를 조회합니다.

    Returns:
        버전 정보 딕셔너리
    """
    try:
        resp = http_requests.get(
            f"http://{host}:{port}/json/version",
            timeout=5,
        )
        version = resp.json()

        print(f"[CDP] 브라우저 버전 정보:")
        print(f"  Browser: {version.get('Browser', 'N/A')}")
        print(f"  Protocol: {version.get('Protocol-Version', 'N/A')}")
        print(f"  User-Agent: {version.get('User-Agent', 'N/A')}")
        # webSocketDebuggerUrl: 브라우저 전체를 제어하는 WebSocket URL
        print(f"  WS (Browser): {version.get('webSocketDebuggerUrl', 'N/A')}")

        return version

    except Exception as e:
        print(f"[CDP] 버전 조회 오류: {e}")
        return {}


# ============================================================
# CDP 클라이언트 (WebSocket 기반)
# ============================================================

class CDPClient:
    """
    CDP WebSocket 클라이언트입니다.

    CDP 통신 프로토콜:
    1. 클라이언트 → 브라우저: JSON 메시지 (id, method, params)
    2. 브라우저 → 클라이언트: JSON 응답 (id, result) 또는 이벤트 (method, params)

    메시지 형식:
    요청: {"id": 1, "method": "Page.navigate", "params": {"url": "..."}}
    응답: {"id": 1, "result": {"frameId": "...", "loaderId": "..."}}
    이벤트: {"method": "Page.loadEventFired", "params": {"timestamp": ...}}
    """

    def __init__(self, ws_url: str):
        """
        Args:
            ws_url: Chrome 탭의 WebSocket URL
                    (예: ws://localhost:9222/devtools/page/ABC123)
        """
        self.ws_url = ws_url
        self.ws = None
        self._message_id = 0  # 요청 ID (순차 증가)
        self._responses = {}  # id -> 응답 저장
        self._events = []     # 수신된 이벤트 목록
        self._listener_thread = None
        self._running = False

    def connect(self):
        """WebSocket으로 Chrome에 연결합니다."""
        if not WEBSOCKET_AVAILABLE:
            raise RuntimeError("websocket-client가 설치되지 않았습니다.")

        print(f"[CDP] WebSocket 연결 중: {self.ws_url}")
        self.ws = websocket.create_connection(
            self.ws_url,
            timeout=10,
        )
        self._running = True

        # 백그라운드 스레드에서 메시지를 수신합니다
        # CDP 이벤트는 언제든 올 수 있으므로 별도 스레드가 필요합니다
        self._listener_thread = threading.Thread(
            target=self._listen,
            daemon=True,  # 메인 스레드 종료 시 함께 종료
        )
        self._listener_thread.start()

        print("[CDP] 연결 성공!")

    def _listen(self):
        """백그라운드에서 WebSocket 메시지를 수신합니다."""
        while self._running:
            try:
                raw = self.ws.recv()
                if raw:
                    msg = json.loads(raw)

                    if "id" in msg:
                        # 요청에 대한 응답
                        self._responses[msg["id"]] = msg
                    else:
                        # CDP 이벤트 (id 없음)
                        self._events.append(msg)

            except websocket.WebSocketTimeoutException:
                continue
            except Exception:
                break

    def send_command(self, method: str, params: dict = None, timeout: float = 30.0) -> dict:
        """
        CDP 명령을 전송하고 응답을 기다립니다.

        Args:
            method: CDP 메서드 (예: "Page.navigate", "Runtime.evaluate")
            params: 메서드 파라미터
            timeout: 응답 대기 시간 (초)

        Returns:
            CDP 응답 딕셔너리
        """
        self._message_id += 1
        msg_id = self._message_id

        # CDP 요청 메시지 구성
        message = {
            "id": msg_id,
            "method": method,
        }
        if params:
            message["params"] = params

        # WebSocket으로 JSON 메시지 전송
        self.ws.send(json.dumps(message))

        # 응답 대기 (폴링)
        start = time.time()
        while time.time() - start < timeout:
            if msg_id in self._responses:
                response = self._responses.pop(msg_id)

                # 오류 확인
                if "error" in response:
                    error = response["error"]
                    print(f"[CDP] 오류: {error.get('message', '알 수 없는 오류')}")

                return response

            time.sleep(0.05)  # 50ms 간격으로 확인

        raise TimeoutError(f"[CDP] 응답 시간 초과 ({timeout}초): {method}")

    def close(self):
        """WebSocket 연결을 종료합니다."""
        self._running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
        print("[CDP] 연결 종료")


# ============================================================
# CDP 명령 예제 함수들
# ============================================================

def cdp_navigate(client: CDPClient, url: str) -> dict:
    """
    CDP로 페이지를 이동합니다.

    Page.navigate 메서드를 사용합니다.
    Playwright의 page.goto()가 내부적으로 이 명령을 호출합니다.
    """
    print(f"\n[CDP] 페이지 이동: {url}")

    # Page 도메인 활성화 (이벤트를 수신하려면 먼저 활성화해야 합니다)
    client.send_command("Page.enable")

    # 페이지 이동 명령
    result = client.send_command("Page.navigate", {"url": url})

    # 로딩 완료 대기
    time.sleep(2)  # 간단한 대기 (실제로는 이벤트 기반이 좋음)

    print(f"[CDP] 이동 완료: {result.get('result', {})}")
    return result


def cdp_evaluate_js(client: CDPClient, expression: str) -> dict:
    """
    CDP로 JavaScript를 실행합니다.

    Runtime.evaluate 메서드를 사용합니다.
    Playwright의 page.evaluate()가 내부적으로 이 명령을 호출합니다.
    """
    print(f"\n[CDP] JavaScript 실행: {expression[:100]}...")

    result = client.send_command("Runtime.evaluate", {
        "expression": expression,
        "returnByValue": True,  # 결과를 값으로 반환 (참조가 아닌)
    })

    eval_result = result.get("result", {}).get("result", {})
    print(f"[CDP] 결과 타입: {eval_result.get('type')}")

    if eval_result.get("type") == "string":
        value = eval_result.get("value", "")
        print(f"[CDP] 결과 값: {value[:200]}...")
        return {"value": value}
    elif eval_result.get("type") == "object":
        return {"value": eval_result.get("value", {})}
    else:
        return {"value": eval_result.get("value")}


def cdp_get_title(client: CDPClient) -> str:
    """페이지 타이틀을 가져옵니다."""
    result = cdp_evaluate_js(client, "document.title")
    return result.get("value", "")


def cdp_get_page_text(client: CDPClient) -> str:
    """페이지의 전체 텍스트를 추출합니다."""
    result = cdp_evaluate_js(
        client,
        "document.body.innerText"
    )
    return result.get("value", "")


def cdp_screenshot(client: CDPClient, output_path: str = "cdp_screenshot.png") -> str:
    """
    CDP로 스크린샷을 촬영합니다.

    Page.captureScreenshot 메서드를 사용합니다.
    결과는 base64 인코딩된 이미지 데이터입니다.
    """
    print(f"\n[CDP] 스크린샷 촬영...")

    result = client.send_command("Page.captureScreenshot", {
        "format": "png",      # png 또는 jpeg
        "quality": 80,        # jpeg일 때 품질 (0-100)
        "fromSurface": True,  # 화면에 보이는 영역만
    })

    # base64 데이터를 파일로 저장
    image_data = result.get("result", {}).get("data", "")
    if image_data:
        abs_path = os.path.abspath(output_path)
        with open(abs_path, "wb") as f:
            f.write(base64.b64decode(image_data))
        size = os.path.getsize(abs_path)
        print(f"[CDP] 스크린샷 저장 완료: {abs_path} ({size:,} bytes)")
        return abs_path
    else:
        print("[CDP] 스크린샷 데이터 없음")
        return ""


def cdp_get_dom_tree(client: CDPClient) -> dict:
    """
    CDP로 DOM 트리를 가져옵니다.

    DOM.getDocument 메서드를 사용합니다.
    전체 DOM 구조를 탐색할 수 있습니다.
    """
    print(f"\n[CDP] DOM 트리 가져오기...")

    # DOM 도메인 활성화
    client.send_command("DOM.enable")

    # 루트 노드 가져오기
    result = client.send_command("DOM.getDocument", {
        "depth": 3,  # DOM 깊이 제한 (성능 고려)
    })

    root = result.get("result", {}).get("root", {})
    print(f"[CDP] 루트 노드: {root.get('nodeName', 'N/A')}")
    print(f"[CDP] 자식 노드 수: {len(root.get('children', []))}")

    return root


def cdp_monitor_network(client: CDPClient, duration: float = 5.0):
    """
    CDP로 네트워크 요청을 모니터링합니다.

    Network 도메인을 활성화하면 모든 HTTP 요청/응답 이벤트를 받습니다.
    Playwright의 page.on("request") / page.on("response")가
    내부적으로 이 메커니즘을 사용합니다.
    """
    print(f"\n[CDP] 네트워크 모니터링 시작 ({duration}초)...")

    # Network 도메인 활성화
    client.send_command("Network.enable")

    # 지정된 시간 동안 이벤트 수집
    start_event_count = len(client._events)
    time.sleep(duration)

    # 수집된 네트워크 이벤트 분석
    network_events = [
        e for e in client._events[start_event_count:]
        if e.get("method", "").startswith("Network.")
    ]

    print(f"[CDP] {len(network_events)}개의 네트워크 이벤트 수집:")
    for event in network_events[:10]:  # 최대 10개만 출력
        method = event.get("method", "")
        params = event.get("params", {})

        if method == "Network.requestWillBeSent":
            req = params.get("request", {})
            print(f"  요청: {req.get('method', 'GET')} {req.get('url', '')[:80]}")
        elif method == "Network.responseReceived":
            resp = params.get("response", {})
            print(f"  응답: {resp.get('status', '?')} {resp.get('url', '')[:80]}")

    # Network 도메인 비활성화
    client.send_command("Network.disable")


# ============================================================
# Playwright와 CDP 비교 예제
# ============================================================

def comparison_playwright_vs_cdp():
    """
    Playwright와 CDP 직접 사용의 코드 비교입니다.
    (실행하지 않고 코드 비교만 합니다)

    이 함수는 두 방식의 차이점을 보여줍니다.
    """
    comparison = """
    ╔══════════════════════════════════════════════════════════════╗
    ║          Playwright vs CDP 직접 사용 비교                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  === 페이지 이동 ===                                         ║
    ║                                                              ║
    ║  [Playwright]                                                ║
    ║  page.goto("https://example.com")                           ║
    ║                                                              ║
    ║  [CDP 직접]                                                  ║
    ║  ws.send(json.dumps({                                       ║
    ║      "id": 1,                                               ║
    ║      "method": "Page.navigate",                             ║
    ║      "params": {"url": "https://example.com"}               ║
    ║  }))                                                         ║
    ║  # + 응답 대기, 로딩 완료 이벤트 처리 필요                    ║
    ║                                                              ║
    ║  === JavaScript 실행 ===                                     ║
    ║                                                              ║
    ║  [Playwright]                                                ║
    ║  title = page.evaluate("document.title")                    ║
    ║                                                              ║
    ║  [CDP 직접]                                                  ║
    ║  ws.send(json.dumps({                                       ║
    ║      "id": 2,                                               ║
    ║      "method": "Runtime.evaluate",                          ║
    ║      "params": {                                            ║
    ║          "expression": "document.title",                    ║
    ║          "returnByValue": true                               ║
    ║      }                                                       ║
    ║  }))                                                         ║
    ║  # + 응답에서 result.result.value 추출 필요                   ║
    ║                                                              ║
    ║  === 성능 비교 ===                                           ║
    ║  CDP 직접:  오버헤드 최소, 최대 성능                          ║
    ║  Playwright: 편의 기능 (auto-wait, retry) 오버헤드           ║
    ║                                                              ║
    ║  === Browser Use 프로젝트의 선택 ===                         ║
    ║  초기: Playwright 사용                                       ║
    ║  현재: raw CDP 전환 → 성능 30%+ 향상                         ║
    ║  이유: 불필요한 추상화 계층 제거, 직접 제어                   ║
    ║                                                              ║
    ║  === 결론 ===                                                ║
    ║  일반적인 자동화 → Playwright 추천                            ║
    ║  고성능 / 세밀한 제어 → CDP 직접 사용 고려                    ║
    ║  학습 목적 → CDP 이해 후 Playwright 사용이 이상적            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(comparison)


# ============================================================
# CDP 도메인 참조 표
# ============================================================

def print_cdp_domains():
    """CDP의 주요 도메인과 메서드를 출력합니다."""
    domains = {
        "Page": {
            "설명": "페이지 이동, 로딩, 스크린샷 등",
            "주요 메서드": [
                "Page.navigate(url) - 페이지 이동",
                "Page.reload() - 새로고침",
                "Page.captureScreenshot() - 스크린샷",
                "Page.printToPDF() - PDF 출력",
                "Page.getFrameTree() - 프레임(iframe) 트리",
            ],
            "주요 이벤트": [
                "Page.loadEventFired - 로딩 완료",
                "Page.frameNavigated - 프레임 이동",
                "Page.domContentEventFired - DOM 로딩 완료",
            ],
        },
        "Runtime": {
            "설명": "JavaScript 실행 및 객체 관리",
            "주요 메서드": [
                "Runtime.evaluate(expression) - JS 실행",
                "Runtime.callFunctionOn() - 객체의 함수 호출",
                "Runtime.getProperties() - 객체 속성 조회",
            ],
            "주요 이벤트": [
                "Runtime.consoleAPICalled - console.log 등",
                "Runtime.exceptionThrown - 예외 발생",
            ],
        },
        "DOM": {
            "설명": "DOM 트리 탐색 및 조작",
            "주요 메서드": [
                "DOM.getDocument() - 문서 루트 노드",
                "DOM.querySelector(nodeId, selector) - CSS 셀렉터 검색",
                "DOM.getOuterHTML(nodeId) - HTML 문자열",
                "DOM.setAttributeValue() - 속성 변경",
            ],
            "주요 이벤트": [
                "DOM.documentUpdated - DOM 변경",
                "DOM.childNodeInserted - 노드 추가",
            ],
        },
        "Network": {
            "설명": "네트워크 요청/응답 모니터링",
            "주요 메서드": [
                "Network.enable() - 모니터링 시작",
                "Network.getResponseBody(requestId) - 응답 본문",
                "Network.setCookie() - 쿠키 설정",
                "Network.setExtraHTTPHeaders() - 헤더 추가",
            ],
            "주요 이벤트": [
                "Network.requestWillBeSent - 요청 전송",
                "Network.responseReceived - 응답 수신",
                "Network.loadingFinished - 로딩 완료",
            ],
        },
        "Input": {
            "설명": "키보드/마우스 입력 시뮬레이션",
            "주요 메서드": [
                "Input.dispatchKeyEvent() - 키보드 이벤트",
                "Input.dispatchMouseEvent() - 마우스 이벤트",
                "Input.insertText(text) - 텍스트 입력",
            ],
            "주요 이벤트": [],
        },
        "Target": {
            "설명": "탭, iframe, worker 관리",
            "주요 메서드": [
                "Target.getTargets() - 모든 대상 조회",
                "Target.createTarget(url) - 새 탭 열기",
                "Target.closeTarget(targetId) - 탭 닫기",
                "Target.attachToTarget(targetId) - 대상에 연결",
            ],
            "주요 이벤트": [
                "Target.targetCreated - 대상 생성",
                "Target.targetDestroyed - 대상 제거",
            ],
        },
    }

    print("=" * 60)
    print("CDP (Chrome DevTools Protocol) 주요 도메인")
    print("=" * 60)

    for domain_name, info in domains.items():
        print(f"\n{'─' * 50}")
        print(f"  {domain_name}: {info['설명']}")
        print(f"{'─' * 50}")

        print("  메서드:")
        for method in info["주요 메서드"]:
            print(f"    - {method}")

        if info["주요 이벤트"]:
            print("  이벤트:")
            for event in info["주요 이벤트"]:
                print(f"    - {event}")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CDP (Chrome DevTools Protocol) 직접 사용 예제")
    print("=" * 60)

    # 1. CDP 도메인 참조 출력
    print("\n[1] CDP 도메인 참조")
    print_cdp_domains()

    # 2. Playwright vs CDP 비교
    print("\n\n[2] Playwright vs CDP 비교")
    comparison_playwright_vs_cdp()

    # 3. 실제 CDP 연결 시도
    print("\n[3] Chrome CDP 연결 시도")
    print("-" * 40)

    # Chrome이 --remote-debugging-port=9222로 실행 중인지 확인
    CDP_HOST = "localhost"
    CDP_PORT = 9222

    # 브라우저 버전 확인
    version = get_browser_version(CDP_HOST, CDP_PORT)

    if not version:
        print("\nChrome이 CDP 모드로 실행되지 않았습니다.")
        print("다음 명령으로 Chrome을 실행하세요:\n")
        print("  [Windows]")
        print(f'  chrome.exe --remote-debugging-port={CDP_PORT} --user-data-dir=C:\\temp\\chrome-debug')
        print()
        print("  [WSL에서 Windows Chrome 사용]")
        print(f'  /mnt/c/Program\\ Files/Google/Chrome/Application/chrome.exe \\')
        print(f'    --remote-debugging-port={CDP_PORT} --user-data-dir=/tmp/chrome-debug')
        print()
        print("Chrome 실행 후 이 스크립트를 다시 실행하세요.")
        sys.exit(0)

    # 탭 목록 조회
    targets = get_cdp_targets(CDP_HOST, CDP_PORT)

    if not targets:
        print("열린 탭이 없습니다.")
        sys.exit(0)

    # 첫 번째 "page" 타입 탭에 연결
    page_targets = [t for t in targets if t.get("type") == "page"]
    if not page_targets:
        print("page 타입 탭이 없습니다.")
        sys.exit(0)

    ws_url = page_targets[0].get("webSocketDebuggerUrl")
    if not ws_url:
        print("WebSocket URL을 찾을 수 없습니다.")
        sys.exit(0)

    # CDP 클라이언트 생성 및 연결
    client = CDPClient(ws_url)

    try:
        client.connect()

        # 페이지 이동
        cdp_navigate(client, "https://www.example.com")
        time.sleep(1)

        # 타이틀 가져오기
        title = cdp_get_title(client)
        print(f"\n[결과] 페이지 타이틀: {title}")

        # 페이지 텍스트 추출
        text = cdp_get_page_text(client)
        print(f"\n[결과] 페이지 텍스트 (처음 500자):")
        print(text[:500])

        # 스크린샷 촬영
        screenshot_path = cdp_screenshot(client, "cdp_screenshot.png")
        if screenshot_path:
            print(f"\n[결과] 스크린샷: {screenshot_path}")

        # DOM 트리 탐색
        dom_root = cdp_get_dom_tree(client)

        print("\n" + "=" * 60)
        print("CDP 직접 사용 데모 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[오류] {e}")

    finally:
        client.close()
