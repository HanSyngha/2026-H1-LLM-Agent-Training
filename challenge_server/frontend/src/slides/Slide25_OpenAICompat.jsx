import { motion } from 'framer-motion';
import { Badge, SlideH2, Box } from './SlideLayout';

function AnimatedBox({ x, y, w, h, fill, stroke, delay, children }) {
  return (
    <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay, duration: 0.4 }}>
      <rect x={x} y={y} width={w} height={h} rx={12} fill={fill} stroke={stroke} strokeWidth={2} />
      {children}
    </motion.g>
  );
}

function AnimatedArrow({ x1, y1, x2, y2, delay, color = '#2563eb' }) {
  return (
    <motion.line
      x1={x1} y1={y1} x2={x2} y2={y2}
      stroke={color} strokeWidth={2} markerEnd={`url(#arrow-${color.replace('#', '')})`}
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 1 }}
      transition={{ delay, duration: 0.6 }}
    />
  );
}

function AnimatedPath({ d, delay, color = '#7c3aed' }) {
  return (
    <motion.path
      d={d}
      stroke={color} strokeWidth={2} fill="none"
      markerEnd={`url(#arrow-${color.replace('#', '')})`}
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 1 }}
      transition={{ delay, duration: 0.6 }}
    />
  );
}

export default function Slide25_OpenAICompat() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">OpenAI Compatible</Badge>
        <SlideH2>OpenAI Compatible 표준이란?</SlideH2>
        <p>OpenAI가 정의한 API 인터페이스를 <strong style={{ color: '#2563eb' }}>다른 모델/서비스</strong>도 동일하게 지원</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 12 }}>
          <svg viewBox="0 0 900 230" width="900" height="230" className="diagram-svg">
            <defs>
              <marker id="arrow-7c3aed-oc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
              </marker>
              <marker id="arrow-2563eb-oc" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
              </marker>
            </defs>

            {/* Your Code */}
            <AnimatedBox x={20} y={70} w={180} h={80} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.4)" delay={0.4}>
              <text x={110} y={104} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={15}>동일한 코드</text>
              <text x={110} y={124} textAnchor="middle" fill="#475569" fontSize={13}>base_url 만 변경</text>
            </AnimatedBox>

            {/* Gateway */}
            <AnimatedBox x={290} y={55} w={190} h={110} fill="rgba(124,58,237,.08)" stroke="rgba(124,58,237,.5)" delay={0.6}>
              <text x={385} y={94} textAnchor="middle" fill="#6d28d9" fontWeight={700} fontSize={15}>Gateway</text>
              <text x={385} y={114} textAnchor="middle" fill="#475569" fontSize={13}>OpenAI Compatible</text>
              <text x={385} y={132} textAnchor="middle" fill="#475569" fontSize={13}>인터페이스</text>
            </AnimatedBox>

            {/* Arrow code → gateway */}
            <AnimatedArrow x1={202} y1={110} x2={288} y2={110} delay={0.7} />

            {/* LLMs */}
            {[
              { y: 10, label: 'OpenAI GPT-4o', color: '#10b981', delay: 0.8 },
              { y: 68, label: 'Claude Sonnet', color: '#ea580c', delay: 0.9 },
              { y: 126, label: 'Gemini', color: '#0891b2', delay: 1.0 },
              { y: 184, label: 'Llama / Local', color: '#d97706', delay: 1.1 },
            ].map((item, i) => (
              <AnimatedBox key={i} x={590} y={item.y} w={180} h={45} fill="rgba(51,65,85,.06)" stroke="rgba(100,116,139,.25)" delay={item.delay}>
                <text x={680} y={item.y + 28} textAnchor="middle" fill={item.color} fontWeight={600} fontSize={14}>{item.label}</text>
              </AnimatedBox>
            ))}

            {/* Arrows gateway → LLMs */}
            <AnimatedPath d="M482,88 Q530,38 588,32" delay={1.2} />
            <AnimatedPath d="M482,100 L588,90" delay={1.3} />
            <AnimatedPath d="M482,115 L588,148" delay={1.4} />
            <AnimatedPath d="M482,128 Q530,185 588,206" delay={1.5} />
          </svg>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.2 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.92em' }}>
            <strong>핵심 가치:</strong> 모델을 바꿔도 코드 변경이 최소화됩니다. <code>base_url</code>만 변경하면 됩니다.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
