"""
프로덕션 수준 Tool Registry 패턴

도구(Tool) 등록, 조회, 실행을 체계적으로 관리하는 레지스트리입니다.

=== 핵심 기능 ===
1. 데코레이터로 간편한 도구 등록
2. Python 함수 시그니처에서 OpenAI Tool Schema 자동 생성
3. 입력값 검증
4. 에러 래핑
5. 도구 목록 조회

=== 사용 예시 ===
    registry = ToolRegistry()

    @registry.tool(description="두 수를 더합니다")
    def add(a: float, b: float) -> float:
        return a + b

    # 자동으로 OpenAI Tool Schema가 생성됩니다!
    schemas = registry.get_tool_schemas()
    result = registry.execute("add", {"a": 1, "b": 2})
"""

import sys
import os
import json
import inspect
import traceback
from typing import Any, Callable, get_type_hints

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# Python 타입 -> JSON Schema 타입 변환
# ============================================================

# Python 타입 힌트를 OpenAI의 JSON Schema 타입으로 매핑
TYPE_MAP = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def python_type_to_json_schema(python_type: type) -> dict:
    """
    Python 타입 힌트를 JSON Schema 타입 정의로 변환합니다.

    예시:
        str → {"type": "string"}
        int → {"type": "integer"}
        float → {"type": "number"}
        list[str] → {"type": "array", "items": {"type": "string"}}
    """
    # None 타입 처리
    if python_type is type(None):
        return {"type": "null"}

    # 기본 타입
    if python_type in TYPE_MAP:
        return {"type": TYPE_MAP[python_type]}

    # typing 제네릭 타입 처리 (예: list[str], dict[str, int])
    origin = getattr(python_type, "__origin__", None)
    args = getattr(python_type, "__args__", None)

    if origin is list and args:
        return {
            "type": "array",
            "items": python_type_to_json_schema(args[0]),
        }

    if origin is dict and args:
        return {
            "type": "object",
            "additionalProperties": python_type_to_json_schema(args[1]) if len(args) > 1 else {},
        }

    # Union 타입 (Optional 포함)
    if origin is type(str | int):  # Python 3.10+ union type
        if type(None) in args:
            # Optional[T] = T | None
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                return python_type_to_json_schema(non_none[0])

    # 알 수 없는 타입은 string으로 fallback
    return {"type": "string"}


# ============================================================
# 함수에서 OpenAI Tool Schema 자동 생성
# ============================================================

def function_to_tool_schema(
    func: Callable,
    name: str | None = None,
    description: str | None = None,
) -> dict:
    """
    Python 함수의 시그니처와 타입 힌트를 분석하여
    OpenAI Tool Schema를 자동 생성합니다.

    Args:
        func: 도구 함수
        name: 도구 이름 (기본: 함수 이름)
        description: 도구 설명 (기본: 함수 docstring)

    Returns:
        OpenAI Tool Schema 딕셔너리

    === 변환 규칙 ===
    - 함수 이름 → tool name
    - docstring → tool description
    - 파라미터 타입 힌트 → JSON Schema properties
    - 기본값 없는 파라미터 → required
    - 기본값 있는 파라미터 → optional
    """
    tool_name = name or func.__name__
    tool_description = description or (func.__doc__ or "").strip()

    # 함수 시그니처 분석
    sig = inspect.signature(func)
    # 타입 힌트 가져오기 (inspect.signature보다 typing을 사용하는 것이 정확)
    try:
        type_hints = get_type_hints(func)
    except Exception:
        type_hints = {}

    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        # self, cls 등은 건너뜀
        if param_name in ("self", "cls"):
            continue

        # 파라미터 타입
        param_type = type_hints.get(param_name, str)  # 타입 힌트 없으면 string
        if param_type is inspect.Parameter.empty:
            param_type = str

        # JSON Schema 타입으로 변환
        schema = python_type_to_json_schema(param_type)

        # 파라미터 설명 (docstring에서 추출 시도)
        param_desc = _extract_param_description(func.__doc__ or "", param_name)
        if param_desc:
            schema["description"] = param_desc

        properties[param_name] = schema

        # 기본값이 없는 파라미터는 required
        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool_description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def _extract_param_description(docstring: str, param_name: str) -> str:
    """
    docstring에서 파라미터 설명을 추출합니다.

    지원 형식:
        Args:
            param_name: 파라미터 설명
        또는
        :param param_name: 파라미터 설명
    """
    if not docstring:
        return ""

    lines = docstring.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Google style: "param_name: 설명" 또는 "param_name (type): 설명"
        if stripped.startswith(f"{param_name}:") or stripped.startswith(f"{param_name} ("):
            desc = stripped.split(":", 1)[-1].strip()
            return desc
        # Sphinx style: ":param param_name: 설명"
        if stripped.startswith(f":param {param_name}:"):
            desc = stripped.split(":", 2)[-1].strip()
            return desc

    return ""


# ============================================================
# Tool Registry 클래스
# ============================================================

