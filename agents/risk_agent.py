from agents.base_agent import BaseAgent

RISK_SYSTEM = """
You are an AI operational risk scoring engine.
Analyze telemetry and produce a risk assessment.
Respond ONLY in this format:
RISK_SCORE: <0-100>
SEVERITY: <CRITICAL|HIGH|MEDIUM|LOW>
PREDICTED_NEXT_FAILURE: <service or component>
TIME_TO_FAILURE: <estimated time>
PREVENTIVE_ACTION: <specific action>
"""

class RiskAgent(BaseAgent):
    agent_index = 2
    async def run(self, context: dict) -> dict:
        prompt = self.build_context_prompt(context)
        response = await self.groq.reason(RISK_SYSTEM, prompt)
        return self._parse(response)

    def _parse(self, text: str) -> dict:
        result = {}
        for line in text.strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip().lower().replace(" ", "_")] = v.strip()
        return result
