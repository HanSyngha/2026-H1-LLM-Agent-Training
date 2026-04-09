import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide61_AgentAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Agentic Loop 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`app.py의 run_agentic_loop(messages) 함수를 구현해줘.

이 함수는 while 루프로 LLM을 반복 호출하여 tool_calls를 처리해야 해.
최대 15회 반복, 무한루프 방지.

구현 로직:
1. tool_called = False (tool 호출 여부 추적)
2. while 루프:
   a. result, error = call_llm(messages) 호출
   b. error면 return None, error
   c. msg = result["choices"][0]["message"]
   d. msg에 tool_calls가 없으면:
      - tool_called가 False면 → 재촉: messages에 msg 추가 후
        {"role":"user","content":"tool을 호출하세요."} 추가, continue
      - tool_called가 True면 → return msg.get("content"), None
   e. tool_calls가 있으면:
      - tool_called = True
      - messages.append(msg)
      - 각 tc에 대해:
        fn_name = tc["function"]["name"]
        fn_args = json.loads(tc["function"]["arguments"]) if tc["function"].get("arguments") else {}
        tool_result = execute_tool(fn_name, fn_args)
        messages.append({"role":"tool","tool_call_id":tc["id"],
                         "content":json.dumps(tool_result, ensure_ascii=False)})
      - 루프 계속

call_llm(), execute_tool(), json 모듈은 이미 코드에 있음.
반환값: (answer_text, error) 튜플.
LLM이 tool 안 부르고 텍스트만 응답하면 재촉해야 함!`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
