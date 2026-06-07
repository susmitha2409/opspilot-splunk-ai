from agents.base_agent import BaseAgent

RCA_SYSTEM = """
You are an elite Site Reliability Engineer AI.
Analyze telemetry and determine the definitive root cause.
Respond ONLY in this format:
ROOT_CAUSE: <concise cause>
AFFECTED_SERVICES: <comma-separated>
CONFIDENCE: <0-100>
EVIDENCE: <key log lines or metrics that confirm the cause>
"""

class RCAAgent(BaseAgent):
    agent_index = 1
    async def run(self, context: dict) -> dict:
        prompt = self.build_context_prompt(context)
        response = await self.groq.reason(RCA_SYSTEM, prompt)
        return self._parse(response)

    def _parse(self, text: str) -> dict:
        result = {}
        for line in text.strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip().lower().replace(" ", "_")] = v.strip()
        return result
