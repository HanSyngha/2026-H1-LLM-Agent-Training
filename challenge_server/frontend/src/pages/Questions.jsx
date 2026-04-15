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

  if (!data) return <div className="loading">질문을 불러오는 중입니다...</div>;
  const questions = Array.isArray(data.questions) ? data.questions : [];
  const total = typeof data.total === 'number' ? data.total : questions.length;

  return (
    <div className="page-shell" style={{ maxWidth: 920 }}>
      <div className="page-hero">
        <div className="page-eyebrow">Live Questions</div>
        <h1 className="page-title">질문 게시판</h1>
        <p className="page-copy">
          수업 중 올라온 질문을 시간순으로 확인할 수 있습니다. 발표 흐름을 끊지 않으면서도
          핵심 질문을 빠르게 훑어볼 수 있게 구성했습니다.
        </p>
        <div className="page-meta">
          <span className="page-chip">총 {total}개 질문</span>
          <span className="page-chip">5초마다 자동 갱신</span>
        </div>
      </div>

      <div className="list-card">
        {questions.length === 0 ? (
          <div className="empty-state">아직 질문이 없습니다.</div>
        ) : (
          [...questions].reverse().map((q, i) => (
            <div key={i} className="list-row">
              <div className="list-row-head">
                <span className="list-row-title">{q.user}</span>
                <span className="list-row-meta">
                  슬라이드 {q.slide} · {new Date(q.timestamp).toLocaleTimeString('ko-KR')}
                </span>
              </div>
              <div className="list-row-body">{q.text}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
