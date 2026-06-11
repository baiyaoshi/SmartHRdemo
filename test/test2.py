"""种子面试题数据（暂用伪向量代替，后续接入阿里云 Embedding）"""
import json
from pymilvus import connections, Collection, utility

connections.connect(alias="default", host="localhost", port="19530")
COLLECTION = "smart_hr_questions"
DIM = 1536

questions = [
    # Java
    {
        "question": "谈谈 Java 中 volatile 关键字的作用，以及和 synchronized 的区别",
        "answer": "volatile 保证可见性和有序性，不保证原子性；synchronized 保证可见性、有序性和原子性。volatile 适合状态标记，synchronized 适合复合操作。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "Java"
    },
    {
        "question": "Spring Boot 自动配置的原理是什么？如何自定义 Starter？",
        "answer": "通过 @EnableAutoConfiguration + spring.factories 加载 AutoConfiguration 类，配合 @Conditional 条件注解实现按需加载。自定义 Starter 需要定义自动配置类和 spring.factories。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "Java"
    },
    {
        "question": "讲一下 JVM 垃圾回收机制，CMS 和 G1 有什么区别？",
        "answer": "JVM GC 分为 Young GC 和 Full GC。CMS 是并发标记清除，追求低停顿，会产生内存碎片。G1 是区域化分代收集，可预测停顿时间，JDK 9+ 默认。",
        "difficulty": "SENIOR",
        "type": "TECHNICAL",
        "domain": "Java"
    },
    # Python
    {
        "question": "Python 中 GIL 是什么？对多线程有什么影响？如何绕过？",
        "answer": "GIL 是全局解释器锁，同一时刻只有一个线程执行 Python 字节码。CPU 密集型用 multiprocessing，IO 密集型用多线程/异步。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "Python"
    },
    {
        "question": "FastAPI 相比 Django 有哪些优势？异步支持如何？",
        "answer": "FastAPI 原生异步支持、自动生成 OpenAPI 文档、基于 Pydantic 校验、性能更高。Django 更重，ORM 强大但同步为主。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "Python"
    },
    # 数据库
    {
        "question": "MySQL 索引失效的常见场景有哪些？如何优化慢查询？",
        "answer": "失效场景：左模糊查询、函数操作、类型隐式转换、不符合最左前缀。优化：EXPLAIN 分析、适当加索引、避免 SELECT *、分页优化。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "数据库"
    },
    {
        "question": "Redis 的持久化机制有哪些？RDB 和 AOF 的优缺点？",
        "answer": "RDB 快照：性能高、恢复快、可能丢数据。AOF 日志：数据更安全、文件大、恢复慢。生产环境常用两者结合。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "数据库"
    },
    # 分布式
    {
        "question": "CAP 理论是什么？在微服务架构中如何取舍？",
        "answer": "Consistency、Availability、Partition Tolerance 三者不可兼得。微服务通常选择 AP+最终一致性，通过消息队列、事件驱动实现最终一致。",
        "difficulty": "SENIOR",
        "type": "TECHNICAL",
        "domain": "分布式"
    },
    {
        "question": "设计一个限流方案，支持接口级别和用户级别的限流",
        "answer": "计数器、滑动窗口、令牌桶、漏桶。可用 Redis + Lua 实现原子操作。接口级别按 Path 限流，用户级别按 UserId 限流。",
        "difficulty": "SENIOR",
        "type": "SCENARIO",
        "domain": "分布式"
    },
    # 场景题
    {
        "question": "如果线上出现频繁 Full GC，你如何排查？",
        "answer": "jstat 查看 GC 频率、jmap dump 堆、MAT 分析大对象、检查缓存/线程池/连接池配置、代码层面查循环创建对象等。",
        "difficulty": "SENIOR",
        "type": "SCENARIO",
        "domain": "Java"
    },
    {
        "question": "如何设计一个高可用的支付系统？需要考虑哪些方面？",
        "answer": "幂等设计、对账机制、补偿事务、状态机、多活部署、限流降级、监控告警。支付链路的每个环节都要有失败处理。",
        "difficulty": "SENIOR",
        "type": "SCENARIO",
        "domain": "系统设计"
    },
    # AI
    {
        "question": "RAG 的基本原理是什么？如何优化检索质量？",
        "answer": "检索增强生成：先检索相关文档，再让 LLM 基于检索结果生成答案。优化：分块策略、Embedding 模型选择、重排序、HyDE 方法。",
        "difficulty": "SENIOR",
        "type": "TECHNICAL",
        "domain": "AI"
    },
    {
        "question": "什么是 Prompt Engineering？有哪些常用技巧？",
        "answer": "通过设计输入提示词引导 LLM 输出。技巧：Few-shot、Chain-of-Thought、角色设定、格式约束、分步推理。",
        "difficulty": "MIDDLE",
        "type": "TECHNICAL",
        "domain": "AI"
    },
]

# 用文本的 hash 生成伪向量（临时用，后续换阿里云 Embedding）
def pseudo_embedding(text: str) -> list[float]:
    import hashlib
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    floats = []
    while len(floats) < DIM:
        for i in range(0, len(digest), 4):
            chunk = digest[i:i+4]
            if len(chunk) < 4:
                continue
            num = int.from_bytes(chunk, byteorder="big")
            floats.append((num % 10000) / 10000.0)
            if len(floats) >= DIM:
                break
    return floats[:DIM]


# 写入 Milvus
coll = Collection(COLLECTION)
coll.load()

# 检查是否已有数据
if coll.num_entities >= len(questions):
    print(f"题库已有 {coll.num_entities} 条数据，跳过")
else:
    vectors = []
    texts = []
    metadatas = []

    for q in questions:
        content = q["question"]
        vectors.append(pseudo_embedding(content))
        texts.append(content)
        metadatas.append(json.dumps({
            "question": q["question"],
            "answer": q["answer"],
            "difficulty": q["difficulty"],
            "type": q["type"],
            "domain": q["domain"],
        }, ensure_ascii=False))

    coll.insert([vectors, texts, metadatas])
    coll.flush()
    print(f"写入 {len(questions)} 条面试题到 {COLLECTION}")

# 验证
coll.load()
print(f"\n题库总量: {coll.num_entities} 条")

# 测试搜索
results = coll.search(
    data=[pseudo_embedding("Java 并发编程 volatile")],
    anns_field="vector",
    param={"metric_type": "COSINE", "params": {"nprobe": 16}},
    limit=3,
    output_fields=["content", "metadata"],
)
print("\n搜索测试: 'Java 并发编程 volatile'")
for hit in results[0]:
    meta = json.loads(hit.entity.get("metadata") or "{}")
    print(f"  分数={hit.score:.4f} | {meta.get('domain')}: {hit.entity.get('content')[:50]}...")
