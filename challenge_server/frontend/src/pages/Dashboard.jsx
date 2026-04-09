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

function buildLeaderboard(challenges) {
  const ids = Object.keys(challenges).filter(id => !EXCLUDED_FROM_RANKING.includes(id));
  const userMap = {}; // sub -> { name, dept, count, latestTimestamp }

  ids.forEach((id) => {
    const comps = challenges[id].completions || [];
    comps.forEach((c) => {
      if (!userMap[c.sub]) {
        userMap[c.sub] = { sub: c.sub, name: c.name, dept: c.dept, count: 0, latestTimestamp: c.timestamp };
      }
      userMap[c.sub].count += 1;
      // Track the latest completion timestamp (= the time they finished their last challenge)
      if (new Date(c.timestamp) > new Date(userMap[c.sub].latestTimestamp)) {
        userMap[c.sub].latestTimestamp = c.timestamp;
      }
    });
  });

  const sorted = Object.values(userMap).sort((a, b) => {
    if (b.count !== a.count) return b.count - a.count;
    // Same count → earlier latest-completion wins
    return new Date(a.latestTimestamp) - new Date(b.latestTimestamp);
  });

  return sorted;
}

/* ── styles (CSS-in-JS for self-contained component) ── */

const S = {
  page: {
    maxWidth: 1100,
    margin: '0 auto',
    padding: '32px 20px 64px',
  },
  header: {
    textAlign: 'center',
    marginBottom: 32,
  },
  title: {
    fontSize: '2rem',
    fontWeight: 900,
    color: '#0f172a',
    letterSpacing: '-0.02em',
  },
  subtitle: {
    color: '#94a3b8',
    fontSize: '0.95rem',
    marginTop: 6,
  },
  refreshDot: {
    display: 'inline-block',
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: '#22c55e',
    marginRight: 8,
    animation: 'pulse-dot 2s ease-in-out infinite',
  },

  /* stats bar */
  statsBar: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: 14,
    marginBottom: 32,
  },
  statCard: {
    background: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: 14,
    padding: '20px 16px',
    textAlign: 'center',
    boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
  },
  statNum: {
    fontSize: '2.2rem',
    fontWeight: 900,
    lineHeight: 1.1,
  },
  statLabel: {
    fontSize: '0.78rem',
    color: '#94a3b8',
    marginTop: 4,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    fontWeight: 600,
  },

  /* leaderboard */
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: '1.15rem',
    fontWeight: 800,
    color: '#1e293b',
    marginBottom: 14,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
  },
  leaderboardCard: {
    background: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: 14,
    overflow: 'hidden',
    boxShadow: '0 1px 4px rgba(0,0,0,0.04)',
  },
  topThree: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: 0,
    borderBottom: '1px solid #e2e8f0',
  },
  podium: (rank) => ({
    padding: '24px 16px',
    textAlign: 'center',
    borderRight: rank < 2 ? '1px solid #e2e8f0' : 'none',
    background: rank === 0 ? 'linear-gradient(180deg, #fffbeb 0%, #fff 100%)' : '#fff',
  }),
  podiumMedal: {
    fontSize: '2.2rem',
    marginBottom: 6,
  },
  podiumName: {
    fontSize: '1rem',
    fontWeight: 800,
    color: '#1e293b',
  },
  podiumDept: {
    fontSize: '0.78rem',
    color: '#94a3b8',
    marginTop: 2,
  },
  podiumCount: (rank) => ({
    marginTop: 8,
    display: 'inline-block',
    padding: '3px 12px',
    borderRadius: 20,
    fontSize: '0.8rem',
    fontWeight: 700,
    background: rank === 0 ? '#fef3c7' : rank === 1 ? '#f1f5f9' : rank === 2 ? '#fef3c7' : '#f1f5f9',
    color: rank === 0 ? '#92400e' : rank === 1 ? '#475569' : rank === 2 ? '#92400e' : '#475569',
  }),
  leaderRow: (isEven) => ({
    display: 'flex',
    alignItems: 'center',
    padding: '12px 20px',
    gap: 14,
    background: isEven ? '#fafbfc' : '#fff',
    borderBottom: '1px solid #f1f5f9',
    fontSize: '0.9rem',
  }),
  leaderRank: {
    width: 32,
    textAlign: 'center',
    fontWeight: 800,
    color: '#94a3b8',
    fontSize: '0.85rem',
    flexShrink: 0,
  },

  /* challenge cards */
  challengeCard: (isOpen) => ({
    background: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: 14,
    overflow: 'hidden',
    boxShadow: isOpen ? '0 4px 20px rgba(0,0,0,0.07)' : '0 1px 3px rgba(0,0,0,0.04)',
    transition: 'box-shadow 0.2s',
    cursor: 'pointer',
  }),
  challengeHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '18px 22px',
    gap: 12,
  },
  challengeName: {
    fontSize: '1rem',
    fontWeight: 700,
    color: '#1e293b',
    flex: 1,
  },
  challengeMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    flexShrink: 0,
  },
  countBadge: (hasComps) => ({
    padding: '3px 12px',
    borderRadius: 20,
    fontSize: '0.78rem',
    fontWeight: 700,
    background: hasComps ? '#dcfce7' : '#f1f5f9',
    color: hasComps ? '#166534' : '#64748b',
  }),
  topCompleter: {
    fontSize: '0.82rem',
    color: '#64748b',
    fontWeight: 600,
    maxWidth: 120,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  chevron: (isOpen) => ({
    width: 20,
    height: 20,
    color: '#94a3b8',
    transition: 'transform 0.25s',
    transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
    flexShrink: 0,
  }),
  expandedBody: {
    borderTop: '1px solid #e2e8f0',
    background: '#fafbfc',
  },
  completionRow: (rank) => ({
    display: 'flex',
    alignItems: 'center',
    padding: '12px 22px',
    gap: 14,
    borderBottom: '1px solid #f1f5f9',
    background: rank < 3 ? (rank === 0 ? '#fffbeb' : '#fff') : '#fafbfc',
  }),
  rankBadge: (rank) => {
    const colors = {
      0: { bg: '#fef3c7', color: '#92400e' },
      1: { bg: '#f1f5f9', color: '#475569' },
      2: { bg: '#fed7aa', color: '#9a3412' },
    };
    const c = colors[rank] || { bg: '#f1f5f9', color: '#94a3b8' };
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
    padding: '28px 16px',
    color: '#94a3b8',
    fontSize: '0.88rem',
  },
  cardsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
    gap: 14,
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
      .dash-top-three > div { border-right: none !important; border-bottom: 1px solid #e2e8f0; }
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
              style={{ padding: '2px 8px', borderRadius: 4, border: '1px solid #ef4444',
                background: 'transparent', color: '#ef4444', fontSize: '.7em', cursor: 'pointer',
                fontWeight: 600 }}>
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
                      <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#1e293b' }}>
                        {c.name}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                        {c.dept}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <div style={{ fontSize: '0.82rem', fontFamily: 'monospace', color: '#475569', fontWeight: 600 }}>
                        {timeAgo(c.timestamp)}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
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

  const isAdmin = user?.sub === 'syngha.han';

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
        <h1 style={S.title}>Challenge Dashboard</h1>
        <p style={S.subtitle}>
          <span style={S.refreshDot} />
          5초마다 자동으로 갱신됩니다
        </p>
        {isAdmin && (
          <button
            onClick={handleReset}
            disabled={resetting}
            style={{
              marginTop: 12, padding: '8px 20px', borderRadius: 8,
              border: '1.5px solid #ef4444', background: resetting ? '#fecaca' : '#fff',
              color: '#ef4444', fontWeight: 700, fontSize: '.85rem',
              cursor: resetting ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => { e.target.style.background = '#fef2f2'; }}
            onMouseLeave={e => { e.target.style.background = '#fff'; }}
          >
            {resetting ? '초기화 중...' : '🔄 전체 초기화'}
          </button>
        )}
      </div>

      {/* ── Stats Bar ── */}
      <div className="dash-stats-bar" style={S.statsBar}>
        <motion.div style={S.statCard} whileHover={{ y: -2 }}>
          <div style={{ ...S.statNum, color: '#2563eb' }}>{ids.length}</div>
          <div style={S.statLabel}>총 챌린지</div>
        </motion.div>
        <motion.div style={S.statCard} whileHover={{ y: -2 }}>
          <div style={{ ...S.statNum, color: '#059669' }}>{totalCompletions}</div>
          <div style={S.statLabel}>총 완료</div>
        </motion.div>
        <motion.div style={S.statCard} whileHover={{ y: -2 }}>
          <div style={{ ...S.statNum, color: '#7c3aed' }}>{allUsers.size}</div>
          <div style={S.statLabel}>참여자</div>
        </motion.div>
        <motion.div style={S.statCard} whileHover={{ y: -2 }}>
          <div style={{ ...S.statNum, color: '#d97706', fontSize: '1.4rem' }}>
            {champion ? `👑 ${champion.name}` : '—'}
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
                      {u.count}개 완료
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
                  <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{u.name}</span>
                  <span style={{ color: '#94a3b8', fontSize: '0.8rem', marginLeft: 8 }}>{u.dept}</span>
                </div>
                <span style={{
                  padding: '3px 12px',
                  borderRadius: 20,
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  background: '#f1f5f9',
                  color: '#475569',
                }}>
                  {u.count}개 완료
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
