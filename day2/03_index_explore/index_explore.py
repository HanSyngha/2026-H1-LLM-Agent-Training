"""
Index-based Code Exploration (인덱스 기반 코드 탐색)

Claude Code가 사용하는 것과 같은 인덱스 기반 코드 탐색 방식을 구현합니다.
벡터 DB 없이 파일 시스템을 직접 탐색하여 코드를 분석하는 접근법입니다.

=== 핵심 전략 ===
- glob 패턴 매칭으로 파일 발견
- grep/regex로 내용 검색
- AST 파싱으로 코드 구조 분석
- 파일 시스템 순회로 프로젝트 구조 파악
- 조합: glob -> grep -> read -> analyze

=== 장점 (Pros) ===
- 정확한 매칭: 함수명, 변수명, 에러 코드 등 정확한 검색
- 비용 없음: API 호출 없이 로컬에서 실행
- 실시간: 파일 변경이 즉시 반영됨
- 코드에 최적: 코드 구조를 이해하는 검색 가능

=== 단점 (Cons) ===
- 의미 기반 검색 불가: 동의어, 유사 개념 검색 불가
- 패턴 설계 필요: 좋은 검색 결과를 위해 적절한 패턴 설계 필요
"""

import sys
import os
import ast
import re
import fnmatch
import json
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 1. Glob 패턴 매칭 - 파일 발견
# ============================================================

def glob_search(
    root_dir: str,
    pattern: str,
    exclude_dirs: list[str] | None = None,
) -> list[str]:
    """
    glob 패턴으로 파일을 검색합니다.

    Claude Code의 Glob 도구와 동일한 원리입니다.
    파일 이름이나 경로 패턴으로 빠르게 파일을 찾아냅니다.

    Args:
        root_dir: 검색 시작 디렉토리
        pattern: glob 패턴 (예: "**/*.py", "*.json", "test_*.py")
        exclude_dirs: 제외할 디렉토리 목록

    Returns:
        매칭된 파일 경로 리스트

    사용 예시:
        # 모든 Python 파일
        glob_search("./project", "**/*.py")

        # 테스트 파일만
        glob_search("./project", "**/test_*.py")

        # 설정 파일
        glob_search("./project", "**/*.{json,yaml,toml}")
    """
    if exclude_dirs is None:
        exclude_dirs = [
            "__pycache__", ".git", "node_modules",
            ".venv", "venv", ".tox", ".mypy_cache",
        ]

    root = Path(root_dir)
    matched_files = []

    for path in root.rglob(pattern):
        # 제외 디렉토리 필터링
        parts = path.parts
        if any(excluded in parts for excluded in exclude_dirs):
            continue

        if path.is_file():
            matched_files.append(str(path))

    # 수정 시간 기준 정렬 (최근 수정 파일 우선)
    matched_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

    return matched_files


def glob_search_multi(root_dir: str, patterns: list[str]) -> list[str]:
    """
    여러 glob 패턴을 동시에 검색합니다.

    Args:
        root_dir: 검색 시작 디렉토리
        patterns: glob 패턴 리스트

    Returns:
        중복 제거된 매칭 파일 경로 리스트
    """
    all_files = set()
    for pattern in patterns:
        files = glob_search(root_dir, pattern)
        all_files.update(files)
    return sorted(all_files)


# ============================================================
# 2. Grep/Regex 검색 - 내용 검색
# ============================================================

@dataclass
class GrepResult:
    """grep 검색 결과를 담는 데이터 클래스"""
    file_path: str          # 파일 경로
    line_number: int        # 줄 번호
    line_content: str       # 매칭된 줄 내용
    match_text: str         # 매칭된 텍스트
    context_before: list[str] = field(default_factory=list)  # 매칭 이전 줄들
    context_after: list[str] = field(default_factory=list)   # 매칭 이후 줄들


