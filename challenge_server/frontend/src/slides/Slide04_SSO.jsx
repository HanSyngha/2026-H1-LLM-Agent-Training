import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider } from './SlideLayout';

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

function AnimatedBox({ x, y, w, h, fill, stroke, delay, children }) {
  return (
    <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay, duration: 0.4 }}>
      <rect x={x} y={y} width={w} height={h} rx={14} fill={fill} stroke={stroke} strokeWidth={2} />
      {children}
    </motion.g>
  );
}

export default function Slide04_SSO() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO</Badge>
        <SlideH2>SSO란?</SlideH2>
        <p>Single Sign-On — 한 번의 로그인으로 여러 서비스에 접근합니다</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 860 280" width="860" height="280" className="diagram-svg">
            <defs>
              <marker id="arrow-2563eb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
              </marker>
            </defs>

            {/* 사용자 */}
            <AnimatedBox x={20} y={90} w={180} h={80} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.4)" delay={0.4}>
              <text x={110} y={125} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={17}>사용자 로그인 (1회)</text>
              <text x={110} y={148} textAnchor="middle" fill="#475569" fontSize={13}>ID/PW 입력</text>
            </AnimatedBox>

            {/* SSO 서버 */}
            <AnimatedBox x={290} y={90} w={200} h={80} fill="rgba(51,65,85,.08)" stroke="rgba(100,116,139,.3)" delay={0.6}>
              <text x={390} y={125} textAnchor="middle" fill="#1e293b" fontWeight={700} fontSize={17}>SSO 서버</text>
              <text x={390} y={148} textAnchor="middle" fill="#475569" fontSize={13}>토큰 발급</text>
            </AnimatedBox>

            {/* 서비스 A/B/C */}
            {[{ y: 20, label: '서비스 A' }, { y: 105, label: '서비스 B' }, { y: 190, label: '서비스 C' }].map((s, i) => (
              <AnimatedBox key={i} x={590} y={s.y} w={170} h={60} fill="rgba(51,65,85,.06)" stroke="rgba(100,116,139,.25)" delay={0.8 + i * 0.15}>
                <text x={675} y={s.y + 35} textAnchor="middle" fill="#1e293b" fontWeight={600} fontSize={15}>{s.label}</text>
              </AnimatedBox>
            ))}

            {/* 화살표 */}
            <AnimatedArrow x1={200} y1={130} x2={288} y2={130} delay={0.7} />
            <AnimatedArrow x1={490} y1={110} x2={588} y2={50} delay={1.1} />
            <AnimatedArrow x1={490} y1={130} x2={588} y2={135} delay={1.2} />
            <AnimatedArrow x1={490} y1={150} x2={588} y2={220} delay={1.3} />

            {/* 레이블 */}
            <motion.text x={540} y={95} textAnchor="middle" fill="#2563eb" fontSize={14} fontWeight={600}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.4 }}>
              같은 토큰
            </motion.text>

            {/* 토큰 아이콘 */}
            <motion.circle cx={390} cy={200} r={22} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.3)" strokeWidth={1.5}
              initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 1.5, type: 'spring' }} />
            <motion.text x={390} y={207} textAnchor="middle" fontSize={22}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.6 }}>
              🔑
            </motion.text>
          </svg>
        </motion.div>
      </div>
    </div>
  );
}