class ToolRegistry:
    """
    도구 등록 및 관리를 위한 레지스트리입니다.

    사용법:
        registry = ToolRegistry()

        # 방법 1: 데코레이터로 등록
        @registry.tool(description="두 수를 더합니다")
        def add(a: float, b: float) -> float:
            return a + b

        # 방법 2: 직접 등록
        registry.register(my_function, name="my_tool", description="설명")

        # 도구 실행
        result = registry.execute("add", {"a": 1, "b": 2})

        # OpenAI Tool Schema 목록
        schemas = registry.get_tool_schemas()
    """

    def __init__(self):
        self._tools: dict[str, dict] = {}
        # {"tool_name": {"func": callable, "schema": dict, "description": str}}

    def tool(
        self,
        name: str | None = None,
        description: str | None = None,
    ) -> Callable:
        """
        도구 등록 데코레이터.

        사용법:
            @registry.tool(description="두 수를 더합니다")
            def add(a: float, b: float) -> float:
                return a + b

        Args:
            name: 도구 이름 (기본: 함수 이름)
            description: 도구 설명 (기본: docstring)
        """
        def decorator(func: Callable) -> Callable:
            self.register(func, name=name, description=description)
            return func
        return decorator

    def register(
        self,
        func: Callable,
        name: str | None = None,
        description: str | None = None,
        schema: dict | None = None,
    ) -> None:
        """
        도구를 레지스트리에 등록합니다.

        Args:
            func: 도구 함수
            name: 도구 이름 (기본: 함수 이름)
            description: 도구 설명 (기본: docstring)
            schema: OpenAI Tool Schema (기본: 자동 생성)
        """
        tool_name = name or func.__name__

        if schema is None:
            schema = function_to_tool_schema(func, name=tool_name, description=description)

        self._tools[tool_name] = {
            "func": func,
            "schema": schema,
            "description": description or (func.__doc__ or "").strip(),
        }

    def get(self, name: str) -> dict | None:
        """도구 정보를 반환합니다."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """등록된 모든 도구 이름을 반환합니다."""
        return list(self._tools.keys())

    def get_tool_schemas(self) -> list[dict]:
        """등록된 모든 도구의 OpenAI Tool Schema 목록을 반환합니다."""
        return [tool["schema"] for tool in self._tools.values()]

    def get_tool_functions(self) -> dict[str, Callable]:
        """도구 이름 -> 함수 매핑을 반환합니다."""
        return {name: tool["func"] for name, tool in self._tools.items()}

    def execute(self, name: str, arguments: dict) -> str:
        """
        도구를 실행하고 결과를 문자열로 반환합니다.

        입력값 검증과 에러 래핑을 포함합니다.
        """
        if name not in self._tools:
            return f"오류: 알 수 없는 도구 '{name}'. 사용 가능한 도구: {self.list_tools()}"

        tool = self._tools[name]
        func = tool["func"]

        # 입력값 검증: 필수 파라미터 확인
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if param.default is inspect.Parameter.empty and param_name not in arguments:
                return f"오류: 필수 파라미터 '{param_name}'이 누락되었습니다. (도구: {name})"

        # 도구 실행 (에러 래핑)
        try:
            result = func(**arguments)
            return str(result)
        except TypeError as e:
            return f"도구 파라미터 오류 ({name}): {e}"
        except Exception as e:
            tb = traceback.format_exc()
            return f"도구 실행 오류 ({name}): {e}\n{tb}"

    def describe(self) -> str:
        """등록된 모든 도구의 설명을 반환합니다. 디버깅/로깅용."""
        lines = [f"=== Tool Registry ({len(self._tools)}개 도구) ==="]
        for name, tool in self._tools.items():
            desc = tool["description"][:80] if tool["description"] else "(설명 없음)"
            params = tool["schema"]["function"]["parameters"]["required"]
            lines.append(f"  - {name}({', '.join(params)}): {desc}")
        return "\n".join(lines)


# ============================================================
# 사용 예시
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Tool Registry 사용 예시")
    print("=" * 60)

    # 레지스트리 생성
    registry = ToolRegistry()

    # 데코레이터로 도구 등록
    @registry.tool(description="두 수를 더합니다")
    def add(a: float, b: float) -> float:
        """
        두 수를 더합니다.

        Args:
            a: 첫 번째 숫자
            b: 두 번째 숫자
        """
        return a + b

    @registry.tool()
    def greet(name: str, language: str = "ko") -> str:
        """
        인사말을 생성합니다.

        Args:
            name: 이름
            language: 언어 코드 (ko: 한국어, en: 영어)
        """
        if language == "ko":
            return f"안녕하세요, {name}님!"
        return f"Hello, {name}!"

    @registry.tool(description="파일의 줄 수를 반환합니다")
    def count_lines(file_path: str) -> int:
        """
        파일의 줄 수를 셉니다.

        Args:
            file_path: 파일 경로
        """
        with open(file_path, "r") as f:
            return sum(1 for _ in f)

    # 레지스트리 정보 출력
    print("\n[레지스트리 정보]")
    print(registry.describe())

    # 도구 목록
    print(f"\n[도구 목록] {registry.list_tools()}")

    # 자동 생성된 OpenAI Tool Schema 확인
    print("\n[자동 생성된 Tool Schema]")
    schemas = registry.get_tool_schemas()
    print(json.dumps(schemas, indent=2, ensure_ascii=False))

    # 도구 실행
    print("\n[도구 실행]")
    print(f"add(1, 2): {registry.execute('add', {'a': 1, 'b': 2})}")
    print(f"greet('홍길동'): {registry.execute('greet', {'name': '홍길동'})}")
    print(f"greet('John', 'en'): {registry.execute('greet', {'name': 'John', 'language': 'en'})}")

    # 에러 처리 예시
    print("\n[에러 처리]")
    print(f"알 수 없는 도구: {registry.execute('unknown_tool', {})}")
    print(f"필수 파라미터 누락: {registry.execute('add', {'a': 1})}")
