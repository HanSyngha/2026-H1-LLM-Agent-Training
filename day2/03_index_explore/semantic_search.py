"""
Semantic Search (벡터 DB 기반 의미 검색)

벡터 데이터베이스를 활용한 의미 기반 검색의 원리와 구현을 다룹니다.

=== 핵심 개념 ===
- 텍스트를 임베딩 벡터로 변환하여 의미적 유사도를 계산
- ChromaDB를 사용한 벡터 저장 및 검색
- 자연어 질의로 관련 문서를 찾는 방식

=== 장점 (Pros) ===
- 의미 기반 검색: 동의어, 유사 표현도 찾아냄
- 유사 문서 발견: 직접적으로 언급되지 않은 관련 문서도 검색 가능
- 자연어 질의: 키워드가 아닌 질문 형태로 검색 가능

=== 단점 (Cons) ===
- 임베딩 비용: API 호출마다 비용 발생
- 청킹 전략 의존: 문서를 어떻게 나누느냐에 따라 검색 품질이 달라짐
- 업데이트 복잡: 문서 변경 시 임베딩을 다시 생성해야 함
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *


# ============================================================
# 1. 샘플 텍스트 코퍼스 (한국어 문서)
# ============================================================

# 다양한 주제의 한국어 문서 모음
# 실제 프로젝트에서는 파일 시스템, DB, API 등에서 문서를 가져옴
SAMPLE_CORPUS = [
    {
        "id": "doc_1",
        "title": "Python 비동기 프로그래밍",
        "content": (
            "Python의 asyncio 모듈은 비동기 프로그래밍을 위한 핵심 라이브러리입니다. "
            "async/await 키워드를 사용하여 코루틴을 정의하고, "
            "이벤트 루프에서 여러 작업을 동시에 실행할 수 있습니다. "
            "I/O 바운드 작업에서 특히 높은 성능 향상을 기대할 수 있습니다."
        ),
        "category": "프로그래밍",
    },
    {
        "id": "doc_2",
        "title": "머신러닝 모델 학습 파이프라인",
        "content": (
            "머신러닝 파이프라인은 데이터 수집, 전처리, 특성 엔지니어링, "
            "모델 학습, 평가, 배포의 단계로 구성됩니다. "
            "scikit-learn의 Pipeline 클래스를 사용하면 이 과정을 체계적으로 관리할 수 있습니다. "
            "교차 검증과 하이퍼파라미터 튜닝을 통해 모델 성능을 최적화합니다."
        ),
        "category": "머신러닝",
    },
    {
        "id": "doc_3",
        "title": "Docker 컨테이너 기초",
        "content": (
            "Docker는 애플리케이션을 컨테이너로 패키징하여 어디서든 동일하게 실행할 수 있게 합니다. "
            "Dockerfile로 이미지를 정의하고, docker-compose로 멀티 컨테이너 환경을 관리합니다. "
            "가상 머신보다 가볍고 빠르며, 마이크로서비스 아키텍처에 적합합니다."
        ),
        "category": "인프라",
    },
    {
        "id": "doc_4",
        "title": "REST API 설계 원칙",
        "content": (
            "REST API는 HTTP 메서드(GET, POST, PUT, DELETE)를 사용하여 리소스를 조작합니다. "
            "URL은 명사형으로 리소스를 표현하고, 상태 코드로 결과를 전달합니다. "
            "버전 관리, 페이지네이션, 에러 처리는 좋은 API 설계의 필수 요소입니다. "
            "OpenAPI(Swagger) 스펙으로 문서를 자동 생성할 수 있습니다."
        ),
        "category": "백엔드",
    },
    {
        "id": "doc_5",
        "title": "데이터베이스 인덱스 최적화",
        "content": (
            "데이터베이스 인덱스는 쿼리 성능을 크게 향상시킵니다. "
            "B-Tree 인덱스는 범위 검색에, Hash 인덱스는 정확한 일치 검색에 적합합니다. "
            "복합 인덱스를 설계할 때는 카디널리티가 높은 컬럼을 앞에 배치합니다. "
            "EXPLAIN 명령어로 쿼리 실행 계획을 분석하여 인덱스 효과를 확인할 수 있습니다."
        ),
        "category": "데이터베이스",
    },
    {
        "id": "doc_6",
        "title": "Python 동시성: 멀티스레딩과 멀티프로세싱",
        "content": (
            "Python에서 동시성을 구현하는 방법은 크게 세 가지입니다. "
            "threading 모듈은 I/O 바운드 작업에 적합하지만 GIL 때문에 CPU 바운드에는 제한적입니다. "
            "multiprocessing 모듈은 프로세스를 분리하여 진정한 병렬 처리를 제공합니다. "
            "concurrent.futures는 두 가지를 통합된 인터페이스로 제공합니다."
        ),
        "category": "프로그래밍",
    },
    {
        "id": "doc_7",
        "title": "CI/CD 파이프라인 구축",
        "content": (
            "CI/CD는 지속적 통합과 지속적 배포를 의미합니다. "
            "GitHub Actions, Jenkins, GitLab CI 등의 도구로 자동화된 빌드, 테스트, 배포 파이프라인을 구축합니다. "
            "코드 변경이 커밋되면 자동으로 테스트가 실행되고, 통과 시 스테이징/프로덕션 환경에 배포됩니다."
        ),
        "category": "DevOps",
    },
    {
        "id": "doc_8",
        "title": "LLM 프롬프트 엔지니어링",
        "content": (
            "대규모 언어 모델(LLM)의 성능은 프롬프트 설계에 크게 좌우됩니다. "
            "시스템 프롬프트로 모델의 역할과 제약을 정의하고, "
            "Few-shot 예시로 원하는 출력 형태를 유도합니다. "
            "Chain-of-Thought 기법은 복잡한 추론 작업의 정확도를 높여줍니다."
        ),
        "category": "AI",
    },
]


# ============================================================
# 2. 임베딩 생성 (OpenAI API via 게이트웨이)
# ============================================================

def create_embedding(text: str) -> list[float]:
    """
    텍스트를 임베딩 벡터로 변환합니다.

    OpenAI의 text-embedding 모델을 게이트웨이를 통해 호출합니다.

    Args:
        text: 임베딩할 텍스트

    Returns:
        임베딩 벡터 (float 리스트)
    """
    client = get_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    # 임베딩 벡터 추출
    embedding = response.data[0].embedding
    return embedding


def create_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    여러 텍스트를 한 번에 임베딩합니다.

    배치 처리로 API 호출 횟수를 줄여 비용을 절감합니다.

    Args:
        texts: 임베딩할 텍스트 리스트

    Returns:
        임베딩 벡터 리스트
    """
    client = get_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    # 인덱스 순서대로 정렬하여 반환
    embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
    return embeddings


