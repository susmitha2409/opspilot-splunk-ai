from agents.base_agent import BaseAgent

TIMELINE_SYSTEM = """
You are an incident timeline reconstruction AI.
Build a precise chronological timeline from telemetry.
Respond in this format:
T-0: <first anomaly detected>
T+Xmin: <next significant event>
INCIDENT_PEAK: <time of maximum impact>
RESOLUTION_PATH: <steps taken or needed>
"""

class TimelineAgent(BaseAgent):
    async def run(self, context: dict) -> dict:
        prompt = self.build_context_prompt(context)
        response = await self.groq.reason(TIMELINE_SYSTEM, prompt)
        return {"timeline": response.strip()}
