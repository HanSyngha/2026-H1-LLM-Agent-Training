import { useState, useEffect } from 'react';
import { fetchJSON } from '../api';

export default function Feedback() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const load = () => fetchJSON('/feedback').then(setData).catch(() => {});
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8' }}>로딩 중...</div>;

  const avg = data.feedback.length > 0
    ? (data.feedback.reduce((s, f) => s + (f.rating || 0), 0) / data.feedback.length).toFixed(1)
    : '-';

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '32px 20px' }}>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#0f172a', marginBottom: 8 }}>
        피드백
      </h1>
      <div style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
        <div style={{ padding: '12px 20px', borderRadius: 10, background: '#f0fdf4', border: '1px solid #86efac' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#059669' }}>{data.total}건</div>
          <div style={{ fontSize: '.8rem', color: '#64748b' }}>총 피드백</div>
        </div>
        <div style={{ padding: '12px 20px', borderRadius: 10, background: '#fefce8', border: '1px solid #fde68a' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, color: '#d97706' }}>⭐ {avg}</div>
          <div style={{ fontSize: '.8rem', color: '#64748b' }}>평균 평점</div>
        </div>
      </div>

      {data.feedback.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>아직 피드백이 없습니다</div>
      ) : (
        [...data.feedback].reverse().map((f, i) => (
          <div key={i} style={{
            padding: '16px 20px', marginBottom: 8, borderRadius: 12,
            background: '#fff', border: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0,0,0,.04)',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <div>
                <span style={{ fontWeight: 700, fontSize: '.9em', color: '#1e293b' }}>{f.user}</span>
                {f.rating > 0 && (
                  <span style={{ marginLeft: 8, fontSize: '.85em' }}>
                    {'⭐'.repeat(f.rating)}
                  </span>
                )}
              </div>
              <span style={{ fontSize: '.78em', color: '#94a3b8' }}>
                {new Date(f.timestamp).toLocaleString('ko-KR')}
              </span>
            </div>
            <div style={{ fontSize: '.95em', color: '#334155', lineHeight: 1.6 }}>{f.text}</div>
          </div>
        ))
      )}
    </div>
  );
}
