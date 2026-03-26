"""
RAG + 대화형 챗봇 예제

RAG 파이프라인에 대화 히스토리를 추가하여,
문서 기반의 대화형 Q&A 챗봇을 구현합니다.

기본 RAG와의 차이점:
- 이전 대화를 기억하여 후속 질문에 대응
- "위에서 말한 것 중에서...", "그것 말고..." 같은 참조 표현 처리
- 대화 맥락을 고려한 질문 재구성 (standalone question)

실행 방법:
    python rag_chatbot.py

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
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# ══════════════════════════════════════════════
# 1. 벡터DB 준비 (문서 로드 → 분할 → 임베딩 → 저장)
# ══════════════════════════════════════════════

def prepare_vectorstore() -> Chroma:
    """문서를 로드하고 벡터DB를 준비합니다."""
    print("[준비] 벡터DB 구성 중...")

    docs_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    persist_dir = os.path.join(os.path.dirname(__file__), "chroma_db_chatbot")

    # 이미 벡터DB가 있으면 로드
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=GATEWAY_BASE_URL,
        api_key=GATEWAY_API_KEY,
        http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
    )

    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print("  -> 기존 벡터DB 로드")
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
        )
        return vectorstore

    # 문서 로드
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documents = loader.load()
    print(f"  -> {len(documents)}개 문서 로드")

    # 텍스트 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  -> {len(chunks)}개 청크로 분할")

    # 벡터DB 생성 및 저장
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    print(f"  -> 벡터DB 저장 완료: {persist_dir}")

    return vectorstore


# ══════════════════════════════════════════════
# 2. LLM 설정
# ══════════════════════════════════════════════
llm = ChatOpenAI(
    model=DEFAULT_MODEL,
    base_url=GATEWAY_BASE_URL,
    api_key=GATEWAY_API_KEY,
    http_client=httpx.Client(proxies=PROXY_URL, timeout=60.0),
    temperature=0.3,
)


# ══════════════════════════════════════════════
# 3. 질문 재구성 체인 (Contextualize Question)
# ══════════════════════════════════════════════
# 대화형 RAG의 핵심: 후속 질문을 독립적인 질문으로 변환
#
# 예시:
#   사용자: "개발팀 구조가 어떻게 되나요?"
#   AI: "개발팀은 프론트엔드팀, 백엔드팀..."
#   사용자: "거기서 가장 큰 팀은?"  ← "거기"가 뭘 의미하는지 모호
#   → 재구성: "개발본부에서 가장 인원이 많은 팀은?"  ← 독립적 질문으로 변환

contextualize_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """대화 히스토리와 최신 사용자 질문이 주어집니다.
사용자 질문이 대화 히스토리의 맥락을 참조할 수 있습니다.
대화 히스토리 없이도 이해할 수 있는 독립적인 질문으로 재구성해주세요.
질문을 재구성할 필요가 없다면 그대로 반환하세요.
질문만 반환하고 답변은 하지 마세요.""",
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# 질문 재구성 체인
contextualize_chain = contextualize_prompt | llm | StrOutputParser()


# ══════════════════════════════════════════════
# 4. RAG 답변 생성 프롬프트
# ══════════════════════════════════════════════
qa_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """당신은 사내 문서 기반 Q&A 어시스턴트입니다.
다음 참고 문서를 활용하여 질문에 답변해주세요.

규칙:
- 문서에 있는 정보만을 기반으로 답변하세요.
- 문서에 없는 내용은 "문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요.
- 답변은 한국어로 작성하세요.
- 답변은 명확하고 구조적으로 작성하세요.

