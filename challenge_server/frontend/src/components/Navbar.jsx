import { NavLink } from 'react-router-dom';

export default function Navbar({ user }) {
  return (
    <div className="navbar">
      <NavLink to="/" className="logo">LLM Agent 교육</NavLink>
      <nav>
        <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>대시보드</NavLink>
        <NavLink to="/slides" className={({ isActive }) => isActive ? 'active' : ''}>강의</NavLink>
{/* 프롬프트 과제는 슬라이드에서 직접 진행 */}
        {/* 설정은 네비에 노출하지 않음 — /settings 직접 입력만 */}
      </nav>
      <div className="user">
        {user ? (
          <>
            <span className="name">{user.name}</span>
            <span>({user.dept})</span>
          </>
        ) : (
          <a href="/auth/login?redirect=/" style={{padding:'6px 16px',borderRadius:'20px',background:'var(--blue)',color:'white',textDecoration:'none',fontSize:'.85em',fontWeight:600}}>로그인</a>
        )}
      </div>
    </div>
  );
}