def grep_search(
    file_paths: list[str],
    pattern: str,
    context_lines: int = 0,
    case_sensitive: bool = True,
    max_results: int = 100,
) -> list[GrepResult]:
    """
    파일 내용에서 정규식 패턴을 검색합니다.

    Claude Code의 Grep 도구와 동일한 원리입니다.
    ripgrep(rg) 기반으로 파일 내용을 빠르게 검색합니다.

    Args:
        file_paths: 검색 대상 파일 경로 리스트
        pattern: 정규식 패턴
        context_lines: 매칭 전후로 포함할 줄 수
        case_sensitive: 대소문자 구분 여부
        max_results: 최대 결과 수

    Returns:
        GrepResult 리스트
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled_pattern = re.compile(pattern, flags)

    results = []

    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            continue

        for i, line in enumerate(lines):
            match = compiled_pattern.search(line)
            if match:
                # 컨텍스트 줄 수집
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)

                result = GrepResult(
                    file_path=file_path,
                    line_number=i + 1,  # 1-based
                    line_content=line.rstrip("\n"),
                    match_text=match.group(),
                    context_before=[l.rstrip("\n") for l in lines[start:i]],
                    context_after=[l.rstrip("\n") for l in lines[i + 1:end]],
                )
                results.append(result)

                if len(results) >= max_results:
                    return results

    return results


def display_grep_results(results: list[GrepResult], show_context: bool = False):
    """
    grep 검색 결과를 보기 좋게 출력합니다.

    Args:
        results: GrepResult 리스트
        show_context: 컨텍스트 줄 표시 여부
    """
    if not results:
        print("  (검색 결과 없음)")
        return

    # 파일별로 그룹화
    by_file: dict[str, list[GrepResult]] = {}
    for r in results:
        by_file.setdefault(r.file_path, []).append(r)

    for file_path, file_results in by_file.items():
        # 상대 경로로 표시
        display_path = os.path.relpath(file_path)
        print(f"\n  {display_path}")
        print(f"  {'─' * 50}")

        for r in file_results:
            if show_context and r.context_before:
                for ctx_line in r.context_before:
                    print(f"    {r.line_number - len(r.context_before):>4} | {ctx_line}")

            print(f"    {r.line_number:>4} | {r.line_content}  <-- match")

            if show_context and r.context_after:
                for j, ctx_line in enumerate(r.context_after, 1):
                    print(f"    {r.line_number + j:>4} | {ctx_line}")


# ============================================================
# 3. AST 파싱 - 코드 구조 분석
# ============================================================

@dataclass
class CodeSymbol:
    """코드 심볼 (함수, 클래스 등) 정보"""
    name: str              # 심볼 이름
    kind: str              # 종류 (function, class, method, import 등)
    file_path: str         # 파일 경로
    line_number: int       # 시작 줄 번호
    end_line: int          # 종료 줄 번호
    docstring: str = ""    # docstring
    parent: str = ""       # 부모 클래스 (메서드인 경우)
    args: list[str] = field(default_factory=list)  # 함수 인자 목록


def parse_python_file(file_path: str) -> list[CodeSymbol]:
    """
    Python 파일을 AST로 파싱하여 코드 구조를 추출합니다.

    AST(Abstract Syntax Tree) 파싱을 통해 정확한 코드 구조를 분석합니다.
    정규식으로는 파악하기 어려운 중첩 구조, 스코프 등을 정확히 파악합니다.

    Args:
        file_path: Python 파일 경로

    Returns:
        CodeSymbol 리스트 (함수, 클래스, 임포트 등)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        return []

    symbols = []

    for node in ast.walk(tree):
        # 함수 정의
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            # 부모 노드가 클래스인지 확인 (메서드 여부)
            parent = _find_parent_class(tree, node)

            # 함수 인자 추출
            args = [arg.arg for arg in node.args.args if arg.arg != "self"]

            symbol = CodeSymbol(
                name=node.name,
                kind="method" if parent else "function",
                file_path=file_path,
                line_number=node.lineno,
                end_line=node.end_lineno or node.lineno,
                docstring=ast.get_docstring(node) or "",
                parent=parent or "",
                args=args,
            )
            symbols.append(symbol)

        # 클래스 정의
        elif isinstance(node, ast.ClassDef):
            # 상속 클래스 목록
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(f"{ast.dump(base)}")

            symbol = CodeSymbol(
                name=node.name,
                kind="class",
                file_path=file_path,
                line_number=node.lineno,
                end_line=node.end_lineno or node.lineno,
                docstring=ast.get_docstring(node) or "",
                args=bases,  # 상속 클래스를 args에 저장
            )
            symbols.append(symbol)

        # import 문
        elif isinstance(node, ast.Import):
            for alias in node.names:
                symbol = CodeSymbol(
                    name=alias.name,
                    kind="import",
                    file_path=file_path,
                    line_number=node.lineno,
                    end_line=node.lineno,
                )
                symbols.append(symbol)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                symbol = CodeSymbol(
                    name=f"{module}.{alias.name}",
                    kind="import_from",
                    file_path=file_path,
                    line_number=node.lineno,
                    end_line=node.lineno,
                )
                symbols.append(symbol)

    return symbols


