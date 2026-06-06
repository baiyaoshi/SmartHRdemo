# -*- coding: utf-8 -*-
"""技能提取服务"""
import logging
import os
from openai import OpenAI
from backend.app.services.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
dashscope_client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
) if DASHSCOPE_API_KEY else None


def extract_skills(content: str) -> list[str]:
    if not content:
        return []
    extracted = set()

    # 知识图谱匹配
    graph_matches = neo4j_client.match_skills_from_text(content)
    for m in graph_matches:
        extracted.add(m["name"])

    # LLM 补充
    try:
        llm_skills = _extract_with_llm(content, list(extracted))
        extracted.update(llm_skills)
    except Exception as e:
        logger.warning(f"LLM 提取失败: {e}")

    return sorted(extracted)


def _extract_with_llm(content: str, already_found: list[str]) -> list[str]:
    if not dashscope_client:
        return []

    prompt = f"""你是一个招聘系统的技能提取助手。

已知简历中已识别出以下技能：
{', '.join(already_found) if already_found else '暂无'}

请从简历内容中补充提取其他技术技能和软技能。
只返回技能名称，用逗号分隔，不要多余内容。

简历内容：
{content[:3000]}

补充技能："""

    resp = dashscope_client.chat.completions.create(
        model="qwen-plus",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300,
    )

    text = resp.choices[0].message.content.strip()
    skills = [s.strip() for s in text.replace("，", ",").split(",") if s.strip()]
    return [s for s in skills if 1 < len(s) <= 30]


def normalize_skills(skills: list[str]) -> list[str]:
    normalized = set()
    all_skills = neo4j_client.get_all_skills()
    name_map = {s["name"].lower(): s["name"] for s in all_skills}
    kw_map = {}
    for s in all_skills:
        for kw in (s.get("keywords") or []):
            kw_map[kw.lower()] = s["name"]

    for skill in skills:
        lower = skill.lower().strip()
        if lower in name_map:
            normalized.add(name_map[lower])
        elif lower in kw_map:
            normalized.add(kw_map[lower])
        else:
            normalized.add(skill)

    return sorted(normalized)