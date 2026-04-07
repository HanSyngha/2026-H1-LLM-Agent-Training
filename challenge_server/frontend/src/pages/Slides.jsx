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

// 떠오르는 이모지 — 우측에서 위로, 여운 있게
function FloatingEmoji({ emoji, id, onDone }) {
  return (
    <motion.div
      key={id}
      initial={{ opacity: 1, y: 0, scale: 0.8 }}
      animate={{ opacity: [1, 1, 0.8, 0], y: -350, scale: [0.8, 1.4, 1.2, 1] }}
      transition={{ duration: 2.5, ease: 'easeOut', times: [0, 0.2, 0.7, 1] }}
      onAnimationComplete={onDone}
      style={{
        position: 'fixed', bottom: 80, right: 30,
        fontSize: '2.2em', pointerEvents: 'none', zIndex: 1000,
      }}
    >
      {emoji}
    </motion.div>
  );
}

// 사용 중인 줄(높이) 추적 — 겹침 방지
const usedLanes = new Set();
const LANE_HEIGHT = 8; // 줄 간격 (% 단위)
const TOTAL_LANES = Math.floor(85 / LANE_HEIGHT); // 약 10줄

function getFreeLane() {
  // 빈 줄 찾기
  for (let i = 0; i < TOTAL_LANES; i++) {
    if (!usedLanes.has(i)) {
      usedLanes.add(i);
      return i;
    }
  }
  // 다 차면 랜덤
  return Math.floor(Math.random() * TOTAL_LANES);
}

function releaseLane(lane) {
  usedLanes.delete(lane);
}

// 떠다니는 질문 — 니코니코 스타일 (겹침 방지, 높이만 랜덤)
function FloatingQuestion({ text, user, id, lane, onDone }) {
  const y = 5 + lane * LANE_HEIGHT; // 줄 번호 → % 높이
  const duration = 13 + Math.random() * 5; // 13~18초
  const colors = ['#dc2626', '#2563eb', '#7c3aed', '#059669', '#d97706', '#0891b2', '#be185d'];
  const color = colors[id % colors.length];
  const styleVariants = [
    { background: color, color: '#fff', borderRadius: 24, padding: '8px 22px' },
    { background: 'transparent', color, border: `2px solid ${color}`, borderRadius: 24, padding: '6px 20px' },
    { background: `${color}15`, color, borderRadius: 8, padding: '8px 20px' },
  ];
  const style = styleVariants[id % styleVariants.length];

  return (
    <motion.div
      key={id}
      initial={{ right: '-50%' }}
      animate={{ right: '150%' }}
      transition={{ duration, ease: 'linear' }}
      onAnimationComplete={() => { releaseLane(lane); onDone(); }}
      style={{
        position: 'absolute', top: `${y}%`,
        ...style,
        fontSize: '1em', fontWeight: 600,
        boxShadow: '0 2px 12px rgba(0,0,0,.1)',
        pointerEvents: 'none', zIndex: 50,
        whiteSpace: 'nowrap',
      }}
    >
      {user}: {text}
    </motion.div>
  );
}

// 슬라이드 내용이 넘치면 자동 축소
function AutoFitSlide({ children }) {
  const containerRef = useRef(null);
  const innerRef = useRef(null);
  const [scale, setScale] = useState(1);

  useEffect(() => {
    const fit = () => {
      if (!containerRef.current || !innerRef.current) return;
      const containerH = containerRef.current.offsetHeight;
      const innerH = innerRef.current.scrollHeight;
      if (innerH > containerH) {
        setScale(Math.max(0.55, containerH / innerH));
      } else {
        setScale(1);
      }
    };
    fit();
    window.addEventListener('resize', fit);
    return () => window.removeEventListener('resize', fit);
  }, [children]);

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
      <div ref={innerRef} style={{ transform: `scale(${scale})`, transformOrigin: 'top center', width: '100%' }}>
        {children}
      </div>
    </div>
  );
}

