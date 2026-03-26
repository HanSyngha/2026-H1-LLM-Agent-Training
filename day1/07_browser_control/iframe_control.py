"""
iframe 제어 예제 - Playwright & CDP

iframe(Inline Frame)은 웹 페이지 안에 다른 웹 페이지를 삽입하는 HTML 요소입니다.
사내 시스템, 관리자 페이지, 레거시 웹앱에서 자주 사용됩니다.

=== iframe이 어려운 이유 ===
1. 별도의 Document: 각 iframe은 독립된 DOM 트리를 가짐
2. 크로스 오리진: 다른 도메인의 iframe은 보안 정책(CORS)으로 접근 제한
3. 중첩 iframe: iframe 안에 iframe이 있는 경우
4. 동적 로딩: JavaScript로 생성되는 iframe
5. Shadow DOM: 웹 컴포넌트의 캡슐화된 DOM 트리

=== iframe 접근 전략 ===
- Playwright: frame() / frame_locator() 메서드
- CDP: Target.getTargets()로 iframe Target 찾기
- JavaScript: contentDocument / contentWindow (동일 오리진만)

=== 사내 시스템 iframe 패턴 ===
많은 사내 시스템(ERP, 그룹웨어 등)이 iframe을 사용합니다:
- 메인 레이아웃: 상단 메뉴, 좌측 메뉴
- 콘텐츠 영역: iframe으로 분리
- 팝업 창: iframe으로 구현

=== 설치 ===
pip install playwright
playwright install chromium
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("경고: playwright가 설치되지 않았습니다.")
    print("설치: pip install playwright && playwright install chromium")


# ============================================================
# iframe 탐지 및 목록 조회
# ============================================================

def detect_iframes(url: str):
    """
    페이지에 포함된 모든 iframe을 탐지합니다.

    iframe 탐지는 자동화의 첫 번째 단계입니다.
    어떤 iframe이 있는지 파악한 후 접근합니다.
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[iframe] playwright를 사용할 수 없습니다")
        return []

    print(f"[iframe 탐지] URL: {url}")
    print("-" * 40)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)  # 동적 iframe 로딩 대기

            # 방법 1: page.frames 속성으로 모든 프레임 조회
            # Playwright는 페이지 내 모든 프레임(iframe 포함)을 자동 추적합니다
            frames = page.frames
            print(f"\n  [방법 1] page.frames: {len(frames)}개 프레임")
            for i, frame in enumerate(frames):
                name = frame.name or "(이름 없음)"
                frame_url = frame.url
                is_main = "(메인)" if frame == page.main_frame else "(iframe)"
                print(f"    {i}. {is_main} name='{name}' url={frame_url[:80]}")

            # 방법 2: JavaScript로 iframe 태그 직접 조회
            iframe_info = page.evaluate("""
                () => {
                    const iframes = document.querySelectorAll('iframe');
                    return Array.from(iframes).map((iframe, index) => ({
                        index: index,
                        id: iframe.id || '',
                        name: iframe.name || '',
                        src: iframe.src || '',
                        width: iframe.width || iframe.offsetWidth,
                        height: iframe.height || iframe.offsetHeight,
                        // 동일 오리진인지 확인
                        sameOrigin: (() => {
                            try {
                                // 크로스 오리진이면 접근 시 에러 발생
                                return !!iframe.contentDocument;
                            } catch(e) {
                                return false;
                            }
                        })(),
                    }));
                }
            """)

            print(f"\n  [방법 2] DOM 직접 조회: {len(iframe_info)}개 iframe")
            for info in iframe_info:
                origin = "동일 오리진" if info["sameOrigin"] else "크로스 오리진"
                print(f"    #{info['index']}: id='{info['id']}' name='{info['name']}'")
                print(f"      src: {info['src'][:80]}")
                print(f"      크기: {info['width']}x{info['height']}, {origin}")

            browser.close()
            return iframe_info

        except Exception as e:
            print(f"  오류: {e}")
            browser.close()
            return []


# ============================================================
# Playwright - iframe 내부 요소 접근
# ============================================================

