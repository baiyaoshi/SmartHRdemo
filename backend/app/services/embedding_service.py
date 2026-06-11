"""文本向量化服务 - 使用阿里云 DashScope text-embedding-v2"""
import logging
import os
from openai import OpenAI
logger = logging.getLogger(__name__)

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
) if DASHSCOPE_API_KEY else None


def embed_text(text: str) -> list[float]:
    """将文本转为向量"""
    if not client:
        logger.warning("DashScope 未配置，返回空向量")
        return [0.0] * 1536

    try:
        resp = client.embeddings.create(
            model="text-embedding-v2",
            input=text,
        )
        return resp.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding 失败: {e}")
        return [0.0] * 1536


def embed_texts(texts: list[str]) -> list[list[float]]:
    """批量将文本转为向量"""
    if not client:
        logger.warning("DashScope 未配置，返回空向量")
        return [[0.0] * 1536] * len(texts)

    try:
        resp = client.embeddings.create(
            model="text-embedding-v2",
            input=texts,
        )
        vectors = [0.0] * len(texts)
        for item in resp.data:
            vectors[item.index] = item.embedding
        return vectors
    except Exception as e:
        logger.error(f"批量 Embedding 失败: {e}")
        return [[0.0] * 1536] * len(texts)

def _generate_with_llm(
    position_title, skills, difficulty, count, question_type,
    include_answers, business_domain, similar_questions,
):
    """调用 LLM 生成面试题"""
    # 如果没有配置 API Key，用备选题
    if not llm_client:
        return _fallback_questions(skills, difficulty, count)

    # 把 Milvus 搜到的相似题拼成文字
    similar_text = ""
    if similar_questions:
        lines = []
        for q in similar_questions:
            meta = q.get("metadata", {})
            lines.append(f"- [{meta.get('difficulty', '')}] {q.get('content', '')}")
        similar_text = "\n".join(lines)

    # 拼 Prompt
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

    # 调阿里云
    try:
        from backend.app.services.interview_service import llm_client
        resp = llm_client.chat.completions.create(
            model="qwen-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
        text = resp.choices[0].message.content.strip()

        # 去掉 markdown 代码块包裹
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            text = text.rsplit("```", 1)[0]

        questions = json.loads(text)
        if isinstance(questions, list):
            return questions
    except Exception as e:
        logger.error(f"LLM 生成失败: {e}")

    # 失败时用备选
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
    # 只返回 count 道题，最多 5 道
    result = []
    for i in range(min(count, len(templates))):
        result.append({"question": templates[i], "answer": ""})
    return result