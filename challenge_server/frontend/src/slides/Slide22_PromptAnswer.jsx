import { motion } from 'framer-motion';
import { Badge, SlideH2, CodeBlock } from './SlideLayout';

export default function Slide22_PromptAnswer() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">프롬프트 실습</Badge>
        <SlideH2>막히면? 예시 답안 프롬프트</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <CodeBlock lang="prompt">{`You are a biomedical data extraction expert.
Extract structured information as a JSON object.

STRICT RULES:
1. Return ONLY valid JSON. No markdown, no code blocks.
2. Boolean: true/false. Numbers: without units. Strings: with context.
3. morphology_findings: array of strings.
   abnormal_values: array of objects {name, value, unit, status}.
4. variants: only detected ones (skip "not detected").
5. interpretation: concise lowercase phrase.
6. diversity_status: "low"/"normal"/"high" vs reference.
7. Counts (num_clusters etc.): count actual items.
8. Simple numbers (fb_ratio, clearance_rate, hazard_ratio,
   half_life_days, accumulation_ratio, auc, etc.):
   plain numbers, NOT nested objects.
9. For cmax, clearance with units:
   use {"value": 83.4, "unit": "ug/mL"} format.
10. dose: string with full context ("200mg IV q3w").`}</CodeBlock>
        </motion.div>
      </div>
    </div>
  );
}
