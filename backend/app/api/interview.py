# -*- coding: utf-8 -*-
"""面试题生成 API"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db, Position, InterviewRecord
from backend.app.schemas import GenerateQuestionsRequest
from backend.app.services.interview_service import generate_interview_questions

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/questions/generate")
def generate(req: GenerateQuestionsRequest, db: Session = Depends(get_db)):
    """根据岗位或技能生成面试题"""
    position = None
    skills = req.skills or []

    # 如果传了岗位ID，从数据库取技能要求
    if req.position_id:
        position = db.query(Position).filter(
            Position.id == req.position_id,
            Position.deleted == False
        ).first()
        if not position:
            raise HTTPException(404, "岗位不存在")
        if not skills:
            skills = position.skills or []

    # 调用生成引擎
    result = generate_interview_questions(
        position=position,
        skills=skills,
        difficulty=req.difficulty,
        count=req.count,
        question_type=req.question_type,
        include_answers=req.include_answers,
        business_domain=req.business_domain,
    )

    # 存到数据库
    if position:
        record = InterviewRecord(
            position_id=req.position_id,
            skills=skills,
            difficulty=req.difficulty,
            question_type=req.question_type,
            questions=result.get("questions", []),
        )
        db.add(record)
        db.commit()

    return {
        "position_title": position.title if position else "自定义",
        "skills": skills,
        "difficulty": req.difficulty,
        "questions": result.get("questions", []),
        "total": len(result.get("questions", [])),
    }