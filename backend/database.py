from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:sumiths%40123@localhost:5432/rag_evaluator"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id                  = Column(Integer, primary_key=True, index=True)
    question            = Column(Text, nullable=False)
    source_document     = Column(String(255), nullable=True)
    answer              = Column(Text, nullable=True)
    retrieval_score     = Column(Float, nullable=True)
    faithfulness_score  = Column(Float, nullable=True)
    utilization_score   = Column(Float, nullable=True)
    overall_score       = Column(Float, nullable=True)
    verdict             = Column(String(50), nullable=True)
    diagnosis           = Column(Text, nullable=True)
    top_k               = Column(Integer, default=3)
    chunks_retrieved    = Column(Integer, default=0)
    created_at          = Column(DateTime, default=datetime.utcnow)


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id              = Column(Integer, primary_key=True, index=True)
    filename        = Column(String(255), nullable=False)
    total_chunks    = Column(Integer, nullable=False)
    file_size_bytes = Column(Integer, nullable=True)
    uploaded_at     = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_evaluation_run(
    db,
    question: str,
    retrieval_score: float,
    overall_score: float,
    verdict: str,
    diagnosis: str,
    answer: str = None,
    faithfulness_score: float = None,
    utilization_score: float = None,
    source_document: str = None,
    top_k: int = 3,
    chunks_retrieved: int = 0
) -> EvaluationRun:
    run = EvaluationRun(
        question=question,
        answer=answer,
        source_document=source_document,
        retrieval_score=retrieval_score,
        faithfulness_score=faithfulness_score,
        utilization_score=utilization_score,
        overall_score=overall_score,
        verdict=verdict,
        diagnosis=diagnosis,
        top_k=top_k,
        chunks_retrieved=chunks_retrieved
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def save_uploaded_document(
    db,
    filename: str,
    total_chunks: int,
    file_size_bytes: int = 0
) -> UploadedDocument:
    doc = UploadedDocument(
        filename=filename,
        total_chunks=total_chunks,
        file_size_bytes=file_size_bytes
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_recent_runs(db, limit: int = 10) -> list:
    return (
        db.query(EvaluationRun)
        .order_by(EvaluationRun.created_at.desc())
        .limit(limit)
        .all()
    )


def get_average_scores(db) -> dict:
    result = db.query(
        func.avg(EvaluationRun.retrieval_score).label("avg_retrieval"),
        func.avg(EvaluationRun.faithfulness_score).label("avg_faithfulness"),
        func.avg(EvaluationRun.utilization_score).label("avg_utilization"),
        func.avg(EvaluationRun.overall_score).label("avg_overall"),
        func.count(EvaluationRun.id).label("total_runs")
    ).first()

    return {
        "avg_retrieval_score": round(result.avg_retrieval or 0, 3),
        "avg_faithfulness_score": round(result.avg_faithfulness or 0, 3),
        "avg_utilization_score": round(result.avg_utilization or 0, 3),
        "avg_overall_score": round(result.avg_overall or 0, 3),
        "total_runs": result.total_runs or 0
    }