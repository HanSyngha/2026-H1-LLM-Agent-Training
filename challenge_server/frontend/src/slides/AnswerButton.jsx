import { useState, useEffect } from 'react';
import { getMe } from '../api';

/**
 * 예시 답안 버튼 + 모달
 *
 * Props:
 *   answerId: string - 답안 식별자 (예: "prompt", "endpoint", "tool_use", "browser")
 *   children: ReactNode - 답안 내용 (기존 Answer 슬라이드 컴포넌트의 내용)
 */
export default function AnswerButton({ answerId, children }) {
  const [isPresenter, setIsPresenter] = useState(false);

  useEffect(() => {
    getMe().then(u => { if (u?.user?.sub === 'syngha.han') setIsPresenter(true); });
  }, []);
  const [unlocked, setUnlocked] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [toast, setToast] = useState(null);

  // 공개 상태 확인
  const checkStatus = async () => {
    try {
      const resp = await fetch('/answers/status', { credentials: 'include' });
      const data = await resp.json();
      setUnlocked((data.unlocked || []).includes(answerId));
    } catch {}
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 3000);
    return () => clearInterval(interval);
  }, [answerId]);

  // 강사: 공개/잠금 토글
  const handleToggle = async () => {
    try {
      const resp = await fetch('/answers/toggle', {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: answerId }),
      });
      const data = await resp.json();
      setUnlocked(data.unlocked);
    } catch {}
  };

  // 수강생: 답안 보기 클릭
  const handleClick = () => {
    if (unlocked) {
      setShowModal(true);
    } else {
      setToast('조금 더 도전해보세요! 곧 예시 답안을 보여드릴게요 💪');
      setTimeout(() => setToast(null), 3000);
    }
  };

  return (
    <>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 12 }}>
        <button onClick={handleClick}
          style={{
            padding: '8px 20px', borderRadius: 8, border: 'none',
            background: unlocked ? '#7c3aed' : '#e2e8f0',
            color: unlocked ? '#fff' : '#64748b',
            fontWeight: 700, fontSize: '.88em', cursor: 'pointer',
            transition: 'all 0.2s',
          }}>
          {unlocked ? '💡 예시 답안 보기' : '🔒 예시 답안'}
        </button>

        {isPresenter && (
          <button onClick={handleToggle}
            style={{
              padding: '6px 14px', borderRadius: 6,
              border: `1.5px solid ${unlocked ? '#dc2626' : '#059669'}`,
              background: 'transparent',
              color: unlocked ? '#dc2626' : '#059669',
              fontWeight: 600, fontSize: '.78em', cursor: 'pointer',
            }}>
            {unlocked ? '🔒 잠금' : '🔓 공개하기'}
          </button>
        )}
      </div>

      {/* 토스트 메시지 */}
      {toast && (
        <div style={{
          marginTop: 8, padding: '10px 16px', borderRadius: 8,
          background: '#fef3c7', color: '#92400e', fontSize: '.88em',
          fontWeight: 600, animation: 'fadeIn .3s',
        }}>
          {toast}
        </div>
      )}

      {/* 모달 */}
      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,.6)', zIndex: 9999,
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          backdropFilter: 'blur(4px)',
        }} onClick={() => setShowModal(false)}>
          <div style={{
            background: '#fff', borderRadius: 16, padding: '32px 36px',
            maxWidth: 800, width: '90%', maxHeight: '80vh', overflowY: 'auto',
            boxShadow: '0 25px 60px rgba(0,0,0,.3)',
            position: 'relative',
          }} onClick={e => e.stopPropagation()}>
            <button onClick={() => setShowModal(false)}
              style={{
                position: 'absolute', top: 12, right: 16,
                background: 'none', border: 'none', fontSize: '1.3em',
                cursor: 'pointer', color: '#94a3b8',
              }}>
              ✕
            </button>
            {children}
          </div>
        </div>
      )}
    </>
  );
}
