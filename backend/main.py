from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import io

from backend.chunker import chunk_document, get_chunk_stats
from backend.retriever import store_chunks, retrieve_chunks
from backend.evaluator import score_multiple_chunks
from backend.llm import generate_answer, check_faithfulness_with_llm
from backend.faithfulness import score_faithfulness_local, score_context_utilization, combine_scores
from backend.database import get_db, init_db, save_evaluation_run, save_uploaded_document, get_recent_runs, get_average_scores
from backend.cache import get_cached_result, set_cached_result, clear_all_cache, get_cache_stats
from backend.semantic_cache import find_similar_cached_result, store_question_embedding, clear_semantic_cache, get_semantic_cache_stats
from backend.templates import get_all_templates, get_template, get_recommended_settings, TemplateType
from backend.debugger import analyze_and_debug, get_quick_diagnosis
from backend.exporter import export_to_csv, export_summary

app = FastAPI(
    title="RAG Quality Evaluator",
    description="Evaluates why your RAG pipeline is failing",
    version="5.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    template: Optional[str] = None


class QueryResponse(BaseModel):
    question: str
    answer: str
    retrieved_chunks: list
    retrieval_score: float
    faithfulness_score: float
    utilization_score: float
    overall_score: float
    grade: str
    verdict: str
    diagnosis: str
    hallucinated: bool
    cache_hit: bool = False
    similarity_score: Optional[float] = None
    matched_question: Optional[str] = None
    debug: Optional[dict] = None


@app.get("/")
def root():
    return {"message": "RAG Quality Evaluator v5.0 is running"}


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith((".txt", ".pdf", ".md")):
        raise HTTPException(status_code=400, detail="Only .txt, .pdf, .md files supported")

    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    if not text.strip():
        raise HTTPException(status_code=400, detail="File is empty")

    chunks = chunk_document(text)
    stats = get_chunk_stats(chunks)

    store_chunks(chunks, source=file.filename)

    save_uploaded_document(
        db=db,
        filename=file.filename,
        total_chunks=len(chunks),
        file_size_bytes=len(content)
    )

    clear_all_cache()
    clear_semantic_cache()

    return {
        "filename": file.filename,
        "total_chunks": len(chunks),
        "chunk_stats": stats,
        "message": f"Successfully stored {len(chunks)} chunks. Cache cleared."
    }


@app.post("/query", response_model=QueryResponse)
def query_document(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Apply template settings if provided
    top_k = request.top_k
    if request.template:
        try:
            template_type = TemplateType(request.template)
            settings = get_recommended_settings(template_type)
            top_k = settings["top_k"]
        except ValueError:
            pass

    # Step 1 — Check exact cache
    cached = get_cached_result(request.question, top_k)
    if cached:
        cached["cache_hit"] = True
        return QueryResponse(**cached)

    # Step 2 — Check semantic cache
    semantic_cached = find_similar_cached_result(request.question)
    if semantic_cached:
        return QueryResponse(**semantic_cached)

    # Step 3 — Retrieve chunks
    chunks = retrieve_chunks(question=request.question, top_k=top_k)
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found. Upload a document first.")

    # Step 4 — Score retrieval
    retrieval_eval = score_multiple_chunks(request.question, chunks)
    retrieval_score = retrieval_eval["overall_score"]

    # Step 5 — Generate answer
    answer = generate_answer(request.question, chunks)

    # Step 6 — Score faithfulness
    faith_eval = score_faithfulness_local(answer, chunks)
    faithfulness_score = faith_eval["faithfulness_score"]

    # Step 7 — Score utilization
    util_eval = score_context_utilization(answer, chunks)
    utilization_score = util_eval["utilization_score"]

    # Step 8 — LLM faithfulness check
    llm_faith = check_faithfulness_with_llm(request.question, answer, chunks)
    hallucinated = llm_faith["hallucinated"]
    blended_faithfulness = round(
        (faithfulness_score + llm_faith["faithfulness_score"]) / 2, 3
    )

    # Step 9 — Combine scores
    combined = combine_scores(
        retrieval_score=retrieval_score,
        faithfulness_score=blended_faithfulness,
        utilization_score=utilization_score
    )

    # Step 10 — Auto debug
    debug = analyze_and_debug(
        retrieval_score=retrieval_score,
        faithfulness_score=blended_faithfulness,
        utilization_score=utilization_score,
        overall_score=combined["overall_score"],
        question=request.question,
        chunks=chunks
    )

    # Step 11 — Save to PostgreSQL
    save_evaluation_run(
        db=db,
        question=request.question,
        answer=answer,
        retrieval_score=retrieval_score,
        faithfulness_score=blended_faithfulness,
        utilization_score=utilization_score,
        overall_score=combined["overall_score"],
        verdict=retrieval_eval["verdict"],
        diagnosis=retrieval_eval["diagnosis"],
        chunks_retrieved=len(chunks),
        top_k=top_k
    )

    result = {
        "question": request.question,
        "answer": answer,
        "retrieved_chunks": chunks,
        "retrieval_score": retrieval_score,
        "faithfulness_score": blended_faithfulness,
        "utilization_score": utilization_score,
        "overall_score": combined["overall_score"],
        "grade": combined["grade"],
        "verdict": retrieval_eval["verdict"],
        "diagnosis": retrieval_eval["diagnosis"],
        "hallucinated": hallucinated,
        "cache_hit": False,
        "similarity_score": None,
        "matched_question": None,
        "debug": debug
    }

    # Step 12 — Store in cache
    set_cached_result(request.question, top_k, result)
    store_question_embedding(request.question, result)

    return QueryResponse(**result)


@app.get("/history")
def get_history(limit: int = 10, db: Session = Depends(get_db)):
    runs = get_recent_runs(db, limit=limit)
    return [
        {
            "id": run.id,
            "question": run.question,
            "answer": run.answer,
            "retrieval_score": run.retrieval_score,
            "faithfulness_score": run.faithfulness_score,
            "utilization_score": run.utilization_score,
            "overall_score": run.overall_score,
            "verdict": run.verdict,
            "created_at": run.created_at
        }
        for run in runs
    ]


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return get_average_scores(db)


@app.get("/cache/stats")
def cache_stats():
    return {
        "exact_cache": get_cache_stats(),
        "semantic_cache": get_semantic_cache_stats()
    }


@app.delete("/cache/clear")
def clear_cache():
    clear_all_cache()
    clear_semantic_cache()
    return {"message": "All caches cleared"}


@app.get("/templates")
def get_templates():
    return get_all_templates()


@app.get("/templates/{template_type}")
def get_single_template(template_type: str):
    try:
        t = TemplateType(template_type)
        return get_template(t)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_type}' not found"
        )


@app.get("/export/csv")
def export_csv():
    csv_content = export_to_csv()
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=rag_evaluation_history.csv"
        }
    )


@app.get("/export/summary")
def export_summary_endpoint():
    return export_summary()


@app.post("/debug")
def debug_scores(
    retrieval_score: float,
    faithfulness_score: float,
    utilization_score: float,
    overall_score: float
):
    return analyze_and_debug(
        retrieval_score=retrieval_score,
        faithfulness_score=faithfulness_score,
        utilization_score=utilization_score,
        overall_score=overall_score
    )