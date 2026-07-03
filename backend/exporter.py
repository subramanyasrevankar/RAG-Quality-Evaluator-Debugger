import csv
import io
from datetime import datetime
from backend.database import SessionLocal, EvaluationRun


def export_to_csv() -> str:
    """
    Exports all evaluation runs to CSV format.
    Returns CSV content as a string.
    """
    db = SessionLocal()
    try:
        runs = db.query(EvaluationRun).order_by(
            EvaluationRun.created_at.desc()
        ).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow([
            "ID",
            "Question",
            "Answer",
            "Retrieval Score",
            "Faithfulness Score",
            "Utilization Score",
            "Overall Score",
            "Grade",
            "Verdict",
            "Diagnosis",
            "Chunks Retrieved",
            "Top K",
            "Created At"
        ])

        # Data rows
        for run in runs:
            overall = run.overall_score or 0
            grade = get_grade(overall)

            writer.writerow([
                run.id,
                run.question,
                run.answer or "",
                round(run.retrieval_score or 0, 3),
                round(run.faithfulness_score or 0, 3),
                round(run.utilization_score or 0, 3),
                round(overall, 3),
                grade,
                run.verdict or "",
                run.diagnosis or "",
                run.chunks_retrieved or 0,
                run.top_k or 3,
                run.created_at.strftime("%Y-%m-%d %H:%M:%S") if run.created_at else ""
            ])

        return output.getvalue()

    finally:
        db.close()


def export_summary() -> dict:
    """
    Returns a summary of all evaluation runs.
    Used for the dashboard summary card.
    """
    db = SessionLocal()
    try:
        runs = db.query(EvaluationRun).all()

        if not runs:
            return {
                "total_runs": 0,
                "avg_retrieval": 0,
                "avg_faithfulness": 0,
                "avg_utilization": 0,
                "avg_overall": 0,
                "best_run": None,
                "worst_run": None
            }

        retrieval_scores = [r.retrieval_score for r in runs if r.retrieval_score]
        faithfulness_scores = [r.faithfulness_score for r in runs if r.faithfulness_score]
        utilization_scores = [r.utilization_score for r in runs if r.utilization_score]
        overall_scores = [r.overall_score for r in runs if r.overall_score]

        best = max(runs, key=lambda r: r.overall_score or 0)
        worst = min(runs, key=lambda r: r.overall_score or 0)

        return {
            "total_runs": len(runs),
            "avg_retrieval": round(sum(retrieval_scores) / len(retrieval_scores), 3) if retrieval_scores else 0,
            "avg_faithfulness": round(sum(faithfulness_scores) / len(faithfulness_scores), 3) if faithfulness_scores else 0,
            "avg_utilization": round(sum(utilization_scores) / len(utilization_scores), 3) if utilization_scores else 0,
            "avg_overall": round(sum(overall_scores) / len(overall_scores), 3) if overall_scores else 0,
            "best_run": {
                "question": best.question,
                "overall_score": best.overall_score
            },
            "worst_run": {
                "question": worst.question,
                "overall_score": worst.overall_score
            }
        }

    finally:
        db.close()


def get_grade(overall: float) -> str:
    if overall >= 0.8:
        return "A"
    elif overall >= 0.6:
        return "B"
    elif overall >= 0.4:
        return "C"
    elif overall >= 0.2:
        return "D"
    return "F"