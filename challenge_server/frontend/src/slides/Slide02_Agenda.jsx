import { motion } from 'framer-motion';
import { SlideH2, Divider, Grid } from './SlideLayout';

const day1 = ['SSO / API 기초', '프롬프트 & 컨텍스트 엔지니어링', 'OpenAI Compatible 표준', 'Structured Output & Tool Calling', 'MCP (Model Context Protocol)', '브라우저 자동화 기초'];
const day2 = ['Agent Framework 비교', 'Agentic Loop 직접 구현', 'bash/powershell Agent', 'Vector DB vs Index Explore', '하네스 엔지니어링', '종합 실습'];

function DayColumn({ title, items, color, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
      style={{
        background: 'linear-gradient(180deg, rgba(255,255,255,.9), rgba(255,252,246,.82))',
        border: '1px solid rgba(88,72,49,.12)',
        borderTop: `4px solid ${color}`,
        borderRadius: 28,
        padding: '30px 30px 28px',
        textAlign: 'left',
        boxShadow: '0 20px 46px rgba(23,34,51,.08)',
      }}
    >
      <h4 style={{ color: '#182230', fontSize: '1.18em', marginBottom: 18, letterSpacing: '-.03em' }}>{title}</h4>
      {items.map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
          transition={{ delay: delay + 0.1 + i * 0.05 }}
          style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 10, fontSize: '.94em', color: '#55606f' }}
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
        <p style={{ maxWidth: 760, margin: '0 auto 8px', color: '#55606f' }}>
          Day 1은 표준과 제어 원리를 익히고, Day 2는 그 아이디어를 직접 조립해 우리 조직에 맞는 agent 구조로 가져오는 흐름입니다.
        </p>
        <Grid cols={2} gap={20}>
          <DayColumn title="Day 1 — LLM 제어의 원리와 도구" items={day1} color="#1d4ed8" delay={0.2} />
          <DayColumn title="Day 2 — Agent 아키텍처 — 프레임워크를 넘어" items={day2} color="#0f766e" delay={0.4} />
        </Grid>
      </div>
    </div>
  );
}
