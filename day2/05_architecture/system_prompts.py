"""
System Prompt 엔지니어링

Agent의 행동을 제어하는 시스템 프롬프트 설계 패턴입니다.

=== System Prompt가 중요한 이유 ===
- Agent의 역할, 성격, 행동 규칙을 정의
- 사용 가능한 도구의 사용법을 안내
- 안전 규칙과 제한 사항을 명시
- Few-shot 예시로 원하는 응답 형태를 유도

=== 좋은 System Prompt의 조건 ===
1. 명확한 역할 정의
2. 구체적인 행동 규칙
3. 도구 사용 가이드
4. 안전 규칙
5. 출력 형식 지정
6. (선택) Few-shot 예시
"""

import sys
import os
import json
from typing import Callable

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 1. Agent 유형별 시스템 프롬프트 템플릿
# ============================================================

# --- 코딩 어시스턴트 ---
CODING_ASSISTANT_PROMPT = """당신은 전문적인 소프트웨어 엔지니어 어시스턴트입니다.

## 역할
- 코드 작성, 디버깅, 리팩토링 지원
- 코드 리뷰 및 개선 제안
- 기술적 질문에 대한 정확한 답변

## 행동 규칙
1. 코드를 작성할 때는 항상 실행 가능한 완전한 코드를 제공하세요.
2. 에러 처리와 엣지 케이스를 고려하세요.
3. 코드에 한국어 주석을 포함하세요.
4. 최신 Python 관행(type hints, f-string 등)을 따르세요.
5. 보안 취약점이 있는 코드는 작성하지 마세요.

## 도구 사용
- 파일을 읽어 코드를 분석할 때: read_file 사용
- 코드를 저장할 때: write_file 사용
- 명령어를 실행할 때: run_command 사용

## 출력 형식
- 코드 블록은 ```python으로 감싸세요
- 복잡한 설명은 번호 목록을 사용하세요
- 핵심 변경 사항은 강조하세요
"""

# --- 데이터 분석 어시스턴트 ---
DATA_ANALYST_PROMPT = """당신은 데이터 분석 전문 어시스턴트입니다.

## 역할
- 데이터 수집, 정리, 분석 지원
- Excel/CSV 파일 처리
- 통계적 인사이트 도출
- 차트 및 시각화 생성

## 행동 규칙
1. 데이터를 다룰 때는 항상 원본 데이터를 보존하세요 (별도 파일에 결과 저장).
2. 분석 결과를 설명할 때는 비전문가도 이해할 수 있도록 쉽게 설명하세요.
3. 수치 데이터는 적절한 단위와 포맷을 사용하세요.
4. 이상치나 결측값이 있으면 반드시 보고하세요.

## 도구 사용
- Excel 생성/읽기: create_excel, read_excel
- 셀 수정: update_excel_cell
- 차트 생성: create_excel_chart
- 파일 검색: search_files

## 출력 형식
- 테이블 데이터는 마크다운 표로 표시
- 통계 요약은 구조화된 형태로 제공
- 핵심 인사이트를 먼저 제시하고 세부 사항은 이후에
"""

# --- 웹 리서치 어시스턴트 ---
WEB_RESEARCHER_PROMPT = """당신은 웹 리서치 전문 어시스턴트입니다.

## 역할
- 웹에서 정보를 검색하고 수집
- 수집한 정보를 정리하여 보고서 작성
- 출처를 명시한 팩트 체크

## 행동 규칙
1. 항상 출처(URL)를 명시하세요.
2. 여러 소스에서 정보를 교차 확인하세요.
3. 사실과 의견을 구분하여 전달하세요.
4. 최신 정보인지 확인하세요 (날짜 확인).
5. 민감한 개인정보는 수집하지 마세요.

## 도구 사용
- 검색: search_google
- 페이지 이동: navigate
- 내용 추출: get_page_content
- 링크 확인: get_links
- 결과 저장: create_excel (표 형태 데이터)

## 리서치 프로세스
1. 키워드로 구글 검색
2. 상위 3-5개 결과 확인
3. 각 페이지에서 관련 정보 추출
4. 정보를 종합하여 정리
5. 출처와 함께 결과 보고
"""

# --- 시스템 관리자 어시스턴트 ---
SYSADMIN_PROMPT = """당신은 시스템 관리 전문 어시스턴트입니다.

## 역할
- 서버/시스템 상태 모니터링
- 파일 시스템 관리
- 프로세스 관리
- 트러블슈팅 지원

## 행동 규칙
1. 시스템을 변경하기 전에 반드시 현재 상태를 먼저 확인하세요.
2. 위험한 작업(삭제, 권한 변경 등)은 반드시 확인을 받으세요.
3. 작업 전후로 로그를 남기세요.
4. 롤백 방법을 항상 안내하세요.

## 금지 사항
- rm -rf / 절대 실행 금지
- 루트 권한 에스컬레이션 금지
- 민감한 파일 (인증서, 키, 비밀번호) 노출 금지
- 네트워크 설정 임의 변경 금지

## 도구 사용
- 명령어 실행: run_command (항상 안전한 명령어만)
- 파일 확인: read_file, list_directory
- 파일 검색: search_files
"""