# ============================================================
# 3. ChromaDB를 활용한 벡터 저장소
# ============================================================

def setup_chromadb_collection(collection_name: str = "lecture_docs"):
    """
    ChromaDB 컬렉션을 생성하고 샘플 문서를 저장합니다.

    ChromaDB는 경량 벡터 데이터베이스로, 로컬에서 쉽게 사용할 수 있습니다.
    내부적으로 임베딩 생성도 지원하지만, 여기서는 OpenAI 임베딩을 직접 사용합니다.

    Args:
        collection_name: 컬렉션 이름

    Returns:
        (chromadb.Client, chromadb.Collection) 튜플
    """
    import chromadb

    # 인메모리 클라이언트 생성 (영구 저장이 필요하면 PersistentClient 사용)
    chroma_client = chromadb.Client()

    # 기존 컬렉션이 있으면 삭제 후 재생성
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=collection_name,
        # cosine 유사도 사용 (임베딩 모델에 따라 적절한 거리 함수 선택)
        metadata={"hnsw:space": "cosine"},
    )

    print(f"[ChromaDB] 컬렉션 '{collection_name}' 생성 완료")
    return chroma_client, collection


def index_documents(collection, documents: list[dict]):
    """
    문서를 ChromaDB 컬렉션에 인덱싱합니다.

    각 문서에 대해:
    1. 텍스트를 임베딩 벡터로 변환
    2. 원본 텍스트와 메타데이터를 함께 저장

    Args:
        collection: ChromaDB 컬렉션
        documents: 문서 리스트 (id, title, content, category 포함)
    """
    # 모든 문서의 텍스트를 한 번에 임베딩 (배치 처리)
    texts = [f"{doc['title']}\n{doc['content']}" for doc in documents]
    print(f"[임베딩] {len(texts)}개 문서 임베딩 생성 중...")

    embeddings = create_embeddings_batch(texts)

    # ChromaDB에 저장
    collection.add(
        ids=[doc["id"] for doc in documents],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {"title": doc["title"], "category": doc["category"]}
            for doc in documents
        ],
    )

    print(f"[ChromaDB] {len(documents)}개 문서 인덱싱 완료")


