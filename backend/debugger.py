def analyze_and_debug(
    retrieval_score: float,
    faithfulness_score: float,
    utilization_score: float,
    overall_score: float,
    question: str = "",
    chunks: list = []
) -> dict:
    """
    Analyzes scores and returns specific, actionable fixes.
    This is the 'debugger' that makes this project unique.
    """
    issues = []
    fixes = []
    severity = "healthy"

    # ── Retrieval issues ─────────────────────────────────────────────
    if retrieval_score < 0.3:
        severity = "critical"
        issues.append("Retrieval has failed — chunks are unrelated to the question")
        fixes.extend([
            "Reduce chunk size from 500 to 200-300 characters",
            "Increase chunk overlap from 50 to 100 characters",
            "Try rephrasing the question using keywords from the document",
            "Check if the correct document was uploaded",
            "Consider using a better embedding model"
        ])
    elif retrieval_score < 0.5:
        if severity != "critical":
            severity = "poor"
        issues.append("Retrieval is weak — chunks are partially relevant")
        fixes.extend([
            "Reduce chunk size to improve precision",
            "Increase top_k from 3 to 5 to retrieve more candidates",
            "Try more specific questions with document terminology"
        ])
    elif retrieval_score < 0.7:
        if severity not in ["critical", "poor"]:
            severity = "average"
        issues.append("Retrieval is average — some chunks are off-topic")
        fixes.append("Fine-tune chunk size or try a domain-specific embedding model")

    # ── Faithfulness issues ──────────────────────────────────────────
    if faithfulness_score < 0.3:
        severity = "critical"
        issues.append("Severe hallucination detected — answer is not grounded in context")
        fixes.extend([
            "Add stricter instructions in the LLM prompt: 'Only use the provided context'",
            "Reduce LLM temperature to 0 for more deterministic answers",
            "Use a smaller, more focused context window",
            "Consider switching to a more instruction-following model"
        ])
    elif faithfulness_score < 0.5:
        if severity != "critical":
            severity = "poor"
        issues.append("Partial hallucination — LLM is adding information not in context")
        fixes.extend([
            "Strengthen the system prompt to restrict outside knowledge",
            "Reduce top_k to provide less but more relevant context"
        ])
    elif faithfulness_score < 0.7:
        if severity not in ["critical", "poor"]:
            severity = "average"
        issues.append("Minor faithfulness issues — answer mostly grounded but has gaps")
        fixes.append("Review LLM prompt instructions for clarity")

    # ── Utilization issues ───────────────────────────────────────────
    if utilization_score < 0.3:
        if severity not in ["critical", "poor"]:
            severity = "average"
        issues.append("Low context utilization — most retrieved chunks were ignored")
        fixes.extend([
            "Reduce top_k — you're retrieving too many irrelevant chunks",
            "Improve retrieval quality so only relevant chunks are fetched",
            "Try a reranker to filter chunks before sending to LLM"
        ])
    elif utilization_score < 0.5:
        issues.append("Medium utilization — some chunks not contributing to answer")
        fixes.append("Reduce top_k from current value to 2-3")

    # ── All good ─────────────────────────────────────────────────────
    if not issues:
        issues.append("No significant issues detected")
        fixes.append("Pipeline is healthy — no changes needed")
        severity = "healthy"

    # ── Priority fix ─────────────────────────────────────────────────
    priority_fix = fixes[0] if fixes else "No fixes needed"

    return {
        "overall_score": overall_score,
        "severity": severity,
        "issues": issues,
        "fixes": fixes,
        "priority_fix": priority_fix,
        "score_breakdown": {
            "retrieval": {
                "score": retrieval_score,
                "status": get_status(retrieval_score),
                "weight": "40%"
            },
            "faithfulness": {
                "score": faithfulness_score,
                "status": get_status(faithfulness_score),
                "weight": "40%"
            },
            "utilization": {
                "score": utilization_score,
                "status": get_status(utilization_score),
                "weight": "20%"
            }
        }
    }


def get_status(score: float) -> str:
    if score >= 0.7:
        return "good"
    elif score >= 0.5:
        return "average"
    elif score >= 0.3:
        return "poor"
    return "critical"


def get_quick_diagnosis(
    retrieval_score: float,
    faithfulness_score: float,
    utilization_score: float
) -> str:
    """
    Returns a single sentence diagnosis — used in API responses.
    """
    lowest = min(retrieval_score, faithfulness_score, utilization_score)
    lowest_metric = "retrieval" if retrieval_score == lowest else \
                    "faithfulness" if faithfulness_score == lowest else \
                    "utilization"

    if lowest >= 0.7:
        return "Pipeline is healthy across all metrics"
    elif lowest_metric == "retrieval":
        return "Primary issue: retrieval — wrong chunks are being fetched"
    elif lowest_metric == "faithfulness":
        return "Primary issue: faithfulness — LLM is hallucinating"
    else:
        return "Primary issue: utilization — retrieved chunks are being ignored"