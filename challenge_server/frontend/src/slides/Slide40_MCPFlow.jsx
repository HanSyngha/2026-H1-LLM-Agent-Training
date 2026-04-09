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

export default function Slide40_MCPFlow() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">MCP</Badge>
        <SlideH2>MCP + LLM 연동 흐름도</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} style={{ marginTop: 8 }}>
          <svg viewBox="0 0 950 340" width="950" height="340" className="diagram-svg">
            <defs>
              <marker id="arrowB40" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
              </marker>
              <marker id="arrowG40" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
              </marker>
            </defs>

            {/* User question */}
            <AnimatedBox x={310} y={10} w={320} h={40} fill="rgba(51,65,85,.06)" stroke="rgba(100,116,139,.3)" delay={0.3}>
              <text x={470} y={35} textAnchor="middle" fill="#1e293b" fontSize={14}>사용자: "김철수 부서 알려줘"</text>
            </AnimatedBox>

            {/* LLM judgment */}
            <AnimatedBox x={310} y={72} w={320} h={52} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.5)" delay={0.45}>
              <text x={470} y={94} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={15}>LLM 판단</text>
              <text x={470} y={114} textAnchor="middle" fill="#475569" fontSize={13}>tools 목록에 search_employee 있음</text>
            </AnimatedBox>

            {/* Arrow: user → LLM */}
            <motion.line x1={470} y1={50} x2={470} y2={70} stroke="#2563eb" strokeWidth={2} markerEnd="url(#arrowB40)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.5, duration: 0.4 }} />

            {/* tool_call */}
            <AnimatedBox x={260} y={148} w={420} h={40} fill="rgba(245,158,11,.08)" stroke="rgba(245,158,11,.5)" delay={0.6}>
              <text x={470} y={173} textAnchor="middle" fill="#d97706" fontFamily="monospace" fontSize={13}>
                tool_call: search_employee(name="김철수")
              </text>
            </AnimatedBox>

            {/* Arrow: LLM → tool_call */}
            <motion.line x1={470} y1={124} x2={470} y2={146} stroke="#2563eb" strokeWidth={2} markerEnd="url(#arrowB40)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.65, duration: 0.4 }} />

            {/* MCP Client */}
            <AnimatedBox x={100} y={212} w={190} h={52} fill="rgba(51,65,85,.06)" stroke="rgba(100,116,139,.3)" delay={0.75}>
              <text x={195} y={243} textAnchor="middle" fill="#1e293b" fontWeight={600} fontSize={15}>MCP Client</text>
            </AnimatedBox>

            {/* MCP Server */}
            <AnimatedBox x={600} y={212} w={190} h={52} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.85}>
              <text x={695} y={237} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={15}>MCP Server</text>
              <text x={695} y={255} textAnchor="middle" fill="#475569" fontSize={13}>(실제 실행)</text>
            </AnimatedBox>

            {/* Arrow: tool_call → MCP Client */}
            <motion.line x1={470} y1={188} x2={195} y2={210} stroke="#2563eb" strokeWidth={2} markerEnd="url(#arrowB40)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.9, duration: 0.4 }} />

            {/* Arrow: Client → Server */}
            <motion.line x1={292} y1={237} x2={598} y2={237} stroke="#10b981" strokeWidth={2} markerEnd="url(#arrowG40)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.0, duration: 0.5 }} />

            {/* JSON-RPC label */}
            <motion.text x={445} y={230} textAnchor="middle" fill="#475569" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.1 }}>
              JSON-RPC
            </motion.text>

            {/* Arrow: Server → Client (return) */}
            <motion.line x1={598} y1={250} x2={292} y2={250} stroke="#10b981" strokeWidth={2} markerEnd="url(#arrowG40)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.15, duration: 0.5 }} />

            {/* LLM response */}
            <AnimatedBox x={250} y={288} w={440} h={44} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.5)" delay={1.25}>
              <text x={470} y={306} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={14}>LLM 응답</text>
              <text x={470} y={324} textAnchor="middle" fill="#475569" fontSize={13}>"김철수님은 개발1팀 소속입니다."</text>
            </AnimatedBox>

            {/* Arrow: Client → LLM response */}
            <motion.line x1={195} y1={266} x2={470} y2={286} stroke="#2563eb" strokeWidth={2} markerEnd="url(#arrowB40)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.3, duration: 0.4 }} />
          </svg>
        </motion.div>
      </div>
    </div>
  );
}
