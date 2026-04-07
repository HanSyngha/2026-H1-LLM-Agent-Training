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

export default function Slide55_AgentLoop() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop</Badge>
        <SlideH2 day2>Agent Loop 패턴</SlideH2>
        <p>모든 Agent의 핵심: <strong style={{ color: '#3b82f6' }}>반복적 LLM ↔ Tool 상호작용</strong></p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 900 320" width="900" height="320" className="diagram-svg">
            <defs>
              <marker id="arrow-blue-loop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
              </marker>
              <marker id="arrow-purple-loop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#8b5cf6" />
              </marker>
              <marker id="arrow-green-loop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
              </marker>
            </defs>

            {/* User Input */}
            <AnimatedBox x={310} y={10} w={180} h={50} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={0.4}>
              <text x={400} y={40} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={15}>User 입력</text>
            </AnimatedBox>

            {/* LLM */}
            <AnimatedBox x={310} y={85} w={180} h={55} fill="rgba(139,92,246,.08)" stroke="rgba(139,92,246,.5)" delay={0.5}>
              <text x={400} y={118} textAnchor="middle" fill="#6d28d9" fontWeight={700} fontSize={16}>LLM</text>
            </AnimatedBox>

            {/* Decision diamond */}
            <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.6, duration: 0.4 }}>
              <polygon points="400,165 468,198 400,231 332,198" fill="rgba(245,158,11,.1)" stroke="rgba(245,158,11,.4)" strokeWidth={1.5} />
              <text x={400} y={202} textAnchor="middle" fill="#92400e" fontWeight={600} fontSize={14}>tool_call?</text>
            </motion.g>

            {/* Arrow user->LLM */}
            <motion.line x1={400} y1={60} x2={400} y2={83} stroke="#3b82f6" strokeWidth={2} markerEnd="url(#arrow-blue-loop)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.5, duration: 0.4 }} />

            {/* Arrow LLM->decision */}
            <motion.line x1={400} y1={140} x2={400} y2={165} stroke="#8b5cf6" strokeWidth={2} markerEnd="url(#arrow-purple-loop)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.6, duration: 0.4 }} />

            {/* Yes path: Execute Tool */}
            <AnimatedBox x={570} y={175} w={170} h={50} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.7}>
              <text x={655} y={205} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={15}>Tool 실행</text>
            </AnimatedBox>

            <motion.line x1={468} y1={198} x2={568} y2={198} stroke="#10b981" strokeWidth={2} markerEnd="url(#arrow-green-loop)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.75, duration: 0.4 }} />
            <motion.text x={510} y={190} textAnchor="middle" fill="#047857" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}>Yes</motion.text>

            {/* Loop back arrow */}
            <motion.path d="M655,175 L655,112 L492,112" stroke="#10b981" strokeWidth={2} fill="none" markerEnd="url(#arrow-green-loop)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.9, duration: 0.6 }} />
            <motion.text x={590} y={95} textAnchor="middle" fill="#475569" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }}>결과를 messages에 추가</motion.text>

            {/* No path: Final Response */}
            <AnimatedBox x={310} y={255} w={180} h={50} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={1.0}>
              <text x={400} y={285} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={15}>최종 응답 반환</text>
            </AnimatedBox>

            <motion.line x1={400} y1={231} x2={400} y2={253} stroke="#3b82f6" strokeWidth={2} markerEnd="url(#arrow-blue-loop)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.05, duration: 0.4 }} />
            <motion.text x={365} y={247} textAnchor="middle" fill="#dc2626" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.1 }}>No</motion.text>

            {/* Loop indicator */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.2 }}>
              <rect x={80} y={88} width={100} height={35} rx={6} fill="rgba(139,92,246,.08)" stroke="rgba(139,92,246,.2)" strokeWidth={1} />
              <text x={130} y={110} textAnchor="middle" fill="#8b5cf6" fontSize={13} fontWeight={600}>Loop</text>
              <line x1={180} y1={106} x2={308} y2={106} stroke="#8b5cf6" strokeWidth={1} strokeDasharray="4 3" fill="none" />
            </motion.g>
          </svg>
        </motion.div>
      </div>
    </div>
  );
}
