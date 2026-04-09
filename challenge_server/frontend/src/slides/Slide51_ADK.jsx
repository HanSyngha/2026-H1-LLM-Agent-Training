import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide51_ADK() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agent Framework</Badge>
        <SlideH2 day2>Google ADK 핵심</SlideH2>
        <p>Agent Development Kit — 간결한 Agent 구성</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <CodeBlock>{`from google.adk import Agent, Tool, Runner

# Tool 정의
def search_web(query: str) → str:
    """웹에서 정보를 검색합니다."""
    return web_api.search(query)

# Agent 생성
agent = Agent(
    name="research_agent",
    model="gemini-2.0-flash",
    instruction="사용자의 질문에 웹 검색으로 답변하세요.",
    tools=[search_web],
)

# 실행
runner = Runner(agent)
result = runner.run("최신 AI 트렌드는?")`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
