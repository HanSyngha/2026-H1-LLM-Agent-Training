"""
Structured Output with JSON Schema 예제

response_format에 json_schema를 사용하여 LLM 응답의 구조를 엄격하게 제어합니다.
Pydantic 모델로 스키마를 정의하고 검증하는 패턴을 다룹니다.

주요 내용:
1. JSON Schema를 사용한 구조화된 출력
2. Pydantic 모델로 스키마 정의 및 응답 검증
3. 이메일 분석 (발신자, 수신자, 주제, 감정, 긴급도 추출)
4. 표 형태 데이터 추출 (여러 항목을 리스트로)
5. 기본 JSON 모드와의 비교

실행 방법:
    python structured_output.py

의존성:
    pip install openai httpx pydantic
"""

import json
import os
import sys
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ══════════════════════════════════════════════
# Pydantic 모델 정의
# ══════════════════════════════════════════════

# ──────────────────────────────────────────────
# 예제 1용 모델: 이메일 분석
# ──────────────────────────────────────────────
class SentimentType(str, Enum):
    """감정 분류 (enum으로 제한하여 일관된 값 보장)"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class UrgencyLevel(str, Enum):
    """긴급도 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EmailAnalysis(BaseModel):
    """
    이메일 분석 결과를 담는 Pydantic 모델.

    Structured Output의 핵심:
    - 각 필드의 타입이 엄격하게 정의됨
    - description이 LLM에게 필드의 의미를 전달
    - enum 타입으로 가능한 값을 제한
    - Optional 필드로 선택적 정보 처리
    """
    sender: str = Field(description="발신자 이름 또는 이메일 주소")
    recipients: list[str] = Field(description="수신자 목록")
    subject: str = Field(description="이메일 주제 (한줄 요약)")
    sentiment: SentimentType = Field(description="전체적인 감정 톤")
    urgency: UrgencyLevel = Field(description="긴급도 레벨")
    key_points: list[str] = Field(description="핵심 내용 요약 (3개 이내)")
    action_required: bool = Field(description="수신자의 조치가 필요한지 여부")
    action_items: Optional[list[str]] = Field(
        default=None,
        description="필요한 조치 항목 목록 (조치 필요 없으면 null)",
    )


# ──────────────────────────────────────────────
# 예제 2용 모델: 표 형태 데이터 추출
# ──────────────────────────────────────────────
class ProductInfo(BaseModel):
    """개별 상품 정보"""
    name: str = Field(description="상품명")
    category: str = Field(description="카테고리")
    price: int = Field(description="가격 (원)")
    in_stock: bool = Field(description="재고 여부")
    features: list[str] = Field(description="주요 특징 (3개 이내)")


class ProductCatalog(BaseModel):
    """상품 카탈로그 (여러 상품을 리스트로 관리)"""
    products: list[ProductInfo] = Field(description="상품 목록")
    total_count: int = Field(description="총 상품 수")
    category_summary: dict[str, int] = Field(
        description="카테고리별 상품 수 (예: {'전자제품': 3, '가구': 2})"
    )


# ══════════════════════════════════════════════
# JSON Schema 변환 유틸리티
# ══════════════════════════════════════════════

def pydantic_to_json_schema(model_class: type[BaseModel], schema_name: str) -> dict:
    """
    Pydantic 모델을 OpenAI의 json_schema response_format으로 변환합니다.

    OpenAI의 Structured Output API가 요구하는 형식:
    {
        "type": "json_schema",
        "json_schema": {
            "name": "스키마 이름",
            "strict": true,
            "schema": { ... JSON Schema ... }
        }
    }

    Args:
        model_class: Pydantic 모델 클래스
        schema_name: 스키마 이름 (API에서 식별용)

    Returns:
        response_format에 전달할 딕셔너리
    """
    # Pydantic v2의 model_json_schema()로 JSON Schema 생성
    schema = model_class.model_json_schema()

    # OpenAI가 요구하는 형식으로 래핑
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema_name,
            "strict": True,
            "schema": schema,
        },
    }


# ══════════════════════════════════════════════
# 예제 1: 이메일 분석
# ══════════════════════════════════════════════

