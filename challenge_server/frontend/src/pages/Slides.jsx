import { useState, useEffect, useCallback, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
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

// 떠오르는 이모지
function FloatingEmoji({ emoji, id, onDone }) {
  const x = Math.random() * 80 + 10; // 10~90%
  return (
    <motion.div
      key={id}
      initial={{ opacity: 1, y: 0, x: `${x}vw`, scale: 1 }}
      animate={{ opacity: 0, y: -400, scale: 1.5 }}
      transition={{ duration: 2, ease: 'easeOut' }}
      onAnimationComplete={onDone}
      style={{
        position: 'fixed', bottom: 80, left: 0,
        fontSize: '2em', pointerEvents: 'none', zIndex: 1000,
      }}
    >
      {emoji}
    </motion.div>
  );
}

// 떠다니는 질문
function FloatingQuestion({ text, user, id, onDone }) {
  const y = Math.random() * 60 + 15; // 15~75% from top
  const colors = ['#dc2626', '#2563eb', '#7c3aed', '#059669', '#d97706'];
  const color = colors[id % colors.length];

  return (
    <motion.div
      key={id}
      initial={{ opacity: 0, x: '110%' }}
      animate={{ opacity: 1, x: '-110%' }}
      transition={{ duration: 12, ease: 'linear' }}
      onAnimationComplete={onDone}
      style={{
        position: 'fixed', top: `${y}%`, right: 0,
        padding: '8px 20px', borderRadius: 24,
        background: color, color: '#fff',
        fontSize: '1em', fontWeight: 600,
        boxShadow: '0 4px 16px rgba(0,0,0,.15)',
        pointerEvents: 'none', zIndex: 999,
        whiteSpace: 'nowrap',
      }}
    >
      {user}: {text}
    </motion.div>
  );
}

export default function Slides({ user }) {
  const [currentSlide, setCurrentSlide] = useState(1);
  const [reactions, setReactions] = useState({});
  const [questionText, setQuestionText] = useState('');
  const [questionSent, setQuestionSent] = useState(false);

  // 떠오르는 이모지 목록
  const [floatingEmojis, setFloatingEmojis] = useState([]);
  const emojiIdRef = useRef(0);

  // 떠다니는 질문 목록
  const [floatingQuestions, setFloatingQuestions] = useState([]);
  const questionIdRef = useRef(0);
  const seenQuestionTimestamps = useRef(new Set());

  const isPresenter = user?.sub === 'syngha.han';
  const totalSlides = SLIDES.length;

  // 수강생: 슬라이드 동기화
  useEffect(() => {
    if (isPresenter) return;
    const sync = () => {
      fetchJSON('/slides/current').then(d => {
        if (d.slide && d.slide !== currentSlide) setCurrentSlide(d.slide);
      }).catch(() => {});
    };
    sync();
    const interval = setInterval(sync, 2000);
    return () => clearInterval(interval);
  }, [isPresenter]);

  // 반응 카운트 가져오기
  useEffect(() => {
    const load = () => fetchJSON(`/reactions?slide=${currentSlide}`).then(setReactions).catch(() => {});
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [currentSlide]);

  // 새 질문 감지 → 떠다니게 표시
  useEffect(() => {
    const load = () => {
      fetchJSON(`/questions?slide=${currentSlide}`).then(qs => {
        qs.forEach(q => {
          if (!seenQuestionTimestamps.current.has(q.timestamp)) {
            seenQuestionTimestamps.current.add(q.timestamp);
            const id = questionIdRef.current++;
            setFloatingQuestions(prev => [...prev, { ...q, id }]);
          }
        });
      }).catch(() => {});
    };
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [currentSlide]);

  // 강사: 슬라이드 변경
  const goTo = useCallback((n) => {
    const next = Math.max(1, Math.min(totalSlides, n));
    setCurrentSlide(next);
    seenQuestionTimestamps.current.clear();
    setFloatingQuestions([]);
    if (isPresenter) postJSON('/slides/current', { slide: next });
  }, [isPresenter, totalSlides]);

  // 키보드 (강사만)
  useEffect(() => {
    if (!isPresenter) return;
    const handler = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); goTo(currentSlide + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(currentSlide - 1); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isPresenter, currentSlide, goTo]);

  // 반응 보내기 + 이모지 뿅
  const sendReaction = async (type, emoji) => {
    const id = emojiIdRef.current++;
    setFloatingEmojis(prev => [...prev, { emoji, id }]);
    await postJSON('/reactions', { slide: currentSlide, type });
    fetchJSON(`/reactions?slide=${currentSlide}`).then(setReactions);
  };

  // 떠오르는 이모지 완료 제거
  const removeEmoji = (id) => {
    setFloatingEmojis(prev => prev.filter(e => e.id !== id));
  };

  // 떠다니는 질문 완료 제거
  const removeQuestion = (id) => {
    setFloatingQuestions(prev => prev.filter(q => q.id !== id));
  };

  // 질문 전송
  const sendQuestion = async () => {
    if (!questionText.trim()) return;
    await postJSON('/questions', { slide: currentSlide, text: questionText });
    setQuestionText('');
    setQuestionSent(true);
    setTimeout(() => setQuestionSent(false), 2000);
  };

  const slideData = SLIDES[currentSlide - 1];
  const SlideComponent = slideData?.component;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 49px)', overflow: 'hidden' }}>
      {/* 떠오르는 이모지 */}
      <AnimatePresence>
        {floatingEmojis.map(e => (
          <FloatingEmoji key={e.id} emoji={e.emoji} id={e.id} onDone={() => removeEmoji(e.id)} />
        ))}
      </AnimatePresence>

      {/* 떠다니는 질문 */}
      <AnimatePresence>
        {floatingQuestions.map(q => (
          <FloatingQuestion key={q.id} text={q.text} user={q.user} id={q.id} onDone={() => removeQuestion(q.id)} />
        ))}
      </AnimatePresence>

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

      {/* 하단 바 */}
      <div style={{
        borderTop: '1px solid #e2e8f0', background: '#fff', padding: '10px 24px',
        display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0,
      }}>
        {REACTIONS.map(r => (
          <button
            key={r.type}
            onClick={() => sendReaction(r.type, r.emoji)}
            style={{
              padding: '6px 10px', border: '1px solid #e2e8f0', borderRadius: 20, background: '#fff',
              fontSize: '1.1em', cursor: 'pointer', transition: 'transform .1s',
            }}
            onMouseDown={e => e.currentTarget.style.transform = 'scale(0.85)'}
            onMouseUp={e => e.currentTarget.style.transform = 'scale(1)'}
          >
            {r.emoji}
            {reactions[r.type] > 0 && (
              <span style={{ fontSize: '.6em', color: '#94a3b8', marginLeft: 2 }}>{reactions[r.type]}</span>
            )}
          </button>
        ))}

        <div style={{ width: 1, height: 24, background: '#e2e8f0' }} />

        <input
          value={questionText}
          onChange={e => setQuestionText(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendQuestion()}
          placeholder="질문을 입력하세요..."
          style={{ flex: 1, padding: '8px 14px', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: '.88em', minWidth: 150 }}
        />
        <button className="btn btn-blue" style={{ padding: '8px 16px', fontSize: '.85em' }} onClick={sendQuestion}>
          전송
        </button>
        {questionSent && <span style={{ fontSize: '.75em', color: '#059669' }}>✅</span>}
      </div>
    </div>
  );
}
