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

  if (!data) return <div className="loading">피드백을 불러오는 중입니다...</div>;
  const feedback = Array.isArray(data.feedback) ? data.feedback : [];
  const total = typeof data.total === 'number' ? data.total : feedback.length;

  const avg = feedback.length > 0
    ? (feedback.reduce((s, f) => s + (f.rating || 0), 0) / feedback.length).toFixed(1)
    : '-';

  return (
    <div className="page-shell" style={{ maxWidth: 980 }}>
      <div className="page-hero">
        <div className="page-eyebrow">Course Feedback</div>
        <h1 className="page-title">피드백</h1>
        <p className="page-copy">
          수강생의 즉시 반응과 후기 데이터를 한 화면에서 보며 수업 품질을 조정할 수 있습니다.
        </p>
      </div>

      <div className="metric-grid" style={{ gridTemplateColumns: 'repeat(2, minmax(0, 1fr))' }}>
        <div className="metric-card">
          <div className="metric-value" style={{ color: 'var(--teal)' }}>{total}</div>
          <div className="metric-label">총 피드백</div>
        </div>
        <div className="metric-card">
          <div className="metric-value" style={{ color: 'var(--amber)' }}>★ {avg}</div>
          <div className="metric-label">평균 평점</div>
        </div>
      </div>

      <div className="list-card">
        {feedback.length === 0 ? (
          <div className="empty-state">아직 피드백이 없습니다.</div>
        ) : (
          [...feedback].reverse().map((f, i) => (
            <div key={i} className="list-row">
              <div className="list-row-head">
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
                  <span className="list-row-title">{f.user}</span>
                  {f.rating > 0 && (
                    <span className="page-chip" style={{ padding: '6px 10px' }}>
                      {'★'.repeat(f.rating)}
                    </span>
                  )}
                </div>
                <span className="list-row-meta">{new Date(f.timestamp).toLocaleString('ko-KR')}</span>
              </div>
              <div className="list-row-body">{f.text}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
