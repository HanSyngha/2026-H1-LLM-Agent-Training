"""
프롬프트 엔지니어링 과제 — 금융 기사 실적 추출

10개 금융 기사에서 10개 항목을 정확히 추출하는 프롬프트를 작성.
Exact match로 검증 — 모든 값이 정확히 일치해야 PASS.
"""

import json
import requests
import os
from threading import Lock

# ============================================
# 10개 금융 기사 테스트 케이스
# ============================================
FIELDS = ["company", "ticker", "revenue", "operating_profit", "net_income",
          "stock_price", "price_change_pct", "consensus_op", "eps", "target_price"]

FIELD_DESC = {
    "company": "회사명 (str)",
    "ticker": "종목코드 (str)",
    "revenue": "매출액 (억원, int)",
    "operating_profit": "영업이익 (억원, int)",
    "net_income": "당기순이익 (억원, int)",
    "stock_price": "현재주가 (원, int)",
    "price_change_pct": "등락률 (%, float, 하락이면 음수)",
    "consensus_op": "컨센서스 영업이익 (억원, int)",
    "eps": "주당순이익 (원, int)",
    "target_price": "목표주가 (원, int)",
}

PROMPT_TEST_CASES = [
    {
        "id": 1, "title": "삼성전자 1Q",
        "input": "삼성전자(005930)는 2026년 1분기 매출 79조 1,000억원, 영업이익 9조 6,400억원, 당기순이익 7조 3,200억원을 기록했다. 전년 동기 대비 매출은 12.3% 증가했다. 현재 주가는 82,400원으로 전일 대비 2.1% 상승했다. 증권가 컨센서스 영업이익 예상치는 9조 2,000억원이었으며, 주당순이익(EPS)은 5,340원이다. 목표주가 평균은 95,000원이다.",
        "expected": {"company": "삼성전자", "ticker": "005930", "revenue": 791000, "operating_profit": 96400, "net_income": 73200, "stock_price": 82400, "price_change_pct": 2.1, "consensus_op": 92000, "eps": 5340, "target_price": 95000},
    },
    {
        "id": 2, "title": "SK하이닉스 HBM",
        "input": "SK하이닉스(000660)의 2026년 1분기 실적이 발표됐다. 매출 18조 7,600억원, 영업이익 7조 4,300억원, 당기순이익 5조 8,100억원을 달성했다. 전년 동기 대비 매출이 45.7% 급증했다. 주가는 234,500원으로 1.8% 하락했다. 시장 예상 영업이익은 7조 1,000억원이었다. EPS는 8,120원, 목표주가 합의는 280,000원이다.",
        "expected": {"company": "SK하이닉스", "ticker": "000660", "revenue": 187600, "operating_profit": 74300, "net_income": 58100, "stock_price": 234500, "price_change_pct": -1.8, "consensus_op": 71000, "eps": 8120, "target_price": 280000},
    },
    {
        "id": 3, "title": "현대자동차",
        "input": "현대자동차(005380)가 1분기 매출 43조 2,800억원, 영업이익 4조 1,500억원, 당기순이익 3조 2,700억원을 공시했다. 전년 대비 8.9% 성장이다. 현재 주가 267,000원, 전일 대비 0.7% 상승. 컨센서스 영업이익은 3조 9,000억원으로 어닝 서프라이즈다. EPS 11,450원, 목표주가 310,000원.",
        "expected": {"company": "현대자동차", "ticker": "005380", "revenue": 432800, "operating_profit": 41500, "net_income": 32700, "stock_price": 267000, "price_change_pct": 0.7, "consensus_op": 39000, "eps": 11450, "target_price": 310000},
    },
    {
        "id": 4, "title": "NAVER 광고",
        "input": "NAVER(035420)는 1분기 매출 2조 8,340억원, 영업이익 4,870억원, 당기순이익 3,620억원을 기록했다. 전년 동기 대비 15.2% 매출 성장을 달성했다. 주가는 218,000원이며 3.4% 상승했다. 증권가 영업이익 예상치는 4,500억원이었다. 주당순이익 7,890원, 목표주가 260,000원.",
        "expected": {"company": "NAVER", "ticker": "035420", "revenue": 28340, "operating_profit": 4870, "net_income": 3620, "stock_price": 218000, "price_change_pct": 3.4, "consensus_op": 4500, "eps": 7890, "target_price": 260000},
    },
    {
        "id": 5, "title": "카카오 콘텐츠",
        "input": "카카오(035720)의 1분기 실적은 매출 2조 1,450억원, 영업이익 1,230억원, 당기순이익 890억원이었다. 전년 대비 매출은 3.1% 감소했다. 주가 46,750원으로 4.2% 하락. 시장 예상 영업이익은 1,500억원이었으나 하회했다. EPS 2,010원, 목표주가 55,000원.",
        "expected": {"company": "카카오", "ticker": "035720", "revenue": 21450, "operating_profit": 1230, "net_income": 890, "stock_price": 46750, "price_change_pct": -4.2, "consensus_op": 1500, "eps": 2010, "target_price": 55000},
    },
    {
        "id": 6, "title": "LG에너지솔루션",
        "input": "LG에너지솔루션(373220)이 1분기 매출 8조 9,200억원, 영업이익 5,340억원, 당기순이익 3,980억원을 발표했다. 전년 동기 대비 22.6% 성장했다. 현재 주가 392,000원, 전일 대비 1.5% 상승. 컨센서스 영업이익은 4,800억원. EPS 17,020원, 목표주가 450,000원.",
        "expected": {"company": "LG에너지솔루션", "ticker": "373220", "revenue": 89200, "operating_profit": 5340, "net_income": 3980, "stock_price": 392000, "price_change_pct": 1.5, "consensus_op": 4800, "eps": 17020, "target_price": 450000},
    },
    {
        "id": 7, "title": "포스코홀딩스",
        "input": "포스코홀딩스(005490) 1분기 매출 18조 4,500억원, 영업이익 1조 2,800억원, 당기순이익 8,940억원 달성. 전년 대비 6.7% 증가했다. 주가 318,500원, 0.3% 하락. 시장 영업이익 예상 1조 1,500억원 대비 상회. EPS 11,560원, 목표주가 380,000원.",
        "expected": {"company": "포스코홀딩스", "ticker": "005490", "revenue": 184500, "operating_profit": 12800, "net_income": 8940, "stock_price": 318500, "price_change_pct": -0.3, "consensus_op": 11500, "eps": 11560, "target_price": 380000},
    },
    {
        "id": 8, "title": "셀트리온 바이오",
        "input": "셀트리온(068270) 1분기 매출 1조 2,340억원, 영업이익 3,450억원, 당기순이익 2,780억원을 기록했다. 전년 대비 31.4% 매출 증가. 주가 198,200원으로 2.8% 상승. 증권가 영업이익 컨센서스 3,200억원. 주당순이익 4,230원, 목표주가 240,000원.",
        "expected": {"company": "셀트리온", "ticker": "068270", "revenue": 12340, "operating_profit": 3450, "net_income": 2780, "stock_price": 198200, "price_change_pct": 2.8, "consensus_op": 3200, "eps": 4230, "target_price": 240000},
    },
    {
        "id": 9, "title": "한화에어로스페이스",
        "input": "한화에어로스페이스(012450)가 1분기 매출 4조 5,670억원, 영업이익 6,120억원, 당기순이익 4,530억원을 공시했다. 전년 동기 대비 매출 38.9% 급증. 현재 주가 412,000원, 5.1% 급등. 시장 예상 영업이익 5,400억원 대비 큰 폭 상회. EPS 9,870원, 목표주가 480,000원.",
        "expected": {"company": "한화에어로스페이스", "ticker": "012450", "revenue": 45670, "operating_profit": 6120, "net_income": 4530, "stock_price": 412000, "price_change_pct": 5.1, "consensus_op": 5400, "eps": 9870, "target_price": 480000},
    },
    {
        "id": 10, "title": "기아 전기차",
        "input": "기아(000270) 1분기 매출 27조 8,900억원, 영업이익 3조 1,200억원, 당기순이익 2조 4,600억원 기록. 전년 대비 11.5% 성장. 주가 128,400원, 1.2% 상승. 컨센서스 영업이익 2조 8,500억원으로 서프라이즈. EPS 6,430원, 목표주가 150,000원.",
        "expected": {"company": "기아", "ticker": "000270", "revenue": 278900, "operating_profit": 31200, "net_income": 24600, "stock_price": 128400, "price_change_pct": 1.2, "consensus_op": 28500, "eps": 6430, "target_price": 150000},
    },
]


