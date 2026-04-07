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

export default function Slide38_MCPArch() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">MCP</Badge>
        <SlideH2>MCP 아키텍처</SlideH2>
        <motion.p
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ color: '#475569' }}
        >
          Client &#8596; Server 구조, 3가지 기본 요소
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 950 290" width="950" height="290" className="diagram-svg">
            <defs>
              <marker id="arrowB38" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#60a5fa" />
              </marker>
            </defs>

            {/* MCP Client */}
            <AnimatedBox x={30} y={80} w={220} h={110} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.5)" delay={0.4}>
              <text x={140} y={118} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={16}>MCP Client</text>
              <text x={140} y={143} textAnchor="middle" fill="#475569" fontSize={13}>Claude, Cursor,</text>
              <text x={140} y={161} textAnchor="middle" fill="#475569" fontSize={13}>VS Code, etc.</text>
            </AnimatedBox>

            {/* Bidirectional arrows */}
            <motion.line x1={252} y1={122} x2={368} y2={122} stroke="#60a5fa" strokeWidth={2} markerEnd="url(#arrowB38)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.7, duration: 0.5 }} />
            <motion.line x1={368} y1={148} x2={252} y2={148} stroke="#60a5fa" strokeWidth={2} markerEnd="url(#arrowB38)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.8, duration: 0.5 }} />
            <motion.text x={310} y={117} textAnchor="middle" fill="#475569" fontSize={13}
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}>
              JSON-RPC
            </motion.text>

            {/* MCP Server outline */}
            <AnimatedBox x={370} y={20} w={550} h={250} fill="rgba(51,65,85,.04)" stroke="rgba(16,185,129,.3)" delay={0.5}>
              <text x={645} y={50} textAnchor="middle" fill="#047857" fontWeight={700} fontSize={16}>MCP Server</text>
            </AnimatedBox>

            {/* Tool box */}
            <AnimatedBox x={400} y={72} w={180} h={80} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.5)" delay={0.7}>
              <text x={490} y={100} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={15}>Tool</text>
              <text x={490} y={120} textAnchor="middle" fill="#475569" fontSize={13}>LLM이 호출 가능한 함수</text>
              <text x={490} y={137} textAnchor="middle" fill="#475569" fontSize={13}>예: search_docs()</text>
            </AnimatedBox>

            {/* Resource box */}
            <AnimatedBox x={620} y={72} w={180} h={80} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.85}>
              <text x={710} y={100} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={15}>Resource</text>
              <text x={710} y={120} textAnchor="middle" fill="#475569" fontSize={13}>LLM에 제공할 데이터</text>
              <text x={710} y={137} textAnchor="middle" fill="#475569" fontSize={13}>예: file://config.yaml</text>
            </AnimatedBox>

            {/* Prompt box */}
            <AnimatedBox x={510} y={172} w={180} h={80} fill="rgba(124,58,237,.08)" stroke="rgba(124,58,237,.5)" delay={1.0}>
              <text x={600} y={200} textAnchor="middle" fill="#6d28d9" fontWeight={600} fontSize={15}>Prompt</text>
              <text x={600} y={220} textAnchor="middle" fill="#475569" fontSize={13}>미리 정의된 템플릿</text>
              <text x={600} y={237} textAnchor="middle" fill="#475569" fontSize={13}>예: summarize_code</text>
            </AnimatedBox>
          </svg>
        </motion.div>
      </div>
    </div>
  );
}