# ============================================================
# 4. 시맨틱 검색 실행
# ============================================================

def semantic_search(collection, query: str, n_results: int = 3) -> list[dict]:
    """
    자연어 질의로 유사한 문서를 검색합니다.

    검색 과정:
    1. 질의 텍스트를 임베딩 벡터로 변환
    2. ChromaDB에서 코사인 유사도 기반으로 가장 가까운 문서 검색
    3. 유사도 점수와 함께 결과 반환

    Args:
        collection: ChromaDB 컬렉션
        query: 자연어 검색 질의
        n_results: 반환할 결과 수

    Returns:
        검색 결과 리스트 (문서, 유사도 점수 포함)
    """
    # 질의 임베딩 생성
    query_embedding = create_embedding(query)

    # ChromaDB에서 검색
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # 결과 정리
    search_results = []
    for i in range(len(results["ids"][0])):
        # ChromaDB의 cosine distance를 similarity score로 변환
        # cosine distance = 1 - cosine similarity
        distance = results["distances"][0][i]
        similarity = 1 - distance

        search_results.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "similarity_score": round(similarity, 4),
            "distance": round(distance, 4),
        })

    return search_results


def display_search_results(query: str, results: list[dict]):
    """
    검색 결과를 보기 좋게 출력합니다.

    Args:
        query: 검색 질의
        results: 검색 결과 리스트
    """
    print(f"\n{'=' * 60}")
    print(f"  검색 질의: \"{query}\"")
    print(f"{'=' * 60}")

    for i, result in enumerate(results, 1):
        title = result["metadata"]["title"]
        category = result["metadata"]["category"]
        score = result["similarity_score"]

        # 유사도 점수에 따른 시각적 표시
        bar_length = int(score * 20)
        bar = "#" * bar_length + "-" * (20 - bar_length)

        print(f"\n  [{i}] {title}")
        print(f"      카테고리: {category}")
        print(f"      유사도:   [{bar}] {score:.4f}")
        print(f"      내용:     {result['document'][:100]}...")

    print(f"\n{'=' * 60}")


# ============================================================
# 5. 다양한 검색 시나리오 테스트
# ============================================================

def run_search_scenarios(collection):
    """
    다양한 질의로 시맨틱 검색의 특성을 보여줍니다.

    시맨틱 검색은 키워드 일치가 아닌 의미적 유사도로 검색하므로,
    동의어나 관련 개념을 포함한 문서도 찾아낼 수 있습니다.
    """
    # 시나리오 1: 직접적인 키워드가 포함된 질의
    print("\n" + "=" * 60)
    print("  시나리오 1: 직접 키워드 질의")
    print("  (문서에 포함된 키워드로 검색)")
    print("=" * 60)
    results = semantic_search(collection, "Python 비동기 처리 방법", n_results=3)
    display_search_results("Python 비동기 처리 방법", results)

    # 시나리오 2: 의미적으로 유사하지만 다른 표현의 질의
    print("\n" + "=" * 60)
    print("  시나리오 2: 의미 기반 질의")
    print("  (직접 키워드 없이 의미만으로 검색)")
    print("=" * 60)
    results = semantic_search(collection, "여러 작업을 동시에 처리하는 방법", n_results=3)
    display_search_results("여러 작업을 동시에 처리하는 방법", results)

    # 시나리오 3: 개념적 질의 (추상적인 질문)
    print("\n" + "=" * 60)
    print("  시나리오 3: 추상적/개념적 질의")
    print("  (구체적 기술이 아닌 문제 해결 관점)")
    print("=" * 60)
    results = semantic_search(collection, "코드를 배포 환경에서 안정적으로 실행하려면?", n_results=3)
    display_search_results("코드를 배포 환경에서 안정적으로 실행하려면?", results)

    # 시나리오 4: 유사도 점수 비교
    print("\n" + "=" * 60)
    print("  시나리오 4: AI 관련 문서 검색")
    print("  (LLM, 프롬프트 관련 질의)")
    print("=" * 60)
    results = semantic_search(collection, "AI 모델의 출력을 제어하는 기법", n_results=3)
    display_search_results("AI 모델의 출력을 제어하는 기법", results)


