import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide57_ToolCallsParse() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop</Badge>
        <SlideH2 day2>tool_calls 파싱 & 실행</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock>{`# Tool 레지스트리
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "search_employee": search_employee,
    "run_query": run_query,
}

def execute_tool(tool_call):
    """tool_call 객체를 파싱하여 실제 함수를 실행"""
    name = tool_call["function"]["name"]
    args = json.loads(tool_call["function"]["arguments"])

    func = TOOL_REGISTRY.get(name)
    if not func:
        return {"error": f"Unknown tool: {name}"}

    try:
        result = func(**args)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
