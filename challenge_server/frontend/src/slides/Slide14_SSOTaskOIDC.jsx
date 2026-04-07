import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, Grid } from './SlideLayout';

export default function Slide14_SSOTaskOIDC() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO 실습</Badge>
        <SlideH2>OIDC -- OAuth2와 다른 점</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <table style={{ marginTop: '1em' }}>
            <thead>
              <tr>
                <th>항목</th>
                <th>OAuth2</th>
                <th>OIDC</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>사용자 정보</strong></td>
                <td><code>/userinfo</code> API 추가 호출</td>
                <td><code>id_token</code> JWT 디코딩</td>
              </tr>
              <tr>
                <td><strong>필수 파라미터</strong></td>
                <td>scope, redirect_uri</td>
                <td>scope, redirect_uri, <strong style={{ color: '#7c3aed' }}>nonce</strong></td>
              </tr>
              <tr>
                <td><strong>scope</strong></td>
                <td>자유 설정</td>
                <td><code>openid profile email</code> 필수</td>
              </tr>
              <tr>
                <td><strong>응답</strong></td>
                <td>access_token만</td>
                <td>access_token + <strong style={{ color: '#7c3aed' }}>id_token</strong></td>
              </tr>
              <tr>
                <td><strong>요청 횟수</strong></td>
                <td style={{ color: '#dc2626' }}>4번 (userinfo 호출 포함)</td>
                <td style={{ color: '#059669', fontWeight: 600 }}>3번 (JWT 디코딩으로 끝)</td>
              </tr>
            </tbody>
          </table>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Box color="purple" style={{ marginTop: 12, fontSize: '1em', textAlign: 'center' }}>
            <strong>핵심:</strong> OIDC는 <code>nonce</code>를 보내야 <code>id_token</code>이 발급됩니다. nonce 없이는 OAuth2와 동일하게 동작합니다.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