# ============================================================
# 6. 시맨틱 검색의 장단점 분석
# ============================================================

def print_analysis():
    """시맨틱 검색의 장단점을 정리하여 출력합니다."""
    print("\n" + "=" * 60)
    print("  시맨틱 검색 분석")
    print("=" * 60)

    print("""
  [장점 - Pros]
  -----------------------------------------------
  1. 의미 기반 검색
     - 키워드가 정확히 일치하지 않아도 의미적으로 관련된 문서를 찾음
     - "동시 처리" 로 검색해도 "비동기", "멀티스레딩" 문서가 나옴

  2. 유사 문서 발견
     - 사용자가 예상하지 못한 관련 문서를 발견할 수 있음
     - 크로스 도메인 연관성도 포착 가능

  3. 자연어 질의
     - 키워드 조합이 아닌 자연스러운 질문으로 검색 가능
     - 비전문가도 쉽게 사용 가능

  4. 다국어 지원
     - 동일 임베딩 모델이 다양한 언어를 지원하면
       언어를 넘나드는 검색도 가능

  [단점 - Cons]
  -----------------------------------------------
  1. 임베딩 비용
     - 문서 인덱싱 시 API 호출 비용 발생
     - 대량 문서 처리 시 비용이 급격히 증가
     - 검색 시마다 질의 임베딩 비용 발생

  2. 청킹 전략 의존
     - 문서를 어떤 크기로 나누느냐에 따라 검색 품질이 달라짐
     - 너무 작으면 맥락 손실, 너무 크면 정밀도 저하
     - 최적의 청킹 전략을 찾는 데 실험이 필요

  3. 업데이트 복잡
     - 문서가 변경되면 임베딩을 다시 생성해야 함
     - 실시간 업데이트가 어려움
     - 인덱스 재구축 비용이 큼

  4. 정확한 매칭 불리
     - 특정 함수명, 변수명, 에러 코드 등 정확한 문자열 매칭에 약함
     - "def process_data" 같은 코드 검색에는 grep이 훨씬 효과적

  5. 환각 가능성
     - 유사도 점수가 높다고 항상 관련성이 높은 것은 아님
     - 임베딩 모델의 한계로 잘못된 유사성을 보고할 수 있음
    """)


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Semantic Search (벡터 DB 기반 의미 검색) 데모")
    print("=" * 60)

    # ChromaDB 설정 및 문서 인덱싱
    print("\n[1단계] ChromaDB 컬렉션 생성 및 문서 인덱싱")
    chroma_client, collection = setup_chromadb_collection()
    index_documents(collection, SAMPLE_CORPUS)

    # 다양한 시나리오로 검색 테스트
    print("\n[2단계] 검색 시나리오 테스트")
    run_search_scenarios(collection)

    # 장단점 분석
    print("\n[3단계] 장단점 분석")
    print_analysis()

    # 컬렉션 통계
    print(f"\n[통계]")
    print(f"  - 인덱싱된 문서 수: {collection.count()}")
    print(f"  - 임베딩 모델: {EMBEDDING_MODEL}")
    print(f"  - 거리 함수: cosine")
