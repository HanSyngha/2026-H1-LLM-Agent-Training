import { useState, useEffect } from 'react';
import { sendReaction, getReactions, postJSON, fetchJSON } from '../api';

const REACTIONS = [
  { type: 'like', emoji: '👍', label: '좋아요' },
  { type: 'question', emoji: '❓', label: '질문' },
  { type: 'confused', emoji: '😕', label: '이해 안 됨' },
  { type: 'yes', emoji: '✅', label: 'Yes' },
  { type: 'no', emoji: '❌', label: 'No' },
  { type: 'fast', emoji: '⏩', label: '빨리' },
  { type: 'slow', emoji: '⏪', label: '천천히' },
];

export default function Slides({ user }) {
  const [currentSlide, setCurrentSlide] = useState(1);
  const [reactions, setReactions] = useState({});
  const [myReaction, setMyReaction] = useState(null);
  const [animate, setAnimate] = useState(null);
  const [questionText, setQuestionText] = useState('');
  const [questions, setQuestions] = useState([]);
  const [questionSent, setQuestionSent] = useState(false);

  // 현재 슬라이드의 반응 + 질문 가져오기
  useEffect(() => {
    const load = () => {
      getReactions(currentSlide).then(setReactions).catch(() => {});
      fetchJSON(`/questions?slide=${currentSlide}`).then(setQuestions).catch(() => {});
    };
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [currentSlide]);

  const sendQuestion = async () => {
    if (!questionText.trim()) return;
    await postJSON('/questions', { slide: currentSlide, text: questionText });
    setQuestionText('');
    setQuestionSent(true);
    setTimeout(() => setQuestionSent(false), 2000);
    fetchJSON(`/questions?slide=${currentSlide}`).then(setQuestions);
  };

  const handleReaction = async (type) => {
    setMyReaction(type);
    setAnimate(type);
    setTimeout(() => setAnimate(null), 600);
    await sendReaction(currentSlide, type);
    const r = await getReactions(currentSlide);
    setReactions(r);
  };

  return (
    <div className="container" style={{ maxWidth: 800 }}>
      <div className="page-header">
        <h1>강의 실시간 반응</h1>
        <p>현재 슬라이드에 대한 반응을 보내주세요</p>
      </div>

      {/* 슬라이드 번호 */}
      <div className="card" style={{ textAlign: 'center', marginBottom: 16, padding: 24 }}>
        <div style={{ fontSize: '.85em', color: 'var(--text3)', marginBottom: 8 }}>현재 슬라이드</div>
        <div style={{ fontSize: '3em', fontWeight: 900, color: 'var(--blue)' }}>{currentSlide}</div>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: 12 }}>
          <button className="btn btn-blue" style={{ padding: '6px 20px' }}
            onClick={() => setCurrentSlide(s => Math.max(1, s - 1))}>← 이전</button>
          <input type="number" value={currentSlide} onChange={e => setCurrentSlide(Number(e.target.value) || 1)}
            style={{ width: 60, textAlign: 'center', border: '1px solid var(--border)', borderRadius: 8, padding: 6 }} />
          <button className="btn btn-blue" style={{ padding: '6px 20px' }}
            onClick={() => setCurrentSlide(s => s + 1)}>다음 →</button>
        </div>
      </div>

      {/* 반응 버튼 */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ textAlign: 'center', marginBottom: 12 }}>반응 보내기</h3>
        <div className="reaction-bar">
          {REACTIONS.map(r => (
            <button key={r.type} className="reaction-btn"
              onClick={() => handleReaction(r.type)}
              style={{
                transform: animate === r.type ? 'scale(1.3)' : 'scale(1)',
                background: myReaction === r.type ? '#dbeafe' : 'var(--bg2)',
                borderColor: myReaction === r.type ? 'var(--blue)' : 'var(--border)',
              }}>
              <span style={{ fontSize: '1.3em' }}>{r.emoji}</span>
              <div style={{ fontSize: '.7em', color: 'var(--text3)', marginTop: 2 }}>{r.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 반응 현황 */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3>현재 반응 현황</h3>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 12 }}>
          {REACTIONS.map(r => (
            <div key={r.type} style={{ textAlign: 'center', minWidth: 60 }}>
              <div style={{ fontSize: '1.5em' }}>{r.emoji}</div>
              <div style={{ fontSize: '1.3em', fontWeight: 800, color: 'var(--blue)' }}>
                {reactions[r.type] || 0}
              </div>
              <div style={{ fontSize: '.7em', color: 'var(--text3)' }}>{r.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 질문 입력 */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3>질문하기</h3>
        <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
          <input
            value={questionText}
            onChange={e => setQuestionText(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendQuestion()}
            placeholder="질문을 입력하세요..."
            style={{ flex: 1, padding: 10, border: '1px solid var(--border)', borderRadius: 8 }}
          />
          <button className="btn btn-blue" onClick={sendQuestion}>전송</button>
        </div>
        {questionSent && <div style={{ fontSize: '.85em', color: 'var(--green)', marginTop: 8 }}>✅ 질문이 전송되었습니다</div>}
      </div>

      {/* 질문 목록 */}
      {questions.length > 0 && (
        <div className="card">
          <h3>질문 목록 ({questions.length})</h3>
          {questions.map((q, i) => (
            <div key={i} style={{ padding: '10px 0', borderBottom: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 600 }}>{q.user}</span>
                <span style={{ fontSize: '.78em', color: 'var(--text3)' }}>
                  {new Date(q.timestamp).toLocaleTimeString('ko-KR')}
                </span>
              </div>
              <div style={{ marginTop: 4, color: 'var(--text2)' }}>{q.text}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
