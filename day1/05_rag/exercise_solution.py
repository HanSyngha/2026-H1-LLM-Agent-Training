"""
RAG 실습 정답: sample_docs 기반 RAG 파이프라인 + 대화형 Q&A

sample_docs 디렉토리의 문서를 기반으로 RAG 파이프라인을 구축하고,
ChromaDB를 사용한 대화형 Q&A 챗봇을 구현합니다.

실행 방법:
    python exercise_solution.py

의존성:
    pip install langchain langchain-openai langchain-community chromadb
"""

import os
import sys
import shutil

# 공통 설정 로드
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
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


# ============================================================
# 1. RAG 파이프라인 구축
# ============================================================

def build_rag_pipeline(chunk_size: int = 500, chunk_overlap: int = 50):
    """RAG 파이프라인을 구축합니다.

    Args:
        chunk_size: 청크 크기 (기본 500자)
        chunk_overlap: 청크 간 겹침 (기본 50자)

    Returns:
        (vectorstore, rag_chain) 튜플
    """
    docs_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    persist_dir = os.path.join(os.path.dirname(__file__), "exercise_chroma_db")

    # 기존 벡터DB가 있으면 삭제합니다 (깨끗한 시작)
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)

    # --- 1단계: 문서 로드 ---
    print("[1단계] 문서를 로드합니다...")
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

    # --- 2단계: 텍스트 분할 ---
    print(f"\n[2단계] 텍스트를 분할합니다 (chunk_size={chunk_size}, overlap={chunk_overlap})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  -> {len(documents)}개 문서 -> {len(chunks)}개 청크로 분할 완료")

    # --- 3단계: 임베딩 + 벡터DB 저장 ---
    print("\n[3단계] 임베딩을 생성하고 벡터DB에 저장합니다...")
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=GATEWAY_BASE_URL,
        api_key=GATEWAY_API_KEY,
        http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    print(f"  -> {len(chunks)}개 청크를 벡터DB에 저장 완료")

    # --- 4단계: RAG 체인 구성 ---
    print("\n[4단계] RAG 체인을 구성합니다...")
    llm = ChatOpenAI(
        model=DEFAULT_MODEL,
        base_url=GATEWAY_BASE_URL,
        api_key=GATEWAY_API_KEY,
        http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
        temperature=0.3,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 대화형 RAG 프롬프트
    prompt = ChatPromptTemplate.from_template(
        """당신은 사내 문서를 기반으로 질문에 답변하는 AI 어시스턴트입니다.
아래 참고 문서의 내용만을 기반으로 정확하게 답변해주세요.
문서에 없는 내용은 "해당 정보는 문서에서 찾을 수 없습니다"라고 답변하세요.

참고 문서:
{context}

질문: {question}

답변:"""
    )

    def format_docs(docs: list[Document]) -> str:
        """검색된 문서들을 하나의 문자열로 합칩니다."""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            formatted.append(f"[문서 {i} - {source}]\n{doc.page_content}")
        return "\n\n---\n\n".join(formatted)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("  -> RAG 체인 구성 완료!")
    return vectorstore, rag_chain


# ============================================================
# 2. 검색 테스트
# ============================================================

def test_retrieval(vectorstore, queries: list[str]):
    """벡터DB 검색을 테스트합니다."""
    print("\n" + "=" * 60)
    print("  유사도 검색 테스트")
    print("=" * 60)

    for query in queries:
        print(f"\n  Q: {query}")
        # 유사도 점수와 함께 검색합니다
        results = vectorstore.similarity_search_with_score(query, k=3)
        for i, (doc, score) in enumerate(results, 1):
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            preview = doc.page_content[:80].replace("\n", " ")
            print(f"  [{i}] (유사도: {score:.4f}) {source}: {preview}...")


# ============================================================
# 3. 대화형 Q&A
# ============================================================

def interactive_qa(rag_chain):
    """대화형 Q&A 세션을 실행합니다."""
    print("\n" + "=" * 60)
    print("  대화형 RAG Q&A")
    print("=" * 60)
    print("질문을 입력하세요. '종료' 또는 'quit'으로 끝냅니다.\n")

    while True:
        try:
            question = input("Q: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n대화를 종료합니다.")
            break

        if not question:
            continue
        if question.lower() in ["종료", "quit", "exit", "q"]:
            print("대화를 종료합니다.")
            break

        # RAG 체인으로 답변을 생성합니다
        answer = rag_chain.invoke(question)
        print(f"A: {answer}\n")


# ============================================================
# 4. 청킹 전략 비교
# ============================================================

def compare_chunking_strategies():
    """청킹 전략을 비교 실험합니다."""
    print("\n" + "=" * 60)
    print("  청킹 전략 비교 실험")
    print("=" * 60)

    docs_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    loader = DirectoryLoader(
        docs_dir, glob="**/*.txt",
        loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=GATEWAY_BASE_URL,
        api_key=GATEWAY_API_KEY,
        http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
    )

    # 테스트 질문
    test_query = "회사의 조직 구조를 알려주세요"

    # 다양한 청킹 설정을 비교합니다
    configs = [
        {"chunk_size": 200, "chunk_overlap": 20, "label": "작은 청크"},
        {"chunk_size": 500, "chunk_overlap": 50, "label": "중간 청크"},
        {"chunk_size": 1000, "chunk_overlap": 100, "label": "큰 청크"},
    ]

    for config in configs:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
        )
        chunks = splitter.split_documents(documents)

        # 임시 벡터DB를 생성합니다
        temp_dir = os.path.join(os.path.dirname(__file__), f"temp_chroma_{config['chunk_size']}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        vs = Chroma.from_documents(chunks, embeddings, persist_directory=temp_dir)
        results = vs.similarity_search_with_score(test_query, k=3)

        print(f"\n  [{config['label']}] chunk_size={config['chunk_size']}, overlap={config['chunk_overlap']}")
        print(f"  총 청크 수: {len(chunks)}")
        for i, (doc, score) in enumerate(results, 1):
            preview = doc.page_content[:60].replace("\n", " ")
            print(f"    [{i}] 유사도: {score:.4f} | {preview}...")

        # 임시 디렉토리를 정리합니다
        shutil.rmtree(temp_dir, ignore_errors=True)


# ============================================================
# 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  RAG 실습 정답: 문서 기반 Q&A 챗봇")
    print("=" * 60)

    # RAG 파이프라인을 구축합니다
    vectorstore, rag_chain = build_rag_pipeline(chunk_size=500, chunk_overlap=50)

    # 검색 테스트를 수행합니다
    test_queries = [
        "회사의 조직 구조가 어떻게 되나요?",
        "사용하는 프로그래밍 언어는?",
        "연차 휴가는 몇 일인가요?",
    ]
    test_retrieval(vectorstore, test_queries)

    # RAG Q&A 테스트를 수행합니다
    print("\n" + "=" * 60)
    print("  RAG 질문-답변 테스트")
    print("=" * 60)

    auto_questions = [
        "회사의 조직 구조를 알려주세요.",
        "사내에서 사용하는 기술 스택은 무엇인가요?",
        "배포 프로세스는 어떻게 되나요?",
        "연차 휴가는 몇 일인가요?",
        "AI/ML팀의 팀장은 누구인가요?",
    ]

    for question in auto_questions:
        print(f"\n{'─' * 60}")
        print(f"Q: {question}")
        answer = rag_chain.invoke(question)
        print(f"A: {answer}")

    # 청킹 전략 비교를 수행합니다
    compare_chunking_strategies()

    # 대화형 모드를 시작합니다
    print("\n이제 직접 질문해보세요!")
    interactive_qa(rag_chain)

    print(f"\n{'=' * 60}")
    print("  RAG 실습 완료!")
    print(f"{'=' * 60}")
