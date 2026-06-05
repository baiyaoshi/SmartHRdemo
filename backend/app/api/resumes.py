# -*- coding: utf-8 -*-
"""简历管理 API"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from backend.app.database import get_db, Resume
from backend.app.services.document_parser import parse_bytes, is_supported

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not is_supported(file.filename):
        raise HTTPException(400, f"不支持的文件格式: {file.filename}")

    data = await file.read()
    content = parse_bytes(file.filename, data)

    if not content:
        raise HTTPException(400, "无法解析文件内容，请确认格式正确")

    resume = Resume(file_name=file.filename, content=content)
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "file_name": resume.file_name,
        "content_preview": resume.content[:200],
        "content_length": len(resume.content),
        "message": "上传成功",
    }


@router.get("")
def list_resumes(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(Resume).order_by(Resume.id.desc())
    total = query.count()
    resumes = query.offset(page * size).limit(size).all()

    items = []
    for resume in resumes:
        items.append(
            {
                "id": resume.id,
                "file_name": resume.file_name,
                "content_preview": (resume.content or "")[:100],
                "extracted_skills": resume.extracted_skills or [],
                "created_at": resume.created_at.isoformat() if resume.created_at else None,
            }
        )
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(404, "简历不存在")
    return resume


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(404, "简历不存在")
    db.delete(resume)
    db.commit()
    return {"message": "已删除"}