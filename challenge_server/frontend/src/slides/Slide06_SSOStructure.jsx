import { motion } from 'framer-motion';
import { Badge, SlideH2 } from './SlideLayout';

function AnimatedArrow({ x1, y1, x2, y2, delay, color = '#2563eb', dashed = false }) {
  return (
    <motion.line
      x1={x1} y1={y1} x2={x2} y2={y2}
      stroke={color} strokeWidth={2}
      strokeDasharray={dashed ? '6 4' : undefined}
      markerEnd={`url(#arrow-${color.replace('#', '')})`}
      initial={{ pathLength: 0, opacity: 0 }}
      animate={{ pathLength: 1, opacity: 1 }}
      transition={{ delay, duration: 0.6 }}
    />
  );
}

function AnimatedPath({ d, delay, color = '#2563eb', dashed = false }) {
  return (
    <motion.path
      d={d}
      stroke={color} strokeWidth={2} fill="none"
      strokeDasharray={dashed ? '6 4' : undefined}
      markerEnd={`url(#arrow-${color.replace('#', '')})`}
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

export default function Slide06_SSOStructure() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO</Badge>
        <SlideH2>사내 SSO 구조</SlideH2>
        <p>1회 요청으로 전체 인물정보 반환</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 860 280" width="860" height="280" className="diagram-svg">
            <defs>
              <marker id="arrow-2563eb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
              </marker>
              <marker id="arrow-059669" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669" />
              </marker>
            </defs>

            {/* Client */}
            <AnimatedBox x={20} y={70} w={180} h={80} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.4)" delay={0.4}>
              <text x={110} y={105} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={17}>클라이언트</text>
              <text x={110} y={128} textAnchor="middle" fill="#475569" fontSize={13}>(우리 서비스)</text>
            </AnimatedBox>

            {/* SSO Server */}
            <AnimatedBox x={290} y={70} w={200} h={80} fill="rgba(51,65,85,.08)" stroke="rgba(100,116,139,.3)" delay={0.6}>
              <text x={390} y={105} textAnchor="middle" fill="#1e293b" fontWeight={700} fontSize={17}>SSO 서버</text>
              <text x={390} y={128} textAnchor="middle" fill="#475569" fontSize={13}>/auth/login</text>
            </AnimatedBox>

            {/* HR DB */}
            <AnimatedBox x={580} y={70} w={180} h={80} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.8}>
              <text x={670} y={105} textAnchor="middle" fill="#047857" fontWeight={700} fontSize={17}>인사 DB</text>
              <text x={670} y={128} textAnchor="middle" fill="#475569" fontSize={13}>인물정보</text>
            </AnimatedBox>

            {/* Arrow: Client → SSO */}
            <AnimatedArrow x1={200} y1={110} x2={288} y2={110} delay={0.9} />
            <motion.text x={244} y={100} textAnchor="middle" fill="#2563eb" fontSize={12}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}>
              1. 로그인
            </motion.text>

            {/* Arrow: SSO → HR DB */}
            <AnimatedArrow x1={490} y1={110} x2={578} y2={110} delay={1.0} color="#059669" />
            <motion.text x={534} y={100} textAnchor="middle" fill="#059669" fontSize={12}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }}>
              2. 조회
            </motion.text>

            {/* Return arrow (dashed) */}
            <AnimatedPath d="M390,152 L390,210 L110,210 L110,152" delay={1.2} dashed />
            <motion.text x={250} y={200} textAnchor="middle" fill="#2563eb" fontSize={12}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.3 }}>
              3. 토큰 + 인물정보 반환
            </motion.text>

            {/* JSON result */}
            <AnimatedBox x={170} y={230} w={280} h={40} fill="rgba(245,158,11,.08)" stroke="rgba(245,158,11,.5)" delay={1.4}>
              <text x={310} y={256} textAnchor="middle" fill="#92400e" fontFamily="monospace" fontWeight={600} fontSize={14}>
                {'{name, dept, email, role, ...}'}
              </text>
            </AnimatedBox>
          </svg>
        </motion.div>
      </div>
    </div>
  );
}
