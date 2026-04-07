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

export default function Slide68_5Pillars() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">하네스 엔지니어링</Badge>
        <SlideH2 day2>하네스 5대 요소</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} style={{ marginTop: 8 }}>
          <svg viewBox="0 0 900 380" width="900" height="380" className="diagram-svg">
            {/* Pentagon shape */}
            <motion.polygon points="450,45 700,155 635,320 265,320 200,155" fill="rgba(139,92,246,.04)" stroke="rgba(139,92,246,.15)" strokeWidth={1.5}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }} />

            {/* Center */}
            <motion.g initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4, type: 'spring' }}>
              <circle cx={450} cy={200} r={40} fill="rgba(139,92,246,.12)" stroke="rgba(139,92,246,.3)" strokeWidth={1.5} />
              <text x={450} y={196} textAnchor="middle" fill="#6d28d9" fontWeight={700} fontSize={14}>하네스</text>
              <text x={450} y={212} textAnchor="middle" fill="#475569" fontSize={13}>5대 요소</text>
            </motion.g>

            {/* Lines from center to vertices */}
            <motion.line x1={450} y1={160} x2={450} y2={72} stroke="rgba(59,130,246,.3)" strokeWidth={1} strokeDasharray="4 3"
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.5, duration: 0.5 }} />
            <motion.line x1={485} y1={185} x2={670} y2={155} stroke="rgba(239,68,68,.3)" strokeWidth={1} strokeDasharray="4 3"
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.6, duration: 0.5 }} />
            <motion.line x1={475} y1={230} x2={610} y2={305} stroke="rgba(16,185,129,.3)" strokeWidth={1} strokeDasharray="4 3"
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.7, duration: 0.5 }} />
            <motion.line x1={425} y1={230} x2={290} y2={305} stroke="rgba(245,158,11,.3)" strokeWidth={1} strokeDasharray="4 3"
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.8, duration: 0.5 }} />
            <motion.line x1={415} y1={185} x2={230} y2={155} stroke="rgba(139,92,246,.3)" strokeWidth={1} strokeDasharray="4 3"
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 0.9, duration: 0.5 }} />

            {/* 1. Tool Orchestration (top) */}
            <AnimatedBox x={355} y={10} w={190} h={58} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={0.55}>
              <text x={450} y={36} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={14}>1. Tool Orchestration</text>
              <text x={450} y={55} textAnchor="middle" fill="#475569" fontSize={13}>Tool 선택/실행/결과 처리</text>
            </AnimatedBox>

            {/* 2. Guardrails (top right) */}
            <AnimatedBox x={630} y={120} w={180} h={58} fill="rgba(239,68,68,.08)" stroke="rgba(239,68,68,.5)" delay={0.65}>
              <text x={720} y={146} textAnchor="middle" fill="#dc2626" fontWeight={600} fontSize={14}>2. Guardrails</text>
              <text x={720} y={165} textAnchor="middle" fill="#475569" fontSize={13}>입/출력 검증, 차단</text>
            </AnimatedBox>

            {/* 3. Error Recovery (bottom right) */}
            <AnimatedBox x={555} y={290} w={180} h={58} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.75}>
              <text x={645} y={316} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={14}>3. Error Recovery</text>
              <text x={645} y={335} textAnchor="middle" fill="#475569" fontSize={13}>재시도, 대안 경로</text>
            </AnimatedBox>

            {/* 4. Observability (bottom left) */}
            <AnimatedBox x={165} y={290} w={180} h={58} fill="rgba(245,158,11,.08)" stroke="rgba(245,158,11,.5)" delay={0.85}>
              <text x={255} y={316} textAnchor="middle" fill="#92400e" fontWeight={600} fontSize={14}>4. Observability</text>
              <text x={255} y={335} textAnchor="middle" fill="#475569" fontSize={13}>로깅, 트레이싱, 비용</text>
            </AnimatedBox>

            {/* 5. Human-in-the-Loop (top left) */}
            <AnimatedBox x={90} y={120} w={190} h={58} fill="rgba(139,92,246,.08)" stroke="rgba(139,92,246,.5)" delay={0.95}>
              <text x={185} y={146} textAnchor="middle" fill="#6d28d9" fontWeight={600} fontSize={14}>5. Human-in-the-Loop</text>
              <text x={185} y={165} textAnchor="middle" fill="#475569" fontSize={13}>위험 작업 승인 요청</text>
            </AnimatedBox>
          </svg>
        </motion.div>
      </div>
    </div>
  );
}
