import { motion } from 'framer-motion';
import { SlideH2, Divider, Grid } from './SlideLayout';

export default function Slide75_Summary() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <SlideH2>2일간 학습 정리</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Grid cols={2} gap={20}>
            <div style={{
              background: 'rgba(255,255,255,.7)', backdropFilter: 'blur(16px)',
              border: '1px solid rgba(148,163,184,.25)', borderTop: '3px solid #3b82f6',
              borderRadius: 16, textAlign: 'left', padding: '24px 26px',
              boxShadow: '0 4px 20px rgba(37,99,235,.08)',
            }}>
              <h4 style={{ color: '#3b82f6', marginBottom: '.5em' }}>Day 1 핵심</h4>
              <ul style={{ fontSize: '.85em', color: '#334155' }}>
                <li>프롬프트 & 컨텍스트 엔지니어링</li>
                <li>OpenAI Compatible 표준</li>
                <li>Structured Output & Tool Calling</li>
                <li>MCP (Model Context Protocol)</li>
                <li>브라우저 자동화 기초</li>
              </ul>
            </div>
            <div style={{
              background: 'rgba(255,255,255,.7)', backdropFilter: 'blur(16px)',
              border: '1px solid rgba(148,163,184,.25)', borderTop: '3px solid #7c3aed',
              borderRadius: 16, textAlign: 'left', padding: '24px 26px',
              boxShadow: '0 4px 20px rgba(124,58,237,.08)',
            }}>
              <h4 style={{ color: '#8b5cf6', marginBottom: '.5em' }}>Day 2 핵심</h4>
              <ul style={{ fontSize: '.85em', color: '#334155' }}>
                <li>Agent Framework 비교 이해</li>
                <li>Agentic Loop 직접 구현</li>
                <li>검색 전략 (Vector vs Index)</li>
                <li>하네스 엔지니어링 5대 요소</li>
                <li>보안과 가드레일 설계</li>
              </ul>
            </div>
          </Grid>
        </motion.div>
      </div>
    </div>
  );
}
