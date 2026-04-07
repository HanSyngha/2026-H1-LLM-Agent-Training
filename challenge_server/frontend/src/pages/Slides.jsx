import { useState, useEffect, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import { postJSON, fetchJSON } from '../api';
import SLIDES from '../slides';
import '../slides/slides.css';

const REACTIONS = [
  { type: 'like', emoji: '👍' },
  { type: 'question', emoji: '❓' },
  { type: 'confused', emoji: '😕' },
  { type: 'yes', emoji: '✅' },
  { type: 'no', emoji: '❌' },
  { type: 'fast', emoji: '⏩' },
  { type: 'slow', emoji: '⏪' },
];

export default function Slides({ user }) {
  const [currentSlide, setCurrentSlide] = useState(1);
  const [reactions, setReactions] = useState({});
  const [questionText, setQuestionText] = useState('');
  const [questions, setQuestions] = useState([]);
  const [questionSent, setQuestionSent] = useState(false);
  const [animate, setAnimate] = useState(null);

  const isPresenter = user?.sub === 'syngha.han';
  const totalSlides = SLIDES.length;

  // 서버에서 현재 슬라이드 번호 가져오기 (수강생 동기화)
  useEffect(() => {
    if (isPresenter) return; // 강사는 동기화 안 함
    const sync = () => {
      fetchJSON('/slides/current').then(d => {
        if (d.slide && d.slide !== currentSlide) setCurrentSlide(d.slide);
      }).catch(() => {});
    };
    sync();
    const interval = setInterval(sync, 2000);
    return () => clearInterval(interval);
  }, [isPresenter, currentSlide]);

  // 반응/질문 가져오기
  useEffect(() => {
    const load = () => {
      fetchJSON(`/reactions?slide=${currentSlide}`).then(setReactions).catch(() => {});
      fetchJSON(`/questions?slide=${currentSlide}`).then(setQuestions).catch(() => {});
    };
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [currentSlide]);

  // 강사: 슬라이드 변경
  const goTo = useCallback((n) => {
    const next = Math.max(1, Math.min(totalSlides, n));
    setCurrentSlide(next);
    if (isPresenter) {
      postJSON('/slides/current', { slide: next });
    }
  }, [isPresenter, totalSlides]);

  // 키보드 네비게이션 (강사만)
  useEffect(() => {
    if (!isPresenter) return;
    const handler = (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); goTo(currentSlide + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(currentSlide - 1); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isPresenter, currentSlide, goTo]);

  // 반응 전송
  const sendReaction = async (type) => {
    setAnimate(type);
    setTimeout(() => setAnimate(null), 500);
    await postJSON('/reactions', { slide: currentSlide, type });
    fetchJSON(`/reactions?slide=${currentSlide}`).then(setReactions);
  };

  // 질문 전송
  const sendQuestion = async () => {
    if (!questionText.trim()) return;
    await postJSON('/questions', { slide: currentSlide, text: questionText });
    setQuestionText('');
    setQuestionSent(true);
    setTimeout(() => setQuestionSent(false), 2000);
    fetchJSON(`/questions?slide=${currentSlide}`).then(setQuestions);
  };

  const slideData = SLIDES[currentSlide - 1];
  const SlideComponent = slideData?.component;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 'calc(100vh - 49px)' }}>
      {/* 슬라이드 영역 */}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        <AnimatePresence mode="wait">
          {SlideComponent && <SlideComponent key={currentSlide} />}
        </AnimatePresence>

        {/* 슬라이드 카운터 */}
        <div style={{
          position: 'absolute', bottom: 8, right: 16, fontSize: '.8em', color: '#94a3b8', fontFamily: 'monospace',
        }}>
          {currentSlide} / {totalSlides}
        </div>

        {/* 강사 컨트롤 */}
        {isPresenter && (
          <div style={{
            position: 'absolute', bottom: 8, left: 16, display: 'flex', gap: 8, alignItems: 'center',
          }}>
            <button onClick={() => goTo(currentSlide - 1)} className="btn btn-blue" style={{ padding: '4px 12px', fontSize: '.8em' }}>←</button>
            <span style={{ fontSize: '.8em', color: '#64748b', fontFamily: 'monospace' }}>{currentSlide}</span>
            <button onClick={() => goTo(currentSlide + 1)} className="btn btn-blue" style={{ padding: '4px 12px', fontSize: '.8em' }}>→</button>
            <span style={{ fontSize: '.7em', color: '#d97706', background: '#fef3c7', padding: '2px 8px', borderRadius: 8 }}>강사 모드</span>
          </div>
        )}
      </div>

      {/* 하단 반응/질문 바 (모든 슬라이드에서) */}
      <div style={{
        borderTop: '1px solid #e2e8f0', background: '#fff', padding: '12px 24px',
        display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap',
      }}>
        {/* 반응 버튼 */}
        <div style={{ display: 'flex', gap: 6 }}>
          {REACTIONS.map(r => (
            <button
              key={r.type}
              onClick={() => sendReaction(r.type)}
              style={{
                padding: '6px 12px', border: '1px solid #e2e8f0', borderRadius: 20, background: '#fff',
                fontSize: '1.1em', cursor: 'pointer', transition: 'all .15s',
                transform: animate === r.type ? 'scale(1.3)' : 'scale(1)',
              }}
            >
              {r.emoji}
              {reactions[r.type] > 0 && (
                <span style={{ fontSize: '.65em', color: '#64748b', marginLeft: 2 }}>{reactions[r.type]}</span>
              )}
            </button>
          ))}
        </div>

        {/* 질문 입력 */}
        <div style={{ flex: 1, display: 'flex', gap: 8, minWidth: 200 }}>
          <input
            value={questionText}
            onChange={e => setQuestionText(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendQuestion()}
            placeholder="질문을 입력하세요..."
            style={{ flex: 1, padding: '8px 14px', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: '.88em' }}
          />
          <button className="btn btn-blue" style={{ padding: '8px 16px', fontSize: '.85em' }} onClick={sendQuestion}>
            전송
          </button>
        </div>

        {questionSent && <span style={{ fontSize: '.8em', color: '#059669' }}>✅ 전송됨</span>}

        {/* 질문 카운트 (강사용) */}
        {isPresenter && questions.length > 0 && (
          <span style={{ fontSize: '.8em', color: '#dc2626', fontWeight: 600 }}>
            💬 질문 {questions.length}개
          </span>
        )}
      </div>
    </div>
  );
}
