"""
Structured Output 실습 정답: 뉴스 분석 + Tool Calling + tool_choice 비교

Part 1: 뉴스 기사 structured output 분석 (Pydantic + json_schema)
Part 2: 2개 이상 tool 정의 + 자동 호출
Part 3: tool_choice 옵션 비교 실험

실행 방법:
    python exercise_solution.py

의존성:
    pip install openai httpx pydantic
"""

import json
import os
import sys
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# Part 1: 뉴스 기사 Structured Output 분석
# ============================================================

# --- Pydantic 모델 정의 ---

class Category(str, Enum):
    """뉴스 카테고리 (enum으로 값을 제한합니다)"""
    POLITICS = "정치"
    ECONOMY = "경제"
    SOCIETY = "사회"
    TECHNOLOGY = "기술"
    CULTURE = "문화"
    SPORTS = "스포츠"


class Sentiment(str, Enum):
    """감정 분류"""
    POSITIVE = "긍정"
    NEGATIVE = "부정"
    NEUTRAL = "중립"


class NewsAnalysis(BaseModel):
    """뉴스 기사 분석 결과 모델입니다."""
    title: str = Field(description="기사 제목 (LLM이 생성)")
    category: Category = Field(description="뉴스 카테고리")
    summary: str = Field(description="3문장 이내 요약")
    keywords: list[str] = Field(description="핵심 키워드 5개")
    sentiment: Sentiment = Field(description="전체적인 감정 톤")
    confidence: float = Field(description="분석 신뢰도 (0.0 ~ 1.0)")


def pydantic_to_json_schema(model_class: type[BaseModel], schema_name: str) -> dict:
    """Pydantic 모델을 OpenAI json_schema response_format으로 변환합니다."""
    schema = model_class.model_json_schema()
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema_name,
            "strict": True,
            "schema": schema,
        },
    }


def part1_news_analysis():
    """Part 1: 뉴스 기사 structured output 분석을 수행합니다."""
    print("=" * 60)
    print("  Part 1: 뉴스 기사 Structured Output 분석")
    print("=" * 60)

    client = get_openai_client()

    # 샘플 뉴스 기사
    news_article = """
삼성전자가 차세대 AI 반도체 'Exynos 2500'을 공개했다.
이번 칩은 4나노 공정으로 제작되며, 온디바이스 AI 성능이
전작 대비 40% 향상됐다. 업계에서는 이 제품이 글로벌
스마트폰 시장에서 퀄컴 스냅드래곤과의 경쟁에서 우위를
점할 수 있을지 주목하고 있다. 삼성전자 반도체 부문
사장은 "AI 시대에 맞는 혁신적인 칩을 선보이게 되어
기쁘다"고 밝혔다.
"""

    print(f"\n[입력 기사]\n{news_article}")

    # Structured Output으로 뉴스 분석을 요청합니다
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "당신은 뉴스 분석 전문가입니다. 뉴스 기사를 분석하여 구조화된 정보를 추출합니다.",
            },
            {
                "role": "user",
                "content": f"다음 뉴스 기사를 분석해주세요:\n\n{news_article}",
            },
        ],
        response_format=pydantic_to_json_schema(NewsAnalysis, "news_analysis"),
        temperature=0.0,
    )

    raw_text = response.choices[0].message.content
    print(f"[LLM 원본 응답]\n{raw_text}\n")

    # Pydantic 모델로 파싱 및 검증합니다
    analysis = NewsAnalysis.model_validate_json(raw_text)

    # 결과를 출력합니다
    print("[분석 결과]")
    print(f"  제목: {analysis.title}")
    print(f"  카테고리: {analysis.category.value}")
    print(f"  요약: {analysis.summary}")
    print(f"  키워드: {', '.join(analysis.keywords)}")
    print(f"  감정: {analysis.sentiment.value}")
    print(f"  신뢰도: {analysis.confidence:.1%}")

    return analysis


# ============================================================
# Part 2: 복수 Tool 정의 및 자동 호출
# ============================================================

# --- 도구 실행 함수 (시뮬레이션) ---

def search_news(query: str, date_range: str = "1week") -> str:
    """뉴스를 검색합니다. (시뮬레이션)"""
    results = {
        "삼성전자": [
            {"title": "삼성전자 Exynos 2500 공개", "date": "2026-03-30", "source": "전자신문"},
            {"title": "삼성전자 1분기 실적 전망", "date": "2026-03-28", "source": "한국경제"},
        ],
        "AI": [
            {"title": "생성형 AI 시장 100조원 돌파", "date": "2026-03-29", "source": "IT조선"},
            {"title": "국내 AI 스타트업 투자 급증", "date": "2026-03-27", "source": "매일경제"},
        ],
    }
    for key, articles in results.items():
        if key.lower() in query.lower():
            return json.dumps({"query": query, "results": articles, "count": len(articles)}, ensure_ascii=False)
    return json.dumps({"query": query, "results": [], "count": 0, "message": "검색 결과가 없습니다."}, ensure_ascii=False)


def get_stock_price(symbol: str) -> str:
    """주식 가격을 조회합니다. (시뮬레이션)"""
    stocks = {
        "005930": {"name": "삼성전자", "price": 72500, "change": 1.2, "volume": 15000000},
        "000660": {"name": "SK하이닉스", "price": 198000, "change": -0.5, "volume": 5000000},
        "035420": {"name": "NAVER", "price": 215000, "change": 0.8, "volume": 2000000},
    }
    if symbol in stocks:
        return json.dumps(stocks[symbol], ensure_ascii=False)
    return json.dumps({"error": f"종목 코드 '{symbol}'를 찾을 수 없습니다."}, ensure_ascii=False)