def _find_parent_class(tree: ast.Module, target_node: ast.AST) -> str | None:
    """
    AST에서 함수 노드의 부모 클래스를 찾습니다.

    Args:
        tree: 전체 AST 트리
        target_node: 찾을 함수 노드

    Returns:
        부모 클래스 이름 (없으면 None)
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in ast.iter_child_nodes(node):
                if child is target_node:
                    return node.name
    return None


def display_code_structure(symbols: list[CodeSymbol]):
    """
    코드 구조를 트리 형태로 출력합니다.

    Args:
        symbols: CodeSymbol 리스트
    """
    # 파일별로 그룹화
    by_file: dict[str, list[CodeSymbol]] = {}
    for s in symbols:
        by_file.setdefault(s.file_path, []).append(s)

    for file_path, file_symbols in by_file.items():
        display_path = os.path.relpath(file_path)
        print(f"\n  {display_path}")
        print(f"  {'─' * 50}")

        # 종류별 정렬
        classes = [s for s in file_symbols if s.kind == "class"]
        functions = [s for s in file_symbols if s.kind == "function"]
        methods = [s for s in file_symbols if s.kind == "method"]
        imports = [s for s in file_symbols if s.kind in ("import", "import_from")]

        # 임포트 표시
        if imports:
            print(f"    imports: {', '.join(s.name for s in imports[:5])}")
            if len(imports) > 5:
                print(f"             ... 외 {len(imports) - 5}개")

        # 함수 표시
        for func in functions:
            args_str = ", ".join(func.args)
            doc_preview = func.docstring[:50] + "..." if func.docstring else ""
            print(f"    def {func.name}({args_str})  [L{func.line_number}]")
            if doc_preview:
                print(f"        # {doc_preview}")

        # 클래스 및 메서드 표시
        for cls in classes:
            bases_str = f"({', '.join(cls.args)})" if cls.args else ""
            print(f"    class {cls.name}{bases_str}  [L{cls.line_number}]")

            # 해당 클래스의 메서드 표시
            cls_methods = [m for m in methods if m.parent == cls.name]
            for method in cls_methods:
                args_str = ", ".join(method.args)
                print(f"        def {method.name}({args_str})  [L{method.line_number}]")


# ============================================================
# 4. 파일 시스템 순회 전략
# ============================================================

@dataclass
class ProjectStructure:
    """프로젝트 구조 분석 결과"""
    root_dir: str
    total_files: int = 0
    total_dirs: int = 0
    file_types: dict[str, int] = field(default_factory=dict)    # 확장자별 파일 수
    dir_tree: dict[str, list] = field(default_factory=dict)     # 디렉토리 트리
    key_files: list[str] = field(default_factory=list)          # 주요 파일 목록


def analyze_project_structure(root_dir: str) -> ProjectStructure:
    """
    프로젝트 디렉토리 구조를 분석합니다.

    파일 시스템 순회를 통해 프로젝트의 전체 구조를 파악합니다.
    Claude Code가 새 프로젝트에서 처음 하는 일과 동일합니다.

    Args:
        root_dir: 프로젝트 루트 디렉토리

    Returns:
        ProjectStructure 분석 결과
    """
    # 제외할 디렉토리
    exclude_dirs = {
        "__pycache__", ".git", "node_modules", ".venv",
        "venv", ".tox", ".mypy_cache", ".pytest_cache",
        "dist", "build", ".eggs",
    }

    # 주요 파일 패턴 (프로젝트 이해에 중요한 파일)
    key_file_patterns = [
        "README*", "setup.py", "setup.cfg", "pyproject.toml",
        "requirements*.txt", "Makefile", "Dockerfile",
        "docker-compose*.yml", ".env.example",
        "CLAUDE.md", "AGENTS.md", ".cursorrules",
    ]

    structure = ProjectStructure(root_dir=root_dir)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 제외 디렉토리 필터링 (in-place 수정으로 하위 순회도 건너뜀)
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        structure.total_dirs += 1

        for filename in filenames:
            structure.total_files += 1
            file_path = os.path.join(dirpath, filename)

            # 확장자 집계
            ext = Path(filename).suffix.lower() or "(no ext)"
            structure.file_types[ext] = structure.file_types.get(ext, 0) + 1

            # 주요 파일 확인
            for pattern in key_file_patterns:
                if fnmatch.fnmatch(filename, pattern):
                    structure.key_files.append(file_path)
                    break

    # 확장자별 내림차순 정렬
    structure.file_types = dict(
        sorted(structure.file_types.items(), key=lambda x: x[1], reverse=True)
    )

    return structure


def display_project_structure(structure: ProjectStructure):
    """
    프로젝트 구조 분석 결과를 출력합니다.

    Args:
        structure: ProjectStructure 분석 결과
    """
    print(f"\n  프로젝트: {structure.root_dir}")
    print(f"  {'─' * 50}")
    print(f"  총 파일 수:    {structure.total_files}")
    print(f"  총 디렉토리 수: {structure.total_dirs}")

    print(f"\n  [파일 유형 분포]")
    for ext, count in list(structure.file_types.items())[:10]:
        bar = "#" * min(count, 30)
        print(f"    {ext:>12}: {bar} ({count})")

    if structure.key_files:
        print(f"\n  [주요 파일]")
        for f in structure.key_files:
            print(f"    - {os.path.relpath(f, structure.root_dir)}")


# ============================================================
# 5. 복합 탐색 전략: glob -> grep -> read -> analyze
# ============================================================

def explore_codebase(root_dir: str, query: str) -> dict:
    """
    Claude Code 스타일의 복합 코드 탐색을 수행합니다.

    탐색 순서:
    1. glob으로 관련 파일 발견
    2. grep으로 내용 검색
    3. AST 파싱으로 구조 분석
    4. 결과 종합

    이 방식은 Claude Code가 코드베이스를 탐색할 때 사용하는 전략과 동일합니다.
    벡터 DB 없이도 정확하고 빠른 코드 검색이 가능합니다.

    Args:
        root_dir: 프로젝트 루트 디렉토리
        query: 검색 질의 (함수명, 클래스명, 키워드 등)

    Returns:
        탐색 결과 딕셔너리
    """
    results = {
        "query": query,
        "steps": [],
        "files_found": [],
        "grep_matches": [],
        "symbols": [],
    }

    # 1단계: glob으로 Python 파일 발견
    print(f"\n  [1단계] glob: Python 파일 검색")
    py_files = glob_search(root_dir, "*.py")
    results["files_found"] = py_files
    results["steps"].append(f"glob '*.py' -> {len(py_files)}개 파일 발견")
    print(f"    발견: {len(py_files)}개 Python 파일")

    # 2단계: grep으로 질의 키워드 검색
    print(f"\n  [2단계] grep: '{query}' 패턴 검색")
    grep_results = grep_search(py_files, query, context_lines=1, case_sensitive=False)
    results["grep_matches"] = [
        {
            "file": r.file_path,
            "line": r.line_number,
            "content": r.line_content,
        }
        for r in grep_results
    ]
    results["steps"].append(f"grep '{query}' -> {len(grep_results)}개 매칭")
    print(f"    매칭: {len(grep_results)}개 줄")
    display_grep_results(grep_results[:5], show_context=True)

    # 3단계: 매칭된 파일의 AST 분석
    matched_files = list(set(r.file_path for r in grep_results))
    if matched_files:
        print(f"\n  [3단계] AST: {len(matched_files)}개 파일 구조 분석")
        all_symbols = []
        for file_path in matched_files[:5]:  # 상위 5개 파일만 분석
            symbols = parse_python_file(file_path)
            all_symbols.extend(symbols)

        results["symbols"] = [
            {
                "name": s.name,
                "kind": s.kind,
                "file": s.file_path,
                "line": s.line_number,
            }
            for s in all_symbols
        ]
        results["steps"].append(f"AST parse -> {len(all_symbols)}개 심볼 발견")
        display_code_structure(all_symbols)

    return results


# ============================================================
# 6. 인덱스 기반 탐색의 장단점 분석
# ============================================================

def print_analysis():
    """인덱스 기반 탐색의 장단점을 정리하여 출력합니다."""
    print("\n" + "=" * 60)
    print("  Index-based Exploration 분석")
    print("=" * 60)

    print("""
  [장점 - Pros]
  -----------------------------------------------
  1. 정확한 매칭
     - 함수명, 클래스명, 변수명 등 정확한 문자열 검색
     - "def process_data" 로 검색하면 정확히 그 함수 정의를 찾음
     - 정규식으로 복잡한 패턴도 검색 가능

  2. 비용 없음
     - API 호출이 불필요, 100% 로컬 실행
     - 아무리 많이 검색해도 추가 비용 없음
     - 네트워크 연결 없이도 작동

  3. 실시간
     - 파일 변경이 즉시 반영됨 (인덱스 재구축 불필요)
     - 항상 최신 상태의 코드를 검색
     - git 변경사항도 바로 반영

  4. 코드에 최적
     - AST 파싱으로 코드의 구조적 의미를 정확히 파악
     - 함수 정의, 호출, 임포트 관계 분석 가능
     - 코드 네비게이션(정의로 이동, 참조 찾기)에 적합

  5. 컨텍스트 보존
     - 검색 결과의 전후 맥락(context lines)을 함께 볼 수 있음
     - 파일 전체를 읽어 정확한 이해 가능

  [단점 - Cons]
  -----------------------------------------------
  1. 의미 기반 검색 불가
     - "동시에 여러 작업 처리" 로 검색해도
       "asyncio", "threading" 코드를 찾지 못함
     - 키워드가 정확히 일치해야만 검색됨

  2. 패턴 설계 필요
     - 효과적인 검색을 위해 적절한 glob/grep 패턴을 알아야 함
     - 잘못된 패턴은 너무 많거나 너무 적은 결과를 반환
     - 정규식 문법에 대한 이해 필요

  3. 대규모 프로젝트 성능
     - 수만 개 파일에서 grep 검색 시 시간이 걸릴 수 있음
     - (ripgrep 같은 최적화된 도구로 해결 가능)

  4. 자연어 질의 미지원
     - "이 프로젝트에서 데이터 처리 로직이 어디에 있어?" 같은
       자연어 질문을 직접 처리할 수 없음
     - 사용자가 적절한 키워드로 변환해야 함
    """)


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Index-based Code Exploration 데모")
    print("  (Claude Code 스타일 코드 탐색)")
    print("=" * 60)

    # 현재 프로젝트의 루트 디렉토리
    # 이 파일 기준 2단계 상위 = 프로젝트 루트
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    # 1. 프로젝트 구조 분석
    print("\n[1] 프로젝트 구조 분석")
    structure = analyze_project_structure(project_root)
    display_project_structure(structure)

    # 2. glob 패턴 검색 예시
    print("\n\n[2] Glob 패턴 검색")
    print("─" * 40)

    # 모든 Python 파일
    py_files = glob_search(project_root, "*.py")
    print(f"  *.py -> {len(py_files)}개 파일")
    for f in py_files[:5]:
        print(f"    - {os.path.relpath(f, project_root)}")

    # 설정 파일
    config_files = glob_search_multi(project_root, ["*.json", "*.yaml", "*.toml", "*.cfg"])
    print(f"\n  설정 파일 -> {len(config_files)}개 파일")

    # 3. grep 검색 예시
    print("\n\n[3] Grep 내용 검색")
    print("─" * 40)

    # 클래스 정의 검색
    print("\n  질의: 'class.*Agent'")
    grep_results = grep_search(py_files, r"class\s+\w*Agent", context_lines=1)
    display_grep_results(grep_results)

    # 함수 정의 검색
    print("\n  질의: 'def.*search'")
    grep_results = grep_search(py_files, r"def\s+\w*search", case_sensitive=False)
    display_grep_results(grep_results)

    # 4. AST 코드 구조 분석
    print("\n\n[4] AST 코드 구조 분석")
    print("─" * 40)

    # 현재 파일을 AST로 분석
    current_file = os.path.abspath(__file__)
    symbols = parse_python_file(current_file)
    display_code_structure(symbols)

    # 5. 복합 탐색 (glob -> grep -> AST)
    print("\n\n[5] 복합 탐색 (Claude Code 스타일)")
    print("─" * 40)
    explore_results = explore_codebase(project_root, "ToolRegistry")

    # 6. 장단점 분석
    print("\n\n[6] 장단점 분석")
    print_analysis()
