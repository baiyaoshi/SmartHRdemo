# -*- coding: utf-8 -*-
"""岗位管理 API - ORM 方式"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db, Position
from backend.app.schemas import PositionCreate, PositionUpdate

router = APIRouter()


@router.get("")
def list_positions(page: int = Query(0, ge=0), size: int = Query(10, ge=1), db: Session = Depends(get_db)):
    query = db.query(Position).filter(Position.deleted == False).order_by(Position.id.desc())
    total = query.count()
    positions = query.offset(page * size).limit(size).all()
    return {"items": positions, "total": total, "page": page, "size": size}


@router.get("/all")
def get_all(db: Session = Depends(get_db)):
    return db.query(Position).filter(Position.deleted == False).order_by(Position.id).all()


@router.get("/{position_id}")
def get_one(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.id == position_id, Position.deleted == False).first()
    if not position:
        raise HTTPException(404, "岗位不存在")
    return position


@router.post("", status_code=201)
def create(data: PositionCreate, db: Session = Depends(get_db)):
    position = Position(**data.model_dump())
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


@router.put("/{position_id}")
def update(position_id: int, data: PositionUpdate, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.id == position_id, Position.deleted == False).first()
    if not position:
        raise HTTPException(404, "岗位不存在")
    for key, value in data.model_dump().items():
        setattr(position, key, value)
    db.commit()
    db.refresh(position)
    return position


@router.delete("/{position_id}")
def delete(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.id == position_id, Position.deleted == False).first()
    if not position:
        raise HTTPException(404, "岗位不存在")
    position.deleted = True
    db.commit()
    return {"message": "已删除"}