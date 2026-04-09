import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, Grid, Card, Quote } from './SlideLayout';

export default function Slide10_WhyTheory() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO</Badge>
        <SlideH2>왜 이 개념을 알아야 하는가?</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Quote borderColor="#dc2626">
            <span style={{ fontStyle: 'normal', fontSize: '1.05em' }}>
              사내 OAuth2/OIDC 구현은 표준과 <strong style={{ color: '#dc2626' }}>살짝 다릅니다.</strong><br />
              AI에게 "OAuth2 로그인 만들어줘"라고만 하면 <strong style={{ color: '#dc2626' }}>100% 에러</strong>가 납니다.
            </span>
          </Quote>
        </motion.div>

        <Grid cols={3} gap={20}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Card borderColor="#dc2626" style={{ padding: '24px 26px' }}>
              <h4 style={{ color: '#dc2626', fontSize: '1em' }}>SSL 인증서</h4>
              <p style={{ fontSize: '.95em', lineHeight: 1.6, textAlign: 'left' }}>
                <strong>표준:</strong> 공인 CA<br />
                <strong>사내:</strong> 자체 인증서<br />
                → AI는 <code>verify=True</code>로 짜줌<br />
                → <strong style={{ color: '#dc2626' }}>연결 거부</strong>
              </p>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Card borderColor="#dc2626" style={{ padding: '24px 26px' }}>
              <h4 style={{ color: '#dc2626', fontSize: '1em' }}>Client Secret</h4>
              <p style={{ fontSize: '.95em', lineHeight: 1.6, textAlign: 'left' }}>
                <strong>표준:</strong> 긴 시크릿 필수<br />
                <strong>사내:</strong> 빈 문자열<br />
                → AI는 시크릿을 넣어줌<br />
                → <strong style={{ color: '#dc2626' }}>인증 실패</strong>
              </p>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
            <Card borderColor="#dc2626" style={{ padding: '24px 26px' }}>
              <h4 style={{ color: '#dc2626', fontSize: '1em' }}>id_token 발급</h4>
              <p style={{ fontSize: '.95em', lineHeight: 1.6, textAlign: 'left' }}>
                <strong>표준:</strong> scope만으로 발급<br />
                <strong>사내:</strong> nonce 필수<br />
                → AI는 nonce를 안 넣음<br />
                → <strong style={{ color: '#dc2626' }}>토큰 없음</strong>
              </p>
            </Card>
          </motion.div>
        </Grid>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.9 }}>
          <Box color="blue" style={{ marginTop: 12, fontSize: '1.1em', textAlign: 'center' }}>
            <strong>결론:</strong> 프로토콜의 원리를 이해해야 AI에게 <strong>"우리 환경은 이렇게 다르다"</strong>고 정확히 설명할 수 있고, 바이브 코딩이 <strong>한 번에</strong> 성공합니다.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
