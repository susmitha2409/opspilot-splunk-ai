from agents.base_agent import BaseAgent

CORR_SYSTEM = """
You are a distributed systems failure correlation engine.
Given telemetry data, identify correlated failures across services.
Respond in this format:
CORRELATED_FAILURES: <list of correlated events>
FAILURE_CHAIN: <service A -> service B -> service C>
BLAST_RADIUS: <impacted systems>
PATTERN: <known failure pattern if any>
"""

class CorrelationAgent(BaseAgent):
    agent_index = 3
    async def run(self, context: dict) -> dict:
        prompt = self.build_context_prompt(context)
        response = await self.groq.reason(CORR_SYSTEM, prompt)
        return self._parse(response)

    def _parse(self, text: str) -> dict:
        result = {}
        for line in text.strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip().lower().replace(" ", "_")] = v.strip()
        return result
