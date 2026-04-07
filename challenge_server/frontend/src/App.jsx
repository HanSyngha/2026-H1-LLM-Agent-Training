import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe } from './api';
import Dashboard from './pages/Dashboard';
import PromptChallenge from './pages/PromptChallenge';
import Slides from './pages/Slides';
import Settings from './pages/Settings';
import Navbar from './components/Navbar';
import './App.css';

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe().then(data => {
      if (data?.logged_in) setUser(data.user);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="loading">로딩 중...</div>;

  return (
    <BrowserRouter>
      <Navbar user={user} />
      <Routes>
        <Route path="/" element={<Dashboard user={user} />} />
        <Route path="/slides" element={<Slides user={user} />} />
        <Route path="/challenges/prompt" element={<PromptChallenge user={user} />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </BrowserRouter>
  );
}
