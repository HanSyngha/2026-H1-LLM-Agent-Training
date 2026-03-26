"""
JSON 포맷팅 예제

LLM 응답을 JSON 형식으로 받는 방법을 다룹니다.

주요 내용:
1. 기본 JSON 모드 (response_format={"type": "json_object"})
2. 시스템 프롬프트에서 JSON 형식 요청하기
3. 응답 파싱 및 검증
4. 흔한 실수와 주의사항

실행 방법:
    python json_formatting.py

의존성:
    pip install openai httpx
"""

import json
import os
import sys

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ──────────────────────────────────────────────
# 1. JSON 모드 없이 JSON 요청하기 (주의: 불안정)
# ──────────────────────────────────────────────
def request_json_without_json_mode():
    """
    JSON 모드를 사용하지 않고 프롬프트만으로 JSON을 요청하는 예제.

    주의: 이 방법은 LLM이 항상 유효한 JSON을 반환한다는 보장이 없습니다.
    - 마크다운 코드블록(```json ... ```)으로 감싸는 경우가 많음
    - 추가 설명 텍스트가 포함될 수 있음
    - JSON 구문 오류가 발생할 수 있음
    """
    print("=" * 60)
    print("1. JSON 모드 없이 JSON 요청 (불안정한 방법)")
    print("=" * 60)

    client = get_openai_client()

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "당신은 영화 정보를 정리하는 도우미입니다.",
            },
            {
                "role": "user",
                "content": (
                    "영화 '기생충'의 정보를 JSON 형식으로 알려주세요. "
                    "title, director, year, genre, rating 필드를 포함해주세요."
                ),
            },
        ],
        temperature=0.0,
    )

    raw_text = response.choices[0].message.content
    print(f"\n[원본 응답]\n{raw_text}")

    # 문제점: LLM이 마크다운 코드블록이나 추가 텍스트를 포함할 수 있음
    # 수동으로 파싱을 시도해야 함
    try:
        # 코드블록이 포함된 경우를 대비한 전처리
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            # ```json ... ``` 형식 제거
            lines = cleaned.split("\n")
            # 첫 줄(```json)과 마지막 줄(```) 제거
            cleaned = "\n".join(lines[1:-1])

        data = json.loads(cleaned)
        print(f"\n[파싱 결과] {json.dumps(data, ensure_ascii=False, indent=2)}")
    except json.JSONDecodeError as e:
        print(f"\n[파싱 실패] JSON 디코딩 오류: {e}")
        print("→ 이것이 JSON 모드를 사용해야 하는 이유입니다!")

    return raw_text


# ──────────────────────────────────────────────
# 2. JSON 모드 사용하기 (안정적)
# ──────────────────────────────────────────────
def request_json_with_json_mode():
    """
    response_format={"type": "json_object"}을 사용하여
    LLM이 항상 유효한 JSON만 반환하도록 강제하는 예제.

    핵심 포인트:
    - response_format을 설정하면 LLM은 반드시 유효한 JSON을 반환
    - 단, 시스템 프롬프트나 사용자 메시지에서 JSON을 요청해야 함
      (그렇지 않으면 API 오류 발생 가능)
    - JSON의 스키마(필드 구조)는 프롬프트로 제어해야 함
    """
    print("\n" + "=" * 60)
    print("2. JSON 모드 사용 (안정적인 방법)")
    print("=" * 60)

    client = get_openai_client()

    # JSON 모드를 사용할 때는 반드시 시스템 프롬프트에 JSON 출력을 명시해야 합니다
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 영화 정보를 JSON 형식으로 정리하는 도우미입니다. "
                    "반드시 JSON 형식으로 응답하세요."
                ),
            },
            {
                "role": "user",
                "content": (
                    "영화 '기생충'의 정보를 알려주세요. "
                    "다음 필드를 포함해주세요: "
                    "title(영문), title_kr(한글), director, year, "
                    "genre(리스트), rating(10점 만점), synopsis(한줄 요약)"
                ),
            },
        ],
        # ★ 핵심: JSON 모드 활성화
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    raw_text = response.choices[0].message.content
    print(f"\n[원본 응답]\n{raw_text}")

    # JSON 모드를 사용하면 json.loads()가 항상 성공합니다
    data = json.loads(raw_text)
    print(f"\n[파싱된 데이터]")
    print(f"  제목: {data.get('title_kr', 'N/A')} ({data.get('title', 'N/A')})")
    print(f"  감독: {data.get('director', 'N/A')}")
    print(f"  연도: {data.get('year', 'N/A')}")
    print(f"  장르: {', '.join(data.get('genre', []))}")
    print(f"  평점: {data.get('rating', 'N/A')}/10")
    print(f"  줄거리: {data.get('synopsis', 'N/A')}")

    return data


