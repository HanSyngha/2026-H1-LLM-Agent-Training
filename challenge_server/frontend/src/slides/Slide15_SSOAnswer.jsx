import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, CodeBlock } from './SlideLayout';

export default function Slide15_SSOAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <CodeBlock lang="prompt">{`이 Streamlit 앱(app.py)에 OIDC 로그인을 연동해줘.

인증 서버: http://a2g.samsungds.net:8090
Authorize: GET http://a2g.samsungds.net:8090/oidc/authorize
Token: POST http://a2g.samsungds.net:8090/oidc/token
client_id: cli-default
client_secret: 빈 문자열 (Basic Auth에서 password 비움)
redirect_uri: http://localhost:3000
scope: openid profile email
response_type: code
nonce: UUID로 생성 (필수! 없으면 id_token 안 옴)

token 응답에서 id_token을 PyJWT로 디코딩해서 이름/부서 추출.
jwt.decode(id_token, options={"verify_signature": False})
claims의 name이 한글 이름, dept가 한글 부서명.
/userinfo 호출 하지 마.

로그인 성공하면:
- st.session_state.user = {"name":"...","dept":"...","email":"...","sub":"..."}
- st.session_state.access_token = access_token
- st.session_state.method = "oidc"

앱 내 "Challenge 서버에 제출" 버튼으로
POST http://a2g.samsungds.net:47777/challenges/sso_oidc/submit
에 {"token":"access_token","answer":{"name":"홍길동","dept":"개발팀","method":"oidc"}}
형태로 제출되게 해줘.`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
