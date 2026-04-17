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
  const colors = ['#1d4ed8', '#0f766e', '#b45309', '#0b5cad', '#8a5b24'];
  const color = colors[id % colors.length];
  const styleVariants = [
    { background: `${color}E8`, color: '#fff', borderRadius: 999, padding: '10px 18px' },
    { background: 'rgba(255,255,255,.92)', color, border: `1px solid ${color}40`, borderRadius: 999, padding: '9px 18px' },
    { background: `${color}18`, color, border: `1px solid ${color}26`, borderRadius: 18, padding: '10px 18px' },
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
        fontSize: '.92em', fontWeight: 700,
        boxShadow: '0 16px 30px rgba(23,34,51,.12)',
        pointerEvents: 'none', zIndex: 50,
        whiteSpace: 'nowrap',
      }}
    >
      {user}: {text}
    </motion.div>
  );
}


export default function Slides({ user }) {
  const [currentSlide, setCurrentSlide] = useState(1);
  const [locked, setLocked] = useState(true);   // 강사 슬라이드 잠금 여부 (기본 잠김)
  const [reactions, setReactions] = useState({});
  const [questionText, setQuestionText] = useState('');
  const [questionSent, setQuestionSent] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [allQuestions, setAllQuestions] = useState([]);

  // 떠오르는 이모지 목록
  const [floatingEmojis, setFloatingEmojis] = useState([]);
  const emojiIdRef = useRef(0);

  // 떠다니는 질문 목록
  const [floatingQuestions, setFloatingQuestions] = useState([]);
  const questionIdRef = useRef(0);
  const seenQuestionTimestamps = useRef(new Set());

  const isPresenter = user?.is_presenter;
  const isOfflineArchive = typeof window !== 'undefined' && Boolean(window.__OFFLINE_ARCHIVE__);
  const totalSlides = SLIDES.length;

  // 수강생: 슬라이드 동기화 (locked일 때만) + lock 상태 polling
  useEffect(() => {
    if (isPresenter) return;
    const sync = () => {
      fetchJSON('/slides/current').then(d => {
        if (typeof d.locked === 'boolean') setLocked(d.locked);
        // 잠긴 상태일 때만 강사 슬라이드를 강제로 따라감
        if (d.locked && d.slide) {
          setCurrentSlide(Number(d.slide));   // 동일값이면 React가 재렌더 스킵
        }
      }).catch(() => {});
    };
    sync();
    const interval = setInterval(sync, 2000);
    return () => clearInterval(interval);
  }, [isPresenter]);

  // 강사: lock 상태 초기 로드 (서버 재시작 후 동기화)
  useEffect(() => {
    if (!isPresenter) return;
    fetchJSON('/slides/current').then(d => {
      if (typeof d.locked === 'boolean') setLocked(d.locked);
    }).catch(() => {});
  }, [isPresenter]);

  // 강사: lock 토글
  const toggleLock = useCallback(async () => {
    if (!isPresenter) return;
    const next = !locked;
    setLocked(next);
    try {
      await postJSON('/slides/lock', { locked: next });
    } catch {
      setLocked(locked);   // 실패 시 롤백
    }
  }, [isPresenter, locked]);

  // 반응 카운트 가져오기
  useEffect(() => {
    if (isOfflineArchive) return;
    const load = () => fetchJSON(`/reactions?slide=${currentSlide}`).then(setReactions).catch(() => {});
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [currentSlide, isOfflineArchive]);

  // 강사: 전체 질문 히스토리 로드
  useEffect(() => {
    if (isOfflineArchive) return;
    if (!isPresenter) return;
    const load = () => fetchJSON('/questions?slide=0').then(setAllQuestions).catch(() => {});
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [isPresenter, isOfflineArchive]);

  // 새 질문 감지 → 떠다니게 표시
  useEffect(() => {
    if (isOfflineArchive) return;
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
  }, [currentSlide, isOfflineArchive]);

  // 강사: 슬라이드 변경
  const goTo = useCallback((n) => {
    const next = Math.max(1, Math.min(totalSlides, n));
    setCurrentSlide(next);
    seenQuestionTimestamps.current.clear();
    setFloatingQuestions([]);
    if (isPresenter) postJSON('/slides/current', { slide: next });
  }, [isPresenter, totalSlides]);

  // 키보드 (강사는 항상, 수강생은 unlock 상태일 때)
  useEffect(() => {
    if (!isPresenter && locked) return;
    const handler = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); goTo(currentSlide + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(currentSlide - 1); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isPresenter, locked, currentSlide, goTo]);

  // 반응 보내기 + 이모지 뿅
  const sendReaction = async (type, emoji) => {
    if (isOfflineArchive) return;
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
    if (isOfflineArchive) return;
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
  const slideRuntime = {
    locked,
    isPresenter,
    downloadsEnabled: isPresenter || !locked,
    offlineArchive: isOfflineArchive,
  };

  return (
    <div className="presentation-shell" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* 떠오르는 이모지 */}
      <AnimatePresence>
        {floatingEmojis.map(e => (
          <FloatingEmoji key={e.id} emoji={e.emoji} id={e.id} onDone={() => removeEmoji(e.id)} />
        ))}
      </AnimatePresence>

      {/* 슬라이드 영역 — 반응바와 독립, 질문은 이 안에서만 흐름 */}
      <div className="presentation-stage" style={{ flex: 1, position: 'relative', overflow: 'hidden', minHeight: 0 }}>
        {/* 떠다니는 질문 (슬라이드 영역 내) */}
        <AnimatePresence>
          {floatingQuestions.map(q => (
            <FloatingQuestion key={q.id} text={q.text} user={q.user} id={q.id} lane={q.lane} onDone={() => removeQuestion(q.id)} />
          ))}
        </AnimatePresence>
        <AnimatePresence mode="wait">
          {SlideComponent && <SlideComponent key={currentSlide} slideRuntime={slideRuntime} />}
        </AnimatePresence>

        {/* 사이드바 토글 버튼 (강사 항상, 수강생은 unlock 시) */}
        {(isPresenter || !locked) && (
          <button
            type="button"
            onClick={() => setShowSidebar(prev => !prev)}
            className="presentation-sidebar-toggle"
            style={{
              position: 'fixed', top: 16, left: 16,
              width: 42, height: 42, zIndex: 260,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            ☰
          </button>
        )}

        {/* 수강생용 잠금 상태 인디케이터 */}
        {!isPresenter && (
          <div className="presentation-lock-badge" style={{
            position: 'absolute', top: 12, right: 12, zIndex: 60,
            fontSize: '.75em', fontWeight: 700,
          }}>
            {locked ? '🔒 강사 화면 따라감' : '🔓 자유 탐색 중'}
          </div>
        )}

        {/* 슬라이드 카운터 */}
        <div className="presentation-counter" style={{
          position: 'absolute', bottom: 8, right: 16, fontSize: '.8em', color: '#94a3b8', fontFamily: 'monospace',
        }}>
          {currentSlide} / {totalSlides}
        </div>

        {/* 사이드바 (강사 항상, 수강생은 unlock 시) */}
        {(isPresenter || !locked) && showSidebar && (
          <motion.div
            initial={{ opacity: 0, x: -280 }} animate={{ opacity: 1, x: 0 }}
            className="presentation-sidebar"
            style={{
              position: 'fixed', top: 0, left: 0, bottom: 0, width: 280,
              overflowY: 'auto', zIndex: 250, padding: '12px 0',
            }}
          >
            <div className="presentation-sidebar-header" style={{ padding: '8px 16px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 700, fontSize: '.9em', color: '#1e293b' }}>슬라이드 목록</span>
              <button type="button" onClick={() => setShowSidebar(false)} style={{ border: 'none', background: 'none', cursor: 'pointer', color: '#94a3b8', fontSize: '1.1em' }}>✕</button>
            </div>
            {isOfflineArchive ? (
              <div className="presentation-sidebar-links" style={{ display: 'flex', gap: 6, padding: '8px 16px' }}>
                <span className="presentation-sidebar-link" style={{ cursor: 'default' }}>오프라인 보관본</span>
              </div>
            ) : (
              <div className="presentation-sidebar-links" style={{ display: 'flex', gap: 6, padding: '8px 16px' }}>
                <a href="/" className="presentation-sidebar-link">대시보드</a>
                <a href="/challenges/prompt" className="presentation-sidebar-link">프롬프트 과제</a>
              </div>
            )}
            {SLIDES.map((s, i) => {
              const num = i + 1;
              const isCurrent = num === currentSlide;
              const isSection = s.title.startsWith('#') || s.title === 'Day 1' || s.title === 'Day 2' || s.title === '종합 실습' || s.title === 'Day 1 실습' || s.title === '마무리';
              const canNav = isPresenter || !locked;
              return (
                <div
                  key={num}
                  onClick={() => { if (canNav) { goTo(num); setShowSidebar(false); } }}
                  className="presentation-slide-row"
                  style={{
                    padding: isSection ? '8px 16px 4px' : '6px 16px 6px 28px',
                    cursor: canNav ? 'pointer' : 'default',
                    background: isCurrent ? 'rgba(29,78,216,.08)' : 'transparent',
                    borderLeft: isCurrent ? '3px solid #1d4ed8' : '3px solid transparent',
                    transition: 'background .15s',
                    fontSize: isSection ? '.78em' : '.82em',
                    fontWeight: isSection ? 700 : 400,
                    color: isSection ? '#1d4ed8' : isCurrent ? '#182230' : '#55606f',
                    textTransform: isSection ? 'uppercase' : 'none',
                    letterSpacing: isSection ? '.5px' : 0,
                    marginTop: isSection ? 8 : 0,
                  }}
                  onMouseEnter={e => { if (!isCurrent) e.currentTarget.style.background = 'rgba(255,255,255,.54)'; }}
                  onMouseLeave={e => { if (!isCurrent) e.currentTarget.style.background = 'transparent'; }}
                >
                  {!isSection && <span style={{ color: '#94a3b8', marginRight: 8, fontFamily: 'monospace', fontSize: '.85em' }}>{num}</span>}
                  {s.title}
                </div>
              );
            })}
          </motion.div>
        )}

        {/* 강사 전용: 슬라이드 넘기기는 반응바에 있음 */}

        {/* 강사 전용 질문 히스토리 */}
        {isPresenter && showHistory && (
          <motion.div
            initial={{ opacity: 0, x: 300 }} animate={{ opacity: 1, x: 0 }}
            className="presentation-history"
            style={{
              position: 'absolute', top: 0, right: 0, bottom: 0, width: 360,
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
      <div className="presentation-dock" style={{
        padding: '12px 24px',
        display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0,
      }}>
        {/* 네비게이션 컨트롤 (강사 항상, 수강생은 unlock 시) */}
        {(isPresenter || !locked) && (
          <div className="presentation-nav" style={{ display: 'flex', gap: 6, alignItems: 'center', marginRight: 8 }}>
            <button className="presentation-nav-btn" onClick={() => goTo(currentSlide - 1)} style={{ padding: '6px 10px', fontSize: '.85em' }}>←</button>
            <span style={{ fontSize: '.8em', color: '#64748b', fontFamily: 'monospace', minWidth: 50, textAlign: 'center' }}>{currentSlide}/{SLIDES.length}</span>
            <button className="presentation-nav-btn" onClick={() => goTo(currentSlide + 1)} style={{ padding: '6px 10px', fontSize: '.85em' }}>→</button>
            {isPresenter && (
              <>
                <button onClick={toggleLock}
                  className="presentation-state-btn"
                  title={locked ? '수강생 자유 탐색 허용' : '수강생을 강사 화면으로 잠금'}
                  style={{
                    padding: '6px 10px', borderRadius: 8, cursor: 'pointer', fontSize: '.78em', fontWeight: 700,
                    border: `1px solid ${locked ? '#fde68a' : '#86efac'}`,
                    background: locked ? '#fef3c7' : '#dcfce7',
                    color: locked ? '#92400e' : '#166534',
                  }}>
                  {locked ? '🔒 잠김' : '🔓 해제'}
                </button>
                <button onClick={() => setShowHistory(prev => !prev)}
                  className="presentation-state-btn"
                  style={{ padding: '6px 10px', border: '1px solid #dbeafe', borderRadius: 8, background: '#eff6ff', cursor: 'pointer', fontSize: '.78em', color: '#2563eb' }}>
                  💬{allQuestions.length > 0 ? ` ${allQuestions.length}` : ''}
                </button>
              </>
            )}
            <div style={{ width: 1, height: 24, background: '#e2e8f0' }} />
          </div>
        )}

        {!locked && !isOfflineArchive && (
          <>
            <a
              href="/downloads/lecture/html"
              download
              className="presentation-state-btn"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: '10px 14px',
                border: '1px solid rgba(37,99,235,.18)',
                borderRadius: 12,
                background: 'linear-gradient(180deg, #ffffff 0%, #eff6ff 100%)',
                color: '#1d4ed8',
                textDecoration: 'none',
                fontSize: '.82em',
                fontWeight: 700,
                whiteSpace: 'nowrap',
                boxShadow: '0 10px 24px rgba(37,99,235,.12)',
              }}
              title="오프라인 열람용 HTML 강의안 다운로드"
            >
              강의안 다운로드
            </a>
            <div style={{ width: 1, height: 32, background: 'rgba(88,72,49,.12)', flexShrink: 0 }} />
          </>
        )}

        {isOfflineArchive ? (
          <>
            <div style={{ width: 1, height: 32, background: 'rgba(88,72,49,.12)', flexShrink: 0 }} />
            <div style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              padding: '0 4px',
              color: '#55606f',
              fontSize: '.84em',
              fontWeight: 700,
            }}>
              오프라인 보관본에서는 질문, 반응, 실시간 동기화, 실습 제출이 비활성화됩니다.
            </div>
          </>
        ) : (
          <>
            <div className="presentation-reactions" style={{ display: 'flex', gap: 8 }}>
              {REACTIONS.map(r => (
                <button
                  key={r.type}
                  onClick={() => sendReaction(r.type, r.emoji)}
                  className="presentation-reaction-btn"
                  style={{
                    width: 48, height: 48,
                    fontSize: '1.2em',
                    cursor: 'pointer', transition: 'all .15s',
                    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                    position: 'relative',
                  }}
                  onMouseDown={e => { e.currentTarget.style.transform = 'scale(0.9)'; }}
                  onMouseUp={e => { e.currentTarget.style.transform = 'scale(1)'; }}
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

            <div style={{ width: 1, height: 32, background: 'rgba(88,72,49,.12)', flexShrink: 0 }} />

            <div style={{ flex: 1, display: 'flex', gap: 8, alignItems: 'center' }}>
              <input
                value={questionText}
                onChange={e => setQuestionText(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendQuestion()}
                placeholder="💬 질문을 입력하세요..."
                className="presentation-question-input"
                style={{
                  flex: 1, padding: '12px 18px',
                  fontSize: '.92em',
                }}
              />
              <button
                onClick={sendQuestion}
                className="presentation-submit-btn"
                style={{
                  padding: '12px 20px', borderRadius: 12,
                  fontSize: '.88em', fontWeight: 600, cursor: 'pointer',
                  transition: 'all .15s', whiteSpace: 'nowrap',
                }}
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
          </>
        )}
      </div>
    </div>
  );
}
