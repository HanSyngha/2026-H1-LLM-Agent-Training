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

export default function Slide44_CDP() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 자동화</Badge>
        <SlideH2>CDP (Chrome DevTools Protocol)</SlideH2>
        <motion.p
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ color: '#475569' }}
        >
          Chrome과 WebSocket으로 직접 대화하는 저수준 프로토콜
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 12 }}>
          <svg viewBox="0 0 950 210" width="950" height="210" className="diagram-svg">
            <defs>
              <marker id="arrowB44" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#60a5fa" />
              </marker>
              <marker id="arrowG44" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
              </marker>
            </defs>

            {/* Browser */}
            <AnimatedBox x={20} y={35} w={220} h={140} fill="rgba(37,99,235,.08)" stroke="rgba(37,99,235,.5)" delay={0.4}>
              <text x={130} y={68} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={15}>Chrome</text>
              <text x={130} y={88} textAnchor="middle" fill="#475569" fontSize={13}>Browser</text>
            </AnimatedBox>

            {/* Domain boxes inside browser */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}>
              <rect x={35} y={105} width={90} height={30} rx={6} fill="rgba(59,130,246,.15)" stroke="rgba(59,130,246,.3)" strokeWidth={1} />
              <text x={80} y={124} textAnchor="middle" fill="#3b82f6" fontSize={13}>Page</text>
              <rect x={135} y={105} width={90} height={30} rx={6} fill="rgba(59,130,246,.15)" stroke="rgba(59,130,246,.3)" strokeWidth={1} />
              <text x={180} y={124} textAnchor="middle" fill="#3b82f6" fontSize={13}>DOM</text>
              <rect x={35} y={143} width={90} height={26} rx={5} fill="rgba(59,130,246,.08)" stroke="rgba(59,130,246,.15)" strokeWidth={1} />
              <text x={80} y={160} textAnchor="middle" fill="#475569" fontSize={13}>Network</text>
              <rect x={135} y={143} width={90} height={26} rx={5} fill="rgba(59,130,246,.08)" stroke="rgba(59,130,246,.15)" strokeWidth={1} />
              <text x={180} y={160} textAnchor="middle" fill="#475569" fontSize={13}>Runtime</text>
            </motion.g>

            {/* WebSocket */}
            <AnimatedBox x={335} y={55} w={220} h={95} fill="rgba(245,158,11,.08)" stroke="rgba(245,158,11,.5)" delay={0.55}>
              <text x={445} y={90} textAnchor="middle" fill="#92400e" fontWeight={600} fontSize={15}>WebSocket</text>
              <text x={445} y={112} textAnchor="middle" fill="#475569" fontSize={13}>DevTools Protocol</text>
              <text x={445} y={130} textAnchor="middle" fill="#475569" fontSize={13}>ws://localhost:9222</text>
            </AnimatedBox>

            {/* Your Code */}
            <AnimatedBox x={650} y={35} w={220} h={140} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.65}>
              <text x={760} y={78} textAnchor="middle" fill="#047857" fontWeight={700} fontSize={15}>Your Code</text>
              <text x={760} y={100} textAnchor="middle" fill="#475569" fontSize={13}>Python / Node.js</text>
              <text x={760} y={132} textAnchor="middle" fill="#475569" fontSize={13}>Page.navigate()</text>
              <text x={760} y={150} textAnchor="middle" fill="#475569" fontSize={13}>Runtime.evaluate()</text>
            </AnimatedBox>

            {/* Arrows: Browser <-> WebSocket */}
            <motion.line x1={242} y1={92} x2={333} y2={92} stroke="#60a5fa" strokeWidth={2} markerEnd="url(#arrowB44)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.8, duration: 0.5 }} />
            <motion.line x1={333} y1={112} x2={242} y2={112} stroke="#60a5fa" strokeWidth={2} markerEnd="url(#arrowB44)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.9, duration: 0.5 }} />

            {/* Arrows: WebSocket <-> Code */}
            <motion.line x1={557} y1={92} x2={648} y2={92} stroke="#10b981" strokeWidth={2} markerEnd="url(#arrowG44)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.0, duration: 0.5 }} />
            <motion.line x1={648} y1={112} x2={557} y2={112} stroke="#10b981" strokeWidth={2} markerEnd="url(#arrowG44)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 1.1, duration: 0.5 }} />
          </svg>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.0 }}>
          <CodeBlock lang="python">{`await ws.send(json.dumps({"id":1, "method":"Page.navigate", "params":{"url":url}}))`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