def playwright_iframe_access():
    """
    Playwright로 iframe 내부 요소에 접근합니다.

    Playwright는 iframe 접근을 위한 두 가지 방법을 제공합니다:
    1. frame(): Frame 객체를 직접 가져오기
    2. frame_locator(): iframe 내부의 Locator 생성 (권장)
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[iframe 접근] playwright를 사용할 수 없습니다")
        return

    print("[iframe 접근] Playwright iframe 접근 예제")
    print("-" * 40)

    # iframe이 포함된 테스트 페이지를 생성합니다
    # (실제 환경에서는 대상 URL을 사용합니다)
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>iframe 테스트 페이지</title></head>
    <body>
        <h1>메인 페이지</h1>
        <p>이 페이지에는 iframe이 포함되어 있습니다.</p>

        <!-- iframe 1: 이름으로 접근 -->
        <iframe name="content-frame" id="frame1"
                srcdoc="
                    <html>
                    <body>
                        <h2>iframe 1 - 콘텐츠 프레임</h2>
                        <p>iframe 내부 텍스트입니다.</p>
                        <input type='text' id='iframe-input' placeholder='iframe 입력 필드'>
                        <button id='iframe-btn'>iframe 버튼</button>
                        <ul>
                            <li>항목 1</li>
                            <li>항목 2</li>
                            <li>항목 3</li>
                        </ul>
                    </body>
                    </html>
                "
                width="600" height="300"
                style="border: 2px solid blue;">
        </iframe>

        <!-- iframe 2: 중첩 iframe -->
        <iframe name="nested-frame" id="frame2"
                srcdoc="
                    <html>
                    <body>
                        <h2>iframe 2 - 중첩 프레임</h2>
                        <iframe name='inner-frame'
                                srcdoc='<html><body><p>중첩 iframe 내부</p></body></html>'
                                width='400' height='100'>
                        </iframe>
                    </body>
                    </html>
                "
                width="600" height="250"
                style="border: 2px solid red;">
        </iframe>
    </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.new_page()

        # 테스트 HTML 로드
        page.set_content(test_html)
        time.sleep(1)

        print(f"  메인 페이지 타이틀: {page.title()}")
        print(f"  전체 프레임 수: {len(page.frames)}")

        # ─── 방법 1: frame() 메서드 ───
        print("\n  === 방법 1: frame() 메서드 ===")

        # 이름으로 iframe 찾기
        content_frame = page.frame(name="content-frame")
        if content_frame:
            # Frame 객체의 메서드는 Page와 거의 동일합니다
            text = content_frame.inner_text("h2")
            print(f"  frame(name): {text}")

            # iframe 내부 요소의 텍스트 추출
            items = content_frame.eval_on_selector_all(
                "li",
                "elements => elements.map(e => e.innerText)"
            )
            print(f"  리스트 항목: {items}")

            # iframe 내부 입력 필드에 값 입력
            content_frame.fill("#iframe-input", "자동 입력된 텍스트")
            print("  입력 필드에 텍스트 입력 완료")

            # iframe 내부 버튼 클릭
            content_frame.click("#iframe-btn")
            print("  버튼 클릭 완료")

        # URL로 iframe 찾기 (외부 URL일 때 유용)
        # frame = page.frame(url="https://example.com/widget")

        # ─── 방법 2: frame_locator() (권장) ───
        print("\n  === 방법 2: frame_locator() (권장) ===")

        # frame_locator(): CSS 셀렉터로 iframe을 선택하고
        # 내부 요소에 접근하는 Locator를 생성합니다
        fl = page.frame_locator("#frame1")

        # frame_locator 내부에서 locator 사용
        heading = fl.locator("h2")
        print(f"  frame_locator → h2: {heading.inner_text()}")

        input_field = fl.locator("#iframe-input")
        input_field.fill("frame_locator로 입력")
        print("  frame_locator → 입력 필드 값 변경")

        btn = fl.locator("#iframe-btn")
        btn.click()
        print("  frame_locator → 버튼 클릭")

        # 모든 리스트 항목
        li_items = fl.locator("li")
        print(f"  리스트 항목 수: {li_items.count()}")
        for i in range(li_items.count()):
            print(f"    - {li_items.nth(i).inner_text()}")

        # ─── 방법 3: 중첩 iframe 접근 ───
        print("\n  === 방법 3: 중첩 iframe 접근 ===")

        # 중첩 iframe은 frame_locator를 체이닝합니다
        # 메인 → frame2 → inner-frame
        nested_fl = page.frame_locator("#frame2").frame_locator("[name='inner-frame']")

        try:
            nested_text = nested_fl.locator("p").inner_text()
            print(f"  중첩 iframe 텍스트: {nested_text}")
        except Exception as e:
            print(f"  중첩 iframe 접근 오류: {e}")

        # 전체 프레임 트리 출력
        print("\n  === 프레임 트리 ===")
        for frame in page.frames:
            parent = frame.parent_frame
            depth = 0
            temp = frame
            while temp.parent_frame:
                depth += 1
                temp = temp.parent_frame
            indent = "  " * depth
            name = frame.name or "(이름 없음)"
            print(f"    {indent}└ {name}: {frame.url[:60]}")

        browser.close()

    print("\n[iframe 접근] 완료!")


# ============================================================
# CDP를 사용한 iframe 접근
# ============================================================

def cdp_iframe_access_example():
    """
    CDP의 Target 도메인을 사용한 iframe 접근 방법을 설명합니다.

    CDP에서 iframe 접근은 Playwright보다 복잡합니다:
    1. Target.getTargets()로 iframe Target ID 확인
    2. Target.attachToTarget()으로 iframe에 연결
    3. 연결된 세션을 통해 CDP 명령 전송

    또는 Page.getFrameTree()로 프레임 트리를 조회하고
    Runtime.evaluate를 executionContextId와 함께 사용합니다.
    """
    print("[CDP iframe] CDP를 사용한 iframe 접근")
    print("-" * 40)

    # Playwright의 CDP 세션을 사용한 예제
    # (Playwright가 이미 CDP 위에서 동작하므로 CDP 세션에 직접 접근 가능)
    if not PLAYWRIGHT_AVAILABLE:
        print("  playwright를 사용할 수 없습니다")
        _print_cdp_iframe_reference()
        return

    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>CDP iframe 테스트</title></head>
    <body>
        <h1>CDP iframe 테스트</h1>
        <iframe id="test-iframe"
                srcdoc="<html><body><h2>iframe 내용</h2><p>CDP로 접근합니다</p></body></html>"
                width="500" height="200">
        </iframe>
    </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.new_page()
        page.set_content(test_html)
        time.sleep(1)

        # Playwright를 통해 CDP 세션에 접근
        # new_cdp_session(): 이 탭의 CDP 세션을 가져옵니다
        cdp_session = page.context.new_cdp_session(page)

        # 1. Page.getFrameTree: 프레임 트리 조회
        print("\n  [1] Page.getFrameTree (CDP 명령)")
        frame_tree = cdp_session.send("Page.getFrameTree")
        print(f"  프레임 트리: {json.dumps(frame_tree, indent=2, ensure_ascii=False)[:500]}")

        # 프레임 ID 추출
        def extract_frames(node, depth=0):
            """프레임 트리에서 모든 프레임 ID를 추출합니다."""
            frame = node.get("frame", {})
            frame_id = frame.get("id", "")
            frame_url = frame.get("url", "")
            name = frame.get("name", "")
            indent = "  " * depth
            print(f"    {indent}프레임: id={frame_id[:20]}... name='{name}' url={frame_url[:50]}")

            for child in node.get("childFrames", []):
                extract_frames(child, depth + 1)

        extract_frames(frame_tree.get("frameTree", {}))

        # 2. Runtime.evaluate를 특정 프레임 컨텍스트에서 실행
        print("\n  [2] 프레임별 JavaScript 실행 (Playwright 방식)")
        for frame in page.frames:
            name = frame.name or "main"
            try:
                title_or_text = frame.evaluate("document.body ? document.body.innerText.substring(0, 50) : ''")
                print(f"    {name}: {title_or_text}")
            except Exception as e:
                print(f"    {name}: 접근 불가 ({e})")

        cdp_session.detach()
        browser.close()

    # CDP 직접 사용 시 참조 자료 출력
    _print_cdp_iframe_reference()

    print("\n[CDP iframe] 완료!")


def _print_cdp_iframe_reference():
    """CDP로 iframe에 접근하는 방법에 대한 참조 자료를 출력합니다."""
    print("""
  ┌─────────────────────────────────────────────────────────┐
  │ CDP로 iframe 접근하는 방법 (cdp_direct.py와 함께 사용)   │
  ├─────────────────────────────────────────────────────────┤
  │                                                         │
  │ 1. 프레임 트리 조회                                      │
  │    send_command("Page.getFrameTree")                    │
  │    → frameTree.childFrames에서 iframe 정보 확인          │
  │                                                         │
  │ 2. Target으로 iframe 접근 (out-of-process iframe)       │
  │    send_command("Target.getTargets")                    │
  │    → type: "iframe"인 대상 찾기                          │
  │    send_command("Target.attachToTarget",                │
  │                 {"targetId": iframe_target_id,           │
  │                  "flatten": True})                       │
  │    → 반환된 sessionId로 iframe에 명령 전송               │
  │                                                         │
  │ 3. ExecutionContext로 iframe 접근                        │
  │    send_command("Runtime.enable")                       │
  │    → executionContextCreated 이벤트에서                  │
  │      각 프레임의 contextId 확인                          │
  │    send_command("Runtime.evaluate",                     │
  │                 {"expression": "document.title",         │
  │                  "contextId": iframe_context_id})        │
  │                                                         │
  │ 참고: Playwright는 이 복잡한 과정을 frame() /            │
  │ frame_locator()로 추상화합니다.                          │
  └─────────────────────────────────────────────────────────┘
    """)


# ============================================================
# 크로스 오리진 iframe 처리
# ============================================================

def cross_origin_iframe_strategies():
    """
    크로스 오리진 iframe 처리 전략을 설명합니다.

    크로스 오리진(다른 도메인) iframe은 보안 정책으로
    JavaScript에서 직접 접근할 수 없습니다.
    하지만 Playwright/CDP는 브라우저 수준에서 접근 가능합니다.
    """
    print("[크로스 오리진] iframe 처리 전략")
    print("-" * 40)

    strategies = """
    === 크로스 오리진 iframe 접근 전략 ===

    1. Playwright frame() / frame_locator()
       - Playwright는 브라우저 내부 프로토콜(CDP)로 통신하므로
         크로스 오리진 iframe에도 접근 가능
       - 코드:
         frame = page.frame(url="*external-domain.com*")
         frame.locator("#element").click()

    2. CDP Target.attachToTarget
       - 크로스 오리진 iframe은 별도의 Target으로 생성됨
       - Target.getTargets()로 찾아서 attachToTarget()
       - 성능이 중요한 경우 사용

    3. postMessage 활용
       - 메인 페이지와 iframe 간 통신 프로토콜
       - 양쪽 코드 수정 권한이 있을 때 사용
       - window.postMessage() / addEventListener("message")

    4. 프록시 서버 우회
       - 크로스 오리진 요청을 프록시 서버를 통해 동일 오리진으로 변환
       - 네트워크 설정이 필요

    === JavaScript 보안 정책 ===

    동일 오리진 (접근 가능):
      메인: https://app.company.com
      iframe: https://app.company.com/widget

    크로스 오리진 (접근 불가 - JavaScript에서):
      메인: https://app.company.com
      iframe: https://external.service.com/widget

    Playwright/CDP (모두 접근 가능):
      → 브라우저 내부 프로토콜은 오리진 정책 적용 안 됨
    """
    print(strategies)

    # Playwright 크로스 오리진 예제
    if PLAYWRIGHT_AVAILABLE:
        print("\n  [데모] Playwright 크로스 오리진 iframe 접근")

        test_html = """
        <!DOCTYPE html>
        <html>
        <head><title>크로스 오리진 테스트</title></head>
        <body>
            <h1>메인 페이지</h1>
            <iframe id="external"
                    src="https://www.example.com"
                    width="600" height="300">
            </iframe>
        </body>
        </html>
        """

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox"],
            )
            page = browser.new_page()

            try:
                page.set_content(test_html)
                time.sleep(2)

                # 크로스 오리진 iframe에도 접근 가능
                for frame in page.frames:
                    name = frame.name or "main"
                    url = frame.url[:60]
                    try:
                        text = frame.inner_text("body")[:80]
                        print(f"    프레임 '{name}' ({url}): {text}...")
                    except Exception as e:
                        print(f"    프레임 '{name}' ({url}): 접근 오류 - {e}")

            except Exception as e:
                print(f"    데모 오류: {e}")

            browser.close()

    print("\n[크로스 오리진] 완료!")


# ============================================================
# 사내 시스템 iframe 접근 패턴
# ============================================================

def enterprise_iframe_patterns():
    """
    사내 시스템(ERP, 그룹웨어 등)에서 흔히 볼 수 있는
    iframe 패턴과 접근 방법을 설명합니다.
    """
    print("[사내 시스템] iframe 접근 패턴")
    print("-" * 40)

    patterns = """
    === 사내 시스템 일반적인 iframe 구조 ===

    ┌──────────────────────────────────────┐
    │ 상단 메뉴 (header)                    │
    ├──────────┬───────────────────────────┤
    │          │                           │
    │ 좌측     │  콘텐츠 영역              │
    │ 메뉴     │  <iframe name="content">  │
    │ (nav)    │     ┌──────────────┐      │
    │          │     │ 실제 업무    │      │
    │          │     │ 화면이 여기  │      │
    │          │     │ 로딩됨       │      │
    │          │     └──────────────┘      │
    │          │                           │
    └──────────┴───────────────────────────┘

    === 접근 코드 예시 ===

    # 1. 메인 페이지 로그인
    page.goto("https://erp.company.com")
    page.fill("#userid", "user123")
    page.fill("#password", "pass123")
    page.click("#login-btn")
    page.wait_for_load_state("networkidle")

    # 2. 좌측 메뉴에서 원하는 항목 클릭 (메인 프레임)
    page.click("text=인사관리")
    page.click("text=근태조회")

    # 3. 콘텐츠 iframe으로 전환
    content_frame = page.frame(name="content")
    # 또는
    content_frame = page.frame_locator("#content-iframe")

    # 4. iframe 내부 요소 조작
    content_frame.locator("#search-date").fill("2024-01-01")
    content_frame.locator("#search-btn").click()

    # 5. iframe 내부 데이터 추출
    rows = content_frame.locator("table tbody tr")
    for i in range(rows.count()):
        cells = rows.nth(i).locator("td")
        data = [cells.nth(j).inner_text() for j in range(cells.count())]
        print(data)

    === iframe 탐지 팁 ===

    1. DevTools에서 확인:
       - F12 → Elements 탭에서 iframe 태그 검색
       - 또는 Console에서: document.querySelectorAll('iframe')

    2. Playwright에서 확인:
       - page.frames로 모든 프레임 목록 확인
       - 각 프레임의 name, url 속성 확인

    3. 프레임이 동적으로 생성되는 경우:
       - page.wait_for_selector("iframe") 후 접근
       - 또는 page.wait_for_event("frameattached")

    === 주의사항 ===

    - iframe 로딩은 비동기이므로 wait_for_load_state() 필요
    - 메뉴 클릭 후 iframe src가 변경되면 새 frame 객체 필요
    - 일부 사내 시스템은 frameset (레거시)을 사용하기도 함
    """
    print(patterns)


# ============================================================
# Shadow DOM 처리 (보너스)
# ============================================================

def shadow_dom_handling():
    """
    Shadow DOM 처리 방법을 설명합니다.

    Shadow DOM은 웹 컴포넌트의 캡슐화된 DOM 트리입니다.
    일반 CSS 셀렉터로 내부 요소에 접근할 수 없습니다.
    Playwright는 Shadow DOM 자동 관통(pierce)을 지원합니다.
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[Shadow DOM] playwright를 사용할 수 없습니다")
        _print_shadow_dom_reference()
        return

    print("[Shadow DOM] Shadow DOM 처리 예제")
    print("-" * 40)

    # Shadow DOM이 포함된 테스트 페이지
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Shadow DOM 테스트</title></head>
    <body>
        <h1>Shadow DOM 테스트</h1>

        <!-- 커스텀 엘리먼트 정의 -->
        <div id="host"></div>

        <script>
            // Shadow DOM 생성
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <style>
                    .shadow-title { color: blue; }
                    .shadow-content { padding: 10px; }
                </style>
                <div class="shadow-container">
                    <h2 class="shadow-title">Shadow DOM 내부 제목</h2>
                    <p class="shadow-content">Shadow DOM 내부 콘텐츠입니다.</p>
                    <input type="text" id="shadow-input" placeholder="Shadow 입력">
                    <button id="shadow-btn">Shadow 버튼</button>
                </div>
            `;
        </script>
    </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.new_page()
        page.set_content(test_html)
        time.sleep(1)

        # Playwright는 기본적으로 Shadow DOM을 관통(pierce)합니다
        # 일반 CSS 셀렉터로 Shadow DOM 내부 요소에 접근 가능

        # 1. Shadow DOM 내부 텍스트 추출
        print("\n  [1] Shadow DOM 내부 텍스트")
        try:
            # Playwright의 locator는 기본적으로 Shadow DOM 관통
            shadow_title = page.locator(".shadow-title")
            if shadow_title.count() > 0:
                print(f"  Shadow 제목: {shadow_title.inner_text()}")

            shadow_content = page.locator(".shadow-content")
            if shadow_content.count() > 0:
                print(f"  Shadow 콘텐츠: {shadow_content.inner_text()}")
        except Exception as e:
            print(f"  오류: {e}")

        # 2. Shadow DOM 내부 입력
        print("\n  [2] Shadow DOM 내부 입력")
        try:
            page.locator("#shadow-input").fill("Shadow DOM에 입력!")
            print("  입력 완료")
        except Exception as e:
            print(f"  오류: {e}")

        # 3. Shadow DOM 내부 클릭
        print("\n  [3] Shadow DOM 내부 클릭")
        try:
            page.locator("#shadow-btn").click()
            print("  클릭 완료")
        except Exception as e:
            print(f"  오류: {e}")

        # 4. JavaScript로 Shadow DOM 접근 (수동)
        print("\n  [4] JavaScript로 Shadow DOM 접근")
        shadow_text = page.evaluate("""
            () => {
                const host = document.getElementById('host');
                const shadow = host.shadowRoot;
                if (shadow) {
                    return {
                        title: shadow.querySelector('.shadow-title')?.innerText || '',
                        content: shadow.querySelector('.shadow-content')?.innerText || '',
                        inputValue: shadow.querySelector('#shadow-input')?.value || '',
                    };
                }
                return null;
            }
        """)
        if shadow_text:
            print(f"  JS 접근 결과: {json.dumps(shadow_text, ensure_ascii=False)}")

        browser.close()

    _print_shadow_dom_reference()
    print("\n[Shadow DOM] 완료!")


def _print_shadow_dom_reference():
    """Shadow DOM 참조 자료를 출력합니다."""
    print("""
    ┌─────────────────────────────────────────────────┐
    │ Shadow DOM 참조                                  │
    ├─────────────────────────────────────────────────┤
    │                                                  │
    │ Shadow DOM 구조:                                 │
    │   <div id="host">                               │
    │     #shadow-root (open)                          │
    │       <h2>Shadow 내부</h2>                       │
    │       <p>캡슐화된 DOM</p>                        │
    │                                                  │
    │ Playwright (자동 관통):                           │
    │   page.locator("h2")  → Shadow 내부도 검색       │
    │   page.locator("#shadow-input").fill("...")      │
    │                                                  │
    │ CDP (수동 접근):                                  │
    │   DOM.describeNode({nodeId, pierce: true})       │
    │   Runtime.evaluate에서 element.shadowRoot 사용   │
    │                                                  │
    │ JavaScript (수동 접근):                           │
    │   host.shadowRoot.querySelector("h2")            │
    │   (mode: 'open'인 경우만 가능)                    │
    │                                                  │
    │ 주의:                                            │
    │   - mode: 'closed': JS에서 shadowRoot 접근 불가   │
    │   - Playwright/CDP는 closed도 접근 가능           │
    │   - Shadow DOM + iframe 조합 시 복잡도 증가       │
    └─────────────────────────────────────────────────┘
    """)


# ============================================================
# 종합 실습: iframe 내부 테이블 데이터 추출
# ============================================================

def extract_iframe_table_data():
    """
    iframe 내부의 테이블 데이터를 추출하는 종합 예제입니다.

    사내 시스템에서 가장 흔한 패턴:
    메인 페이지 → iframe → 테이블 → 데이터 추출
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("[테이블 추출] playwright를 사용할 수 없습니다")
        return []

    print("[테이블 추출] iframe 내부 테이블 데이터 추출")
    print("-" * 40)

    # 테이블이 포함된 iframe 테스트 페이지
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>사내 시스템 (시뮬레이션)</title></head>
    <body>
        <h1>인사관리 시스템</h1>
        <nav>메뉴: 근태조회 | 급여조회 | 인사정보</nav>
        <hr>
        <iframe name="content" id="content-frame"
                srcdoc="
                    <html>
                    <head>
                        <style>
                            table { border-collapse: collapse; width: 100%; }
                            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                            th { background-color: #4CAF50; color: white; }
                            tr:nth-child(even) { background-color: #f2f2f2; }
                        </style>
                    </head>
                    <body>
                        <h2>근태 조회 결과</h2>
                        <p>조회 기간: 2024-01-01 ~ 2024-01-31</p>
                        <table id='attendance-table'>
                            <thead>
                                <tr>
                                    <th>사번</th>
                                    <th>이름</th>
                                    <th>부서</th>
                                    <th>출근일수</th>
                                    <th>지각</th>
                                    <th>연차사용</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>EMP001</td><td>김철수</td><td>개발팀</td><td>22</td><td>1</td><td>2</td></tr>
                                <tr><td>EMP002</td><td>이영희</td><td>기획팀</td><td>20</td><td>0</td><td>4</td></tr>
                                <tr><td>EMP003</td><td>박지민</td><td>데이터팀</td><td>21</td><td>2</td><td>3</td></tr>
                                <tr><td>EMP004</td><td>정수연</td><td>AI팀</td><td>22</td><td>0</td><td>2</td></tr>
                                <tr><td>EMP005</td><td>최동훈</td><td>인프라팀</td><td>19</td><td>3</td><td>5</td></tr>
                            </tbody>
                        </table>
                    </body>
                    </html>
                "
                width="100%" height="400">
        </iframe>
    </body>
    </html>
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        page = browser.new_page()
        page.set_content(test_html)
        time.sleep(1)

        # iframe 접근
        content_frame = page.frame(name="content")
        if not content_frame:
            print("  content iframe을 찾을 수 없습니다")
            browser.close()
            return []

        print(f"  iframe 접근 성공: {content_frame.name}")

        # 테이블 데이터 추출 (JavaScript 실행)
        table_data = content_frame.evaluate("""
            () => {
                const table = document.getElementById('attendance-table');
                if (!table) return [];

                const rows = table.querySelectorAll('tr');
                const data = [];

                rows.forEach((row, index) => {
                    const cells = row.querySelectorAll('th, td');
                    const rowData = Array.from(cells).map(cell => cell.innerText.trim());
                    data.push({
                        rowIndex: index,
                        isHeader: index === 0,
                        cells: rowData,
                    });
                });

                return data;
            }
        """)

        # 결과 출력
        print(f"\n  테이블 데이터 ({len(table_data)}행):")
        print("  " + "-" * 70)

        headers = []
        records = []

        for row in table_data:
            if row["isHeader"]:
                headers = row["cells"]
                print(f"  | {'  | '.join(f'{h:>8}' for h in headers)} |")
                print("  " + "-" * 70)
            else:
                cells = row["cells"]
                print(f"  | {'  | '.join(f'{c:>8}' for c in cells)} |")
                # 딕셔너리로 변환
                record = dict(zip(headers, cells))
                records.append(record)

        print("  " + "-" * 70)
        print(f"\n  추출된 레코드 수: {len(records)}")

        # JSON 형태로 출력
        print("\n  JSON 형태:")
        for record in records:
            print(f"    {json.dumps(record, ensure_ascii=False)}")

        browser.close()

    print("\n[테이블 추출] 완료!")
    return records


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("iframe 제어 예제 - Playwright & CDP")
    print("=" * 60)

    # 1. iframe 접근 패턴 (사내 시스템)
    print("\n[1] 사내 시스템 iframe 패턴")
    enterprise_iframe_patterns()

    # 2. Playwright iframe 접근
    print("\n\n[2] Playwright iframe 접근")
    playwright_iframe_access()

    # 3. CDP iframe 접근
    print("\n\n[3] CDP iframe 접근")
    cdp_iframe_access_example()

    # 4. 크로스 오리진 iframe 전략
    print("\n\n[4] 크로스 오리진 iframe 전략")
    cross_origin_iframe_strategies()

    # 5. Shadow DOM 처리
    print("\n\n[5] Shadow DOM 처리 (보너스)")
    shadow_dom_handling()

    # 6. 종합 실습: iframe 테이블 데이터 추출
    print("\n\n[6] 종합 실습: iframe 테이블 데이터 추출")
    extract_iframe_table_data()

    # 7. 실제 사이트에서 iframe 탐지
    print("\n\n[7] 실제 사이트 iframe 탐지")
    detect_iframes("https://www.example.com")

    print("\n" + "=" * 60)
    print("모든 iframe 제어 예제 완료!")
    print("=" * 60)
