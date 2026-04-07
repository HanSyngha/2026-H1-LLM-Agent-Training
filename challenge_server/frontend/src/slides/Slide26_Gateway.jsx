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

function AnimatedLine({ d, stroke, delay, isPath }) {
  if (isPath) {
    return (
      <motion.path
        d={d} stroke={stroke} strokeWidth={2} fill="none" markerEnd="url(#arrowPurple)"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ delay, duration: 0.6 }}
      />
    );
  }
  return null;
}

export default function Slide26_Gateway() {
  const llms = [
    { y: 10, label: 'OpenAI GPT-4o', color: '#10b981' },
    { y: 68, label: 'Claude Sonnet', color: '#ea580c' },
    { y: 126, label: 'Gemini', color: '#0891b2' },
    { y: 184, label: 'Llama / Local', color: '#d97706' },
  ];

  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">OpenAI Compatible</Badge>
        <SlideH2>OpenAI Compatible 표준이란?</SlideH2>
        <motion.p
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ color: '#475569' }}
        >
          OpenAI가 정의한 API 인터페이스를 <strong style={{ color: '#2563eb' }}>다른 모델/서비스</strong>도 동일하게 지원
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 900 230" width="900" height="230" className="diagram-svg">
            <defs>
              <marker id="arrowBlue26" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
              </marker>
              <marker id="arrowPurple" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
              </marker>
            </defs>

            {/* Your Code */}
            <AnimatedBox x={20} y={70} w={180} h={80} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.5)" delay={0.4}>
              <text x={110} y={104} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={15}>동일한 코드</text>
              <text x={110} y={124} textAnchor="middle" fill="#475569" fontSize={13}>base_url 만 변경</text>
            </AnimatedBox>

            {/* Gateway */}
            <AnimatedBox x={290} y={55} w={190} h={110} fill="rgba(124,58,237,.08)" stroke="rgba(124,58,237,.5)" delay={0.6}>
              <text x={385} y={94} textAnchor="middle" fill="#6d28d9" fontWeight={700} fontSize={15}>Gateway</text>
              <text x={385} y={114} textAnchor="middle" fill="#475569" fontSize={13}>OpenAI Compatible</text>
              <text x={385} y={132} textAnchor="middle" fill="#475569" fontSize={13}>인터페이스</text>
            </AnimatedBox>

            {/* Arrow: Code -> Gateway */}
            <motion.line
              x1={202} y1={110} x2={288} y2={110}
              stroke="#2563eb" strokeWidth={2} markerEnd="url(#arrowBlue26)"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 0.7, duration: 0.6 }}
            />

            {/* LLMs */}
            {llms.map((llm, i) => (
              <AnimatedBox key={i} x={590} y={llm.y} w={180} h={45} fill="rgba(51,65,85,.06)" stroke="rgba(100,116,139,.25)" delay={0.8 + i * 0.12}>
                <text x={680} y={llm.y + 28} textAnchor="middle" fill={llm.color} fontWeight={600} fontSize={14}>{llm.label}</text>
              </AnimatedBox>
            ))}

            {/* Arrows: Gateway -> LLMs */}
            <motion.path d="M482,88 Q530,38 588,32" stroke="#7c3aed" strokeWidth={2} fill="none" markerEnd="url(#arrowPurple)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.2, duration: 0.5 }} />
            <motion.path d="M482,100 L588,90" stroke="#7c3aed" strokeWidth={2} fill="none" markerEnd="url(#arrowPurple)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.3, duration: 0.5 }} />
            <motion.path d="M482,115 L588,148" stroke="#7c3aed" strokeWidth={2} fill="none" markerEnd="url(#arrowPurple)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.4, duration: 0.5 }} />
            <motion.path d="M482,128 Q530,185 588,206" stroke="#7c3aed" strokeWidth={2} fill="none" markerEnd="url(#arrowPurple)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.5, duration: 0.5 }} />
          </svg>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.0 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.92em' }}>
            <strong>핵심 가치:</strong> 모델을 바꿔도 코드 변경이 최소화됩니다. <code>base_url</code>만 변경하면 됩니다.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
