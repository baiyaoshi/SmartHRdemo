# -*- coding: utf-8 -*-
"""数据库连接 + ORM 模型定义"""
from datetime import datetime
from sqlalchemy import create_engine, Column, BigInteger, String, Text, Float, Boolean, DateTime, JSON, ForeignKey, \
    Integer
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://smarthr:smarthr123@localhost:13306/smarthr"

engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== ORM 模型 ==========

class Position(Base):
    """岗位"""
    __tablename__ = "positions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    company = Column(String(100))
    salary_range = Column(String(50))
    experience = Column(String(50))
    education = Column(String(50))
    location = Column(String(50))
    responsibilities = Column(Text)
    requirements = Column(Text)
    skills = Column(JSON)  # 数组存成 JSON
    deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Resume(Base):
    """简历"""
    __tablename__ = "resumes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    file_name = Column(String(255))
    file_path = Column(String(500))
    content = Column(Text)
    extracted_skills = Column(JSON)  # 提取的技能列表
    created_at = Column(DateTime, default=datetime.now)


class MatchRecord(Base):
    """匹配记录"""
    __tablename__ = "match_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    resume_id = Column(BigInteger, ForeignKey("resumes.id"), nullable=False)
    position_id = Column(BigInteger, ForeignKey("positions.id"), nullable=False)
    final_score = Column(Float)
    graph_score = Column(Float)
    llm_score = Column(Float)
    matched_skills = Column(JSON)
    missing_skills = Column(JSON)
    extra_skills = Column(JSON)
    llm_report = Column(Text)
    match_grade = Column(String(10))
    recommend_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class InterviewRecord(Base):
    """面试题记录"""
    __tablename__ = "interview_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    position_id = Column(BigInteger, ForeignKey("positions.id"))
    skills = Column(JSON)
    difficulty = Column(String(20))
    question_type = Column(String(20))
    questions = Column(JSON)  # 面试题列表存 JSON
    created_at = Column(DateTime, default=datetime.now)