# ============================================
# LLM 호출 (동시성 고려 — 상태 없음, thread-safe)
# ============================================
async def call_llm(prompt: str, input_text: str, expected_keys: list, llm_config: dict) -> dict:
    """수강생 프롬프트 + 입력 데이터로 LLM 호출 → JSON 파싱"""
    import asyncio, functools

    if not llm_config.get("base_url"):
        return {"error": "LLM이 설정되지 않았습니다."}

    try:
        _call = functools.partial(
            requests.post,
            f"{llm_config['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {llm_config.get('api_key', '')}",
                "Content-Type": "application/json",
            },
            json={
                "model": llm_config.get("model", ""),
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": input_text},
                ],
                "temperature": 0,
                "max_tokens": 500,
            },
            verify=False,
            timeout=180,
            proxies={"http": None, "https": None},
        )
        resp = await asyncio.to_thread(_call)

        if resp.status_code != 200:
            return {"error": f"LLM HTTP {resp.status_code}"}

        raw_content = (resp.json()["choices"][0]["message"].get("content") or "").strip()

        # JSON 추출 — 여러 형태 대응
        content = raw_content

        # 1. 코드블록 제거 (```json ... ``` 또는 ``` ... ```)
        if "```" in content:
            import re
            m = re.search(r'```(?:json)?\s*\n?(.*?)```', content, re.DOTALL)
            if m:
                content = m.group(1).strip()

        # 2. 직접 파싱 시도
        try:
            return {"content": raw_content, "parsed": json.loads(content)}
        except json.JSONDecodeError:
            pass

        # 3. { } 블록 추출 시도
        import re
        m = re.search(r'\{.*\}', content, re.DOTALL)
        if m:
            try:
                return {"content": raw_content, "parsed": json.loads(m.group())}
            except json.JSONDecodeError:
                pass

        return {"error": "LLM 응답이 유효한 JSON이 아닙니다", "raw": raw_content[:500]}
    except requests.Timeout:
        return {"error": "LLM 응답 시간 초과 (3분)"}
    except Exception as e:
        return {"error": str(e)}


# ============================================
# Exact Match 검증
# ============================================
def validate_result(actual: dict, expected: dict) -> dict:
    """Exact match — 모든 필드가 정확히 일치해야 PASS"""
    details = []
    all_pass = True

    for key in FIELDS:
        exp = expected.get(key)
        act = actual.get(key, "__MISSING__")

        if act == "__MISSING__":
            details.append({"key": key, "pass": False, "expected": exp, "actual": "(키 없음)"})
            all_pass = False
            continue

        # 타입 변환 시도
        if isinstance(exp, int) and isinstance(act, float) and act == int(act):
            act = int(act)
        if isinstance(exp, float) and isinstance(act, int):
            act = float(act)
        if isinstance(exp, float):
            ok = abs(act - exp) < 0.01
        else:
            ok = act == exp

        details.append({"key": key, "pass": ok, "expected": exp, "actual": act})
        if not ok:
            all_pass = False

    return {"pass": all_pass, "details": details}