참고 문서:
{context}""",
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])


# ══════════════════════════════════════════════
# 5. RAG 챗봇 클래스
# ══════════════════════════════════════════════

class RAGChatbot:
    """대화 히스토리를 유지하는 RAG 챗봇"""

    def __init__(self, vectorstore: Chroma):
        self.vectorstore = vectorstore
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        self.chat_history: list = []  # 대화 히스토리

        # RAG 답변 체인
        self.qa_chain = qa_prompt | llm | StrOutputParser()

    def _format_docs(self, docs: list[Document]) -> str:
        """검색된 문서들을 하나의 문자열로 합칩니다."""
        return "\n\n---\n\n".join(doc.page_content for doc in docs)

    def _contextualize_question(self, question: str) -> str:
        """대화 맥락을 고려하여 질문을 재구성합니다."""
        if not self.chat_history:
            # 첫 질문이면 재구성 불필요
            return question

        # LLM을 사용하여 질문 재구성
        standalone_question = contextualize_chain.invoke({
            "chat_history": self.chat_history,
            "question": question,
        })
        return standalone_question

    def ask(self, question: str) -> str:
        """질문에 대한 답변을 생성합니다.

        Args:
            question: 사용자 질문

        Returns:
            RAG 기반 답변 문자열
        """
        # 1. 질문 재구성 (대화 맥락 반영)
        standalone_question = self._contextualize_question(question)
        if standalone_question != question:
            print(f"  [재구성된 질문] {standalone_question}")

        # 2. 관련 문서 검색
        retrieved_docs = self.retriever.invoke(standalone_question)
        context = self._format_docs(retrieved_docs)

        # 검색된 문서 출처 표시
        sources = set()
        for doc in retrieved_docs:
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            sources.add(source)
        print(f"  [참조 문서] {', '.join(sources)}")

        # 3. 답변 생성
        answer = self.qa_chain.invoke({
            "context": context,
            "chat_history": self.chat_history,
            "question": question,
        })

        # 4. 대화 히스토리 업데이트
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))

        return answer

    def clear_history(self):
        """대화 히스토리를 초기화합니다."""
        self.chat_history = []
        print("  대화 히스토리가 초기화되었습니다.")

    def show_history(self):
        """대화 히스토리를 출력합니다."""
        print(f"\n{'─'*40}")
        print(f"  대화 히스토리 ({len(self.chat_history) // 2}턴)")
        print(f"{'─'*40}")
        for msg in self.chat_history:
            role = "Q" if isinstance(msg, HumanMessage) else "A"
            content = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
            print(f"  [{role}] {content}")
        print(f"{'─'*40}")


# ══════════════════════════════════════════════
# 6. 대화형 인터페이스
# ══════════════════════════════════════════════
def interactive_rag_chat(chatbot: RAGChatbot):
    """대화형 RAG 챗봇을 실행합니다."""

    print("\n" + "=" * 60)
    print("  사내 문서 RAG 챗봇")
    print("=" * 60)
    print()
    print("  사내 문서를 기반으로 질문에 답변합니다.")
    print()
    print("  명령어:")
    print("    /history  - 대화 히스토리 보기")
    print("    /clear    - 대화 히스토리 초기화")
    print("    /quit     - 종료")
    print()
    print("─" * 60)

    while True:
        try:
            user_input = input("\nQ: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n챗봇을 종료합니다!")
            break

        if not user_input:
            continue

        if user_input == "/history":
            chatbot.show_history()
            continue
        elif user_input == "/clear":
            chatbot.clear_history()
            continue
        elif user_input in ["/quit", "/exit", "종료"]:
            print("\n챗봇을 종료합니다!")
            break

        try:
            answer = chatbot.ask(user_input)
            print(f"\nA: {answer}")
        except Exception as e:
            print(f"\n오류 발생: {e}")


# ══════════════════════════════════════════════
# 7. 실행
# ══════════════════════════════════════════════
if __name__ == "__main__":
    # 벡터DB 준비
    vectorstore = prepare_vectorstore()

    # 챗봇 인스턴스 생성
    chatbot = RAGChatbot(vectorstore)

    # 데모 모드: 대화 맥락 유지 기능 확인
    print("\n" + "=" * 60)
    print("  데모 모드: 대화 맥락 유지 기능 확인")
    print("=" * 60)

    demo_questions = [
        "회사의 개발본부 조직 구조를 알려줘",
        "그중에서 가장 인원이 많은 팀은?",
        "그 팀의 팀장은 누구야?",
        "회사에서 사용하는 배포 전략은 뭐야?",
    ]

    for q in demo_questions:
        print(f"\n{'─'*60}")
        print(f"Q: {q}")
        answer = chatbot.ask(q)
        print(f"\nA: {answer}")

    chatbot.show_history()

    # 대화 히스토리 초기화 후 대화형 모드 시작
    chatbot.clear_history()
    print("\n이제 직접 질문해보세요!")
    interactive_rag_chat(chatbot)
