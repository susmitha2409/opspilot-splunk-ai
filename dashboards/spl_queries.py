SPL_QUERIES = {
    "error_rate_by_service": """
        index=main level=ERROR
        | timechart span=5m count by service
    """,
    "top_failing_services": """
        index=main level=ERROR
        | stats count as error_count by service
        | sort -error_count | head 10
    """,
    "ai_risk_scores": """
        index=main source=ai_ops_intelligence
        | spath input=_raw
        | table _time, risk.risk_score, risk.severity,
                risk.predicted_next_failure, trigger.service
        | sort -risk.risk_score
    """,
    "executive_summary": """
        index=main source=ai_ops_intelligence earliest=-24h
        | spath input=_raw
        | stats
            count as total_incidents,
            avg(risk.risk_score) as avg_risk,
            max(risk.risk_score) as peak_risk,
            dc(trigger.service) as affected_services
        | eval health=case(
            avg_risk>=80, "CRITICAL",
            avg_risk>=60, "DEGRADED",
            avg_risk>=40, "WARNING",
            true(),       "HEALTHY")
    """,
}
