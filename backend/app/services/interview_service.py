# -*- coding: utf-8 -*-
"""面试题生成服务"""
import json
import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
llm_client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
) if DASHSCOPE_API_KEY else None


def generate_interview_questions(
    position=None,
    skills=None,
    difficulty="MIDDLE",
    count=5,
    question_type="MIXED",
    include_answers=True,
    business_domain="企业金融/支付",
):
    """生成面试题"""
    skills = skills or []
    skill_text = ", ".join(skills) if skills else "通用技术"

    # 1. RAG 检索
    similar = _search_similar_questions(skill_text, top_k=5)

    # 2. LLM 生成
    questions = _generate_with_llm(
        position_title=position.title if position else "",
        skills=skill_text,
        difficulty=difficulty,
        count=count,
        question_type=question_type,
        include_answers=include_answers,
        business_domain=business_domain,
        similar_questions=similar,
    )

    return {"questions": questions}

def _search_similar_questions(query: str, top_k: int = 5) -> list[dict]:
    """从 Milvus 题库检索相似题目"""
    try:
        from backend.app.services.embedding_service import embed_text
        from backend.app.services.milvus_client import milvus_client

        vector = embed_text(query)
        if vector and any(v != 0.0 for v in vector):
            results = milvus_client.search("smart_hr_questions", vector, top_k=top_k)
            return results
    except Exception as e:
        logger.warning(f"题库检索失败: {e}")
    return []


def _generate_with_llm(
    position_title, skills, difficulty, count, question_type,
    include_answers, business_domain, similar_questions,
):
    """调用 LLM 生成面试题"""
    if not llm_client:
        return _fallback_questions(skills, difficulty, count)

    similar_text = ""
    if similar_questions:
        lines = []
        for q in similar_questions:
            meta = q.get("metadata", {})
            lines.append(f"- [{meta.get('difficulty', '')}] {q.get('content', '')}")
        similar_text = "\n".join(lines)

    prompt = f"""你是一个资深技术面试官。请根据以下要求生成技术面试题。

【岗位】{position_title or '通用技术岗位'}
【技能要求】{skills}
【难度等级】{difficulty}
【题目类型】{question_type}
【业务领域】{business_domain}
【生成数量】{count} 道
{"【需要包含答案】" if include_answers else ""}

参考题库中的相似题目：
{similar_text if similar_text else "（无）"}

请严格按照 JSON 数组格式输出，每个题目包含 question 和 answer 字段。
示例格式：
[
  {{"question": "题目内容", "answer": "参考答案"}},
  {{"question": "题目内容", "answer": "参考答案"}}
]

只输出 JSON 数组，不要多余内容："""

    try:
        resp = llm_client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
        text = resp.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]
        questions = json.loads(text)
        if isinstance(questions, list):
            return questions
    except Exception as e:
        logger.error(f"LLM 生成失败: {e}")

    return _fallback_questions(skills, difficulty, count)


def _fallback_questions(skills: str, difficulty: str, count: int) -> list[dict]:
    """LLM 不可用时的备选题目"""
    templates = [
        f"请谈谈你在 {skills} 项目中的实践经验？",
        f"在 {skills} 开发中，你遇到过哪些挑战？如何解决的？",
        f"如何对 {skills} 相关的系统进行性能优化？",
        f"请设计一个基于 {skills} 的微服务架构方案",
        f"在 {skills} 开发中，如何进行代码质量保障？",
    ]
    result = []
    for i in range(min(count, len(templates))):
        result.append({"question": templates[i], "answer": ""})
    return result
