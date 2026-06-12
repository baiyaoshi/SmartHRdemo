# -*- coding: utf-8 -*-
"""混合匹配引擎：知识图谱 50% + LLM 评估 50%"""
import json
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

GRAPH_WEIGHT = 0.5
LLM_WEIGHT = 0.5


def hybrid_match(resume_text, resume_skills, position_title, position_skills, position_requirements):
    graph_result = neo4j_client.calculate_match_score(
        required_skills=position_skills,
        candidate_skills=resume_skills,
    )
    graph_score = graph_result["score"]

    if graph_score >= 60:
        llm_result = _llm_evaluate(
            resume_text, resume_skills, position_title, position_skills,
            position_requirements, graph_result,
        )
        llm_score = llm_result["score"]
        llm_report = llm_result["report"]
    else:
        llm_score = graph_score
        llm_report = "图谱匹配度较低，未进行 LLM 评估，最终得分以图谱评分为主"


    final_score = round(graph_score * GRAPH_WEIGHT + llm_score * LLM_WEIGHT, 1)
    grade, level = _to_grade_and_level(final_score)

    return {
        "final_score": final_score,
        "graph_score": round(graph_score, 1),
        "llm_score": round(llm_score, 1),
        "matched_skills": graph_result["matched"],
        "missing_skills": graph_result["missing"],
        "extra_skills": graph_result["extra"],
        "llm_report": llm_report,
        "match_grade": grade,
        "recommend_level": level,
    }


def _llm_evaluate(resume_text, resume_skills, position_title, position_skills, position_requirements, graph_match_info):
    if not dashscope_client:
        return {"score": graph_match_info["score"], "report": "LLM 未配置，使用图谱评分"}

    prompt = f"""你是一个专业的招聘匹配评估专家。请评估简历与岗位的匹配程度。

【岗位信息】
- 岗位名称：{position_title}
- 技能要求：{', '.join(position_skills)}
- 职责/要求：{position_requirements[:1000]}

【简历信息】
- 技能列表：{', '.join(resume_skills)}
- 知识图谱匹配结果：
  - 匹配技能：{', '.join(graph_match_info['matched'])}
  - 缺失技能：{', '.join(graph_match_info['missing'])}
  - 额外技能：{', '.join(graph_match_info['extra'])}
  - 图谱得分：{graph_match_info['score']}/100

【简历内容节选】
{resume_text[:1500]}

请输出 JSON 格式（不要 markdown 包裹）：
{{"score": <0-100 的综合评分>, "analysis": "<匹配分析>", "suggestions": "<建议>"}}"""

    try:
        resp = dashscope_client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        result = json.loads(text)
        score = float(result.get("score", graph_match_info["score"]))
        report = f"【LLM 分析】{result.get('analysis', '')}\n【建议】{result.get('suggestions', '')}"
        return {"score": score, "report": report}
    except Exception as e:
        logger.warning(f"LLM 评估失败: {e}")
        return {"score": graph_match_info["score"], "report": f"LLM 评估异常: {e}"}


def _to_grade_and_level(score: float):
    if score >= 90: return "A", 5
    elif score >= 80: return "A", 4
    elif score >= 70: return "B", 4
    elif score >= 60: return "B", 3
    elif score >= 50: return "C", 3
    elif score >= 40: return "C", 2
    elif score >= 30: return "D", 2
    else: return "D", 1