import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider } from './SlideLayout';

const sources = [
  { label: 'RAG 검색 결과', icon: '🔍', color: '#3b82f6' },
  { label: 'Tool 실행 결과', icon: '🔧', color: '#f59e0b' },
  { label: 'Agent 루프 상태', icon: '🤖', color: '#8b5cf6' },
  { label: '대화 히스토리', icon: '💬', color: '#06b6d4' },
  { label: '시스템 지시문', icon: '📋', color: '#10b981' },
];

export default function Slide18_Prompt1() {
  return (
    <div className="slide-container">
      <div className="slide-inner" style={{ maxWidth: 900 }}>
        <Badge variant="day1">프롬프트</Badge>
        <SlideH2>결국 Prompt가 전부입니다</SlideH2>
        <Divider />

        <motion.p
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ fontSize: '1.05em', lineHeight: 1.7, color: '#334155', marginTop: '.4em' }}
        >
          로직을 어떻게 짜든, RAG를 어떻게 하든 —<br />
          결국 <strong style={{ color: '#2563eb' }}>prompt에 무엇이 들어가는지</strong>를 체크하고 디자인하는 것이<br />
          모든 LLM 서비스의 <strong style={{ color: '#2563eb' }}>근간이자 마지막</strong>입니다.
        </motion.p>

        {/* ── 수렴 다이어그램 ── */}
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: 0, marginTop: 28, position: 'relative',
          }}
        >
          {/* 왼쪽: 입력 소스들 */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, minWidth: 170 }}>
            {sources.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + i * 0.1 }}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  background: `${s.color}12`, border: `1.5px solid ${s.color}40`,
                  borderRadius: 10, padding: '6px 14px', fontSize: '.85em', fontWeight: 600,
                  color: s.color,
                }}
              >
                <span>{s.icon}</span>
                <span>{s.label}</span>
              </motion.div>
            ))}
          </div>

          {/* 화살표 영역 */}
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.0 }}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0 8px' }}
          >
            <svg width="80" height="160" viewBox="0 0 80 160" fill="none">
              {[0,1,2,3,4].map(i => (
                <motion.path
                  key={i}
                  d={`M 4 ${16 + i * 32} Q 40 ${16 + i * 32} 72 80`}
                  stroke="#94a3b8" strokeWidth="1.5" strokeDasharray="4 3" fill="none"
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                  transition={{ delay: 1.0 + i * 0.08, duration: 0.5 }}
                />
              ))}
              <motion.polygon
                points="68,74 78,80 68,86" fill="#64748b"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }}
              />
            </svg>
          </motion.div>

          {/* 중앙: PROMPT 블록 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.2, type: 'spring', stiffness: 200 }}
            style={{
              background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
              borderRadius: 16, padding: '22px 28px', textAlign: 'center',
              color: '#fff', minWidth: 140, boxShadow: '0 8px 32px rgba(37,99,235,.35)',
              position: 'relative',
            }}
          >
            <div style={{ fontSize: '1.6em', fontWeight: 900, letterSpacing: 2 }}>PROMPT</div>
            <div style={{ fontSize: '.75em', opacity: .7, marginTop: 4 }}>context window</div>
          </motion.div>

          {/* 오른쪽 화살표 */}
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }}
            style={{ padding: '0 8px' }}
          >
            <svg width="60" height="40" viewBox="0 0 60 40" fill="none">
              <motion.line x1="0" y1="20" x2="46" y2="20" stroke="#64748b" strokeWidth="2.5"
                initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ delay: 1.5, duration: 0.4 }} />
              <polygon points="44,13 56,20 44,27" fill="#64748b" />
            </svg>
          </motion.div>

          {/* 오른쪽: LLM 호출 */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1.6, type: 'spring', stiffness: 200 }}
            style={{
              background: '#0f172a', borderRadius: 16, padding: '22px 24px',
              textAlign: 'center', color: '#f1f5f9', minWidth: 120,
              border: '2px solid #334155',
            }}
          >
            <div style={{ fontSize: '1.3em', fontWeight: 800 }}>LLM</div>
            <div style={{
              display: 'flex', gap: 6, justifyContent: 'center', marginTop: 8,
              fontSize: '.7em', fontWeight: 600,
            }}>
              <span style={{
                background: 'rgba(59,130,246,.2)', color: '#60a5fa',
                padding: '2px 8px', borderRadius: 6,
              }}>stream</span>
              <span style={{
                background: 'rgba(139,92,246,.2)', color: '#a78bfa',
                padding: '2px 8px', borderRadius: 6,
              }}>invoke</span>
            </div>
          </motion.div>
        </motion.div>

        {/* 핵심 메시지 */}
        <motion.div
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.8 }}
          style={{
            marginTop: 28, padding: '14px 24px',
            background: 'linear-gradient(135deg, rgba(37,99,235,.08), rgba(124,58,237,.08))',
            borderRadius: 12, borderLeft: '4px solid #2563eb',
            fontSize: '.95em', lineHeight: 1.7, color: '#1e293b',
          }}
        >
          어떤 아키텍처를 쓰든, 마지막에 LLM을 부르는 것은
          <code style={{
            background: 'rgba(37,99,235,.1)', padding: '2px 6px', borderRadius: 4,
            fontWeight: 700, color: '#2563eb',
          }}>stream()</code> 또는
          <code style={{
            background: 'rgba(139,92,246,.1)', padding: '2px 6px', borderRadius: 4,
            fontWeight: 700, color: '#7c3aed',
          }}>invoke()</code> 한 줄입니다.<br />
          그 한 줄에 <strong>무엇이 담기는지</strong>가 서비스의 품질을 결정합니다.
        </motion.div>
      </div>
    </div>
  );
}
