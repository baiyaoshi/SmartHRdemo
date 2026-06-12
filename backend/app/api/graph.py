# -*- coding: utf-8 -*-
"""知识图谱管理 API"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.app.services.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)
router = APIRouter()


class SkillCreate(BaseModel):
    name: str
    level: int = 2
    description: str = ""
    keywords: list[str] = []
    category_code: str = "GENERAL"
    requires: list[str] = []
    related_to: list[str] = []


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    description: Optional[str] = None
    keywords: Optional[list[str]] = None
    category_code: Optional[str] = None


# ==================== 读取 ====================

@router.get("/graph/skills")
def get_all_skills():
    """获取所有技能节点"""
    skills = neo4j_client.get_all_skills()
    return skills


@router.get("/graph/skills/search")
def search_skills(keyword: str = ""):
    """搜索技能"""
    if keyword:
        return neo4j_client.search_skills(keyword)
    return neo4j_client.get_all_skills()


@router.get("/graph/skills/{name}")
def get_skill_detail(name: str):
    """获取技能详情，含前置、相关、所属分类、后继技能"""
    skill = neo4j_client.find_skill_by_name(name)
    if not skill:
        raise HTTPException(404, f"技能 '{name}' 不存在")

    # 获取前置技能 (REQUIRES 目标)
    prerequisites = neo4j_client.get_prerequisite_skills(name)
    # 获取相关技能
    related = neo4j_client.get_related_skills(name)
    # 获取后继技能 (被其他技能 REQUIRES)
    advanced = neo4j_client.get_advanced_skills(name)
    # 获取分类
    category = neo4j_client.get_skill_category(name)

    return {
        **skill,
        "prerequisites": [p["name"] for p in prerequisites],
        "related": [r["name"] for r in related],
        "advanced": [a["name"] for a in advanced],
        "category": category,
    }


@router.get("/graph/categories")
def get_categories():
    """获取所有技能分类"""
    return neo4j_client.get_all_categories()


@router.get("/graph/relations")
def get_all_relations():
    """获取所有技能关系（用于前端可视化连线）"""
    return neo4j_client.get_all_relations()


# ==================== 新增 ====================

@router.post("/graph/skills", status_code=201)
def create_skill(data: SkillCreate):
    """创建技能节点"""
    existing = neo4j_client.find_skill_by_name(data.name)
    if existing:
        raise HTTPException(400, f"技能 '{data.name}' 已存在")

    result = neo4j_client.create_skill(
        name=data.name,
        level=data.level,
        description=data.description,
        keywords=data.keywords,
        category_code=data.category_code,
        requires=data.requires,
        related_to=data.related_to,
    )
    return {"message": "创建成功", "skill": result}


# ==================== 修改 ====================

@router.put("/graph/skills/{name}")
def update_skill(name: str, data: SkillUpdate):
    """更新技能"""
    existing = neo4j_client.find_skill_by_name(name)
    if not existing:
        raise HTTPException(404, f"技能 '{name}' 不存在")

    update_data = data.model_dump(exclude_none=True)
    if not update_data:
        return {"message": "无变更"}

    neo4j_client.update_skill(name, update_data)
    return {"message": "更新成功"}


# ==================== 删除 ====================

@router.delete("/graph/skills/{name}")
def delete_skill(name: str):
    """删除技能节点及其关系"""
    existing = neo4j_client.find_skill_by_name(name)
    if not existing:
        raise HTTPException(404, f"技能 '{name}' 不存在")

    neo4j_client.delete_skill(name)
    return {"message": "删除成功"}
