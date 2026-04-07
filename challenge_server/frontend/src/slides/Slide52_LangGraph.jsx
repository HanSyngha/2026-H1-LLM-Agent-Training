import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide52_LangGraph() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agent Framework</Badge>
        <SlideH2 day2>LangGraph 핵심</SlideH2>
        <p>StateGraph — Node — Edge — 그래프 기반 워크플로우</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <CodeBlock>{`from langgraph.graph import StateGraph, END

# 상태 정의
class AgentState(TypedDict):
    messages: list
    next_action: str

# 노드 함수
def call_llm(state): ...
def execute_tool(state): ...

# 그래프 구성
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("tool", execute_tool)
graph.add_edge("llm", "tool")      # llm -> tool
graph.add_edge("tool", "llm")      # tool -> llm (루프)
graph.add_conditional_edges("llm", should_continue)

app = graph.compile()`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
