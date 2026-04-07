import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, Grid } from './SlideLayout';

function AnimatedBox({ x, y, w, h, fill, stroke, delay, children }) {
  return (
    <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay, duration: 0.4 }}>
      <rect x={x} y={y} width={w} height={h} rx={12} fill={fill} stroke={stroke} strokeWidth={2} />
      {children}
    </motion.g>
  );
}

export default function Slide73_FinalTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">종합 실습</Badge>
        <SlideH2 day2>종합 실습 과제</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          style={{
            background: 'rgba(255,255,255,.7)', backdropFilter: 'blur(16px)',
            border: '1px solid rgba(139,92,246,.2)', borderRadius: 16,
            padding: '16px 24px', maxWidth: 800, margin: '.8em auto',
            boxShadow: '0 4px 20px rgba(124,58,237,.08)',
          }}>
          <div style={{ color: '#8b5cf6', fontWeight: 700, fontSize: '1.1em', textAlign: 'center' }}>
            브라우저 검색 → 추출 → Excel 저장 Agent
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 950 90" width="950" height="90" className="diagram-svg">
            <defs>
              <marker id="arrow-blue-final" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#3b82f6" />
              </marker>
              <marker id="arrow-green-final" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
              </marker>
              <marker id="arrow-purple-final" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#8b5cf6" />
              </marker>
            </defs>

            <AnimatedBox x={10} y={15} w={150} h={55} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={0.45}>
              <text x={85} y={47} textAnchor="middle" fill="#1d4ed8" fontWeight={600} fontSize={14}>사용자 질문</text>
            </AnimatedBox>

            <AnimatedBox x={195} y={15} w={150} h={55} fill="rgba(51,65,85,.1)" stroke="rgba(100,116,139,.4)" delay={0.55}>
              <text x={270} y={47} textAnchor="middle" fill="#1e293b" fontWeight={600} fontSize={14}>LLM 판단</text>
            </AnimatedBox>

            <AnimatedBox x={380} y={15} w={150} h={55} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.65}>
              <text x={455} y={40} textAnchor="middle" fill="#047857" fontWeight={600} fontSize={14}>Playwright</text>
              <text x={455} y={57} textAnchor="middle" fill="#475569" fontSize={13}>웹 검색</text>
            </AnimatedBox>

            <AnimatedBox x={565} y={15} w={150} h={55} fill="rgba(245,158,11,.08)" stroke="rgba(245,158,11,.5)" delay={0.75}>
              <text x={640} y={40} textAnchor="middle" fill="#92400e" fontWeight={600} fontSize={14}>데이터 추출</text>
              <text x={640} y={57} textAnchor="middle" fill="#475569" fontSize={13}>정제</text>
            </AnimatedBox>

            <AnimatedBox x={750} y={15} w={150} h={55} fill="rgba(139,92,246,.08)" stroke="rgba(139,92,246,.5)" delay={0.85}>
              <text x={825} y={40} textAnchor="middle" fill="#6d28d9" fontWeight={600} fontSize={14}>Excel 저장</text>
              <text x={825} y={57} textAnchor="middle" fill="#475569" fontSize={13}>openpyxl</text>
            </AnimatedBox>

            <motion.line x1={162} y1={42} x2={193} y2={42} stroke="#3b82f6" strokeWidth={2} markerEnd="url(#arrow-blue-final)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.6, duration: 0.3 }} />
            <motion.line x1={347} y1={42} x2={378} y2={42} stroke="#3b82f6" strokeWidth={2} markerEnd="url(#arrow-blue-final)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.7, duration: 0.3 }} />
            <motion.line x1={532} y1={42} x2={563} y2={42} stroke="#10b981" strokeWidth={2} markerEnd="url(#arrow-green-final)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.8, duration: 0.3 }} />
            <motion.line x1={717} y1={42} x2={748} y2={42} stroke="#8b5cf6" strokeWidth={2} markerEnd="url(#arrow-purple-final)"
              initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }} transition={{ delay: 0.9, duration: 0.3 }} />
          </svg>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Grid cols={2} gap={16}>
            <Box color="blue">
              <BoxTitle>바이브 코딩으로 구현</BoxTitle>
              <ul style={{ fontSize: '.95em' }}>
                <li><code>web_search(query)</code> — Playwright 검색</li>
                <li><code>extract_data(url)</code> — 데이터 추출</li>
                <li><code>save_excel(data, path)</code> — 저장</li>
              </ul>
            </Box>
            <Box color="green">
              <BoxTitle color="#059669">제출</BoxTitle>
              <div style={{ fontSize: '.95em', lineHeight: 1.8 }}>
                <code>POST /challenges/final/submit</code><br />
                <code>{`{"token": "...", "answer": {"items": [...]}}`}</code><br />
                <strong style={{ color: '#059669' }}>→ 홍길동님, 종합 실습 통과!</strong>
              </div>
            </Box>
          </Grid>
        </motion.div>
      </div>
    </div>
  );
}
