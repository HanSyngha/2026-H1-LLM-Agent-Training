import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide24_APITool() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">API</Badge>
        <SlideH2>API를 Tool로 래핑하는 법</SlideH2>
        <p>함수 + JSON Schema = LLM이 호출할 수 있는 Tool</p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <CodeBlock lang="python">{`# 1. 일반 Python 함수 작성
def get_weather(city: str) → dict:
    """도시의 현재 날씨를 조회합니다."""
    resp = requests.get(f"https://weather.api/{city}")
    return resp.json()

# 2. JSON Schema로 설명 (LLM이 이해하는 형태)
tool_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "도시의 현재 날씨를 조회합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "도시명"}
            },
            "required": ["city"]
        }
    }
}`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
