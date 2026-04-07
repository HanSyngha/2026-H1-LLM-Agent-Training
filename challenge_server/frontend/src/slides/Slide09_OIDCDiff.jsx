import { motion } from 'framer-motion';
import { Badge, SlideH2, Box, Grid } from './SlideLayout';

export default function Slide09_OIDCDiff() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO</Badge>
        <SlideH2>OIDC -- OAuth2와 무엇이 다른가?</SlideH2>
        <p>OAuth2 위에 <strong style={{ color: '#2563eb' }}>"사용자가 누구인지"</strong>를 추가한 프로토콜입니다</p>

        <Grid cols={2} gap={20}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <div style={{
              background: '#fff',
              border: '1px solid rgba(37,99,235,.2)',
              borderTop: '3px solid #2563eb',
              borderRadius: 14,
              padding: '28px 32px',
              textAlign: 'left',
              boxShadow: '0 4px 20px rgba(37,99,235,.08)'
            }}>
              <h4 style={{ color: '#2563eb', fontSize: '1.15em', marginBottom: '.8em' }}>OAuth2</h4>
              <div style={{ fontSize: '1em', lineHeight: 2 }}>
                <div>1. <code>/authorize</code> -> 로그인</div>
                <div>2. <code>callback?code=</code></div>
                <div>3. <code>POST /token</code> -> <strong>access_token</strong></div>
                <div style={{ color: '#dc2626', fontWeight: 600 }}>4. <code>GET /userinfo</code> {'<-'} 추가 호출 필요!</div>
              </div>
              <div style={{ marginTop: '1em', padding: '8px 12px', background: 'rgba(59,130,246,.06)', borderRadius: 8, fontSize: '.9em', color: '#334155' }}>
                요청 <strong>4번</strong> -- 마지막에 API를 한 번 더 호출해야 합니다
              </div>
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <div style={{
              background: '#fff',
              border: '1px solid rgba(124,58,237,.2)',
              borderTop: '3px solid #7c3aed',
              borderRadius: 14,
              padding: '28px 32px',
              textAlign: 'left',
              boxShadow: '0 4px 20px rgba(124,58,237,.08)'
            }}>
              <h4 style={{ color: '#7c3aed', fontSize: '1.15em', marginBottom: '.8em' }}>OIDC (OpenID Connect)</h4>
              <div style={{ fontSize: '1em', lineHeight: 2 }}>
                <div>1. <code>/authorize</code> -> 로그인 <span style={{ color: '#7c3aed' }}>(+ nonce!)</span></div>
                <div>2. <code>callback?code=</code></div>
                <div>3. <code>POST /token</code> -> access_token <strong style={{ color: '#7c3aed' }}>+ id_token</strong></div>
                <div style={{ color: '#059669', fontWeight: 600 }}>-> JWT 디코딩만 하면 끝!</div>
              </div>
              <div style={{ marginTop: '1em', padding: '8px 12px', background: 'rgba(124,58,237,.06)', borderRadius: 8, fontSize: '.9em', color: '#334155' }}>
                요청 <strong>3번</strong> -- id_token 안에 사용자 정보가 이미 들어있습니다
              </div>
            </div>
          </motion.div>
        </Grid>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
          <Box color="green" style={{ marginTop: 12, fontSize: '1em', textAlign: 'center' }}>
            <strong>OIDC의 핵심:</strong> <code>nonce</code> 파라미터를 보내야 <code>id_token</code>이 발급됩니다. <strong>nonce가 없으면 id_token이 안 옵니다!</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
