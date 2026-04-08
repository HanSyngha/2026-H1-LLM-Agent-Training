import { motion } from 'framer-motion';

export default function Slide01b_NoRightAnswer() {
  return (
    <div className="slide-container" style={{ background: '#0f172a' }}>
      <div className="slide-inner" style={{ textAlign: 'center', justifyContent: 'center' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <p style={{ fontSize: '1.1em', color: '#64748b', marginBottom: 24, letterSpacing: 1 }}>
            이 강의를 시작하기 전에
          </p>
          <h1 style={{ fontSize: '2.2em', fontWeight: 900, color: '#f1f5f9', lineHeight: 1.3, marginBottom: 32 }}>
            소프트웨어에 <span style={{ color: '#ef4444' }}>정답</span>은 없습니다
          </h1>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
          <p style={{ fontSize: '1.5em', fontWeight: 700, color: '#60a5fa', lineHeight: 1.5, marginBottom: 40 }}>
            언제나 <span style={{ color: '#fbbf24' }}>가장 최선의 선택</span>이 있을 뿐입니다.
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.0 }}>
          <div style={{
            display: 'inline-block', padding: '20px 36px', borderRadius: 16,
            background: 'rgba(255,255,255,.05)', border: '1px solid rgba(255,255,255,.1)',
          }}>
            <p style={{ fontSize: '1em', color: '#94a3b8', lineHeight: 1.8, margin: 0 }}>
              <strong style={{ color: '#f1f5f9' }}>CAP 정리</strong> — 분산 시스템에서<br />
              <span style={{ color: '#22c55e' }}>Consistency</span>,{' '}
              <span style={{ color: '#3b82f6' }}>Availability</span>,{' '}
              <span style={{ color: '#f59e0b' }}>Partition tolerance</span><br />
              세 가지를 <strong style={{ color: '#ef4444' }}>동시에 만족할 수 없습니다.</strong>
            </p>
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }}>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 16, marginTop: 28 }}>
            {[
              { label: 'CP', desc: 'MongoDB, HBase', color: '#22c55e', sub: '일관성 + 파티션' },
              { label: 'AP', desc: 'Cassandra, DynamoDB', color: '#3b82f6', sub: '가용성 + 파티션' },
              { label: 'CA', desc: 'RDBMS (단일 노드)', color: '#f59e0b', sub: '일관성 + 가용성' },
            ].map((item, i) => (
              <motion.div key={item.label}
                initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.7 + i * 0.15 }}
                style={{
                  padding: '14px 20px', borderRadius: 12, textAlign: 'center', minWidth: 150,
                  background: `${item.color}15`, border: `1.5px solid ${item.color}40`,
                }}>
                <div style={{ fontSize: '1.3em', fontWeight: 900, color: item.color }}>{item.label}</div>
                <div style={{ fontSize: '.75em', color: '#94a3b8', marginTop: 4 }}>{item.sub}</div>
                <div style={{ fontSize: '.7em', color: '#64748b', marginTop: 2 }}>{item.desc}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 2.2 }}
          style={{ fontSize: '.9em', color: '#475569', marginTop: 24 }}>
          어떤 DB를 쓸지, 어떤 아키텍처를 쓸지 — 항상 <strong style={{ color: '#94a3b8' }}>트레이드오프</strong>입니다.
        </motion.p>
      </div>
    </div>
  );
}
