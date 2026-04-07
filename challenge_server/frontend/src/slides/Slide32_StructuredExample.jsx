import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide32_StructuredExample() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Structured Output</Badge>
        <SlideH2>JSON Schema로 응답 구조 강제하기</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="python">{`response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "서울 날씨 분석해줘"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "weather_analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "city":    {"type": "string"},
                    "temp_c":  {"type": "number"},
                    "summary": {"type": "string"},
                },
                "required": ["city", "temp_c", "summary"]
            }
        }
    }
)`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
