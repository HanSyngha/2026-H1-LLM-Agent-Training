import { useState, useEffect } from 'react';
import { getCompletions } from '../api';

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const load = () => getCompletions().then(setData);
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return <div className="container">로딩 중...</div>;

  const challenges = data.challenges;
  const ids = Object.keys(challenges);
  let totalCompletions = 0;
  const allUsers = new Set();
  ids.forEach(id => {
    challenges[id].completions.forEach(c => { totalCompletions++; allUsers.add(c.sub); });
  });

  return (
    <div className="container">
      <div className="page-header">
        <h1>Challenge Dashboard</h1>
        <p>과제를 풀고, SSO 토큰과 함께 정답을 제출하세요</p>
      </div>

      <div className="stats">
        <div className="stat"><div className="num">{ids.length}</div><div className="label">과제</div></div>
        <div className="stat"><div className="num">{totalCompletions}</div><div className="label">총 통과</div></div>
        <div className="stat"><div className="num">{allUsers.size}</div><div className="label">참여자</div></div>
      </div>

      <div className="grid grid-3">
        {ids.map(id => {
          const ch = challenges[id];
          const comps = ch.completions || [];
          return (
            <div className={`card ${comps.length ? 'has-completions' : ''}`} key={id} style={comps.length ? {borderLeft: '3px solid var(--green)'} : {}}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:8}}>
                <h3>{ch.name}</h3>
                <span className={`badge ${comps.length ? 'badge-pass' : 'badge-pending'}`}>{comps.length}명</span>
              </div>
              <div style={{fontSize:'.78em',color:'var(--text3)',fontFamily:'monospace',marginBottom:8}}>
                POST /challenges/{id}/submit
              </div>
              {comps.length > 0 ? comps.map((c, i) => (
                <div className="completion" key={i}>
                  <div className={`rank ${i===0?'gold':i===1?'silver':i===2?'bronze':''}`}>{i+1}</div>
                  <div style={{flex:1}}>
                    <div style={{fontWeight:600}}>{c.name}</div>
                    <div style={{fontSize:'.78em',color:'var(--text3)'}}>{c.dept}</div>
                  </div>
                  <div style={{fontSize:'.72em',color:'var(--text3)',fontFamily:'monospace'}}>
                    {new Date(c.timestamp).toLocaleTimeString('ko-KR')}
                  </div>
                </div>
              )) : (
                <div style={{textAlign:'center',padding:'16px',color:'var(--text3)',fontSize:'.85em'}}>
                  아직 통과자가 없습니다
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
