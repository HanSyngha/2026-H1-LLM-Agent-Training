import { motion } from 'framer-motion';
import { Badge, SlideH2 } from './SlideLayout';

function AnimatedBox({ x, y, w, h, fill, stroke, delay, children }) {
  return (
    <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay, duration: 0.4 }}>
      <rect x={x} y={y} width={w} height={h} rx={12} fill={fill} stroke={stroke} strokeWidth={1.5} />
      {children}
    </motion.g>
  );
}

export default function Slide58_MultiIteration() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop</Badge>
        <SlideH2 day2>Multi-iteration 아키텍처</SlideH2>
        <p>Claude Code 방식 — 여러 Tool을 연쇄 호출하여 복잡한 작업 수행</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 950 280" width="950" height="280" className="diagram-svg">
            <defs>
              <marker id="arrow-blue-mi" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
              </marker>
              <marker id="arrow-purple-mi" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#8b5cf6" />
              </marker>
              <marker id="arrow-green-mi" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
              </marker>
            </defs>

            {/* User question */}
            <AnimatedBox x={10} y={10} w={400} h={36} fill="rgba(51,65,85,.1)" stroke="rgba(100,116,139,.4)" delay={0.3}>
              <text x={210} y={33} textAnchor="middle" fill="#1e293b" fontSize={14}>"프로젝트에서 TODO 찾아서 이슈 생성해줘"</text>
            </AnimatedBox>

            {/* Iteration boxes */}
            <AnimatedBox x={10} y={62} w={200} h={50} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={0.4}>
              <text x={110} y={82} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={13}>반복 1: glob("**/*.py")</text>
              <text x={110} y={100} textAnchor="middle" fill="#475569" fontSize={13}>→ 파일 목록 반환</text>
            </AnimatedBox>

            <AnimatedBox x={245} y={62} w={220} h={50} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={0.55}>
              <text x={355} y={82} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={13}>반복 2: grep("TODO", files)</text>
              <text x={355} y={100} textAnchor="middle" fill="#475569" fontSize={13}>→ TODO 항목들 반환</text>
            </AnimatedBox>

            <AnimatedBox x={500} y={62} w={200} h={50} fill="rgba(139,92,246,.08)" stroke="rgba(139,92,246,.5)" delay={0.7}>
              <text x={600} y={82} textAnchor="middle" fill="#6d28d9" fontWeight={600} fontSize={13}>반복 3: read_file(...)</text>
              <text x={600} y={100} textAnchor="middle" fill="#475569" fontSize={13}>→ 컨텍스트 확인</text>
            </AnimatedBox>

            <AnimatedBox x={735} y={62} w={200} h={50} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.85}>
              <text x={835} y={82} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={13}>반복 4: create_issue(...)</text>
              <text x={835} y={100} textAnchor="middle" fill="#475569" fontSize={13}>→ 이슈 생성 완료</text>
            </AnimatedBox>

            {/* Arrows between iterations */}
            <motion.line x1={212} y1={87} x2={243} y2={87} stroke="#3b82f6" strokeWidth={2} markerEnd="url(#arrow-blue-mi)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.6, duration: 0.3 }} />
            <motion.line x1={467} y1={87} x2={498} y2={87} stroke="#8b5cf6" strokeWidth={2} markerEnd="url(#arrow-purple-mi)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.75, duration: 0.3 }} />
            <motion.line x1={702} y1={87} x2={733} y2={87} stroke="#10b981" strokeWidth={2} markerEnd="url(#arrow-green-mi)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.9, duration: 0.3 }} />

            {/* Final response */}
            <AnimatedBox x={220} y={130} w={500} h={40} fill="rgba(51,65,85,.1)" stroke="rgba(100,116,139,.4)" delay={1.0}>
              <text x={470} y={155} textAnchor="middle" fill="#10b981" fontSize={14}>반복 5: "3개의 TODO를 찾아 이슈를 생성했습니다." (종료)</text>
            </AnimatedBox>

            {/* Growing message bars */}
            <motion.text x={40} y={198} fill="#475569" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.1 }}>messages 배열이 매 반복마다 성장:</motion.text>

            <motion.rect x={40} y={208} width={100} height={11} rx={3} fill="rgba(59,130,246,.3)"
              initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 1.2, duration: 0.3 }} style={{ transformOrigin: 'left' }} />
            <motion.rect x={40} y={224} width={250} height={11} rx={3} fill="rgba(59,130,246,.4)"
              initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 1.3, duration: 0.3 }} style={{ transformOrigin: 'left' }} />
            <motion.rect x={40} y={240} width={430} height={11} rx={3} fill="rgba(59,130,246,.5)"
              initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 1.4, duration: 0.3 }} style={{ transformOrigin: 'left' }} />
            <motion.rect x={40} y={256} width={630} height={11} rx={3} fill="rgba(59,130,246,.6)"
              initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 1.5, duration: 0.3 }} style={{ transformOrigin: 'left' }} />
            <motion.text x={690} y={266} fill="#475569" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.6 }}>context grows →</motion.text>
          </svg>
        </motion.div>

        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.7 }}
          style={{ fontSize: '.88em', color: '#64748b' }}>
          핵심: max_iterations로 무한 루프 방지, 각 단계의 결과가 다음 판단의 입력
        </motion.p>
      </div>
    </div>
  );
}