# ============================================================
# 2. 동적 시스템 프롬프트 생성
# ============================================================

def generate_dynamic_prompt(
    role: str,
    tools: list[dict],
    safety_rules: list[str] | None = None,
    few_shot_examples: list[dict] | None = None,
    additional_context: str = "",
) -> str:
    """
    사용 가능한 도구와 규칙에 따라 시스템 프롬프트를 동적으로 생성합니다.

    Args:
        role: Agent의 역할 설명
        tools: OpenAI Tool Schema 리스트
        safety_rules: 안전 규칙 리스트
        few_shot_examples: Few-shot 예시 리스트 [{"user": "...", "assistant": "..."}]
        additional_context: 추가 컨텍스트 (환경 정보 등)

    Returns:
        완성된 시스템 프롬프트 문자열
    """
    sections = []

    # 역할 정의
    sections.append(f"## 역할\n{role}")

    # 사용 가능한 도구 목록 (자동 생성)
    if tools:
        tool_descriptions = []
        for tool in tools:
            func_info = tool.get("function", {})
            name = func_info.get("name", "")
            desc = func_info.get("description", "")
            params = func_info.get("parameters", {}).get("properties", {})

            param_strs = []
            for p_name, p_info in params.items():
                p_type = p_info.get("type", "string")
                p_desc = p_info.get("description", "")
                param_strs.append(f"{p_name}: {p_type}")

            params_text = ", ".join(param_strs) if param_strs else ""
            tool_descriptions.append(f"- **{name}({params_text})**: {desc}")

        sections.append("## 사용 가능한 도구\n" + "\n".join(tool_descriptions))

    # 안전 규칙
    if safety_rules:
        rules_text = "\n".join(f"{i + 1}. {rule}" for i, rule in enumerate(safety_rules))
        sections.append(f"## 안전 규칙\n{rules_text}")

    # 추가 컨텍스트
    if additional_context:
        sections.append(f"## 환경 정보\n{additional_context}")

    # Few-shot 예시
    if few_shot_examples:
        examples_text = ""
        for i, example in enumerate(few_shot_examples):
            examples_text += f"\n### 예시 {i + 1}\n"
            examples_text += f"사용자: {example['user']}\n"
            examples_text += f"어시스턴트: {example['assistant']}\n"
        sections.append(f"## 응답 예시\n{examples_text}")

    # 기본 지침
    sections.append("## 기본 지침\n- 항상 한국어로 응답하세요.\n- 정확하고 유용한 응답을 제공하세요.")

    return "\n\n".join(sections)


# ============================================================
# 3. 안전 규칙 템플릿
# ============================================================

# 공통 안전 규칙
COMMON_SAFETY_RULES = [
    "사용자의 개인정보를 노출하지 마세요.",
    "악의적인 코드를 생성하지 마세요.",
    "확실하지 않은 정보는 '확실하지 않다'고 명시하세요.",
    "저작권이 있는 콘텐츠를 그대로 복사하지 마세요.",
]

# CLI Agent 안전 규칙
CLI_SAFETY_RULES = COMMON_SAFETY_RULES + [
    "시스템 파일을 수정하거나 삭제하지 마세요.",
    "허용된 디렉토리 범위 밖의 파일에 접근하지 마세요.",
    "위험한 명령어(rm -rf, format 등)를 실행하지 마세요.",
    "네트워크 설정을 변경하지 마세요.",
]

# 브라우저 Agent 안전 규칙
BROWSER_SAFETY_RULES = COMMON_SAFETY_RULES + [
    "악성 웹사이트에 접속하지 마세요.",
    "로그인이 필요한 서비스에 임의로 접근하지 마세요.",
    "개인정보를 웹 폼에 입력하지 마세요.",
    "과도한 요청으로 서버에 부하를 주지 마세요.",
]


# ============================================================
# 4. Few-shot 예시 템플릿
# ============================================================

CLI_FEW_SHOT = [
    {
        "user": "현재 디렉토리의 Python 파일을 보여줘",
        "assistant": (
            "현재 디렉토리에서 Python 파일을 검색하겠습니다.\n"
            "[search_files 도구를 호출하여 *.py 패턴으로 검색]\n"
            "검색 결과, 다음 Python 파일이 있습니다:\n"
            "1. main.py (2.3 KB)\n"
            "2. utils.py (1.1 KB)\n"
            "3. config.py (0.5 KB)"
        ),
    },
    {
        "user": "main.py의 내용을 요약해줘",
        "assistant": (
            "main.py 파일을 읽어 분석하겠습니다.\n"
            "[read_file 도구로 main.py 읽기]\n\n"
            "main.py 요약:\n"
            "- Flask 웹 서버 애플리케이션\n"
            "- 3개의 API 엔드포인트 정의\n"
            "- SQLite 데이터베이스 사용\n"
            "- 총 150줄, 함수 5개"
        ),
    },
]

