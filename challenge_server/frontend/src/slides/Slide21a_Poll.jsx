import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { postJSON, fetchJSON } from '../api';

export default function Slide21a_Poll() {
  const [votes, setVotes] = useState({ yes: 0, no: 0 });
  const [myVote, setMyVote] = useState(null);
  const [showResult, setShowResult] = useState(false);

  // 실시간 집계 polling
  useEffect(() => {
    const load = () => fetchJSON('/reactions?slide=9999').then(d => {
      setVotes({ yes: d.poll_yes || 0, no: d.poll_no || 0 });
    }).catch(() => {});
    load();
    const interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, []);

  const vote = async (choice) => {
    if (myVote) return; // 중복 투표 방지
    setMyVote(choice);
    await postJSON('/reactions', { slide: 9999, type: `poll_${choice}` });
    const d = await fetchJSON('/reactions?slide=9999');
    setVotes({ yes: d.poll_yes || 0, no: d.poll_no || 0 });
    // 1초 후 결과 공개
    setTimeout(() => setShowResult(true), 800);
  };

  const total = votes.yes + votes.no;
  const yesPct = total > 0 ? Math.round((votes.yes / total) * 100) : 0;
  const noPct = total > 0 ? Math.round((votes.no / total) * 100) : 0;

  return (
    <div className="slide-container" style={{ background: 'linear-gradient(135deg, #0f172a, #1e293b)', color: '#f1f5f9' }}>
      <div className="slide-inner" style={{ maxWidth: 800 }}>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          style={{ fontSize: '1.5em', marginBottom: 16, opacity: 0.5 }}
        >
          💬
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          style={{
            fontSize: '2.4em', fontWeight: 900, lineHeight: 1.3,
            background: 'linear-gradient(135deg, #60a5fa, #a78bfa)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}
        >
          "이제 Prompt Engineering의<br />시대는 끝났다"
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          style={{ color: 'rgba(241,245,249,.5)', marginTop: 12, fontSize: '1.1em' }}
        >
          동의하십니까?
        </motion.p>

        {/* 투표 버튼 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          style={{ display: 'flex', gap: 24, justifyContent: 'center', marginTop: 40 }}
        >
          <button
            onClick={() => vote('yes')}
            disabled={!!myVote}
            style={{
              width: 160, height: 160, borderRadius: 24,
              border: myVote === 'yes' ? '3px solid #22c55e' : '2px solid rgba(241,245,249,.15)',
              background: myVote === 'yes' ? 'rgba(34,197,94,.15)' : 'rgba(241,245,249,.05)',
              color: '#f1f5f9', cursor: myVote ? 'default' : 'pointer',
              transition: 'all .2s', display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', gap: 8,
            }}
          >
            <span style={{ fontSize: '3em' }}>⭕</span>
            <span style={{ fontSize: '1.2em', fontWeight: 700 }}>YES</span>
          </button>

          <button
            onClick={() => vote('no')}
            disabled={!!myVote}
            style={{
              width: 160, height: 160, borderRadius: 24,
              border: myVote === 'no' ? '3px solid #ef4444' : '2px solid rgba(241,245,249,.15)',
              background: myVote === 'no' ? 'rgba(239,68,68,.15)' : 'rgba(241,245,249,.05)',
              color: '#f1f5f9', cursor: myVote ? 'default' : 'pointer',
              transition: 'all .2s', display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', gap: 8,
            }}
          >
            <span style={{ fontSize: '3em' }}>❌</span>
            <span style={{ fontSize: '1.2em', fontWeight: 700 }}>NO</span>
          </button>
        </motion.div>

        {/* 실시간 참여자 수 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          style={{ marginTop: 24, color: 'rgba(241,245,249,.4)', fontSize: '.9em' }}
        >
          {total > 0 ? `${total}명 참여` : '아래 버튼을 눌러주세요'}
        </motion.div>

        {/* 결과 바 (투표 후 표시) */}
        <AnimatePresence>
          {(showResult || total > 3) && total > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              style={{ marginTop: 32, width: '100%', maxWidth: 500, margin: '32px auto 0' }}
            >
              {/* YES 바 */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                <span style={{ width: 40, textAlign: 'right', fontWeight: 700, color: '#22c55e' }}>YES</span>
                <div style={{ flex: 1, height: 32, background: 'rgba(241,245,249,.1)', borderRadius: 8, overflow: 'hidden', position: 'relative' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${yesPct}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    style={{ height: '100%', background: 'linear-gradient(90deg, #22c55e, #16a34a)', borderRadius: 8 }}
                  />
                  <span style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', fontSize: '.85em', fontWeight: 700 }}>
                    {yesPct}% ({votes.yes})
                  </span>
                </div>
              </div>

              {/* NO 바 */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ width: 40, textAlign: 'right', fontWeight: 700, color: '#ef4444' }}>NO</span>
                <div style={{ flex: 1, height: 32, background: 'rgba(241,245,249,.1)', borderRadius: 8, overflow: 'hidden', position: 'relative' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${noPct}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    style={{ height: '100%', background: 'linear-gradient(90deg, #ef4444, #dc2626)', borderRadius: 8 }}
                  />
                  <span style={{ position: 'absolute', right: 8, top: '50%', transform: 'translateY(-50%)', fontSize: '.85em', fontWeight: 700 }}>
                    {noPct}% ({votes.no})
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
