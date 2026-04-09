import { useState, useEffect } from 'react';
import { fetchJSON } from '../api';

export default function Questions() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const load = () => fetchJSON('/questions/all').then(setData).catch(() => {});
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>로딩 중...</div>;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '32px 20px' }}>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#0f172a', marginBottom: 8 }}>
        질문 게시판
      </h1>
      <p style={{ color: '#94a3b8', fontSize: '.9rem', marginBottom: 24 }}>
        총 {data.total}개 질문 | 5초마다 자동 갱신
      </p>

      {data.questions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>아직 질문이 없습니다</div>
      ) : (
        [...data.questions].reverse().map((q, i) => (
          <div key={i} style={{
            padding: '16px 20px', marginBottom: 8, borderRadius: 12,
            background: '#fff', border: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0,0,0,.04)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ fontWeight: 700, fontSize: '.9em', color: '#1e293b' }}>
                {q.user}
              </span>
              <span style={{ fontSize: '.78em', color: '#94a3b8' }}>
                슬라이드 {q.slide} | {new Date(q.timestamp).toLocaleTimeString('ko-KR')}
              </span>
            </div>
            <div style={{ fontSize: '1em', color: '#334155', lineHeight: 1.6 }}>
              {q.text}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
