"""
RAG (Retrieval-Augmented Generation) 파이프라인 예제

RAG는 LLM의 답변을 외부 문서 기반으로 보강하는 기법입니다.
LLM이 학습하지 않은 사내 문서, 최신 정보 등을 활용하여 정확한 답변을 생성합니다.

RAG 파이프라인 전체 흐름:
1. 문서 로드 (Load): 텍스트 파일, PDF 등에서 문서를 읽어옴
2. 텍스트 분할 (Split): 긴 문서를 작은 청크(chunk)로 나눔
3. 임베딩 생성 (Embed): 각 청크를 벡터(숫자 배열)로 변환
4. 벡터 저장 (Store): 벡터를 벡터DB에 저장
5. 검색 (Retrieve): 질문과 유사한 청크를 벡터DB에서 검색
6. 답변 생성 (Generate): 검색된 청크를 참고하여 LLM이 답변 생성

실행 방법:
    python rag_pipeline.py

의존성:
    pip install langchain langchain-openai langchain-community chromadb
"""

import os
import sys

# ──────────────────────────────────────────────
# 공통 설정 로드
# ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from common.config import *

import httpx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ══════════════════════════════════════════════
# 1단계: 문서 로드 (Load)
# ══════════════════════════════════════════════
# 다양한 형식의 문서를 로드할 수 있습니다.
# TextLoader: 텍스트 파일 로드
# DirectoryLoader: 디렉토리 내 모든 파일 로드
# PyPDFLoader, CSVLoader 등도 사용 가능

def load_documents() -> list[Document]:
    """sample_docs 디렉토리에서 문서를 로드합니다."""
    print("\n[1단계] 문서 로드 중...")

    docs_dir = os.path.join(os.path.dirname(__file__), "sample_docs")

    # DirectoryLoader: 지정된 디렉토리의 모든 .txt 파일을 로드
    # glob: 로드할 파일 패턴 (여기서는 .txt 파일만)
    # loader_cls: 각 파일을 로드할 때 사용할 로더 클래스
    # loader_kwargs: 로더에 전달할 추가 인자
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )

    documents = loader.load()
    print(f"  -> {len(documents)}개 문서 로드 완료")
    for doc in documents:
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        print(f"     - {source} ({len(doc.page_content)}자)")

    return documents


# ══════════════════════════════════════════════
# 2단계: 텍스트 분할 (Split / Chunking)
# ══════════════════════════════════════════════
# 긴 문서를 작은 청크로 나누는 이유:
# - LLM의 컨텍스트 윈도우 제한
# - 더 정확한 유사도 검색 (관련 부분만 검색)
# - 임베딩 품질 향상 (짧은 텍스트가 더 정확한 벡터 표현)
#
# RecursiveCharacterTextSplitter 전략:
# - 여러 구분자를 순서대로 시도: ["\n\n", "\n", " ", ""]
# - 먼저 큰 단위(단락)로 나누고, 청크 크기를 초과하면 더 작은 단위로 나눔
# - 문맥을 최대한 유지하면서 분할

def split_documents(documents: list[Document]) -> list[Document]:
    """문서를 작은 청크로 분할합니다."""
    print("\n[2단계] 텍스트 분할 중...")

    # chunk_size: 각 청크의 최대 문자 수
    # chunk_overlap: 인접한 청크 간 겹치는 문자 수
    #   - 겹침이 있어야 청크 경계에서 정보가 끊기지 않음
    #   - 일반적으로 chunk_size의 10-20%가 적당
    # separators: 분할 시 사용할 구분자 (우선순위 순)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # 각 청크 최대 500자
        chunk_overlap=50,      # 인접 청크 간 50자 겹침
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = text_splitter.split_documents(documents)
    print(f"  -> {len(documents)}개 문서 → {len(chunks)}개 청크로 분할")

    # 분할 결과 샘플 출력
    print(f"\n  [청크 샘플 - 처음 3개]")
    for i, chunk in enumerate(chunks[:3]):
        preview = chunk.page_content[:80].replace("\n", " ")
        source = os.path.basename(chunk.metadata.get("source", "unknown"))
        print(f"  청크 {i+1} ({source}): {preview}...")

    return chunks


# ══════════════════════════════════════════════
# 3단계: 임베딩 생성 & 벡터DB 저장 (Embed & Store)
# ══════════════════════════════════════════════
# 임베딩(Embedding):
# - 텍스트를 고차원 벡터(숫자 배열)로 변환하는 과정
# - 의미가 유사한 텍스트는 벡터 공간에서 가까운 위치에 놓임
# - 이를 통해 "의미 기반 검색" 가능
#
# 벡터DB (ChromaDB):
# - 벡터를 효율적으로 저장하고 유사도 검색하는 데이터베이스
# - 코사인 유사도, 유클리드 거리 등으로 유사 벡터 검색
# - persist_directory: 로컬 파일 시스템에 영구 저장

