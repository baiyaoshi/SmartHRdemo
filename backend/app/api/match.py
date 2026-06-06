# -*- coding: utf-8 -*-
"""匹配分析 API"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db, Resume, Position, MatchRecord
from backend.app.schemas import MatchRequest
from backend.app.services.skill_extractor import extract_skills, normalize_skills
from backend.app.services.hybrid_match import hybrid_match

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/match", status_code=200)
def match(req: MatchRequest, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == req.resume_id).first()
    if not resume:
        raise HTTPException(404, "简历不存在")

    position = db.query(Position).filter(Position.id == req.position_id, Position.deleted == False).first()
    if not position:
        raise HTTPException(404, "岗位不存在")

    if not resume.extracted_skills:
        skills = extract_skills(resume.content or "")
        resume.extracted_skills = normalize_skills(skills)
        db.commit()

    result = hybrid_match(
        resume_text=resume.content or "",
        resume_skills=resume.extracted_skills or [],
        position_title=position.title or "",
        position_skills=position.skills or [],
        position_requirements=(position.requirements or "") + "\n" + (position.responsibilities or ""),
    )

    record = MatchRecord(
        resume_id=req.resume_id,
        position_id=req.position_id,
        final_score=result["final_score"],
        graph_score=result["graph_score"],
        llm_score=result["llm_score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        extra_skills=result["extra_skills"],
        llm_report=result["llm_report"],
        match_grade=result["match_grade"],
        recommend_level=result["recommend_level"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "resume_id": record.resume_id,
        "position_id": record.position_id,
        "position_title": position.title,
        **result,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@router.get("/match/records")
def list_match_records(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(MatchRecord).order_by(MatchRecord.id.desc())
    total = query.count()
    records = query.offset(page * size).limit(size).all()

    items = []
    for r in records:
        position = db.query(Position).filter(Position.id == r.position_id).first()
        resume = db.query(Resume).filter(Resume.id == r.resume_id).first()
        items.append({
            "id": r.id,
            "resume_id": r.resume_id,
            "resume_name": resume.file_name if resume else "",
            "position_id": r.position_id,
            "position_title": position.title if position else "",
            "final_score": r.final_score,
            "graph_score": r.graph_score,
            "llm_score": r.llm_score,
            "match_grade": r.match_grade,
            "recommend_level": r.recommend_level,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/match/records/{record_id}")
def get_match_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(MatchRecord).filter(MatchRecord.id == record_id).first()
    if not record:
        raise HTTPException(404, "匹配记录不存在")

    position = db.query(Position).filter(Position.id == record.position_id).first()
    resume = db.query(Resume).filter(Resume.id == record.resume_id).first()

    return {
        "id": record.id,
        "resume_id": record.resume_id,
        "resume_name": resume.file_name if resume else "",
        "resume_content": (resume.content or "")[:500] if resume else "",
        "resume_skills": resume.extracted_skills if resume else [],
        "position_id": record.position_id,
        "position_title": position.title if position else "",
        "position_skills": position.skills if position else [],
        "final_score": record.final_score,
        "graph_score": record.graph_score,
        "llm_score": record.llm_score,
        "matched_skills": record.matched_skills,
        "missing_skills": record.missing_skills,
        "extra_skills": record.extra_skills,
        "llm_report": record.llm_report,
        "match_grade": record.match_grade,
        "recommend_level": record.recommend_level,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }