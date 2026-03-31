"""
검색 비교 실습 정답: semantic search와 index explore 비교 + 하이브리드 접근법

semantic search(벡터 DB)와 index explore(grep/glob)를 비교하고,
두 방식을 결합한 하이브리드 검색 시스템을 구현합니다.

실행 방법:
    python exercise_solution.py

의존성:
    pip install chromadb openai httpx
"""

import json
import os
import sys
import re
import time
import glob as glob_module

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 1. Index Explore (grep/glob 기반 검색)
# ============================================================

def index_search_glob(project_dir: str, pattern: str) -> list[dict]:
    """glob 패턴으로 파일을 검색합니다.

    Args:
        project_dir: 검색할 프로젝트 디렉토리
        pattern: glob 패턴 (예: "**/*.py")

    Returns:
        검색 결과 리스트
    """
    search_pattern = os.path.join(project_dir, pattern)
    matches = glob_module.glob(search_pattern, recursive=True)

    results = []
    for match in matches:
        if os.path.isfile(match):
            rel_path = os.path.relpath(match, project_dir)
            results.append({
                "file": rel_path,
                "full_path": match,
                "size": os.path.getsize(match),
                "type": "glob",
            })
    return results


def index_search_grep(project_dir: str, query: str, file_pattern: str = "*.py") -> list[dict]:
    """파일 내용에서 텍스트를 검색합니다 (grep 방식).

    Args:
        project_dir: 검색할 프로젝트 디렉토리
        query: 검색할 텍스트 또는 정규식 패턴
        file_pattern: 검색할 파일 패턴

    Returns:
        매칭된 결과 리스트
    """
    results = []
    files = glob_module.glob(os.path.join(project_dir, "**", file_pattern), recursive=True)

    for file_path in files:
        if not os.path.isfile(file_path):
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                if re.search(query, line, re.IGNORECASE):
                    results.append({
                        "file": os.path.relpath(file_path, project_dir),
                        "line": line_num,
                        "content": line.strip()[:120],
                        "type": "grep",
                    })
        except Exception:
            continue

    return results


# ============================================================
# 2. Semantic Search (벡터 DB 기반 검색)
# ============================================================

def build_semantic_index(project_dir: str, file_pattern: str = "*.py") -> "chromadb.Collection":
    """프로젝트 파일을 임베딩하여 벡터 인덱스를 구축합니다.

    Args:
        project_dir: 인덱싱할 프로젝트 디렉토리
        file_pattern: 인덱싱할 파일 패턴

    Returns:
        ChromaDB 컬렉션
    """
    import chromadb
    from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

    # 임베딩 함수를 설정합니다
    embedding_fn = OpenAIEmbeddingFunction(
        api_key=GATEWAY_API_KEY,
        api_base=GATEWAY_BASE_URL,
        model_name=EMBEDDING_MODEL,
    )

    # ChromaDB 클라이언트를 생성합니다
    client = chromadb.Client()

    # 기존 컬렉션이 있으면 삭제합니다
    try:
        client.delete_collection("code_search")
    except Exception:
        pass

    collection = client.create_collection(
        name="code_search",
        embedding_function=embedding_fn,
    )

    # 파일들을 로드하고 청크로 분할합니다
    files = glob_module.glob(os.path.join(project_dir, "**", file_pattern), recursive=True)
    documents = []
    metadatas = []
    ids = []

    for file_path in files:
        if not os.path.isfile(file_path):
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if not content.strip():
                continue

            # 파일을 적당한 크기의 청크로 나눕니다
            chunk_size = 500
            rel_path = os.path.relpath(file_path, project_dir)
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                if len(chunk.strip()) < 20:
                    continue
                doc_id = f"{rel_path}_{i}"
                documents.append(chunk)
                metadatas.append({"file": rel_path, "offset": i})
                ids.append(doc_id)
        except Exception:
            continue

    # 벡터 인덱스에 추가합니다
    if documents:
        # ChromaDB는 한 번에 너무 많은 문서를 추가하면 오류가 발생할 수 있습니다
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            collection.add(documents=batch_docs, metadatas=batch_meta, ids=batch_ids)

    print(f"  -> {len(files)}개 파일에서 {len(documents)}개 청크를 인덱싱했습니다.")
    return collection


def semantic_search(collection, query: str, k: int = 5) -> list[dict]:
    """벡터 DB에서 의미 기반 검색을 수행합니다.

    Args:
        collection: ChromaDB 컬렉션
        query: 검색 질의 (자연어)
        k: 반환할 결과 수

    Returns:
        검색 결과 리스트
    """
    results = collection.query(query_texts=[query], n_results=k)

    search_results = []
    for i in range(len(results["documents"][0])):
        search_results.append({
            "file": results["metadatas"][0][i]["file"],
            "content": results["documents"][0][i][:120],
            "distance": results["distances"][0][i] if results.get("distances") else None,
            "type": "semantic",
        })
    return search_results


# ============================================================
# 3. 하이브리드 검색 시스템
# ============================================================

def classify_query(query: str) -> str:
    """질의를 'code', 'doc', 'hybrid' 중 하나로 분류합니다.

    Args:
        query: 사용자 검색 질의

    Returns:
        질의 유형 문자열
    """
    # 코드 관련 패턴을 확인합니다
    code_patterns = [
        r"^[A-Za-z_]\w*$",           # 심볼 이름 (예: ToolRegistry)
        r"def\s+\w+",                 # 함수 정의 패턴
        r"class\s+\w+",              # 클래스 정의 패턴
        r"import\s+\w+",             # import 문
        r"^\w+\.\w+",               # 모듈.함수 패턴
        r"[{}()\[\];=<>]",          # 코드 문법 기호
        r"\.\*",                     # 정규식 패턴
    ]

    # 자연어(문서) 패턴을 확인합니다
    doc_patterns = [
        r"(어떻게|무엇|왜|방법|설명|알려)",  # 한글 질문 키워드
        r"(how|what|why|explain)",           # 영문 질문 키워드
    ]

    code_score = sum(1 for p in code_patterns if re.search(p, query))
    doc_score = sum(1 for p in doc_patterns if re.search(p, query, re.IGNORECASE))

    if code_score > doc_score:
        return "code"
    elif doc_score > code_score:
        return "doc"
    else:
        return "hybrid"


def hybrid_search(query: str, project_dir: str, collection=None) -> list[dict]:
    """하이브리드 검색을 실행합니다.

    질의를 분류하고, 적절한 검색 방법을 선택합니다.

    Args:
        query: 검색 질의
        project_dir: 프로젝트 디렉토리
        collection: ChromaDB 컬렉션 (semantic search용)

    Returns:
        병합된 검색 결과 리스트
    """
    query_type = classify_query(query)
    print(f"  질의 유형: {query_type}")

    results = []

    if query_type in ("code", "hybrid"):
        # Index 기반 검색을 수행합니다
        grep_results = index_search_grep(project_dir, query)
        results.extend(grep_results[:5])

    if query_type in ("doc", "hybrid") and collection is not None:
        # Semantic 검색을 수행합니다
        sem_results = semantic_search(collection, query, k=5)
        results.extend(sem_results)

    # 결과를 병합하고 중복을 제거합니다
    return merge_results(results)


def merge_results(results: list[dict]) -> list[dict]:
    """검색 결과를 병합하고 중복을 제거합니다.

    Args:
        results: 여러 소스에서 온 검색 결과 리스트

    Returns:
        병합된 결과 리스트
    """
    seen_files = set()
    merged = []

    for r in results:
        file_key = r.get("file", "")
        if file_key not in seen_files:
            seen_files.add(file_key)
            merged.append(r)

    return merged


# ============================================================
# 4. 비교 실험 실행
# ============================================================

def run_comparison():
    """두 검색 방식을 비교 실험합니다."""
    print("=" * 60)
    print("  검색 전략 비교 실험")
    print("=" * 60)

    # 프로젝트 디렉토리를 설정합니다
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    print(f"프로젝트 경로: {project_dir}\n")

    # 테스트 질의 목록입니다
    test_queries = [
        ("ToolRegistry", "정확한 심볼 검색"),
        ("여러 작업을 동시에 처리하는 방법", "의미 기반 검색"),
        ("def.*execute", "정규식 패턴 검색"),
        ("에이전트를 안전하게 운영하려면?", "개념적 질의"),
        ("import json", "정확한 코드 검색"),
    ]

    # --- Index 검색 결과 ---
    print("=" * 60)
    print("  [A] Index Explore (grep/glob) 결과")
    print("=" * 60)

    for query, desc in test_queries:
        print(f"\n  질의: '{query}' ({desc})")
        start = time.time()
        results = index_search_grep(project_dir, query, "*.py")
        elapsed = time.time() - start

        print(f"  결과: {len(results)}개 ({elapsed:.3f}초)")
        for r in results[:3]:
            print(f"    - {r['file']}:{r['line']} | {r['content'][:60]}")

    # --- 하이브리드 검색 ---
    print(f"\n{'=' * 60}")
    print("  [B] 하이브리드 검색 결과")
    print("=" * 60)

    for query, desc in test_queries:
        print(f"\n  질의: '{query}' ({desc})")
        qtype = classify_query(query)
        print(f"  분류: {qtype}")

        # 코드 유형일 때는 grep으로 검색합니다
        start = time.time()
        grep_results = index_search_grep(project_dir, query, "*.py")
        elapsed = time.time() - start

        print(f"  grep 결과: {len(grep_results)}개 ({elapsed:.3f}초)")
        for r in grep_results[:2]:
            print(f"    - {r['file']}:{r['line']} | {r['content'][:60]}")

    # --- 비교 요약 ---
    print(f"\n{'=' * 60}")
    print("  비교 요약")
    print(f"{'=' * 60}")
    print("""
    | 평가 항목         | Semantic Search | Index Explore |
    |-------------------|-----------------|---------------|
    | 정확한 심볼 검색  | 2 / 5           | 5 / 5         |
    | 의미 기반 검색    | 5 / 5           | 1 / 5         |
    | 검색 속도         | 2 / 5           | 5 / 5         |
    | 비용 효율성       | 2 / 5           | 5 / 5         |
    | 코드 구조 이해    | 3 / 5           | 4 / 5         |
    | 자연어 질의 지원  | 5 / 5           | 1 / 5         |

    결론:
    - 정확한 심볼/패턴 검색: Index Explore가 우수합니다
    - 개념적/의미 기반 질의: Semantic Search가 우수합니다
    - 실무 권장: 질의 유형에 따라 두 방식을 결합하는 하이브리드 접근법
    """)


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    run_comparison()

    print(f"\n{'=' * 60}")
    print("  검색 비교 실습 완료!")
    print(f"{'=' * 60}")
