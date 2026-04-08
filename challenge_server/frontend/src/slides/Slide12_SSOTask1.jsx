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
              <code style={{ fontSize: '.95em' }}>
                pip install streamlit requests PyJWT && streamlit run app.py --server.port 3000
              </code>
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.88em', padding: '16px 24px' }}>
            <strong>인증 서버 정보 (OIDC)</strong>
            <table style={{ fontSize: '.92em', margin: '8px 0 0', width: '100%' }}>
              <tbody>
                <tr>
                  <th style={{ width: '18%', padding: '4px 8px' }}>Authorize</th>
                  <td style={{ padding: '4px 8px' }}><code>GET http://a2g.samsungds.net:8090/oidc/authorize</code></td>
                </tr>
                <tr>
                  <th style={{ padding: '4px 8px' }}>Token</th>
                  <td style={{ padding: '4px 8px' }}><code>POST http://a2g.samsungds.net:8090/oidc/token</code></td>
                </tr>
                <tr>
                  <th style={{ padding: '4px 8px' }}>Client ID</th>
                  <td style={{ padding: '4px 8px' }}><code>cli-default</code> (secret 없음)</td>
                </tr>
              </tbody>
            </table>
            <div style={{ marginTop: 8, lineHeight: 1.7 }}>
              scope=<code>openid profile email</code>, <code>nonce</code>=필수 (없으면 id_token 안 옴)<br />
              <code>id_token</code>을 JWT 디코딩 → <code>name</code>, <code>dept</code> 추출 → 제출
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="green" style={{ marginTop: 8, textAlign: 'center', fontSize: '1em' }}>
            <strong>2단계:</strong> 바이브 코딩으로 로그인 버튼에 OIDC를 연결하세요 → 로그인 성공 → 제출!
          </Box>
        </motion.div>

        <AnswerButton answerId="sso"><Slide15_SSOAnswer /></AnswerButton>
      </div>
    </div>
  );
}
