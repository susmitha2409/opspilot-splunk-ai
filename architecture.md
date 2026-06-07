## Data Flow
1. Logs ingested into Splunk via HEC
2. MCP Server exposes Splunk as AI tools
3. Orchestrator activates 6 agents in parallel
4. Each agent calls Groq AI with structured prompt
5. Remediation Engine executes matched playbook
6. AI report written back to Splunk via HEC
7. Dashboard displays results in real time
