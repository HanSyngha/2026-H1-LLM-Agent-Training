import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

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

export default function Slide23_APIBasic() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">API</Badge>
        <SlideH2>REST API란?</SlideH2>
        <p>HTTP 요청을 보내면, 서버가 응답하는 구조</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 12 }}>
          <svg viewBox="0 0 900 210" width="900" height="210" className="diagram-svg">
            <defs>
              <marker id="arrow-2563eb-api" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
              </marker>
              <marker id="arrow-10b981" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
              </marker>
            </defs>

            {/* Client top */}
            <AnimatedBox x={30} y={30} w={160} h={60} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.4)" delay={0.4}>
              <text x={110} y={57} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={15}>Client</text>
              <text x={110} y={76} textAnchor="middle" fill="#475569" fontSize={13}>(Python)</text>
            </AnimatedBox>

            {/* Server top */}
            <AnimatedBox x={650} y={30} w={160} h={60} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.5}>
              <text x={730} y={57} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={15}>Server</text>
              <text x={730} y={76} textAnchor="middle" fill="#475569" fontSize={13}>(API)</text>
            </AnimatedBox>

            {/* Request arrow */}
            <AnimatedArrow x1={192} y1={50} x2={648} y2={50} delay={0.6} />

            {/* HTTP POST label */}
            <AnimatedBox x={330} y={30} w={180} h={44} fill="rgba(51,65,85,.08)" stroke="rgba(100,116,139,.3)" delay={0.7}>
              <text x={420} y={50} textAnchor="middle" fill="#d97706" fontSize={14} fontWeight={600}>HTTP POST</text>
              <text x={420} y={66} textAnchor="middle" fill="#475569" fontSize={13}>JSON body</text>
            </AnimatedBox>

            {/* Response arrow */}
            <motion.line x1={648} y1={74} x2={192} y2={74} stroke="#10b981" strokeWidth={2}
              markerEnd="url(#arrow-10b981)"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 0.8, duration: 0.6 }} />

            {/* Client bottom */}
            <AnimatedBox x={30} y={125} w={160} h={60} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.4)" delay={0.9}>
              <text x={110} y={160} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={15}>Client</text>
            </AnimatedBox>

            {/* Server bottom */}
            <AnimatedBox x={650} y={125} w={160} h={60} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={1.0}>
              <text x={730} y={160} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={15}>Server</text>
            </AnimatedBox>

            {/* Response label */}
            <AnimatedBox x={310} y={133} w={220} h={44} fill="rgba(51,65,85,.08)" stroke="rgba(100,116,139,.3)" delay={1.1}>
              <text x={420} y={153} textAnchor="middle" fill="#10b981" fontSize={14} fontWeight={600}>HTTP 200 OK</text>
              <text x={420} y={169} textAnchor="middle" fill="#475569" fontSize={13}>JSON response</text>
            </AnimatedBox>

            {/* Response arrow bottom */}
            <motion.line x1={648} y1={157} x2={192} y2={157} stroke="#10b981" strokeWidth={2}
              markerEnd="url(#arrow-10b981)"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ delay: 1.2, duration: 0.6 }} />
          </svg>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.0 }}>
          <CodeBlock lang="python">{`import requests

response = requests.post(
    "https://api.example.com/v1/chat",
    headers={"Authorization": f"Bearer {api_key}"},
    json={"messages": messages}
)
result = response.json()`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
