import { motion } from 'framer-motion';
import { SlideH2, Divider, Grid } from './SlideLayout';

const day1 = ['SSO / API 기초', '프롬프트 & 컨텍스트 엔지니어링', 'OpenAI Compatible 표준', 'Structured Output & Tool Calling', 'MCP (Model Context Protocol)', '브라우저 자동화 기초'];
const day2 = ['Agent Framework 비교', 'Agentic Loop 직접 구현', 'bash/powershell Agent', 'Vector DB vs Index Explore', '하네스 엔지니어링', '종합 실습'];

function DayColumn({ title, items, color, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
      style={{
        background: '#fff', border: '1px solid #e2e8f0', borderTop: `3px solid ${color}`,
        borderRadius: 14, padding: '28px 30px', textAlign: 'left',
      }}
    >
      <h4 style={{ color, fontSize: '1.1em', marginBottom: 16 }}>{title}</h4>
      {items.map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
          transition={{ delay: delay + 0.1 + i * 0.05 }}
          style={{ display: 'flex', alignItems: 'baseline', gap: 10, marginBottom: 8, fontSize: '.95em', color: '#475569' }}
        >
          <span style={{ color, fontWeight: 700, fontFamily: 'monospace', minWidth: 20 }}>
            {String(i + 1).padStart(2, '0')}
          </span>
          {item}
        </motion.div>
      ))}
    </motion.div>
  );
}

export default function Slide02_Agenda() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <SlideH2>전체 과정 구성</SlideH2>
        <Divider />
        <Grid cols={2} gap={20}>
          <DayColumn title="Day 1 — LLM 제어의 원리와 도구" items={day1} color="#2563eb" delay={0.2} />
          <DayColumn title="Day 2 — Agent 아키텍처 — 프레임워크를 넘어" items={day2} color="#7c3aed" delay={0.4} />
        </Grid>
      </div>
    </div>
  );
}
