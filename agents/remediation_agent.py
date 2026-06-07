from agents.base_agent import BaseAgent
from remediation.remediation_engine import RemediationEngine

REMED_SYSTEM = """
You are an autonomous remediation AI for cloud-native systems.
Given a root cause and risk score, generate a precise remediation plan.
Respond in this format:
IMMEDIATE_ACTION: <action within 5 minutes>
SHORT_TERM_FIX: <action within 1 hour>
LONG_TERM_FIX: <permanent solution>
ROLLBACK_PLAN: <if remediation fails>
AUTOMATION_SCRIPT: <bash or kubectl command>
"""

class RemediationAgent(BaseAgent):
    agent_index = 4
    def __init__(self):
        super().__init__()
        self.engine = RemediationEngine()

    async def run(self, context: dict) -> dict:
        prompt = self.build_context_prompt(context)
        response = await self.groq.reason(REMED_SYSTEM, prompt)
        parsed = self._parse(response)
        playbook_result = await self.engine.execute(
            context.get("root_cause", ""),
            context.get("risk_score", "0")
        )
        parsed["playbook_executed"] = playbook_result
        return parsed

    def _parse(self, text: str) -> dict:
        result = {}
        for line in text.strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                result[k.strip().lower().replace(" ", "_")] = v.strip()
        return result