def analyze_email():
    """
    이메일 텍스트에서 구조화된 정보를 추출하는 예제.

    Structured Output의 장점:
    - 반환되는 JSON이 정의한 스키마에 100% 부합
    - enum 값이 정의된 범위 내에서만 선택됨
    - 필수/선택 필드가 정확히 처리됨
    - Pydantic으로 타입 안전한 파싱 가능
    """
    print("=" * 60)
    print("예제 1: 이메일 분석 (Structured Output)")
    print("=" * 60)

    client = get_openai_client()

    # 분석할 샘플 이메일
    sample_email = """
From: 김팀장 <kim.teamlead@company.com>
To: 개발팀 <dev-team@company.com>, 박매니저 <park.manager@company.com>
Date: 2024-03-15 09:30
Subject: [긴급] 프로덕션 서버 장애 대응 요청

개발팀 여러분,

오늘 새벽 3시경 프로덕션 서버에서 메모리 누수로 인한 장애가 발생했습니다.
현재 임시로 서버를 재시작하여 서비스는 복구된 상태이나,
근본 원인 분석 및 수정이 시급합니다.

다음 사항을 오늘 중으로 처리해주세요:
1. 메모리 프로파일링 실행 및 누수 원인 파악
2. 핫픽스 브랜치 생성 및 수정 코드 작성
3. 스테이징 환경에서 부하 테스트 수행
4. 오후 5시까지 결과 보고

장애 로그는 Confluence에 공유해두었습니다.
질문 있으시면 바로 연락주세요.

감사합니다.
김팀장 드림
"""

    print(f"\n[입력 이메일]\n{sample_email}")

    # Structured Output으로 이메일 분석 요청
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 이메일 분석 전문가입니다. "
                    "이메일의 내용을 분석하여 구조화된 정보를 추출합니다."
                ),
            },
            {
                "role": "user",
                "content": f"다음 이메일을 분석해주세요:\n\n{sample_email}",
            },
        ],
        # ★ 핵심: json_schema를 사용한 Structured Output
        response_format=pydantic_to_json_schema(EmailAnalysis, "email_analysis"),
        temperature=0.0,
    )

    raw_text = response.choices[0].message.content
    print(f"\n[LLM 원본 응답]\n{raw_text}")

    # Pydantic 모델로 파싱 및 검증
    # model_validate_json()은 JSON 문자열을 직접 Pydantic 모델로 변환
    analysis = EmailAnalysis.model_validate_json(raw_text)

    # 타입 안전한 접근 (IDE 자동완성 지원)
    print(f"\n[분석 결과]")
    print(f"  발신자: {analysis.sender}")
    print(f"  수신자: {', '.join(analysis.recipients)}")
    print(f"  주제: {analysis.subject}")
    print(f"  감정: {analysis.sentiment.value}")
    print(f"  긴급도: {analysis.urgency.value}")
    print(f"  핵심 내용:")
    for point in analysis.key_points:
        print(f"    - {point}")
    print(f"  조치 필요: {'예' if analysis.action_required else '아니오'}")
    if analysis.action_items:
        print(f"  조치 항목:")
        for item in analysis.action_items:
            print(f"    - {item}")

    return analysis


# ══════════════════════════════════════════════
# 예제 2: 표 형태 데이터 추출
# ══════════════════════════════════════════════

def extract_product_data():
    """
    비정형 텍스트에서 표 형태의 구조화된 데이터를 추출하는 예제.

    여러 항목을 리스트로 추출하고, 집계 정보도 함께 생성합니다.
    실무에서 자주 사용되는 패턴입니다:
    - 비정형 보고서 → 구조화된 데이터
    - 자연어 설명 → 데이터베이스 레코드
    - 회의록 → 액션 아이템 목록
    """
    print("\n" + "=" * 60)
    print("예제 2: 표 형태 데이터 추출 (리스트)")
    print("=" * 60)

    client = get_openai_client()

    # 비정형 텍스트 (자연어로 작성된 상품 설명)
    product_text = """
이번 분기 신상품 목록입니다.

첫 번째는 "에어프로 무선이어폰"으로, 전자제품 카테고리이며
가격은 89,000원입니다. 노이즈캔슬링, 30시간 배터리, IPX5 방수가 특징이고
현재 재고가 있습니다.

두 번째로 "스마트 데스크 램프"는 조명 카테고리 제품으로 45,000원에
판매합니다. 밝기 자동 조절, 무선 충전 패드 내장, 타이머 기능이 있으며
재고가 있습니다.

세 번째는 "어반 백팩 프로"로 패션잡화에 해당하며 120,000원입니다.
노트북 수납(15인치), 방수 소재, USB 충전 포트 제공하며
현재 품절 상태입니다.

마지막으로 "미니 블루투스 스피커"는 전자제품이며 35,000원에
판매 중입니다. 360도 사운드, 15시간 재생, IP67 방수 등급이 특징이고
재고가 있습니다.
"""

    print(f"\n[입력 텍스트]\n{product_text}")

    # Structured Output으로 상품 정보 추출
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 데이터 추출 전문가입니다. "
                    "비정형 텍스트에서 상품 정보를 정확하게 추출합니다."
                ),
            },
            {
                "role": "user",
                "content": f"다음 텍스트에서 상품 정보를 추출해주세요:\n\n{product_text}",
            },
        ],
        response_format=pydantic_to_json_schema(ProductCatalog, "product_catalog"),
        temperature=0.0,
    )

    raw_text = response.choices[0].message.content

    # Pydantic 모델로 파싱
    catalog = ProductCatalog.model_validate_json(raw_text)

    # 표 형태로 출력
    print(f"\n[추출 결과] 총 {catalog.total_count}개 상품")
    print(f"\n{'상품명':<25} {'카테고리':<12} {'가격':>10} {'재고':>6}")
    print("-" * 60)
    for product in catalog.products:
        stock_str = "있음" if product.in_stock else "품절"
        print(
            f"  {product.name:<23} {product.category:<10} "
            f"{product.price:>8,}원 {stock_str:>6}"
        )
        print(f"    특징: {', '.join(product.features)}")

    print(f"\n[카테고리 요약]")
    for category, count in catalog.category_summary.items():
        print(f"  {category}: {count}개")

    return catalog


