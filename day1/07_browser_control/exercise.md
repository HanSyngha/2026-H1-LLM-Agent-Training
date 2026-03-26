# 브라우저 자동화 실습

## 학습 목표
- CDP, COM, Playwright, iframe 4가지 브라우저 제어 기술을 이해합니다
- 실무에서 사용할 수 있는 브라우저 자동화 스크립트를 작성합니다
- iframe 내부 요소 접근 패턴을 익힙니다

---

## 실습 1: Playwright 기본 자동화

**목표:** Playwright로 웹페이지를 자동화합니다.

### 요구사항
- [ ] 네이버(https://www.naver.com)에 접속합니다
- [ ] 검색어를 입력하고 검색을 실행합니다
- [ ] 검색 결과에서 상위 5개 링크의 제목과 URL을 추출합니다
- [ ] 결과를 JSON 파일로 저장합니다
- [ ] 검색 결과 페이지의 스크린샷을 저장합니다

### 힌트
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 1. 네이버 접속
    page.goto("https://www.naver.com")

    # 2. 검색어 입력 (셀렉터 확인 필요)
    page.fill("#query", "검색어")
    page.keyboard.press("Enter")

    # 3. 결과 추출 (page.evaluate 사용)
    results = page.evaluate("""...""")

    # 4. 스크린샷
    page.screenshot(path="result.png")

    browser.close()
```

### 체크리스트
- [ ] playwright 설치 확인: `pip install playwright && playwright install chromium`
- [ ] headless 모드에서 정상 동작하는지 확인
- [ ] 네트워크 오류 시 예외 처리가 되는지 확인
- [ ] 추출 결과가 JSON으로 올바르게 저장되는지 확인

---

## 실습 2: CDP 직접 연결

**목표:** Chrome DevTools Protocol을 직접 사용하여 브라우저를 제어합니다.

### 사전 준비
```bash
# Chrome을 CDP 모드로 실행 (Windows)
chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug

# WSL에서 Windows Chrome 실행
/mnt/c/Program\ Files/Google/Chrome/Application/chrome.exe \
    --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

### 요구사항
- [ ] `http://localhost:9222/json/list`로 열린 탭 목록을 조회합니다
- [ ] WebSocket으로 첫 번째 탭에 연결합니다
- [ ] `Page.navigate` 명령으로 원하는 URL로 이동합니다
- [ ] `Runtime.evaluate`로 페이지 타이틀을 가져옵니다
- [ ] `Page.captureScreenshot`으로 스크린샷을 촬영합니다

### 힌트
```python
import requests
import websocket
import json

# 1. 탭 목록 조회
tabs = requests.get("http://localhost:9222/json/list").json()
ws_url = tabs[0]["webSocketDebuggerUrl"]

# 2. WebSocket 연결
ws = websocket.create_connection(ws_url)

# 3. CDP 명령 전송
ws.send(json.dumps({
    "id": 1,
    "method": "Page.navigate",
    "params": {"url": "https://www.example.com"}
}))
result = json.loads(ws.recv())
```

### 체크리스트
- [ ] Chrome이 `--remote-debugging-port`로 실행되고 있는지 확인
- [ ] `websocket-client` 패키지 설치: `pip install websocket-client`
- [ ] CDP 응답에서 에러 메시지 처리
- [ ] WebSocket 연결 종료 처리

---

## 실습 3: iframe 내부 데이터 추출

**목표:** iframe이 포함된 페이지에서 내부 데이터를 추출합니다.

### 요구사항
- [ ] iframe이 포함된 테스트 페이지를 로드합니다
- [ ] `page.frames`로 모든 프레임 목록을 확인합니다
- [ ] `frame_locator()` 또는 `frame()`으로 iframe에 접근합니다
- [ ] iframe 내부의 테이블 데이터를 추출합니다
- [ ] 추출된 데이터를 딕셔너리 리스트로 변환합니다

### 힌트
```python
# iframe 접근 방법 1: frame()
content_frame = page.frame(name="content")
text = content_frame.inner_text("h2")

# iframe 접근 방법 2: frame_locator() (권장)
fl = page.frame_locator("#content-iframe")
fl.locator("#element").click()

# 중첩 iframe
nested = page.frame_locator("#outer").frame_locator("#inner")

# 테이블 데이터 추출 (JavaScript)
data = content_frame.evaluate("""
    () => {
        const rows = document.querySelectorAll('table tr');
        return Array.from(rows).map(row => {
            const cells = row.querySelectorAll('td, th');
            return Array.from(cells).map(c => c.innerText.trim());
        });
    }
""")
```

### 체크리스트
- [ ] iframe 로딩 대기 처리 (wait_for_load_state)
- [ ] 크로스 오리진 iframe의 경우 frame(url=...) 사용
- [ ] 동적으로 생성되는 iframe 처리
- [ ] 테이블 헤더와 데이터를 분리하여 딕셔너리로 변환

---

## 실습 4: (Windows 전용) COM 자동화

**목표:** Windows COM을 사용하여 Excel을 자동으로 제어합니다.

### 요구사항
- [ ] Excel을 COM으로 실행합니다
- [ ] 새 워크북을 생성하고 데이터를 입력합니다
- [ ] 셀 서식(글꼴, 색상, 숫자 포맷)을 설정합니다
- [ ] SUM, AVERAGE 등 함수를 추가합니다
- [ ] 파일을 저장하고 Excel을 종료합니다

### 힌트
```python
import win32com.client
import pythoncom

pythoncom.CoInitialize()
excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = True

wb = excel.Workbooks.Add()
ws = wb.ActiveSheet

# 셀 값 입력
ws.Cells(1, 1).Value = "이름"
ws.Range("A1").Font.Bold = True

# 수식 입력
ws.Cells(10, 2).Formula = "=SUM(B2:B9)"

# 저장
wb.SaveAs(r"C:\Users\사용자\Desktop\test.xlsx")

excel.Quit()
pythoncom.CoUninitialize()
```

### 체크리스트
- [ ] Windows 환경에서 실행하는지 확인
- [ ] `pywin32` 설치: `pip install pywin32`
- [ ] Excel이 설치되어 있는지 확인
- [ ] pythoncom.CoInitialize() / CoUninitialize() 호출
- [ ] 예외 발생 시 Excel 프로세스가 정리되는지 확인

---

## 심화 과제

### 과제 A: 브라우저 에이전트 만들기
`browser_agent.py`를 참고하여, 자연어 명령으로 웹을 탐색하는 Agent를 만드세요.
- 사용자: "네이버에서 오늘 뉴스 헤드라인 3개 가져와"
- Agent: navigate → get_page_content → 분석 → 응답

### 과제 B: 데이터 수집 파이프라인
Playwright로 특정 사이트에서 주기적으로 데이터를 수집하는 스크립트를 작성하세요.
- 대상 사이트 선정 (뉴스, 주식, 날씨 등)
- 데이터 추출 및 CSV/JSON 저장
- 오류 처리 및 재시도 로직

### 과제 C: CDP 네트워크 모니터링
CDP의 Network 도메인을 사용하여 웹페이지의 모든 네트워크 요청을 기록하세요.
- 요청 URL, 메서드, 상태 코드
- 응답 크기, 응답 시간
- 리소스 유형별 분류 (JS, CSS, 이미지 등)

---

## 참고 자료

| 자료 | URL |
|------|-----|
| Playwright 공식 문서 | https://playwright.dev/python/ |
| CDP 프로토콜 문서 | https://chromedevtools.github.io/devtools-protocol/ |
| pywin32 문서 | https://mhammond.github.io/pywin32/ |
| pywinauto 문서 | https://pywinauto.readthedocs.io/ |
| Browser Use 프로젝트 | https://github.com/browser-use/browser-use |

---

## 환경 설정 요약

```bash
# 필수 패키지
pip install playwright websocket-client requests

# Playwright 브라우저 설치
playwright install chromium

# Windows COM (Windows에서만)
pip install pywin32 pywinauto

# Excel 대안 (크로스 플랫폼)
pip install openpyxl
```
