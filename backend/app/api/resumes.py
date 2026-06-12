"""简历管理 API"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from backend.app.database import get_db, Resume, Position
from backend.app.services.document_parser import parse_bytes, is_supported
from backend.app.services.skill_extractor import extract_skills, normalize_skills
from backend.app.services.hybrid_match import hybrid_match

logger = logging.getLogger(__name__)
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


@router.post("/upload-and-match", status_code=201)
async def upload_and_match(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传简历并自动匹配所有岗位"""
    if not is_supported(file.filename):
        raise HTTPException(400, f"不支持的文件格式: {file.filename}")

    # 1. 解析简历
    data = await file.read()
    content = parse_bytes(file.filename, data)
    if not content:
        raise HTTPException(400, "无法解析文件内容")

    # 2. 提取技能
    skills = extract_skills(content)
    skills = normalize_skills(skills)

    # 3. 保存简历
    resume = Resume(file_name=file.filename, content=content, extracted_skills=skills)
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # 4. 获取所有岗位
    positions = db.query(Position).filter(Position.deleted == False).all()

    # 5. 逐个匹配
    results = []
    for pos in positions:
        try:
            result = hybrid_match(
                resume_text=content,
                resume_skills=skills,
                position_title=pos.title or "",
                position_skills=pos.skills or [],
                position_requirements=(pos.requirements or "") + "\n" + (pos.responsibilities or ""),
            )
            from backend.app.database import MatchRecord
            record = MatchRecord(
                resume_id=resume.id,
                position_id=pos.id,
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

            results.append({
                "position_id": pos.id,
                "position_title": pos.title,
                "company": pos.company,
                "salary_range": pos.salary_range,
                **result,
            })
        except Exception as e:
            logger.error(f"匹配岗位 {pos.id} 失败: {e}")
            results.append({
                "position_id": pos.id,
                "position_title": pos.title,
                "final_score": 0,
                "match_grade": "E",
                "error": str(e),
            })

    # 按分数倒序
    results.sort(key=lambda x: x.get("final_score", 0), reverse=True)

    return {
        "resume_id": resume.id,
        "file_name": file.filename,
        "skills": skills,
        "total_positions": len(positions),
        "results": results,
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