def create_vectorstore(chunks: list[Document]) -> Chroma:
    """청크를 임베딩하여 벡터DB에 저장합니다."""
    print("\n[3단계] 임베딩 생성 & 벡터DB 저장 중...")

    # OpenAIEmbeddings: 게이트웨이를 통해 임베딩 모델 사용
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=GATEWAY_BASE_URL,
        api_key=GATEWAY_API_KEY,
        http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
    )

    # 벡터DB 저장 경로
    persist_dir = os.path.join(os.path.dirname(__file__), "chroma_db")

    # Chroma.from_documents: 문서 청크를 임베딩하여 ChromaDB에 저장
    # - documents: 임베딩할 문서 청크 리스트
    # - embedding: 사용할 임베딩 모델
    # - persist_directory: 벡터DB 영구 저장 경로
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )

    print(f"  -> {len(chunks)}개 청크를 벡터DB에 저장 완료")
    print(f"  -> 저장 경로: {persist_dir}")

    return vectorstore


# ══════════════════════════════════════════════
# 4단계: 검색 (Retrieve)
# ══════════════════════════════════════════════
# 사용자 질문을 임베딩하여 벡터DB에서 유사한 청크를 검색합니다.
# similarity_search: 코사인 유사도 기반으로 가장 유사한 k개 청크 반환

def test_retrieval(vectorstore: Chroma, query: str, k: int = 3):
    """벡터DB에서 유사 문서를 검색하여 결과를 출력합니다."""
    print(f"\n[4단계] 유사도 검색: '{query}'")

    # similarity_search: 질문과 가장 유사한 k개 청크 반환
    results = vectorstore.similarity_search(query, k=k)

    print(f"  -> {len(results)}개 관련 문서 검색됨:")
    for i, doc in enumerate(results):
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        preview = doc.page_content[:100].replace("\n", " ")
        print(f"\n  [{i+1}] 출처: {source}")
        print(f"      내용: {preview}...")

    return results


# ══════════════════════════════════════════════
# 5단계: 답변 생성 (Generate) - RAG 체인 구성
# ══════════════════════════════════════════════
# 검색된 문서(context)와 질문(question)을 LLM에 전달하여 답변을 생성합니다.

def create_rag_chain(vectorstore: Chroma):
    """RAG 체인을 구성합니다."""
    print("\n[5단계] RAG 체인 구성 중...")

    # LLM 설정
    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        base_url=GATEWAY_BASE_URL,
        api_key=GATEWAY_API_KEY,
        http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
        temperature=0.3,  # 사실 기반 답변이므로 낮은 temperature
    )

    # 검색기(Retriever) 생성
    # as_retriever: 벡터스토어를 검색기 인터페이스로 변환
    # search_kwargs: 검색 파라미터 (k: 반환할 문서 수)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # RAG 프롬프트 템플릿
    # context: 검색된 문서 내용이 삽입되는 위치
    # question: 사용자 질문이 삽입되는 위치
    prompt = ChatPromptTemplate.from_template(
        """다음 문서 내용을 참고하여 질문에 답변해주세요.
문서에 없는 내용은 "문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요.

참고 문서:
{context}

질문: {question}

답변:"""
    )

    def format_docs(docs: list[Document]) -> str:
        """검색된 문서들을 하나의 문자열로 합칩니다."""
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    # RAG 체인 구성 (LCEL 사용)
    # 1. retriever로 관련 문서 검색 → format_docs로 텍스트화 → context로 전달
    # 2. RunnablePassthrough()로 원래 질문을 그대로 question으로 전달
    # 3. prompt로 프롬프트 완성
    # 4. llm으로 답변 생성
    # 5. StrOutputParser로 문자열 추출
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("  -> RAG 체인 구성 완료")
    print("  -> 체인 흐름: 질문 → 검색(retriever) → 프롬프트 조합 → LLM → 답변")

    return rag_chain


# ══════════════════════════════════════════════
# 전체 파이프라인 실행
# ══════════════════════════════════════════════
def run_rag_pipeline():
    """전체 RAG 파이프라인을 실행합니다."""

    print("=" * 60)
    print("  RAG (Retrieval-Augmented Generation) 파이프라인")
    print("=" * 60)

    # 1단계: 문서 로드
    documents = load_documents()

    # 2단계: 텍스트 분할
    chunks = split_documents(documents)

    # 3단계: 임베딩 & 벡터DB 저장
    vectorstore = create_vectorstore(chunks)

    # 4단계: 검색 테스트
    test_retrieval(vectorstore, "회사 조직 구조가 어떻게 되나요?")
    test_retrieval(vectorstore, "사용하는 프로그래밍 언어는?")

    # 5단계: RAG 체인 구성
    rag_chain = create_rag_chain(vectorstore)

    # 질문-답변 테스트
    print("\n" + "=" * 60)
    print("  RAG 질문-답변 테스트")
    print("=" * 60)

    test_questions = [
        "회사의 조직 구조를 알려주세요.",
        "사내에서 사용하는 기술 스택은 무엇인가요?",
        "배포 프로세스는 어떻게 되나요?",
        "연차 휴가는 몇 일인가요?",
        "AI/ML팀의 팀장은 누구인가요?",
    ]

    for question in test_questions:
        print(f"\n{'─'*60}")
        print(f"Q: {question}")
        print(f"{'─'*60}")
        answer = rag_chain.invoke(question)
        print(f"A: {answer}")

    print(f"\n{'='*60}")
    print("  RAG 파이프라인 실행 완료!")
    print(f"{'='*60}")

    return vectorstore, rag_chain


if __name__ == "__main__":
    vectorstore, rag_chain = run_rag_pipeline()