export default function Slides({ user }) {
  const [currentSlide, setCurrentSlide] = useState(1);
  const [reactions, setReactions] = useState({});
  const [questionText, setQuestionText] = useState('');
  const [questionSent, setQuestionSent] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [allQuestions, setAllQuestions] = useState([]);

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

  // 강사: 전체 질문 히스토리 로드
  useEffect(() => {
    if (!isPresenter) return;
    const load = () => fetchJSON('/questions?slide=0').then(setAllQuestions).catch(() => {});
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [isPresenter]);

  // 새 질문 감지 → 떠다니게 표시
  useEffect(() => {
    const load = () => {
      fetchJSON(`/questions?slide=${currentSlide}`).then(qs => {
        qs.forEach(q => {
          // timestamp + text 조합으로 중복 체크 (본인 질문 + 서버 질문 모두)
          const key = q.timestamp + '|' + q.text;
          if (!seenQuestionTimestamps.current.has(key) && !seenQuestionTimestamps.current.has(q.text)) {
            seenQuestionTimestamps.current.add(key);
            const id = questionIdRef.current++;
            const lane = getFreeLane();
            setFloatingQuestions(prev => [...prev, { ...q, id, lane }]);
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

  // 질문 전송 — 보내자마자 바로 화면에 표시
  const sendQuestion = async () => {
    if (!questionText.trim()) return;
    const text = questionText;
    setQuestionText('');
    setQuestionSent(true);
    setTimeout(() => setQuestionSent(false), 2000);

    // 서버에 보내기 전에 바로 화면에 띄우기
    const id = questionIdRef.current++;
    const lane = getFreeLane();
    const userName = user?.name || '익명';
    const now = new Date().toISOString();
    setFloatingQuestions(prev => [...prev, { text, user: userName, id, lane, timestamp: now }]);
    // 본인 질문은 미리 seen 처리 (polling에서 중복 방지)
    seenQuestionTimestamps.current.add(text);

    await postJSON('/questions', { slide: currentSlide, text });
  };

  const slideData = SLIDES[currentSlide - 1];
  const SlideComponent = slideData?.component;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 49px)' }}>
      {/* 떠오르는 이모지 */}
      <AnimatePresence>
        {floatingEmojis.map(e => (
          <FloatingEmoji key={e.id} emoji={e.emoji} id={e.id} onDone={() => removeEmoji(e.id)} />
        ))}
      </AnimatePresence>

      {/* 슬라이드 영역 — 반응바와 독립, 질문은 이 안에서만 흐름 */}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden', minHeight: 0 }}>
        {/* 떠다니는 질문 (슬라이드 영역 내) */}
        <AnimatePresence>
          {floatingQuestions.map(q => (
            <FloatingQuestion key={q.id} text={q.text} user={q.user} id={q.id} lane={q.lane} onDone={() => removeQuestion(q.id)} />
          ))}
        </AnimatePresence>
        <AnimatePresence mode="wait">
          {SlideComponent && <AutoFitSlide key={currentSlide}><SlideComponent /></AutoFitSlide>}
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
            <button
              onClick={() => setShowHistory(prev => !prev)}
              style={{ fontSize: '.7em', color: '#2563eb', background: '#dbeafe', padding: '2px 8px', borderRadius: 8, border: 'none', cursor: 'pointer' }}
            >
              💬 질문 {allQuestions.length}
            </button>
          </div>
        )}

        {/* 강사 전용 질문 히스토리 */}
        {isPresenter && showHistory && (
          <motion.div
            initial={{ opacity: 0, x: 300 }} animate={{ opacity: 1, x: 0 }}
            style={{
              position: 'absolute', top: 0, right: 0, bottom: 0, width: 360,
              background: '#fff', borderLeft: '1px solid #e2e8f0',
              boxShadow: '-4px 0 20px rgba(0,0,0,.08)',
              overflowY: 'auto', padding: 20, zIndex: 50,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ fontSize: '1em', color: '#1e293b' }}>💬 질문 히스토리</h3>
              <button onClick={() => setShowHistory(false)} style={{ border: 'none', background: 'none', fontSize: '1.2em', cursor: 'pointer', color: '#94a3b8' }}>✕</button>
            </div>
            {allQuestions.length === 0 ? (
              <p style={{ color: '#94a3b8', textAlign: 'center', padding: 20 }}>아직 질문이 없습니다</p>
            ) : (
              allQuestions.map((q, i) => (
                <div key={i} style={{ padding: '10px 0', borderBottom: '1px solid #f1f5f9' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '.8em' }}>
                    <span style={{ fontWeight: 600, color: '#1e293b' }}>{q.user}</span>
                    <span style={{ color: '#94a3b8' }}>슬라이드 {q.slide} · {new Date(q.timestamp).toLocaleTimeString('ko-KR')}</span>
                  </div>
                  <p style={{ color: '#475569', marginTop: 4, fontSize: '.92em' }}>{q.text}</p>
                </div>
              ))
            )}
          </motion.div>
        )}
      </div>

      {/* 하단 반응/질문 바 */}
      <div style={{
        borderTop: '1px solid #e2e8f0',
        background: 'linear-gradient(180deg, #f8fafc, #fff)',
        padding: '16px 32px',
        display: 'flex', alignItems: 'center', gap: 16, flexShrink: 0,
        boxShadow: '0 -2px 12px rgba(0,0,0,.04)',
      }}>
        <div style={{ display: 'flex', gap: 8 }}>
          {REACTIONS.map(r => (
            <button
              key={r.type}
              onClick={() => sendReaction(r.type, r.emoji)}
              style={{
                width: 48, height: 48,
                border: '1px solid #e2e8f0', borderRadius: 14,
                background: '#fff', fontSize: '1.3em',
                cursor: 'pointer', transition: 'all .15s',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                boxShadow: '0 1px 3px rgba(0,0,0,.04)',
                position: 'relative',
              }}
              onMouseDown={e => { e.currentTarget.style.transform = 'scale(0.85)'; e.currentTarget.style.background = '#f1f5f9'; }}
              onMouseUp={e => { e.currentTarget.style.transform = 'scale(1)'; e.currentTarget.style.background = '#fff'; }}
            >
              {r.emoji}
              {reactions[r.type] > 0 && (
                <span style={{
                  position: 'absolute', top: -6, right: -6,
                  fontSize: '.5em', fontWeight: 700, color: '#fff',
                  background: '#2563eb', borderRadius: 10,
                  padding: '1px 5px', minWidth: 16, textAlign: 'center',
                }}>{reactions[r.type]}</span>
              )}
            </button>
          ))}
        </div>

        <div style={{ width: 1, height: 32, background: '#e2e8f0', flexShrink: 0 }} />

        <div style={{ flex: 1, display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            value={questionText}
            onChange={e => setQuestionText(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendQuestion()}
            placeholder="💬 질문을 입력하세요..."
            style={{
              flex: 1, padding: '12px 18px',
              border: '1px solid #e2e8f0', borderRadius: 12,
              fontSize: '.92em', background: '#f8fafc',
              outline: 'none', transition: 'border-color .2s',
            }}
            onFocus={e => e.target.style.borderColor = '#2563eb'}
            onBlur={e => e.target.style.borderColor = '#e2e8f0'}
          />
          <button
            onClick={sendQuestion}
            style={{
              padding: '12px 20px', borderRadius: 12,
              background: '#2563eb', color: '#fff', border: 'none',
              fontSize: '.88em', fontWeight: 600, cursor: 'pointer',
              transition: 'all .15s', whiteSpace: 'nowrap',
            }}
            onMouseDown={e => e.currentTarget.style.background = '#1d4ed8'}
            onMouseUp={e => e.currentTarget.style.background = '#2563eb'}
          >
            전송
          </button>
          {questionSent && (
            <motion.span
              initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }}
              style={{ fontSize: '1.2em' }}
            >✅</motion.span>
          )}
        </div>
      </div>
    </div>
  );
}
