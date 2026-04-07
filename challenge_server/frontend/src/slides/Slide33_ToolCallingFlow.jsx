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

const steps = [
  { x: 10,  label: '1. Define',  sub1: 'Tool Schema 정의', sub2: '(함수 설명서)', fill: 'rgba(37,99,235,.08)',  stroke: 'rgba(37,99,235,.5)',  titleColor: '#1d4ed8' },
  { x: 205, label: '2. Send',    sub1: 'messages + tools',  sub2: 'LLM에 전송',    fill: 'rgba(51,65,85,.06)',   stroke: 'rgba(100,116,139,.3)', titleColor: '#1e293b' },
  { x: 400, label: '3. LLM 판단', sub1: 'tool_calls JSON',  sub2: '응답 생성',     fill: 'rgba(124,58,237,.08)', stroke: 'rgba(124,58,237,.5)',  titleColor: '#6d28d9' },
  { x: 595, label: '4. Execute', sub1: '우리 코드가',       sub2: '함수 실행',     fill: 'rgba(16,185,129,.08)', stroke: 'rgba(16,185,129,.5)',  titleColor: '#047857' },
  { x: 790, label: '5. Return',  sub1: '결과를 LLM에',      sub2: '다시 전달',     fill: 'rgba(245,158,11,.08)', stroke: 'rgba(245,158,11,.5)',  titleColor: '#92400e' },
];

const arrowColors = ['#2563eb', '#2563eb', '#7c3aed', '#059669'];

export default function Slide33_ToolCallingFlow() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Structured Output</Badge>
        <SlideH2>Tool Calling 흐름</SlideH2>
        <motion.p
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ color: '#475569' }}
        >
          LLM이 직접 함수를 "호출"하는 것이 아니라, <strong style={{ color: '#2563eb' }}>호출 의도를 JSON으로 표현</strong>
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 960 160" width="960" height="160" className="diagram-svg">
            <defs>
              <marker id="arrowB33" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb" />
              </marker>
              <marker id="arrowP33" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
              </marker>
              <marker id="arrowG33" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#059669" />
              </marker>
            </defs>

            {steps.map((s, i) => (
              <AnimatedBox key={i} x={s.x} y={20} w={160} h={90} fill={s.fill} stroke={s.stroke} delay={0.4 + i * 0.15}>
                <text x={s.x + 80} y={50} textAnchor="middle" fill={s.titleColor} fontWeight={700} fontSize={16}>{s.label}</text>
                <text x={s.x + 80} y={72} textAnchor="middle" fill="#475569" fontSize={13}>{s.sub1}</text>
                <text x={s.x + 80} y={90} textAnchor="middle" fill="#475569" fontSize={13}>{s.sub2}</text>
              </AnimatedBox>
            ))}

            {/* Arrows between steps */}
            {[0, 1, 2, 3].map((i) => {
              const x1 = steps[i].x + 162;
              const x2 = steps[i + 1].x - 2;
              const markerIds = ['arrowB33', 'arrowB33', 'arrowP33', 'arrowG33'];
              return (
                <motion.line key={i}
                  x1={x1} y1={65} x2={x2} y2={65}
                  stroke={arrowColors[i]} strokeWidth={2} markerEnd={`url(#${markerIds[i]})`}
                  initial={{ pathLength: 0, opacity: 0 }}
                  animate={{ pathLength: 1, opacity: 1 }}
                  transition={{ delay: 0.8 + i * 0.15, duration: 0.4 }}
                />
              );
            })}
          </svg>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.2 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.9em' }}>
            <strong>중요:</strong> LLM은 함수를 실행하지 않습니다. "이 함수를 이 인자로 호출해달라"는 <strong>요청</strong>을 생성할 뿐입니다. 실행은 우리 코드의 몫입니다!
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
