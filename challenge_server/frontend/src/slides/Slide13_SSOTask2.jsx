import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide13_SSOTask2() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO 실습</Badge>
        <SlideH2>인증 서버 정보 & 제출</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue" style={{ fontSize: '.92em', padding: '18px 28px' }}>
            <table style={{ fontSize: '.95em', margin: 0, maxWidth: '100%' }}>
              <tbody>
                <tr>
                  <th style={{ width: '22%', padding: '6px 10px' }}>Authorize</th>
                  <td style={{ padding: '6px 10px' }}><code>GET http://a2g.samsungds.net:8090/oidc/authorize</code></td>
                </tr>
                <tr>
                  <th style={{ padding: '6px 10px' }}>Token</th>
                  <td style={{ padding: '6px 10px' }}><code>POST http://a2g.samsungds.net:8090/oidc/token</code></td>
                </tr>
                <tr>
                  <th style={{ padding: '6px 10px' }}>UserInfo</th>
                  <td style={{ padding: '6px 10px' }}><code>GET http://a2g.samsungds.net:8090/oidc/userinfo</code></td>
                </tr>
              </tbody>
            </table>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.92em', padding: '18px 28px' }}>
            <BoxTitle color="#7c3aed">과제: OIDC 로그인</BoxTitle>
            <div style={{ textAlign: 'left', lineHeight: 1.8 }}>
              <code>id_token</code> JWT 디코딩으로 이름/부서를 표시하세요 (<code>/userinfo</code> 호출 X)<br /><br />
              <strong>필수 파라미터:</strong> scope=<code>openid profile email</code>, <code>nonce</code>=UUID (없으면 id_token 안 옴)<br />
              <strong>JWT 디코딩:</strong> <code>{'jwt.decode(id_token, options={"verify_signature": False})'}</code> → claims의 <code>name</code>, <code>dept</code><br />
              <strong>제출:</strong> 앱 내 "Challenge 서버에 제출" 버튼 → <code>/challenges/sso_oidc/submit</code>
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '1.05em', textAlign: 'center', padding: 16 }}>
            <span role="img" aria-label="celebration">&#x1F389;</span> <strong>홍길동님, OIDC 로그인 통과!</strong> -- 대시보드에 이름이 표시됩니다
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
