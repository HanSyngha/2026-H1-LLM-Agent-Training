import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide30_EndpointAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Endpoint 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`app.py의 TODO를 채워줘. resp = None을 requests.post(...)로 바꿔야 해.

사내 LLM Gateway 정보:
- URL: https://llm-gateway.example.com/v1/chat/completions
- 모델명: testmodel

필수 헤더:
  Content-Type: application/json
  x-service-id: test-service   (코드에 SERVICE_ID 변수로 있음)
  x-user-id: <값>              (코드에 user_id 변수로 있음, SSO 로그인한 ID)

요청 body (JSON):
{
  "model": "testmodel",
  "messages": st.session_state.messages,
  "max_tokens": 1024
}

코드에 이미 SERVICE_ID, user_id, st.session_state.messages 변수가 있으니
그대로 사용하면 됨. timeout은 60초로 설정해.`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
