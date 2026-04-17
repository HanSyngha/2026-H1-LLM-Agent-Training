import { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getCompletions, resetCompletions, getMe } from '../api';

/* ── helpers ───────────────────────────────────────── */

function medal(rank) {
  if (rank === 0) return '🥇';
  if (rank === 1) return '🥈';
  if (rank === 2) return '🥉';
  return `${rank + 1}`;
}

function timeAgo(ts) {
  const d = new Date(ts);
  return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function relativeTime(ts) {
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return '방금 전';
  if (mins < 60) return `${mins}분 전`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}시간 전`;
  return `${Math.floor(hrs / 24)}일 전`;
}

/* ── build overall leaderboard ─────────────────────── */

// 순위에서 제외할 과제 (연습/워밍업용)
const EXCLUDED_FROM_RANKING = ['sso_oidc', 'prompt'];
// 점수제 과제 (VL 채점 — score 필드 사용)
const SCORE_BASED = ['react_dashboard'];

function buildLeaderboard(challenges) {
  const rankedIds = Object.keys(challenges).filter(id => !EXCLUDED_FROM_RANKING.includes(id) && !SCORE_BASED.includes(id));
  const userMap = {}; // sub -> { name, dept, totalScore }

  // 1. 일반 과제: 완료 순서 기반 점수 (1위=20점, 꼴찌=1점, 균등 분배)
  rankedIds.forEach((id) => {
    const comps = challenges[id].completions || [];
    const n = comps.length;
    comps.forEach((c, rank) => {
      if (!userMap[c.sub]) {
        userMap[c.sub] = { sub: c.sub, name: c.name, dept: c.dept, totalScore: 0, challenges: 0 };
      }
      // 점수: 1위=20, 꼴찌=1, 균등 분배
      const score = n <= 1 ? 20 : Math.round(20 - (rank * 19) / (n - 1));
      userMap[c.sub].totalScore += score;
      userMap[c.sub].challenges += 1;
    });
  });

  // 2. 점수제 과제: score 필드 그대로 합산
  SCORE_BASED.forEach((id) => {
    const comps = challenges[id]?.completions || [];
    comps.forEach((c) => {
      if (!userMap[c.sub]) {
        userMap[c.sub] = { sub: c.sub, name: c.name, dept: c.dept, totalScore: 0, challenges: 0 };
      }
      userMap[c.sub].totalScore += (c.score || 0);
      userMap[c.sub].challenges += 1;
    });
  });

  return Object.values(userMap).sort((a, b) => b.totalScore - a.totalScore);
}

/* ── styles (CSS-in-JS for self-contained component) ── */

const S = {
  page: {
    maxWidth: 1240,
    margin: '0 auto',
    padding: '42px 24px 72px',
  },
  header: {
    position: 'relative',
    overflow: 'hidden',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    gap: 24,
    marginBottom: 28,
    padding: '34px 36px',
    borderRadius: 32,
    border: '1px solid rgba(88,72,49,.12)',
    background: 'linear-gradient(145deg, rgba(255,255,255,.9), rgba(255,251,244,.82))',
    boxShadow: '0 24px 60px rgba(23,34,51,.12)',
  },
  title: {
    fontSize: 'clamp(2.3rem, 4vw, 3.25rem)',
    fontWeight: 900,
    color: '#182230',
    letterSpacing: '-0.05em',
    lineHeight: 1,
  },
  subtitle: {
    color: '#55606f',
    fontSize: '0.96rem',
    marginTop: 14,
    lineHeight: 1.7,
    maxWidth: 620,
  },
  refreshDot: {
    display: 'inline-block',
    width: 10,
    height: 10,
    borderRadius: '50%',
    background: '#0f766e',
    marginRight: 8,
    animation: 'pulse-dot 2s ease-in-out infinite',
  },
  heroGlow: {
    position: 'absolute',
    width: 260,
    height: 260,
    right: -100,
    top: -100,
    borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(15,118,110,.12), transparent 68%)',
    pointerEvents: 'none',
  },
  heroActions: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    flexWrap: 'wrap',
    justifyContent: 'flex-end',
    zIndex: 1,
  },
  heroChip: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    padding: '10px 14px',
    borderRadius: 999,
    border: '1px solid rgba(88,72,49,.12)',
    background: 'rgba(255,255,255,.72)',
    color: '#55606f',
    fontSize: '.84rem',
    fontWeight: 700,
  },
  resetButton: {
    padding: '12px 18px',
    borderRadius: 999,
    border: '1px solid rgba(180,35,24,.18)',
    background: 'rgba(255,244,242,.94)',
    color: '#b42318',
    fontWeight: 800,
    fontSize: '.84rem',
    cursor: 'pointer',
    boxShadow: '0 12px 24px rgba(180,35,24,.08)',
  },

  /* stats bar */
  statsBar: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: 16,
    marginBottom: 32,
  },
  statCard: {
    background: 'linear-gradient(180deg, rgba(255,255,255,.88), rgba(255,252,246,.82))',
    border: '1px solid rgba(88,72,49,.12)',
    borderRadius: 28,
    padding: '24px 22px',
    textAlign: 'left',
    boxShadow: '0 18px 44px rgba(23,34,51,.08)',
  },
  statNum: {
    fontSize: '2.35rem',
    fontWeight: 900,
    lineHeight: 1.1,
    letterSpacing: '-0.05em',
  },
  statLabel: {
    fontSize: '0.74rem',
    color: '#7a8697',
    marginTop: 12,
    textTransform: 'uppercase',
    letterSpacing: '.12em',
    fontWeight: 800,
  },

  /* leaderboard */
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: '1.1rem',
    fontWeight: 900,
    color: '#182230',
    marginBottom: 16,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    letterSpacing: '-0.03em',
  },
  leaderboardCard: {
    background: 'linear-gradient(180deg, rgba(255,255,255,.9), rgba(255,252,246,.82))',
    border: '1px solid rgba(88,72,49,.12)',
    borderRadius: 28,
    overflow: 'hidden',
    boxShadow: '0 18px 46px rgba(23,34,51,.08)',
  },
  topThree: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 0,
    borderBottom: '1px solid rgba(88,72,49,.12)',
  },
  podium: (rank) => ({
    padding: '28px 18px',
    textAlign: 'center',
    borderRight: rank < 2 ? '1px solid rgba(88,72,49,.12)' : 'none',
    background: rank === 0 ? 'linear-gradient(180deg, rgba(255,247,229,.98) 0%, rgba(255,255,255,.92) 100%)' : 'rgba(255,255,255,.72)',
  }),
  podiumMedal: {
    fontSize: '2rem',
    marginBottom: 6,
  },
  podiumName: {
    fontSize: '1.02rem',
    fontWeight: 900,
    color: '#182230',
  },
  podiumDept: {
    fontSize: '0.78rem',
    color: '#7a8697',
    marginTop: 4,
  },
  podiumCount: (rank) => ({
    marginTop: 10,
    display: 'inline-block',
    padding: '6px 12px',
    borderRadius: 999,
    fontSize: '0.8rem',
    fontWeight: 800,
    background: rank === 0 ? 'rgba(180,83,9,.1)' : rank === 1 ? 'rgba(29,78,216,.08)' : 'rgba(15,118,110,.08)',
    color: rank === 0 ? '#b45309' : rank === 1 ? '#1d4ed8' : '#0f766e',
  }),
  leaderRow: (isEven) => ({
    display: 'flex',
    alignItems: 'center',
    padding: '14px 22px',
    gap: 14,
    background: isEven ? 'rgba(255,255,255,.5)' : 'rgba(255,255,255,.76)',
    borderBottom: '1px solid rgba(88,72,49,.08)',
    fontSize: '0.9rem',
  }),
  leaderRank: {
    width: 32,
    textAlign: 'center',
    fontWeight: 800,
    color: '#7a8697',
    fontSize: '0.85rem',
    flexShrink: 0,
  },

  /* challenge cards */
  challengeCard: (isOpen) => ({
    background: 'linear-gradient(180deg, rgba(255,255,255,.88), rgba(255,252,246,.82))',
    border: '1px solid rgba(88,72,49,.12)',
    borderRadius: 26,
    overflow: 'hidden',
    boxShadow: isOpen ? '0 24px 56px rgba(23,34,51,.12)' : '0 16px 38px rgba(23,34,51,.08)',
    transition: 'box-shadow 0.2s, transform .2s',
    cursor: 'pointer',
  }),
  challengeHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '20px 24px',
    gap: 12,
  },
  challengeName: {
    fontSize: '1rem',
    fontWeight: 900,
    color: '#182230',
    flex: 1,
  },
  challengeMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    flexShrink: 0,
  },
  countBadge: (hasComps) => ({
    padding: '6px 12px',
    borderRadius: 999,
    fontSize: '0.78rem',
    fontWeight: 800,
    background: hasComps ? 'rgba(15,118,110,.08)' : 'rgba(29,78,216,.06)',
    color: hasComps ? '#0f766e' : '#55606f',
  }),
  topCompleter: {
    fontSize: '0.82rem',
    color: '#55606f',
    fontWeight: 700,
    maxWidth: 120,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  chevron: (isOpen) => ({
    width: 20,
    height: 20,
    color: '#7a8697',
    transition: 'transform 0.25s',
    transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
    flexShrink: 0,
  }),
  expandedBody: {
    borderTop: '1px solid rgba(88,72,49,.12)',
    background: 'rgba(255,255,255,.46)',
  },
  completionRow: (rank) => ({
    display: 'flex',
    alignItems: 'center',
    padding: '14px 22px',
    gap: 14,
    borderBottom: '1px solid rgba(88,72,49,.08)',
    background: rank < 3 ? (rank === 0 ? 'rgba(255,247,229,.7)' : 'rgba(255,255,255,.68)') : 'rgba(255,255,255,.42)',
  }),
  rankBadge: (rank) => {
    const colors = {
      0: { bg: 'rgba(180,83,9,.12)', color: '#b45309' },
      1: { bg: 'rgba(29,78,216,.08)', color: '#1d4ed8' },
      2: { bg: 'rgba(15,118,110,.08)', color: '#0f766e' },
    };
    const c = colors[rank] || { bg: 'rgba(88,72,49,.08)', color: '#7a8697' };
    return {
      width: 30,
      height: 30,
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: rank < 3 ? '1rem' : '0.78rem',
      fontWeight: 800,
      background: c.bg,
      color: c.color,
      flexShrink: 0,
    };
  },
  emptyState: {
    textAlign: 'center',
    padding: '34px 18px',
    color: '#7a8697',
    fontSize: '0.9rem',
  },
  cardsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
    gap: 16,
  },
};

/* ── CSS keyframes injected once ──────────────────── */

const styleId = '__dashboard-keyframes';
if (typeof document !== 'undefined' && !document.getElementById(styleId)) {
  const style = document.createElement('style');
  style.id = styleId;
  style.textContent = `
    @keyframes pulse-dot {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }
    @media (max-width: 768px) {
      .dash-stats-bar { grid-template-columns: repeat(2, 1fr) !important; }
      .dash-top-three { grid-template-columns: 1fr !important; }
      .dash-top-three > div { border-right: none !important; border-bottom: 1px solid rgba(88,72,49,.12); }
      .dash-cards-grid { grid-template-columns: 1fr !important; }
    }
    @media (max-width: 480px) {
      .dash-stats-bar { grid-template-columns: 1fr !important; }
    }
  `;
  document.head.appendChild(style);
}

/* ── Chevron SVG icon ─────────────────────────────── */

function ChevronDown({ style }) {
  return (
    <svg style={style} viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clipRule="evenodd" />
    </svg>
  );
}

/* ── Challenge Card component ─────────────────────── */

function ChallengeCard({ name, completions, isAdmin, challengeId, onReset }) {
  const [open, setOpen] = useState(false);
  const comps = completions || [];
  const topCompleter = comps.length > 0 ? comps[0] : null;

  return (
    <motion.div
      style={S.challengeCard(open)}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.15 }}
      layout
    >
      <div style={S.challengeHeader} onClick={() => setOpen(!open)}>
        <div style={S.challengeName}>{name}</div>
        <div style={S.challengeMeta}>
          {topCompleter && (
            <span style={S.topCompleter}>
              {medal(0)} {topCompleter.name}
            </span>
          )}
          <span style={S.countBadge(comps.length > 0)}>
            {comps.length}명 완료
          </span>
          {isAdmin && comps.length > 0 && (
            <button onClick={(e) => { e.stopPropagation(); onReset(challengeId); }}
              style={{ padding: '8px 12px', borderRadius: 999, border: '1px solid rgba(180,35,24,.18)',
                background: 'rgba(255,244,242,.9)', color: '#b42318', fontSize: '.72em', cursor: 'pointer',
                fontWeight: 800 }}>
              초기화
            </button>
          )}
          <ChevronDown style={S.chevron(open)} />
        </div>
      </div>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="body"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
            style={{ overflow: 'hidden' }}
          >
            <div style={S.expandedBody}>
              {comps.length === 0 ? (
                <div style={S.emptyState}>아직 완료한 분이 없습니다</div>
              ) : (
                comps.map((c, i) => (
                  <div key={c.sub + i} style={S.completionRow(i)}>
                    <div style={S.rankBadge(i)}>
                      {i < 3 ? medal(i) : i + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 800, fontSize: '0.92rem', color: '#182230' }}>
                        {c.name}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: '#7a8697' }}>
                        {c.dept}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <div style={{ fontSize: '0.82rem', fontFamily: 'monospace', color: '#55606f', fontWeight: 700 }}>
                        {timeAgo(c.timestamp)}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#7a8697' }}>
                        {relativeTime(c.timestamp)}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/* ── Main Dashboard ───────────────────────────────── */

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [user, setUser] = useState(null);
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    getMe().then(u => { if (u && u.logged_in) setUser(u.user); });
  }, []);

  useEffect(() => {
    const load = () => getCompletions().then(setData).catch(() => {});
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  const isAdmin = user?.is_presenter;

  const handleReset = async () => {
    if (!confirm('정말 모든 과제 기록을 초기화하시겠습니까?')) return;
    setResetting(true);
    try {
      await resetCompletions();
      const fresh = await getCompletions();
      setData(fresh);
    } catch (e) {
      alert('초기화 실패: ' + e.message);
    }
    setResetting(false);
  };

  const { challenges, ids, totalCompletions, allUsers, leaderboard } = useMemo(() => {
    if (!data) return { challenges: {}, ids: [], totalCompletions: 0, allUsers: new Set(), leaderboard: [] };

    const ch = data.challenges || {};
    const cids = Object.keys(ch);
    const rankedIds = cids.filter(id => !EXCLUDED_FROM_RANKING.includes(id));
    let total = 0;
    const users = new Set();

    rankedIds.forEach((id) => {
      (ch[id].completions || []).forEach((c) => {
        total++;
        users.add(c.sub);
      });
    });

    return {
      challenges: ch,
      ids: cids,
      totalCompletions: total,
      allUsers: users,
      leaderboard: buildLeaderboard(ch),
    };
  }, [data]);

  if (!data) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh', color: '#94a3b8', fontSize: '1.1rem' }}>
        <motion.div
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          로딩 중입니다...
        </motion.div>
      </div>
    );
  }

  const champion = leaderboard.length > 0 ? leaderboard[0] : null;

  return (
    <div style={S.page}>
      {/* ── Header ── */}
      <div style={S.header}>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ fontSize: '.8rem', color: '#b45309', fontWeight: 800, letterSpacing: '.12em', textTransform: 'uppercase', marginBottom: 10 }}>
            Lecture Operations
          </div>
          <h1 style={S.title}>Challenge Dashboard</h1>
          <p style={S.subtitle}>
            <span style={S.refreshDot} />
            실습 진행도, 종합 순위, 과제별 완료 현황을 한 화면에서 확인합니다. 강의 중 운영 판단이 빠르게 되도록 설계했습니다.
          </p>
        </div>
        <div style={S.heroActions}>
          <span style={S.heroChip}>A2G Intranet</span>
          <span style={S.heroChip}>5초 자동 갱신</span>
          {isAdmin && (
            <button
              onClick={handleReset}
              disabled={resetting}
              style={{ ...S.resetButton, opacity: resetting ? 0.7 : 1 }}
            >
              {resetting ? '초기화 중...' : '전체 초기화'}
            </button>
          )}
        </div>
        <div style={S.heroGlow} />
      </div>

      {/* ── Stats Bar ── */}
      <div className="dash-stats-bar" style={S.statsBar}>
        <motion.div style={S.statCard} whileHover={{ y: -2 }}>
          <div style={{ ...S.statNum, color: '#2563eb' }}>{ids.length}</div>
          <div style={S.statLabel}>총 챌린지</div>
        </motion.div>
        <motion.div style={S.statCard} whileHover={{ y: -2 }}>
          <div style={{ ...S.statNum, color: '#0f766e' }}>{totalCompletions}</div>
          <div style={S.statLabel}>총 완료</div>
        </motion.div>
        <motion.div style={S.statCard} whileHover={{ y: -2 }}>
          <div style={{ ...S.statNum, color: '#b45309' }}>{allUsers.size}</div>
          <div style={S.statLabel}>참여자</div>
        </motion.div>
        <motion.div style={S.statCard} whileHover={{ y: -2 }}>
          <div style={{ ...S.statNum, color: '#182230', fontSize: '1.4rem', lineHeight: 1.3 }}>
            {champion ? `👑 ${champion.name} (${champion.totalScore}점)` : '—'}
          </div>
          <div style={S.statLabel}>현재 1위</div>
        </motion.div>
      </div>

      {/* ── Overall Leaderboard ── */}
      {leaderboard.length > 0 && (
        <div style={S.section}>
          <div style={S.sectionTitle}>
            🏆 종합 순위
          </div>
          <div style={S.leaderboardCard}>
            {/* Top 3 podium */}
            {leaderboard.length >= 1 && (
              <div className="dash-top-three" style={S.topThree}>
                {leaderboard.slice(0, 3).map((u, i) => (
                  <motion.div
                    key={u.sub}
                    style={S.podium(i)}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1, duration: 0.35 }}
                  >
                    <div style={S.podiumMedal}>{medal(i)}</div>
                    <div style={S.podiumName}>{u.name}</div>
                    <div style={S.podiumDept}>{u.dept}</div>
                    <div style={S.podiumCount(i)}>
                      {u.totalScore}점
                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Remaining ranks (4th+) */}
            {leaderboard.slice(3).map((u, idx) => (
              <div key={u.sub} style={S.leaderRow(idx % 2 === 0)}>
                <div style={S.leaderRank}>{idx + 4}</div>
                <div style={{ flex: 1 }}>
                  <span style={{ fontWeight: 800, fontSize: '0.9rem', color: '#182230' }}>{u.name}</span>
                  <span style={{ color: '#7a8697', fontSize: '0.8rem', marginLeft: 8 }}>{u.dept}</span>
                </div>
                <span style={{
                  padding: '6px 12px',
                  borderRadius: 999,
                  fontSize: '0.78rem',
                  fontWeight: 800,
                  background: 'rgba(29,78,216,.06)',
                  color: '#1d4ed8',
                }}>
                  {u.totalScore}점
                </span>
              </div>
            ))}

            {leaderboard.length === 0 && (
              <div style={S.emptyState}>아직 참여자가 없습니다</div>
            )}
          </div>
        </div>
      )}

      {/* ── Challenge Cards ── */}
      <div style={S.section}>
        <div style={S.sectionTitle}>
          📋 챌린지별 현황
        </div>
        <div className="dash-cards-grid" style={S.cardsGrid}>
          {ids.map((id) => (
            <ChallengeCard
              key={id}
              challengeId={id}
              name={challenges[id].name}
              completions={challenges[id].completions}
              isAdmin={isAdmin}
              onReset={async (cid) => {
                if (!confirm(`'${challenges[cid].name}' 과제를 초기화하시겠습니까?`)) return;
                await resetCompletions(cid);
                const fresh = await getCompletions();
                setData(fresh);
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
