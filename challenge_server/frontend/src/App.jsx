import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe } from './api';
import Dashboard from './pages/Dashboard';
import PromptChallenge from './pages/PromptChallenge';
import Questions from './pages/Questions';
import Feedback from './pages/Feedback';
import Slides from './pages/Slides';
import Settings from './pages/Settings';
import Navbar from './components/Navbar';
import './App.css';

function HoverNavbar({ user }) {
  const [visible, setVisible] = useState(false);
  return (
    <>
      <div
        onMouseEnter={() => setVisible(true)}
        style={{ position: 'fixed', top: 0, left: 0, right: 0, height: 8, zIndex: 200 }}
      />
      <div
        onMouseEnter={() => setVisible(true)}
        onMouseLeave={() => setVisible(false)}
        style={{
          position: 'fixed', top: 0, left: 0, right: 0, zIndex: 199,
          transform: visible ? 'translateY(0)' : 'translateY(-100%)',
          transition: 'transform .25s ease',
        }}
      >
        <Navbar user={user} />
      </div>
    </>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const isOfflineArchive = typeof window !== 'undefined' && Boolean(window.__OFFLINE_ARCHIVE__);

  useEffect(() => {
    getMe().then(data => {
      if (data?.logged_in) setUser(data.user);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading">로딩 중...</div>;

  // 미로그인 시 자동 SSO 리다이렉트 (설정 페이지 제외)
  if (!user && window.location.pathname !== '/settings') {
    window.location.href = `/auth/login?redirect=${encodeURIComponent(window.location.pathname)}`;
    return <div className="loading">SSO 로그인으로 이동 중...</div>;
  }

  return (
    <BrowserRouter>
      {!isOfflineArchive && <HoverNavbar user={user} />}
      {isOfflineArchive ? (
        <Routes>
          <Route path="*" element={<Slides user={user} />} />
        </Routes>
      ) : (
        <Routes>
          <Route path="/" element={<Dashboard user={user} />} />
          <Route path="/slides" element={<Slides user={user} />} />
          <Route path="/challenges/prompt" element={<PromptChallenge user={user} />} />
          <Route path="/questions" element={<Questions />} />
          <Route path="/feedback" element={<Feedback />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      )}
    </BrowserRouter>
  );
}