# --- 도구 스키마 정의 ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "키워드로 최신 뉴스를 검색합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색 키워드"},
                    "date_range": {"type": "string", "description": "검색 기간 (1day, 1week, 1month)", "default": "1week"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "종목 코드로 현재 주식 가격을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "종목 코드 (예: 005930=삼성전자, 000660=SK하이닉스)"},
                },
                "required": ["symbol"],
            },
        },
    },
]

# --- 도구 디스패치 테이블 ---
TOOL_FUNCTIONS = {
    "search_news": search_news,
    "get_stock_price": get_stock_price,
}


def execute_tool_call(tool_name: str, arguments: dict) -> str:
    """도구를 실행하고 결과를 반환합니다."""
    if tool_name in TOOL_FUNCTIONS:
        return TOOL_FUNCTIONS[tool_name](**arguments)
    return json.dumps({"error": f"알 수 없는 도구: {tool_name}"})


def part2_tool_calling():
    """Part 2: 복수 Tool 정의 및 자동 호출을 수행합니다."""
    print("\n" + "=" * 60)
    print("  Part 2: 복수 Tool 정의 및 자동 호출")
    print("=" * 60)

    client = get_openai_client()

    # 테스트 질문들입니다
    test_questions = [
        "삼성전자 관련 최근 뉴스 찾아줘",
        "삼성전자 주가 알려줘 (종목코드: 005930)",
    ]

    for question in test_questions:
        print(f"\n{'─' * 60}")
        print(f"Q: {question}")
        print(f"{'─' * 60}")

        messages = [
            {"role": "system", "content": "도구를 사용하여 사용자의 질문에 답변하세요. 한국어로 응답하세요."},
            {"role": "user", "content": question},
        ]

        # 1차 LLM 호출 (도구 호출 여부 결정)
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_msg = response.choices[0].message

        if assistant_msg.tool_calls:
            messages.append(assistant_msg)
            print(f"  도구 호출 {len(assistant_msg.tool_calls)}개:")

            for tc in assistant_msg.tool_calls:
                func_name = tc.function.name
                func_args = json.loads(tc.function.arguments)
                print(f"    - {func_name}({func_args})")

                # 도구를 실행합니다
                result = execute_tool_call(func_name, func_args)
                print(f"    결과: {result[:150]}...")

                # tool 메시지를 추가합니다 (tool_call_id 매칭 필수)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

            # 2차 LLM 호출 (최종 답변 생성)
            final = client.chat.completions.create(model=DEFAULT_MODEL, messages=messages)
            print(f"\n  답변: {final.choices[0].message.content}")
        else:
            print(f"  답변: {assistant_msg.content}")


# ============================================================
# Part 3: tool_choice 옵션 비교 실험
# ============================================================

def part3_tool_choice_comparison():
    """Part 3: tool_choice 옵션을 비교 실험합니다."""
    print("\n" + "=" * 60)
    print("  Part 3: tool_choice 옵션 비교")
    print("=" * 60)

    client = get_openai_client()

    # 테스트할 질문 2개입니다
    questions = {
        "도구 필요": "삼성전자 최근 뉴스 찾아줘",
        "도구 불필요": "안녕하세요, 반갑습니다",
    }

    # tool_choice 옵션 4가지입니다
    tool_choices = {
        "auto": "auto",
        "required": "required",
        "none": "none",
        "특정 함수": {"type": "function", "function": {"name": "search_news"}},
    }

    # 결과를 저장합니다
    results = {}

    for q_type, question in questions.items():
        results[q_type] = {}
        for tc_name, tc_value in tool_choices.items():
            print(f"\n  [{q_type}] tool_choice={tc_name}")

            messages = [
                {"role": "system", "content": "도구를 활용하여 답변하세요."},
                {"role": "user", "content": question},
            ]

            try:
                response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice=tc_value,
                )

                msg = response.choices[0].message
                if msg.tool_calls:
                    tool_names = [tc.function.name for tc in msg.tool_calls]
                    result = f"도구 호출: {tool_names}"
                else:
                    content = msg.content or "(내용 없음)"
                    result = f"텍스트: {content[:60]}..."

                results[q_type][tc_name] = result
                print(f"    -> {result}")

            except Exception as e:
                results[q_type][tc_name] = f"오류: {e}"
                print(f"    -> 오류: {e}")

    # 결과 표 출력
    print(f"\n\n{'=' * 80}")
    print("  tool_choice 비교 결과 표")
    print(f"{'=' * 80}")
    print(f"{'질문 유형':<12} | {'auto':<25} | {'required':<25} | {'none':<25} | {'특정 함수':<25}")
    print("-" * 120)
    for q_type in questions:
        row = f"{q_type:<12}"
        for tc_name in tool_choices:
            val = results.get(q_type, {}).get(tc_name, "N/A")[:23]
            row += f" | {val:<25}"
        print(row)


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("Structured Output + Tool Calling 실습 정답\n")

    # Part 1: 뉴스 기사 분석
    part1_news_analysis()

    # Part 2: 복수 Tool 자동 호출
    part2_tool_calling()

    # Part 3: tool_choice 비교
    part3_tool_choice_comparison()

    print(f"\n{'=' * 60}")
    print("  모든 파트 완료!")
    print(f"{'=' * 60}")
