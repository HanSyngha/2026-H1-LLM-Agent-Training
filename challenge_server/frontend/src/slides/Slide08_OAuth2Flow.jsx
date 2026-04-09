import { motion } from 'framer-motion';
import { Badge, SlideH2 } from './SlideLayout';

function AnimatedBox({ x, y, w, h, fill, stroke, delay, children }) {
  return (
    <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay, duration: 0.4 }}>
      <rect x={x} y={y} width={w} height={h} rx={14} fill={fill} stroke={stroke} strokeWidth={2} />
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

export default function Slide08_OAuth2Flow() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO</Badge>
        <SlideH2>OAuth2 Authorization Code Flow</SlideH2>
        <p>"대신 로그인해주는" 프로토콜 -- 4단계 흐름</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 12 }}>
          <svg viewBox="0 0 960 320" width="960" height="320" className="diagram-svg">
            <defs>
              <marker id="arrow-2563eb-o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
              </marker>
              <marker id="arrow-059669-o" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669" />
              </marker>
              <marker id="arrow-7c3aed" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
              </marker>
            </defs>

            {/* Step 1: /authorize */}
            <AnimatedBox x={20} y={20} w={200} h={70} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.4)" delay={0.4}>
              <text x={120} y={50} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={16}>1. /authorize</text>
              <text x={120} y={72} textAnchor="middle" fill="#475569" fontSize={13}>로그인 페이지로 이동</text>
            </AnimatedBox>

            {/* Step 2: Login */}
            <AnimatedBox x={260} y={20} w={200} h={70} fill="rgba(51,65,85,.08)" stroke="rgba(100,116,139,.3)" delay={0.6}>
              <text x={360} y={50} textAnchor="middle" fill="#1e293b" fontWeight={700} fontSize={16}>2. 로그인</text>
              <text x={360} y={72} textAnchor="middle" fill="#475569" fontSize={13}>ID/PW 입력</text>
            </AnimatedBox>

            {/* Step 3: callback?code= */}
            <AnimatedBox x={500} y={20} w={200} h={70} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.8}>
              <text x={600} y={50} textAnchor="middle" fill="#047857" fontWeight={700} fontSize={16}>3. callback?code=</text>
              <text x={600} y={72} textAnchor="middle" fill="#475569" fontSize={13}>인가 코드 수신</text>
            </AnimatedBox>

            {/* Step 4: POST /token */}
            <AnimatedBox x={740} y={20} w={200} h={70} fill="rgba(124,58,237,.08)" stroke="rgba(124,58,237,.5)" delay={1.0}>
              <text x={840} y={50} textAnchor="middle" fill="#6d28d9" fontWeight={700} fontSize={16}>4. POST /token</text>
              <text x={840} y={72} textAnchor="middle" fill="#475569" fontSize={13}>{'code → access_token'}</text>
            </AnimatedBox>

            {/* Arrows between steps */}
            <AnimatedArrow x1={222} y1={55} x2={258} y2={55} delay={0.7} />
            <AnimatedArrow x1={462} y1={55} x2={498} y2={55} delay={0.9} />
            <AnimatedArrow x1={702} y1={55} x2={738} y2={55} delay={1.1} color="#059669" />

            {/* Result box: GET /userinfo */}
            <AnimatedBox x={260} y={130} w={680} h={70} fill="rgba(245,158,11,.08)" stroke="rgba(245,158,11,.5)" delay={1.2}>
              <text x={600} y={158} textAnchor="middle" fill="#92400e" fontWeight={700} fontSize={16}>5. GET /userinfo (access_token으로 호출)</text>
              <text x={600} y={180} textAnchor="middle" fill="#475569" fontSize={14}>{'-> {name: "홍길동", dept: "개발팀", email: "..."}'}</text>
            </AnimatedBox>

            {/* Arrow from token to userinfo */}
            <AnimatedPath d="M840,92 L840,115 L600,115 L600,128" delay={1.3} />

            {/* Key point */}
            <AnimatedBox x={260} y={235} w={680} h={55} fill="rgba(51,65,85,.08)" stroke="rgba(100,116,139,.3)" delay={1.5}>
              <text x={600} y={268} textAnchor="middle" fill="#1e293b" fontWeight={600} fontSize={15}>핵심: access_token만으로는 사용자가 누군지 모릅니다 → /userinfo API 호출 필수</text>
            </AnimatedBox>
          </svg>
        </motion.div>
      </div>
    </div>
  );
}
