# -*- coding: utf-8 -*-
"""Pydantic 数据模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ===== 岗位 =====
class PositionBase(BaseModel):
    title: str
    company: Optional[str] = None
    salary_range: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    location: Optional[str] = None
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    skills: list[str] = []


class PositionCreate(PositionBase):
    pass


class PositionUpdate(PositionBase):
    pass


class Position(PositionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== 简历 =====
class ResumeBase(BaseModel):
    file_name: Optional[str] = None
    content: Optional[str] = None
    extracted_skills: list[str] = []


class Resume(ResumeBase):
    id: int
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ===== 匹配记录 =====
class MatchRecordBase(BaseModel):
    resume_id: int
    position_id: int
    final_score: Optional[float] = None
    graph_score: Optional[float] = None
    llm_score: Optional[float] = None
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    extra_skills: list[str] = []
    llm_report: Optional[str] = None
    match_grade: Optional[str] = None
    recommend_level: Optional[int] = None


class MatchRecord(MatchRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MatchRequest(BaseModel):
    resume_id: int
    position_id: int


# ===== 面试题 =====
class GenerateQuestionsRequest(BaseModel):
    position_id: Optional[int] = None
    skills: list[str] = []
    difficulty: str = "MIDDLE"
    count: int = 5
    question_type: str = "MIXED"
    include_answers: bool = True
    business_domain: str = "企业金融/支付"


class InterviewRecord(BaseModel):
    id: int
    position_id: Optional[int] = None
    skills: Optional[list[str]] = None
    difficulty: Optional[str] = None
    question_type: Optional[str] = None
    questions: Optional[list] = None
    created_at: datetime

    class Config:
        from_attributes = True
