import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide36_StructuredAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Tool Use 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`app.py의 TODO 1과 TODO 2를 채워줘.

== TODO 1: tools 리스트 정의 ==
OpenAI Function Calling 형식으로 2개 tool 정의:

Tool 1 - get_secret_key:
  설명: "과제용 시크릿 키를 발급받습니다"
  파라미터: 없음 (properties: {}, required: [])

Tool 2 - submit_secret_key:
  설명: "발급받은 시크릿 키를 제출합니다"
  파라미터: secret_key (string, 필수)

== TODO 2: execute_tool(tool_name, arguments) 함수 구현 ==
코드 상단에 token 변수(SSO access_token)와
CHALLENGE_SERVER 변수(http://a2g.samsungds.net:47777)가 이미 있음.

get_secret_key 호출 시:
  requests.get(f"{CHALLENGE_SERVER}/challenges/tool_use/secret", params={"token": token})
  resp.json()을 return

submit_secret_key 호출 시:
  requests.post(f"{CHALLENGE_SERVER}/challenges/tool_use/submit",
    json={"token": token, "answer": {"secret_key": arguments["secret_key"]}})
  resp.json()을 return

tool_name이 위 두 개 중 하나가 아니면 {"error": "unknown tool"}을 return.
Agentic Loop는 이미 구현되어 있으니 tool만 연결하면 됨.`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
