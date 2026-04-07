import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide64_SemanticSearch() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">검색 전략</Badge>
        <SlideH2 day2>Semantic Search: 임베딩 기반</SlideH2>
        <p>텍스트를 벡터로 변환 → 유사도로 검색</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <CodeBlock>{`import chromadb

# 1. ChromaDB 컬렉션 생성
client = chromadb.Client()
collection = client.create_collection("company_docs")

# 2. 문서 임베딩 & 저장
collection.add(
    documents=["휴가 신청은 3일 전에...", "출장비 정산은..."],
    ids=["doc1", "doc2"],
)

# 3. 의미 기반 검색 (키워드 일치 불필요!)
results = collection.query(
    query_texts=["연차 사용 방법"],  # "휴가"와 유사!
    n_results=3,
)
print(results["documents"])`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
