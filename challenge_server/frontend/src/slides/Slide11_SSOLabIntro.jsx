import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, Quote } from './SlideLayout';

export default function Slide11_SSOLabIntro() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO</Badge>
        <SlideH2>실습 안내</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Box color="blue" style={{ fontSize: '1.1em', lineHeight: 1.8, textAlign: 'center' }}>
            Agent Dashboard에 <strong>OAuth2 / OIDC 인증 서버</strong>를 준비해 두었습니다.<br />
            여러분은 <strong>클라이언트</strong>를 만들어서 연결하면 됩니다.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Quote borderColor="#059669">
            <span style={{ fontStyle: 'normal' }}>
              OAuth2와 OIDC의 <strong>대략적인 개념</strong>만 이해하면 쉽게 성공할 수 있습니다.<br />
              단, 사내 SSO의 <strong>3가지 주의사항</strong>을 AI에게 정확히 전달해야 합니다.<br />
              이 토큰은 <strong>이후 모든 과제의 인증 수단</strong>으로 사용됩니다.
            </span>
          </Quote>
        </motion.div>
      </div>
    </div>
  );
}
