# 실습: Office 자동화 Agent

## 목표
데이터를 받아 Excel 파일로 생성하고 관리하는 Agent를 구현합니다.

---

## 사전 준비

```bash
# openpyxl 설치 (Excel 파일 처리)
pip install openpyxl
```

---

## 요구사항

### 필수

1. **Excel 파일 생성**
   - 사용자가 자연어로 설명한 데이터를 JSON으로 구조화
   - openpyxl로 Excel 파일 생성
   - 헤더 스타일 적용 (볼드, 배경색)
   - 열 너비 자동 조정

2. **Excel 파일 읽기**
   - 기존 Excel 파일의 내용을 읽어 사용자에게 전달
   - 시트 목록, 행/열 수, 데이터 미리보기

3. **Agent Loop 통합**
   - Office 도구를 Agent Loop에 등록
   - 자연어 명령 → 도구 호출 → 결과 반환

### 보너스

4. **차트 추가**
   - 막대(bar), 선(line), 원형(pie) 차트 지원
   - 데이터 범위를 자동으로 감지

5. **서식 적용**
   - 통화 형식 (예: ₩1,000,000)
   - 퍼센트 형식 (예: 95.5%)
   - 조건부 서식 (예: 목표 달성 시 녹색)

---

## 테스트 시나리오

### 시나리오 1: 기본 Excel 생성
```
사용자: 다음 직원 정보를 Excel로 만들어줘.
        홍길동, 개발팀, 연봉 5000만원
        김철수, 마케팅팀, 연봉 4500만원
        이영희, 디자인팀, 연봉 4800만원

예상 동작:
1. LLM이 데이터를 JSON으로 구조화
2. create_excel() 호출
3. 결과 파일 경로 반환
```

### 시나리오 2: Excel 읽기 + 수정
```
사용자: output.xlsx 파일을 읽어줘
사용자: 홍길동의 연봉을 5500만원으로 수정해줘

예상 동작:
1. read_excel() → 현재 내용 파악
2. update_excel_cell() → 셀 수정
```

### 시나리오 3: 차트 생성
```
사용자: 월별 매출 데이터를 Excel로 만들고 막대 차트도 추가해줘
        1월: 1000, 2월: 1200, 3월: 1500, 4월: 1100

예상 동작:
1. create_excel() → 데이터 파일 생성
2. create_excel_chart() → 차트 추가
```

---

## 구현 힌트

### JSON 데이터 형식
```python
# 딕셔너리 배열 (추천)
data = [
    {"이름": "홍길동", "부서": "개발팀", "연봉": 5000},
    {"이름": "김철수", "부서": "마케팅팀", "연봉": 4500},
]

# 2차원 배열
data = [
    ["이름", "부서", "연봉"],
    ["홍길동", "개발팀", 5000],
    ["김철수", "마케팅팀", 4500],
]
```

### 차트 추가
```python
from openpyxl.chart import BarChart, Reference

chart = BarChart()
data = Reference(ws, min_col=2, min_row=1, max_row=ws.max_row)
categories = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)
chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)
ws.add_chart(chart, "E1")
```

---

## 참고 파일

- `office_tools.py`: Excel 도구 구현 (생성, 읽기, 수정, 차트)
- `app_control_tools.py`: Windows 앱 제어 도구 (pywinauto, CDP)
- `office_agent.py`: Agent 통합 예시
- openpyxl 문서: https://openpyxl.readthedocs.io/
