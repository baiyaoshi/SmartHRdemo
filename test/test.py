"""创建 Milvus 集合"""
from pymilvus import (
    connections, Collection, CollectionSchema,
    FieldSchema, DataType, utility
)

connections.connect(alias="default", host="localhost", port="19530")

DIM = 1536  # 阿里云 text-embedding-v2 的维度


def create_collection(name, desc):
    if utility.has_collection(name):
        print(f"集合已存在: {name}")
        coll = Collection(name)
        coll.load()
        return coll

    fields = [
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("vector", DataType.FLOAT_VECTOR, dim=DIM),
        FieldSchema("content", DataType.VARCHAR, max_length=65535),
        FieldSchema("metadata", DataType.VARCHAR, max_length=65535),
    ]
    schema = CollectionSchema(fields, description=desc)
    coll = Collection(name=name, schema=schema)
    coll.create_index("vector", {
        "index_type": "IVF_FLAT",
        "metric_type": "COSINE",
        "params": {"nlist": 1024},
    })
    coll.load()
    print(f"创建成功: {name}")
    return coll


# 1. 面试题库
create_collection("smart_hr_questions", "面试题库")

# 2. 简历库
create_collection("smart_hr_resumes", "简历向量库")

print("\n所有集合:")
for c in utility.list_collections():
    coll = Collection(c)
    print(f"  {c}: {coll.num_entities} 条数据")
