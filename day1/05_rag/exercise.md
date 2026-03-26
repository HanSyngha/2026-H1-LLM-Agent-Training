# 실습: 사내 문서 RAG 챗봇 만들기

## 목표

RAG (Retrieval-Augmented Generation) 파이프라인을 구축하고, 자신만의 문서를 추가하여 문서 기반 Q&A 챗봇을 만듭니다.

---

## 요구사항

### 1. 문서 추가

`sample_docs/` 디렉토리에 자신만의 문서를 1개 이상 추가하세요.

**아이디어:**
- 팀 내부 규정/가이드
- 프로젝트 문서
- FAQ 모음
- 기술 문서

### 2. RAG 파이프라인 구축

```
문서 로드 → 텍스트 분할 → 임베딩 → 벡터DB 저장 → 검색 → 답변 생성
```

### 3. 질문-답변 테스트

추가한 문서에 대해 최소 5개 질문을 만들어 테스트하세요.

### 4. 청킹 전략 변경 및 비교

`chunk_size`와 `chunk_overlap`을 변경하며 검색 품질을 비교하세요.

| 설정 | chunk_size | chunk_overlap | 검색 품질 | 비고 |
|------|-----------|---------------|----------|------|
| 설정 1 | 200 | 20 | ? | 작은 청크 |
| 설정 2 | 500 | 50 | ? | 중간 청크 |
| 설정 3 | 1000 | 100 | ? | 큰 청크 |

---

## 체크리스트

- [ ] sample_docs에 자신만의 문서가 추가됨
- [ ] 문서가 정상적으로 로드됨
- [ ] 텍스트 분할이 적절히 수행됨
- [ ] 임베딩이 생성되고 벡터DB에 저장됨
- [ ] 유사도 검색이 관련 문서를 반환함
- [ ] RAG 체인이 문서 기반 답변을 생성함
- [ ] 청킹 전략을 변경하여 결과를 비교해봄

---

## 힌트

### 문서 로드하기
```python
# 단일 파일 로드
from langchain_community.document_loaders import TextLoader
loader = TextLoader("path/to/file.txt", encoding="utf-8")
docs = loader.load()

# 디렉토리 전체 로드
from langchain_community.document_loaders import DirectoryLoader
loader = DirectoryLoader("path/to/dir", glob="**/*.txt", loader_cls=TextLoader)
docs = loader.load()
```

### 청킹 전략 비교하기
```python
# 작은 청크: 정밀한 검색, 맥락 부족 가능
small_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)

# 큰 청크: 풍부한 맥락, 관련 없는 내용 포함 가능
large_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# 동일한 질문으로 검색 결과 비교
for splitter in [small_splitter, large_splitter]:
    chunks = splitter.split_documents(docs)
    vs = Chroma.from_documents(chunks, embeddings)
    results = vs.similarity_search("질문", k=3)
    print(f"청크 크기: {splitter._chunk_size}, 결과 수: {len(results)}")
    for r in results:
        print(f"  - {r.page_content[:50]}...")
```

### 검색 결과 품질 평가 포인트
- 질문에 관련된 내용이 검색 결과에 포함되는가?
- 불필요한 내용이 너무 많이 포함되지는 않는가?
- 답변이 문서의 내용을 정확히 반영하는가?
- 문서에 없는 내용을 생성(hallucination)하지는 않는가?

### 벡터DB 초기화
```python
# 기존 벡터DB를 삭제하고 새로 만들려면:
import shutil
shutil.rmtree("chroma_db", ignore_errors=True)
```

---

## 보너스 도전

- PDF, CSV 등 다른 형식의 문서도 로드해보기
- 검색된 문서의 출처를 답변에 포함하기
- 검색 결과에 점수(score)를 표시하기 (`similarity_search_with_score`)
- 멀티 벡터 검색 전략 시도 (ParentDocumentRetriever, MultiQueryRetriever)
- 대화 히스토리를 파일로 저장하여 세션 간 유지