# ──────────────────────────────────────────────
# 3. JSON 모드로 복잡한 구조 요청하기
# ──────────────────────────────────────────────
def request_complex_json():
    """
    JSON 모드로 중첩된 복잡한 JSON 구조를 요청하는 예제.

    프롬프트 엔지니어링으로 원하는 스키마를 유도합니다.
    - 중첩 객체 (nested objects)
    - 배열 (arrays)
    - 다양한 데이터 타입 (string, number, boolean)
    """
    print("\n" + "=" * 60)
    print("3. 복잡한 JSON 구조 요청")
    print("=" * 60)

    client = get_openai_client()

    # 원하는 JSON 스키마를 프롬프트에 명시적으로 기술
    schema_description = """
다음 JSON 형식으로 응답해주세요:
{
    "movies": [
        {
            "title": "영화 제목",
            "year": 2024,
            "director": {
                "name": "감독 이름",
                "nationality": "국적"
            },
            "cast": ["배우1", "배우2"],
            "box_office": {
                "domestic": 1000000,
                "international": 5000000,
                "currency": "USD"
            },
            "awards": [
                {
                    "name": "상 이름",
                    "category": "부문",
                    "year": 2024,
                    "won": true
                }
            ]
        }
    ]
}
"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"당신은 영화 데이터베이스입니다. {schema_description}",
            },
            {
                "role": "user",
                "content": "봉준호 감독의 대표작 3편을 정리해주세요.",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    data = json.loads(response.choices[0].message.content)

    print(f"\n총 {len(data.get('movies', []))}편의 영화 정보:")
    for i, movie in enumerate(data.get("movies", []), 1):
        print(f"\n  [{i}] {movie.get('title', 'N/A')} ({movie.get('year', 'N/A')})")
        director = movie.get("director", {})
        print(f"      감독: {director.get('name', 'N/A')} ({director.get('nationality', 'N/A')})")
        print(f"      출연: {', '.join(movie.get('cast', []))}")

        # 수상 내역 출력
        awards = movie.get("awards", [])
        if awards:
            for award in awards:
                won_str = "수상" if award.get("won") else "후보"
                print(
                    f"      🏆 {award.get('name', 'N/A')} "
                    f"- {award.get('category', 'N/A')} ({won_str})"
                )

    return data


# ──────────────────────────────────────────────
# 4. JSON 응답 검증 유틸리티
# ──────────────────────────────────────────────
def validate_json_response(json_data: dict, required_fields: list[str]) -> dict:
    """
    JSON 응답에서 필수 필드가 존재하는지 검증하는 유틸리티 함수.

    Args:
        json_data: 파싱된 JSON 데이터
        required_fields: 필수 필드 이름 리스트

    Returns:
        검증 결과 딕셔너리 (valid, missing_fields, data)
    """
    missing = [f for f in required_fields if f not in json_data]
    return {
        "valid": len(missing) == 0,
        "missing_fields": missing,
        "data": json_data,
    }


def request_and_validate():
    """
    JSON 응답을 받고 필수 필드 존재 여부를 검증하는 전체 워크플로우.
    실무에서는 이렇게 검증 단계를 반드시 포함해야 합니다.
    """
    print("\n" + "=" * 60)
    print("4. JSON 응답 검증 워크플로우")
    print("=" * 60)

    client = get_openai_client()

    # 필수 필드 목록 정의
    required_fields = ["title", "director", "year", "genre", "rating"]

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "영화 정보를 JSON으로 반환하세요. "
                    "반드시 title, director, year, genre, rating 필드를 포함하세요."
                ),
            },
            {
                "role": "user",
                "content": "영화 '올드보이'의 정보를 알려주세요.",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )

    data = json.loads(response.choices[0].message.content)

    # 검증 수행
    result = validate_json_response(data, required_fields)

    if result["valid"]:
        print("\n[검증 성공] 모든 필수 필드가 존재합니다.")
        print(json.dumps(result["data"], ensure_ascii=False, indent=2))
    else:
        print(f"\n[검증 실패] 누락된 필드: {result['missing_fields']}")
        print("→ 프롬프트를 수정하여 누락된 필드를 명시적으로 요청해야 합니다.")

    return result


# ──────────────────────────────────────────────
# 5. 흔한 실수와 주의사항 정리
# ──────────────────────────────────────────────
def common_pitfalls_demo():
    """
    JSON 모드 사용 시 흔히 발생하는 실수와 해결 방법을 보여줍니다.

    주요 주의사항:
    1. JSON 모드를 켜면 시스템/사용자 프롬프트에 "JSON"이라는 단어가 있어야 함
    2. JSON 모드는 구조(스키마)를 보장하지 않음 → 필드 누락 가능
    3. max_tokens가 너무 작으면 JSON이 잘릴 수 있음
    4. 긴 응답에서는 finish_reason 확인 필요
    """
    print("\n" + "=" * 60)
    print("5. 흔한 실수와 주의사항")
    print("=" * 60)

    client = get_openai_client()

    # ── 주의사항 1: finish_reason 확인 ──
    # max_tokens가 너무 작으면 JSON이 중간에 잘릴 수 있습니다
    print("\n[주의사항 1] max_tokens가 너무 작은 경우")
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "영화 정보를 JSON으로 반환하세요.",
            },
            {
                "role": "user",
                "content": "한국 영화 5편의 상세 정보를 알려주세요.",
            },
        ],
        response_format={"type": "json_object"},
        max_tokens=50,  # 의도적으로 매우 작은 값 설정
        temperature=0.0,
    )

    finish_reason = response.choices[0].finish_reason
    raw_text = response.choices[0].message.content

    print(f"  finish_reason: {finish_reason}")
    if finish_reason == "length":
        print("  → 경고: 토큰 제한으로 응답이 잘렸습니다!")
        print(f"  → 잘린 응답: {raw_text[:100]}...")
        # 잘린 JSON은 파싱 실패할 수 있음
        try:
            json.loads(raw_text)
            print("  → 파싱 성공 (운이 좋은 경우)")
        except json.JSONDecodeError:
            print("  → 파싱 실패! max_tokens를 늘려야 합니다.")
    else:
        print("  → 정상 완료")

    # ── 주의사항 2: JSON 모드 vs 스키마 보장 ──
    print("\n[주의사항 2] JSON 모드는 유효한 JSON만 보장 (스키마는 미보장)")
    print("  → response_format={'type': 'json_object'}:")
    print("    - 보장: 응답이 유효한 JSON임")
    print("    - 미보장: 원하는 필드가 반드시 포함됨")
    print("  → 스키마까지 보장하려면 json_schema 모드를 사용하세요")
    print("    (structured_output.py 참고)")

    # ── 주의사항 3: 프롬프트에 JSON 키워드 필수 ──
    print("\n[주의사항 3] 프롬프트에 'JSON' 키워드 필요")
    print("  → response_format을 설정했더라도")
    print("    시스템 또는 사용자 메시지에 'JSON'이 언급되어야 합니다.")
    print("  → 없으면 일부 모델에서 오류가 발생할 수 있습니다.")


# ──────────────────────────────────────────────
# 메인 실행
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("📌 JSON 포맷팅 예제")
    print("LLM 응답을 JSON으로 받는 다양한 방법을 알아봅니다.\n")

    # 예제 1: JSON 모드 없이 요청 (불안정)
    request_json_without_json_mode()

    # 예제 2: JSON 모드 사용 (안정적)
    request_json_with_json_mode()

    # 예제 3: 복잡한 JSON 구조 요청
    request_complex_json()

    # 예제 4: 응답 검증 워크플로우
    request_and_validate()

    # 예제 5: 주의사항 정리
    common_pitfalls_demo()

    print("\n" + "=" * 60)
    print("다음 단계: structured_output.py에서 JSON Schema를 사용한")
    print("더 강력한 구조화된 출력을 알아보세요.")
    print("=" * 60)