BROWSER_FEW_SHOT = [
    {
        "user": "구글에서 Python 3.12 새 기능을 검색해줘",
        "assistant": (
            "구글에서 검색하겠습니다.\n"
            "[search_google 도구로 'Python 3.12 new features' 검색]\n\n"
            "검색 결과 상위 3개:\n"
            "1. Python 3.12 Release Notes - python.org\n"
            "   - 개선된 에러 메시지, 새 타입 힌트 문법 등\n"
            "2. What's New in Python 3.12 - Real Python\n"
            "   - 실용적인 예시와 함께 설명\n"
            "3. Python 3.12 Features - Medium\n"
            "   - 성능 개선 벤치마크 포함"
        ),
    },
]


# ============================================================
# 5. 프롬프트 빌더 (Builder 패턴)
# ============================================================

class SystemPromptBuilder:
    """
    시스템 프롬프트를 단계적으로 구성하는 빌더 클래스입니다.

    사용법:
        prompt = (SystemPromptBuilder()
            .set_role("코딩 어시스턴트")
            .add_tools(tool_schemas)
            .add_safety_rules(CLI_SAFETY_RULES)
            .add_few_shot(CLI_FEW_SHOT)
            .set_language("ko")
            .build()
        )
    """

    def __init__(self):
        self._role = ""
        self._tools: list[dict] = []
        self._safety_rules: list[str] = []
        self._few_shot: list[dict] = []
        self._context = ""
        self._language = "ko"
        self._custom_sections: list[tuple[str, str]] = []

    def set_role(self, role: str) -> "SystemPromptBuilder":
        """Agent의 역할을 설정합니다."""
        self._role = role
        return self

    def add_tools(self, tools: list[dict]) -> "SystemPromptBuilder":
        """사용 가능한 도구를 추가합니다."""
        self._tools.extend(tools)
        return self

    def add_safety_rules(self, rules: list[str]) -> "SystemPromptBuilder":
        """안전 규칙을 추가합니다."""
        self._safety_rules.extend(rules)
        return self

    def add_few_shot(self, examples: list[dict]) -> "SystemPromptBuilder":
        """Few-shot 예시를 추가합니다."""
        self._few_shot.extend(examples)
        return self

    def set_context(self, context: str) -> "SystemPromptBuilder":
        """추가 컨텍스트를 설정합니다."""
        self._context = context
        return self

    def set_language(self, language: str) -> "SystemPromptBuilder":
        """응답 언어를 설정합니다."""
        self._language = language
        return self

    def add_section(self, title: str, content: str) -> "SystemPromptBuilder":
        """커스텀 섹션을 추가합니다."""
        self._custom_sections.append((title, content))
        return self

    def build(self) -> str:
        """최종 시스템 프롬프트를 생성합니다."""
        language_map = {
            "ko": "한국어",
            "en": "English",
            "ja": "日本語",
        }

        return generate_dynamic_prompt(
            role=self._role,
            tools=self._tools,
            safety_rules=self._safety_rules,
            few_shot_examples=self._few_shot if self._few_shot else None,
            additional_context=self._context + (
                f"\n- 응답 언어: {language_map.get(self._language, self._language)}"
            ),
        )


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("시스템 프롬프트 엔지니어링 예시")
    print("=" * 60)

    # 예시 1: 미리 정의된 프롬프트
    print("\n[1] 코딩 어시스턴트 프롬프트")
    print("-" * 40)
    print(CODING_ASSISTANT_PROMPT[:300] + "...")

    # 예시 2: 동적 생성
    print("\n[2] 동적 생성 프롬프트")
    print("-" * 40)

    sample_tools = [
        {
            "function": {
                "name": "search_files",
                "description": "파일을 검색합니다",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "디렉토리"},
                        "pattern": {"type": "string", "description": "검색 패턴"},
                    },
                },
            }
        },
    ]

    prompt = generate_dynamic_prompt(
        role="파일 관리 전문 어시스턴트입니다.",
        tools=sample_tools,
        safety_rules=CLI_SAFETY_RULES[:3],
        few_shot_examples=CLI_FEW_SHOT[:1],
        additional_context="OS: WSL2 (Ubuntu 22.04)",
    )
    print(prompt)

    # 예시 3: Builder 패턴
    print("\n[3] Builder 패턴 프롬프트")
    print("-" * 40)

    prompt = (
        SystemPromptBuilder()
        .set_role("데이터 분석 전문 AI 어시스턴트입니다.")
        .add_tools(sample_tools)
        .add_safety_rules(["데이터 원본을 수정하지 마세요."])
        .set_context("Python 3.11, openpyxl 사용 가능")
        .set_language("ko")
        .build()
    )
    print(prompt)
