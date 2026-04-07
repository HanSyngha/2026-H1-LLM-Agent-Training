import { motion } from 'framer-motion';
import { Badge, SlideH2 } from './SlideLayout';

function AnimatedBox({ x, y, w, h, fill, stroke, delay, children }) {
  return (
    <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay, duration: 0.4 }}>
      <rect x={x} y={y} width={w} height={h} rx={12} fill={fill} stroke={stroke} strokeWidth={2} />
      {children}
    </motion.g>
  );
}

export default function Slide72_RAG() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">검색 전략</Badge>
        <SlideH2 day2>RAG 파이프라인</SlideH2>
        <p>Retrieval-Augmented Generation — 문서 기반 답변 생성의 전체 흐름</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 20 }}>
          <svg viewBox="0 0 1040 195" width="1040" height="195" className="diagram-svg">
            <defs>
              <marker id="arrow-blue-rag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
              </marker>
              <marker id="arrow-purple-rag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#8b5cf6" />
              </marker>
              <marker id="arrow-green-rag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
              </marker>
              <marker id="arrow-yellow-rag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#d97706" />
              </marker>
            </defs>

            {/* Step 1: Documents */}
            <AnimatedBox x={10} y={52} w={140} h={80} fill="rgba(51,65,85,.1)" stroke="rgba(100,116,139,.4)" delay={0.35}>
              <text x={80} y={80} textAnchor="middle" fill="#1e293b" fontWeight={600} fontSize={15}>문서</text>
              <text x={80} y={100} textAnchor="middle" fill="#475569" fontSize={13}>PDF, DB,</text>
              <text x={80} y={116} textAnchor="middle" fill="#475569" fontSize={13}>Confluence</text>
            </AnimatedBox>

            {/* Step 2: Chunking */}
            <AnimatedBox x={185} y={52} w={140} h={80} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={0.45}>
              <text x={255} y={80} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={15}>청킹</text>
              <text x={255} y={100} textAnchor="middle" fill="#475569" fontSize={13}>Chunk</text>
              <text x={255} y={116} textAnchor="middle" fill="#475569" fontSize={13}>512 tokens</text>
            </AnimatedBox>

            {/* Step 3: Embedding */}
            <AnimatedBox x={360} y={52} w={140} h={80} fill="rgba(139,92,246,.08)" stroke="rgba(139,92,246,.5)" delay={0.55}>
              <text x={430} y={80} textAnchor="middle" fill="#6d28d9" fontWeight={600} fontSize={15}>임베딩</text>
              <text x={430} y={100} textAnchor="middle" fill="#475569" fontSize={13}>text → vector</text>
              <text x={430} y={116} textAnchor="middle" fill="#475569" fontSize={13}>[0.12, ...]</text>
            </AnimatedBox>

            {/* Step 4: Vector DB */}
            <AnimatedBox x={535} y={52} w={140} h={80} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.65}>
              <text x={605} y={80} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={15}>Vector DB</text>
              <text x={605} y={100} textAnchor="middle" fill="#475569" fontSize={13}>저장 &</text>
              <text x={605} y={116} textAnchor="middle" fill="#475569" fontSize={13}>인덱싱</text>
            </AnimatedBox>

            {/* Step 5: Search */}
            <AnimatedBox x={710} y={52} w={140} h={80} fill="rgba(245,158,11,.08)" stroke="rgba(245,158,11,.5)" delay={0.75}>
              <text x={780} y={80} textAnchor="middle" fill="#92400e" fontWeight={600} fontSize={15}>검색</text>
              <text x={780} y={100} textAnchor="middle" fill="#475569" fontSize={13}>질의 →</text>
              <text x={780} y={116} textAnchor="middle" fill="#475569" fontSize={13}>Top-K 결과</text>
            </AnimatedBox>

            {/* Step 6: Generate */}
            <AnimatedBox x={880} y={42} w={145} h={95} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={0.85}>
              <text x={952} y={73} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={15}>LLM 생성</text>
              <text x={952} y={95} textAnchor="middle" fill="#475569" fontSize={13}>질문 + 검색결과</text>
              <text x={952} y={113} textAnchor="middle" fill="#475569" fontSize={13}>→ 최종 답변</text>
            </AnimatedBox>

            {/* Arrows */}
            <motion.line x1={152} y1={92} x2={183} y2={92} stroke="#3b82f6" strokeWidth={2} markerEnd="url(#arrow-blue-rag)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.5, duration: 0.3 }} />
            <motion.line x1={327} y1={92} x2={358} y2={92} stroke="#3b82f6" strokeWidth={2} markerEnd="url(#arrow-blue-rag)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.6, duration: 0.3 }} />
            <motion.line x1={502} y1={92} x2={533} y2={92} stroke="#8b5cf6" strokeWidth={2} markerEnd="url(#arrow-purple-rag)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.7, duration: 0.3 }} />
            <motion.line x1={677} y1={92} x2={708} y2={92} stroke="#10b981" strokeWidth={2} markerEnd="url(#arrow-green-rag)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.8, duration: 0.3 }} />
            <motion.line x1={852} y1={92} x2={878} y2={92} stroke="#3b82f6" strokeWidth={2} markerEnd="url(#arrow-blue-rag)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.9, duration: 0.3 }} />

            {/* Labels above */}
            <motion.text x={80} y={42} textAnchor="middle" fill="#475569" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.95 }}>Indexing Phase</motion.text>
            <motion.line x1={10} y1={46} x2={675} y2={46} stroke="rgba(148,163,184,.1)" strokeWidth={1} strokeDasharray="4 3"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }} />
            <motion.text x={780} y={42} textAnchor="middle" fill="#d97706" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.05 }}>Query Phase</motion.text>

            {/* User query input */}
            <motion.g initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.1 }}>
              <rect x={690} y={155} width={180} height={32} rx={12} fill="rgba(51,65,85,.1)" stroke="rgba(100,116,139,.4)" strokeWidth={1.5} />
              <text x={780} y={176} textAnchor="middle" fill="#1e293b" fontSize={13}>사용자 질문</text>
              <line x1={780} y1={155} x2={780} y2={134} stroke="#d97706" strokeWidth={1.5} markerEnd="url(#arrow-yellow-rag)" />
            </motion.g>
          </svg>
        </motion.div>
      </div>
    </div>
  );
}
