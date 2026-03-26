# 종합 실습: 검색 → 정리 → 저장 Agent 만들기

## 목표

브라우저로 웹 검색을 수행하고, 검색 결과를 정리하여 Excel 파일로 저장하는 **종합 Agent**를 구현합니다.

이 실습은 Day 2에서 배운 모든 내용을 통합합니다:
- Session 1: Agent Loop
- Session 2: CLI 도구
- Session 3: 브라우저 도구
- Session 4: Office 도구
- Session 5: 아키텍처 패턴

---

## 사전 준비

```bash
# 필수 패키지 설치
pip install requests playwright openpyxl

# 브라우저 설치
playwright install chromium
```

---

## 실습 파일

| 파일 | 설명 |
|------|------|
| `mini_agent_template.py` | 시작 코드 (TODO 구현 필요) |
| `mini_agent_solution.py` | 완전한 솔루션 (참고용) |

---

## Step-by-Step 가이드

### Step 1: 템플릿 파일 복사

```bash
cp mini_agent_template.py my_agent.py
```

### Step 2: search_google 함수 구현

`my_agent.py`에서 `search_google` 함수의 TODO를 구현합니다.

**목표**: 구글에서 검색하고 결과(제목, URL, 설명)를 문자열로 반환

**구현 순서**:
1. `BrowserManager.get_page()`로 브라우저 페이지 획득
2. `page.goto(f"https://www.google.com/search?q={query}&hl=ko")` 로 이동
3. `page.evaluate(javascript)` 로 검색 결과 추출
4. 결과를 읽기 좋은 문자열로 정리

**힌트**:
```python
# 검색 결과 추출 JavaScript
results = page.evaluate("""
    () => {
        const items = document.querySelectorAll('div.g');
        return Array.from(items).slice(0, 10).map(item => {
            const titleEl = item.querySelector('h3');
            const linkEl = item.querySelector('a');
            return {
                title: titleEl ? titleEl.innerText : '',
                url: linkEl ? linkEl.href : ''
            };
        }).filter(r => r.title && r.url);
    }
""")
```

### Step 3: get_page_content 함수 구현

**목표**: URL로 이동하여 페이지의 텍스트 내용을 추출

**구현 순서**:
1. `page.goto(url)` 로 이동
2. `page.inner_text("body")` 로 텍스트 추출
3. 연속 줄바꿈/공백 정리 (`re.sub`)
4. 최대 길이 제한 (8000자 권장)

### Step 4: extract_and_format 함수 구현

**목표**: 원시 텍스트에서 주제 관련 정보를 추출

**간단한 구현**:
- 키워드 기반 문장 필터링
- 중복 제거
- 번호 매기기

**고급 구현** (보너스):
- LLM을 한 번 더 호출하여 정보 추출 (sub-agent)
- 정규표현식으로 패턴 매칭

### Step 5: save_to_excel 함수 구현

**목표**: JSON 데이터를 Excel 파일로 저장

**구현 순서**:
1. `json.loads(data)` 로 파싱
2. `openpyxl.Workbook()` 생성
3. 헤더 행 추가 + 스타일 적용
4. 데이터 행 추가
5. 열 너비 자동 조정
6. 파일 저장

**힌트**:
```python
wb = openpyxl.Workbook()
ws = wb.active
headers = list(parsed_data[0].keys())
ws.append(headers)  # 헤더 행
for row in parsed_data:
    ws.append([row.get(h, "") for h in headers])
wb.save(abs_path)
```

### Step 6: 테스트

```bash
python my_agent.py
```

테스트 질문:
- "Python 3.12 새 기능을 검색하고 Excel로 저장해줘"
- "2024년 AI 트렌드를 검색하고 결과를 정리해서 저장해줘"

---

## 요구사항 체크리스트

### 필수 (기본 점수)
- [ ] search_google: 구글 검색 후 결과 반환
- [ ] get_page_content: 웹 페이지 텍스트 추출
- [ ] save_to_excel: JSON 데이터를 Excel로 저장 (헤더 포함)
- [ ] Agent Loop가 정상 동작 (도구 호출 → 실행 → 결과 반환 → 반복)
- [ ] 전체 플로우 동작: 검색 → 정보 수집 → Excel 저장

### 보너스
- [ ] Excel 스타일링 (헤더 배경색, 테두리, 열 너비 조정)
- [ ] extract_and_format: 텍스트에서 관련 정보 추출
- [ ] 에러 처리 (네트워크 오류, 파싱 오류 등)
- [ ] 대화형 인터페이스 (여러 번 검색 가능)
- [ ] 행 고정, 자동 필터 등 Excel 고급 기능

---

## 평가 기준

| 항목 | 배점 |
|------|------|
| search_google 구현 | 20% |
| get_page_content 구현 | 15% |
| save_to_excel 구현 | 20% |
| 전체 플로우 동작 (검색 → 저장) | 25% |
| 에러 처리 및 코드 품질 | 10% |
| Excel 스타일링 및 추가 기능 | 10% |

---

## 예상 출력

```
사용자: Python 3.12 새 기능을 검색하고 Excel로 저장해줘

--- 반복 #1 ---
  [도구] search_google({"query": "Python 3.12 새 기능"})
  [결과] === 구글 검색 결과: 'Python 3.12 새 기능' (8건) ===  1. Python 3.12 ...

--- 반복 #2 ---
  [도구] get_page_content({"url": "https://docs.python.org/..."})
  [결과] === 페이지 내용 === URL: https://docs.python.org/...

--- 반복 #3 ---
  [도구] save_to_excel({"path": "python312_features.xlsx", "data": "[{...}]"})
  [결과] Excel 파일 저장 완료! 경로: /home/user/python312_features.xlsx ...

검색 결과를 python312_features.xlsx에 저장했습니다.
총 8건의 결과가 포함되어 있으며, 각 항목에는 제목, URL, 요약이 포함됩니다.
```

---

## 트러블슈팅

### "playwright가 설치되지 않았습니다"
```bash
pip install playwright
playwright install chromium
```

### "openpyxl이 설치되지 않았습니다"
```bash
pip install openpyxl
```

### "구글 검색 결과를 추출하지 못했습니다"
- 구글이 봇을 차단했을 수 있습니다
- `headless=False`로 변경하여 브라우저 화면을 확인하세요
- 다른 검색 엔진(Bing, DuckDuckGo)을 시도해보세요

### "API 호출이 실패합니다"
- `.env` 파일의 `LLM_GATEWAY_URL`과 `LLM_GATEWAY_API_KEY`를 확인하세요
- 네트워크 연결 및 프록시 설정을 확인하세요

---

## 참고 자료

- `mini_agent_solution.py`: 완전한 솔루션 코드
- `../01_agent_loop/basic_agent.py`: Agent Loop 기본 구현
- `../03_tool_browser/browser_tools.py`: 브라우저 도구 상세 구현
- `../04_tool_office/office_tools.py`: Excel 도구 상세 구현
- `../05_architecture/tool_registry.py`: Tool Registry 패턴