# ══════════════════════════════════════════════
# 예제 3: 기본 JSON 모드와 비교
# ══════════════════════════════════════════════

def compare_json_modes():
    """
    기본 JSON 모드(json_object)와 Structured Output(json_schema)의 차이를 비교합니다.

    | 항목           | json_object          | json_schema (Structured Output) |
    |---------------|---------------------|--------------------------------|
    | JSON 유효성    | 보장                 | 보장                           |
    | 스키마 준수    | 미보장 (프롬프트 의존)| 보장 (스키마 강제)              |
    | 필드 타입      | 미보장               | 보장 (string, number 등)       |
    | enum 값       | 미보장               | 보장 (정의된 값만 사용)         |
    | 필수 필드      | 미보장               | 보장                           |
    | 설정 복잡도    | 낮음                 | 중간 (스키마 정의 필요)         |
    """
    print("\n" + "=" * 60)
    print("예제 3: 기본 JSON 모드 vs Structured Output 비교")
    print("=" * 60)

    client = get_openai_client()

    test_prompt = "서울의 오늘 날씨를 알려주세요."

    # ── 방법 1: 기본 JSON 모드 ──
    print("\n[방법 1] response_format={'type': 'json_object'}")
    response1 = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "날씨 정보를 JSON으로 반환하세요. "
                    "city, temperature, condition, humidity 필드를 포함하세요."
                ),
            },
            {"role": "user", "content": test_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    data1 = json.loads(response1.choices[0].message.content)
    print(f"  결과: {json.dumps(data1, ensure_ascii=False, indent=4)}")
    print(f"  → JSON 유효: 예")
    print(f"  → 스키마 보장: 아니오 (필드가 다를 수 있음)")

    # ── 방법 2: Structured Output (json_schema) ──
    class WeatherInfo(BaseModel):
        """날씨 정보 스키마"""
        city: str = Field(description="도시명")
        temperature: float = Field(description="기온 (섭씨)")
        condition: str = Field(description="날씨 상태 (맑음, 흐림, 비 등)")
        humidity: int = Field(description="습도 (%)")

    print(f"\n[방법 2] response_format with json_schema")
    response2 = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "날씨 정보를 제공합니다.",
            },
            {"role": "user", "content": test_prompt},
        ],
        response_format=pydantic_to_json_schema(WeatherInfo, "weather_info"),
        temperature=0.0,
    )

    weather = WeatherInfo.model_validate_json(response2.choices[0].message.content)
    print(f"  결과:")
    print(f"    도시: {weather.city}")
    print(f"    기온: {weather.temperature}°C")
    print(f"    상태: {weather.condition}")
    print(f"    습도: {weather.humidity}%")
    print(f"  → JSON 유효: 예")
    print(f"  → 스키마 보장: 예 (필드 타입까지 보장)")

    # ── 비교 요약 ──
    print(f"\n[비교 요약]")
    print(f"  json_object:  간단하지만 스키마 보장 없음 → 간단한 용도에 적합")
    print(f"  json_schema:  스키마 강제 → 프로덕션 환경에 권장")
    print(f"  권장사항:     가능하면 json_schema (Structured Output) 사용")


# ══════════════════════════════════════════════
# 메인 실행
# ══════════════════════════════════════════════

if __name__ == "__main__":
    print("📌 Structured Output with JSON Schema 예제")
    print("Pydantic 모델로 LLM 응답 구조를 엄격하게 제어합니다.\n")

    # 예제 1: 이메일 분석
    analyze_email()

    # 예제 2: 표 형태 데이터 추출
    extract_product_data()

    # 예제 3: JSON 모드 비교
    compare_json_modes()

    print("\n" + "=" * 60)
    print("다음 단계: tool_calling.py에서 LLM에 외부 도구를")
    print("연결하는 방법을 알아보세요.")
    print("=" * 60)
