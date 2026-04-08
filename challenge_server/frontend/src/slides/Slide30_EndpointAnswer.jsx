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
- base URL: http://a2g.samsungds.net:8090/v1
- 모델 목록 확인: GET http://a2g.samsungds.net:8090/v1/models
  (헤더 x-service-id: test-service, x-user-id: 아무값 필수)
- chat API: POST http://a2g.samsungds.net:8090/v1/chat/completions

필수 헤더:
  Content-Type: application/json
  x-service-id: test-service   (코드의 SERVICE_ID 변수)
  x-user-id: <사번>            (코드의 user_id 변수)

요청 body (JSON):
{
  "model": "<위 /v1/models에서 확인한 모델명>",
  "messages": st.session_state.messages,
  "max_tokens": 1024
}

먼저 /v1/models를 호출해서 사용 가능한 모델명을 확인한 뒤,
그 모델명으로 /v1/chat/completions에 POST 요청을 보내줘.
timeout은 60초로 설정해.`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
