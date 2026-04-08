import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import AnswerButton from './AnswerButton';
import Slide15_SSOAnswer from './Slide15_SSOAnswer';

export default function Slide12_SSOTask1() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO 실습</Badge>
        <SlideH2>과제: Streamlit 앱에 OIDC 로그인 연동</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 코드 다운로드 & 실행</BoxTitle>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <a href="/downloads/sso" download
                style={{ display: 'inline-block', padding: '8px 20px', borderRadius: 8, background: '#2563eb', color: '#fff',
                  textDecoration: 'none', fontWeight: 600, fontSize: '.9em', flexShrink: 0 }}>
                📦 다운로드
              </a>
              <code style={{ fontSize: '.9em' }}>
                pip install streamlit requests PyJWT && streamlit run app.py --server.port 3000
              </code>
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.82em', padding: '16px 24px' }}>
            <BoxTitle color="#7c3aed">OIDC 인증 서버 정보</BoxTitle>
            <table style={{ fontSize: '.92em', margin: '6px 0 0', width: '100%' }}>
              <tbody>
                {[
                  ['Authorize', 'GET http://a2g.samsungds.net:8090/oidc/authorize'],
                  ['Token', 'POST http://a2g.samsungds.net:8090/oidc/token'],
                  ['client_id', 'cli-default'],
                  ['client_secret', '빈 문자열 (Basic Auth에서 password 비움)'],
                  ['redirect_uri', 'http://localhost:3000'],
                  ['scope', 'openid profile email'],
                  ['nonce', 'UUID로 생성 (필수! 없으면 id_token 안 옴)'],
                ].map(([k, v]) => (
                  <tr key={k}>
                    <th style={{ width: '20%', padding: '3px 8px', fontSize: '.9em' }}>{k}</th>
                    <td style={{ padding: '3px 8px' }}><code>{v}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.82em', padding: '14px 24px' }}>
            <BoxTitle color="#d97706">핵심 흐름</BoxTitle>
            <div style={{ lineHeight: 1.7 }}>
              authorize → code 받기 → token 교환 → <code>id_token</code> JWT 디코딩 → <code>name</code>, <code>dept</code> 추출<br />
              <code>jwt.decode(id_token, options={'{'}verify_signature: False{'}'})</code> — <strong>/userinfo 호출 X</strong><br />
              로그인 성공 시 앱 내 "Challenge 서버에 제출" 버튼 → <code>/challenges/sso_oidc/submit</code>
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, textAlign: 'center', fontSize: '1em' }}>
            <strong>2단계:</strong> 바이브 코딩으로 로그인 버튼에 OIDC 연결 → 로그인 → 제출!
          </Box>
        </motion.div>

        <AnswerButton answerId="sso"><Slide15_SSOAnswer /></AnswerButton>
      </div>
    </div>
  );
}
