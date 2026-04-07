import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide28_GatewayCode() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">OpenAI Compatible</Badge>
        <SlideH2>사내 Gateway 연결 코드 예시</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="python">{`from openai import OpenAI

client = OpenAI(
    base_url="https://gateway.company.com/v1",
    api_key=os.environ["GATEWAY_API_KEY"],
)

response = client.chat.completions.create(
    model="claude-sonnet-4-20250514",  # Gateway가 라우팅
    messages=[
        {"role": "system", "content": "사내 업무 도우미입니다."},
        {"role": "user",   "content": "오늘 일정 알려줘"},
    ],
    temperature=0.7,
    max_tokens=1024,
)

print(response.choices[0].message.content)`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
