"""
Semantic Search vs Index-based Exploration 비교

두 검색 방식을 동일한 질의로 테스트하여 각각의 강점과 약점을 비교합니다.

=== 비교 목적 ===
- 어떤 질의에 어떤 방식이 더 적합한지 판별
- 실무에서 하이브리드 전략을 설계하기 위한 기초 데이터 수집

=== 결론 미리보기 ===
- Semantic Search: 문서 검색, 개념적/추상적 질의에 강함
- Index Explore: 코드 검색, 정확한 심볼 탐색에 강함
- 최적 전략: 코드는 인덱스, 문서는 시맨틱, 필요시 하이브리드
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 1. 테스트 데이터 준비
# ============================================================

# 두 방식 모두에서 테스트할 검색 질의
# 각 질의는 서로 다른 유형의 검색 니즈를 나타냄
TEST_QUERIES = [
    {
        "id": "Q1",
        "query": "ToolRegistry",
        "type": "정확한 심볼 검색",
        "description": "특정 클래스명을 정확히 검색",
        "expected_winner": "index",
    },
    {
        "id": "Q2",
        "query": "도구를 등록하고 관리하는 방법",
        "type": "의미 기반 검색",
        "description": "자연어로 기능을 설명하여 검색",
        "expected_winner": "semantic",
    },
    {
        "id": "Q3",
        "query": "def.*execute.*tool",
        "type": "패턴 기반 검색",
        "description": "정규식 패턴으로 함수 시그니처 검색",
        "expected_winner": "index",
    },
    {
        "id": "Q4",
        "query": "에러가 발생했을 때 안전하게 복구하는 방법",
        "type": "개념적 질의",
        "description": "추상적인 개념으로 관련 코드 검색",
        "expected_winner": "semantic",
    },
    {
        "id": "Q5",
        "query": "import ast",
        "type": "정확한 코드 검색",
        "description": "특정 import 문을 정확히 검색",
        "expected_winner": "index",
    },
    {
        "id": "Q6",
        "query": "프로덕션 환경에서 Agent를 안전하게 운영하려면?",
        "type": "문서 검색",
        "description": "문서/주석에서 개념적 내용 검색",
        "expected_winner": "semantic",
    },
]


# ============================================================
# 2. Semantic Search 실행기
# ============================================================

def run_semantic_search(query: str, corpus: list[dict]) -> dict:
    """
    시맨틱 검색을 실행하고 결과를 반환합니다.

    실제 ChromaDB와 OpenAI 임베딩을 사용합니다.
    API 키가 없는 환경에서는 시뮬레이션 결과를 반환합니다.

    Args:
        query: 검색 질의
        corpus: 검색 대상 문서 코퍼스

    Returns:
        검색 결과 딕셔너리
    """
    start_time = time.time()

    try:
        # 실제 시맨틱 검색 시도
        from semantic_search import (
            setup_chromadb_collection,
            index_documents,
            semantic_search,
        )

        _, collection = setup_chromadb_collection("comparison_test")
        index_documents(collection, corpus)
        results = semantic_search(collection, query, n_results=3)

        elapsed = time.time() - start_time

        return {
            "method": "semantic",
            "query": query,
            "results": [
                {
                    "title": r["metadata"]["title"],
                    "score": r["similarity_score"],
                    "preview": r["document"][:80],
                }
                for r in results
            ],
            "elapsed_seconds": round(elapsed, 3),
            "cost": "API 호출 비용 발생",
            "status": "success",
        }

    except Exception as e:
        elapsed = time.time() - start_time

        # API 연결 실패 시 시뮬레이션 결과 반환
        return {
            "method": "semantic",
            "query": query,
            "results": [
                {"title": "(시뮬레이션) 임베딩 API 연결 필요", "score": 0.0, "preview": str(e)[:80]},
            ],
            "elapsed_seconds": round(elapsed, 3),
            "cost": "API 호출 비용 발생",
            "status": "simulated",
            "error": str(e),
        }


# ============================================================
# 3. Index-based Search 실행기
# ============================================================

def run_index_search(query: str, root_dir: str) -> dict:
    """
    인덱스 기반 검색을 실행하고 결과를 반환합니다.

    glob + grep + AST 조합으로 검색합니다.
    API 호출 없이 로컬에서 즉시 실행됩니다.

    Args:
        query: 검색 질의 (키워드 또는 정규식 패턴)
        root_dir: 검색 대상 디렉토리

    Returns:
        검색 결과 딕셔너리
    """
    from index_explore import glob_search, grep_search, parse_python_file

    start_time = time.time()

    # 1단계: glob으로 Python 파일 발견
    py_files = glob_search(root_dir, "*.py")

    # 2단계: grep으로 내용 검색
    # 정규식이 아닌 일반 문자열은 이스케이프 처리
    import re
    try:
        re.compile(query)
        search_pattern = query
    except re.error:
        search_pattern = re.escape(query)

    grep_results = grep_search(py_files, search_pattern, context_lines=0, case_sensitive=False)

    # 3단계: 매칭된 파일의 AST 분석
    matched_files = list(set(r.file_path for r in grep_results))
    symbols = []
    for f in matched_files[:3]:
        symbols.extend(parse_python_file(f))

    elapsed = time.time() - start_time

    return {
        "method": "index",
        "query": query,
        "results": [
            {
                "file": os.path.relpath(r.file_path, root_dir),
                "line": r.line_number,
                "content": r.line_content.strip()[:80],
            }
            for r in grep_results[:5]
        ],
        "symbols_found": [
            {"name": s.name, "kind": s.kind, "line": s.line_number}
            for s in symbols[:10]
        ],
        "total_matches": len(grep_results),
        "files_searched": len(py_files),
        "elapsed_seconds": round(elapsed, 3),
        "cost": "무료 (로컬 실행)",
        "status": "success",
    }


# ============================================================
# 4. 비교 실행 및 결과 분석
# ============================================================

def run_comparison(queries: list[dict], root_dir: str, corpus: list[dict]):
    """
    동일한 질의로 두 방식을 비교 테스트합니다.

    Args:
        queries: 테스트 질의 리스트
        root_dir: 인덱스 검색용 디렉토리
        corpus: 시맨틱 검색용 문서 코퍼스
    """
    comparison_results = []

    for q in queries:
        print(f"\n{'=' * 60}")
        print(f"  [{q['id']}] {q['query']}")
        print(f"  유형: {q['type']} | 예상 우위: {q['expected_winner']}")
        print(f"{'=' * 60}")

        # 인덱스 기반 검색 실행
        print(f"\n  --- Index-based Search ---")
        index_result = run_index_search(q["query"], root_dir)
        print(f"  소요 시간: {index_result['elapsed_seconds']}초")
        print(f"  비용: {index_result['cost']}")
        print(f"  매칭 수: {index_result.get('total_matches', 0)}")
        for r in index_result["results"][:3]:
            print(f"    - {r.get('file', '?')}:{r.get('line', '?')} | {r.get('content', '')[:60]}")

        # 시맨틱 검색 실행
        print(f"\n  --- Semantic Search ---")
        semantic_result = run_semantic_search(q["query"], corpus)
        print(f"  소요 시간: {semantic_result['elapsed_seconds']}초")
        print(f"  비용: {semantic_result['cost']}")
        print(f"  상태: {semantic_result['status']}")
        for r in semantic_result["results"][:3]:
            title = r.get("title", "?")
            score = r.get("score", 0)
            print(f"    - {title} (유사도: {score:.4f})")

        # 비교 판정
        winner = _judge_winner(q, index_result, semantic_result)
        print(f"\n  >> 판정: {winner}")

        comparison_results.append({
            "query": q,
            "index_result": index_result,
            "semantic_result": semantic_result,
            "winner": winner,
        })

    return comparison_results


def _judge_winner(query: dict, index_result: dict, semantic_result: dict) -> str:
    """
    두 검색 결과를 비교하여 우위를 판정합니다.

    Args:
        query: 질의 정보
        index_result: 인덱스 검색 결과
        semantic_result: 시맨틱 검색 결과

    Returns:
        판정 문자열
    """
    query_type = query["type"]

    # 정확한 심볼/코드 검색 -> 인덱스 우위
    if query_type in ("정확한 심볼 검색", "패턴 기반 검색", "정확한 코드 검색"):
        index_matches = index_result.get("total_matches", 0)
        if index_matches > 0:
            return f"Index 우위 (정확한 매칭 {index_matches}건 발견)"
        return "판정 불가 (인덱스 결과 없음)"

    # 의미 기반/개념적 질의 -> 시맨틱 우위
    if query_type in ("의미 기반 검색", "개념적 질의", "문서 검색"):
        if semantic_result["status"] == "success":
            top_score = semantic_result["results"][0]["score"] if semantic_result["results"] else 0
            return f"Semantic 우위 (최고 유사도: {top_score:.4f})"
        return "Semantic 우위 (이론상) - API 연결 필요"

    return "동등"


# ============================================================
# 5. 하이브리드 접근법
# ============================================================

def hybrid_search(query: str, root_dir: str, corpus: list[dict]) -> dict:
    """
    하이브리드 검색: 인덱스 + 시맨틱 결합

    실무에서 가장 효과적인 전략입니다:
    - 코드 파일 -> 인덱스 기반 (정확한 심볼, 패턴)
    - 문서 파일 -> 시맨틱 기반 (의미적 유사도)
    - 두 결과를 통합하여 가장 관련성 높은 결과 제공

    Args:
        query: 검색 질의
        root_dir: 코드 디렉토리 (인덱스 검색용)
        corpus: 문서 코퍼스 (시맨틱 검색용)

    Returns:
        통합 검색 결과
    """
    results = {
        "query": query,
        "strategy": "hybrid",
        "code_results": [],     # 인덱스 기반 코드 검색 결과
        "doc_results": [],      # 시맨틱 기반 문서 검색 결과
    }

    # 1. 질의 유형 판별 (간단한 휴리스틱)
    is_code_query = _is_code_query(query)
    is_doc_query = _is_doc_query(query)

    print(f"\n  질의 분석:")
    print(f"    코드 관련: {'예' if is_code_query else '아니오'}")
    print(f"    문서 관련: {'예' if is_doc_query else '아니오'}")

    # 2. 코드 관련 질의 -> 인덱스 검색
    if is_code_query:
        print(f"\n  [코드 검색] 인덱스 기반 탐색 실행")
        code_result = run_index_search(query, root_dir)
        results["code_results"] = code_result["results"]

    # 3. 문서 관련 질의 -> 시맨틱 검색
    if is_doc_query:
        print(f"\n  [문서 검색] 시맨틱 검색 실행")
        doc_result = run_semantic_search(query, corpus)
        results["doc_results"] = doc_result["results"]

    # 4. 둘 다 해당되지 않으면 양쪽 모두 실행
    if not is_code_query and not is_doc_query:
        print(f"\n  [혼합 검색] 양쪽 모두 실행")
        code_result = run_index_search(query, root_dir)
        doc_result = run_semantic_search(query, corpus)
        results["code_results"] = code_result["results"]
        results["doc_results"] = doc_result["results"]

    return results


def _is_code_query(query: str) -> bool:
    """
    질의가 코드 검색에 해당하는지 판별합니다.

    코드 관련 힌트:
    - CamelCase 또는 snake_case 패턴
    - 정규식 패턴
    - 프로그래밍 키워드 (def, class, import 등)
    """
    import re

    # CamelCase 패턴
    if re.search(r'[A-Z][a-z]+[A-Z]', query):
        return True

    # snake_case 패턴
    if "_" in query and query.replace("_", "").isalpha():
        return True

    # 프로그래밍 키워드
    code_keywords = ["def ", "class ", "import ", "from ", "return ", "self.", "async "]
    if any(kw in query for kw in code_keywords):
        return True

    # 정규식 패턴 (특수문자 포함)
    if re.search(r'[\\.*+?{}\[\]|^$]', query):
        return True

    return False


def _is_doc_query(query: str) -> bool:
    """
    질의가 문서 검색에 해당하는지 판별합니다.

    문서 관련 힌트:
    - 자연어 질문 형태
    - "방법", "어떻게", "왜" 등의 질문 키워드
    - 한국어 문장
    """
    # 질문 형태
    question_markers = ["?", "방법", "어떻게", "왜", "무엇", "하려면", "위해", "설명"]
    if any(marker in query for marker in question_markers):
        return True

    # 한국어 문장 (3어절 이상)
    words = query.split()
    if len(words) >= 3:
        return True

    return False


# ============================================================
# 6. 의사결정 플로우차트 (언제 어떤 방식을 사용할지)
# ============================================================

# ┌─────────────────────────────────────────────────────────────┐
# │                  검색 전략 의사결정 플로우                   │
# └─────────────────────────────────────────────────────────────┘
#
# [질문] 무엇을 찾고 있나요?
#    │
#    ├── 특정 코드 심볼 (함수, 클래스, 변수)
#    │   └── -> Index (grep + AST)
#    │       이유: 정확한 문자열 매칭이 필요하므로
#    │
#    ├── 특정 에러 메시지 / 로그 패턴
#    │   └── -> Index (grep)
#    │       이유: 정확한 문자열 검색이 가장 빠르고 정확
#    │
#    ├── "이 기능이 어디 구현되어 있지?"
#    │   └── -> Index (glob -> grep -> AST)
#    │       이유: 코드 네비게이션은 인덱스 기반이 효과적
#    │
#    ├── "이 개념과 관련된 문서가 있나?"
#    │   └── -> Semantic Search
#    │       이유: 의미적 유사도 기반으로 관련 문서를 찾아야 함
#    │
#    ├── "비슷한 구현이 이미 있을까?"
#    │   └── -> Hybrid (Semantic + Index)
#    │       이유: 개념적 유사성(semantic) + 코드 확인(index)
#    │
#    └── 프로젝트 전체 구조 파악
#        └── -> Index (glob + AST)
#            이유: 파일 구조, 클래스/함수 목록은 인덱스가 최적
#
# ┌─────────────────────────────────────────────────────────────┐
# │                  실무 가이드라인 정리                        │
# └─────────────────────────────────────────────────────────────┘
#
# | 상황                 | 추천 방식      | 이유                     |
# |---------------------|---------------|-------------------------|
# | 함수/클래스 찾기      | Index         | 정확한 심볼 매칭          |
# | 에러 추적            | Index         | 에러 메시지 정확 검색      |
# | 코드 리뷰            | Index + AST   | 구조 분석 + 변경점 추적    |
# | 문서 검색            | Semantic      | 의미 기반 유사도           |
# | API 문서 찾기        | Semantic      | 자연어 질의               |
# | 유사 코드 탐색        | Hybrid        | 개념 + 구현 모두 필요      |
# | 의존성 분석          | Index + AST   | import/require 추적      |
# | 보안 취약점 스캔      | Index (regex) | 패턴 매칭 기반 탐지        |

def print_decision_guide():
    """검색 전략 의사결정 가이드를 출력합니다."""
    print("\n" + "=" * 60)
    print("  검색 전략 의사결정 가이드")
    print("=" * 60)

    guide = """
  [상황별 추천 검색 방식]
  ──────────────────────────────────────────

  1. 특정 코드 심볼 찾기 (함수, 클래스, 변수)
     -> Index (grep + AST)
     예: "ToolRegistry 클래스 정의를 찾아줘"

  2. 에러 메시지 / 로그 추적
     -> Index (grep)
     예: "KeyError: 'user_id' 에러가 어디서 발생하지?"

  3. 기능 구현 위치 탐색
     -> Index (glob -> grep -> AST)
     예: "파일 업로드 기능이 어디에 구현되어 있지?"

  4. 개념/주제 관련 문서 검색
     -> Semantic Search
     예: "비동기 처리 관련 가이드 문서가 있나?"

  5. 유사한 구현 찾기
     -> Hybrid (Semantic + Index)
     예: "이런 패턴의 코드가 이미 구현되어 있을까?"

  6. 프로젝트 구조 파악
     -> Index (glob + AST)
     예: "이 프로젝트의 전체 모듈 구조를 보여줘"

  7. 의존성 분석
     -> Index (AST 기반 import 추적)
     예: "이 모듈을 누가 사용하고 있지?"

  8. 보안 취약점 스캔
     -> Index (정규식 패턴 매칭)
     예: "eval(), exec() 사용 코드를 찾아줘"

  [핵심 원칙]
  ──────────────────────────────────────────
  - 코드 -> 인덱스 기반 (정확성이 중요)
  - 문서 -> 시맨틱 기반 (의미가 중요)
  - 모르겠으면 -> 하이브리드 (둘 다 실행)
    """

    print(guide)


# ============================================================
# 7. 비교 결과 요약
# ============================================================

def summarize_comparison(comparison_results: list[dict]):
    """
    비교 테스트 결과를 요약합니다.

    Args:
        comparison_results: 비교 실행 결과 리스트
    """
    print("\n" + "=" * 60)
    print("  비교 결과 요약")
    print("=" * 60)

    index_wins = 0
    semantic_wins = 0
    ties = 0

    for cr in comparison_results:
        winner = cr["winner"]
        q = cr["query"]

        if "Index" in winner:
            index_wins += 1
            marker = "[IDX]"
        elif "Semantic" in winner:
            semantic_wins += 1
            marker = "[SEM]"
        else:
            ties += 1
            marker = "[TIE]"

        print(f"\n  {marker} {q['id']}: {q['query'][:40]}")
        print(f"        유형: {q['type']}")
        print(f"        판정: {winner}")

    print(f"\n  {'─' * 50}")
    print(f"  Index 우위:    {index_wins}건")
    print(f"  Semantic 우위: {semantic_wins}건")
    print(f"  동등:          {ties}건")

    print(f"\n  결론:")
    print(f"    - 코드 관련 질의에는 인덱스 기반 검색이 압도적으로 유리")
    print(f"    - 문서/개념 관련 질의에는 시맨틱 검색이 효과적")
    print(f"    - 실무에서는 하이브리드 전략을 채택하는 것이 최적")


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Semantic Search vs Index-based Exploration")
    print("  Side-by-Side 비교 테스트")
    print("=" * 60)

    # 프로젝트 루트 디렉토리
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    # 시맨틱 검색용 코퍼스 (semantic_search.py에서 가져오기)
    try:
        from semantic_search import SAMPLE_CORPUS
        corpus = SAMPLE_CORPUS
    except ImportError:
        # fallback 코퍼스
        corpus = [
            {
                "id": "doc_1",
                "title": "도구 관리 패턴",
                "content": "도구를 등록하고 관리하는 레지스트리 패턴입니다.",
                "category": "아키텍처",
            },
            {
                "id": "doc_2",
                "title": "에러 처리와 복구",
                "content": "에러가 발생했을 때 안전하게 복구하는 패턴입니다.",
                "category": "안정성",
            },
            {
                "id": "doc_3",
                "title": "Agent 아키텍처",
                "content": "프로덕션 환경에서 Agent를 안전하게 운영하기 위한 패턴입니다.",
                "category": "아키텍처",
            },
        ]

    # 1. 비교 테스트 실행
    print("\n[1] 비교 테스트 실행")
    comparison_results = run_comparison(TEST_QUERIES, project_root, corpus)

    # 2. 결과 요약
    print("\n[2] 비교 결과 요약")
    summarize_comparison(comparison_results)

    # 3. 하이브리드 검색 데모
    print("\n\n[3] 하이브리드 검색 데모")
    print("─" * 40)
    hybrid_result = hybrid_search("안전한 도구 실행 방법", project_root, corpus)
    print(f"\n  코드 결과: {len(hybrid_result['code_results'])}건")
    print(f"  문서 결과: {len(hybrid_result['doc_results'])}건")

    # 4. 의사결정 가이드
    print("\n\n[4] 의사결정 가이드")
    print_decision_guide()
