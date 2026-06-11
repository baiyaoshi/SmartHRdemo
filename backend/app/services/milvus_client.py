# -*- coding: utf-8 -*-
"""Milvus 向量存储客户端"""
import json
import logging
import os
from typing import Optional
from pymilvus import (
    connections, Collection, CollectionSchema,
    FieldSchema, DataType, utility
)

logger = logging.getLogger(__name__)

MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))


class MilvusClient:
    """Milvus 向量数据库客户端"""

    def __init__(self):
        self._connected = False
        self._collections = {}

    def connect(self):
        if self._connected:
            return
        connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
        self._connected = True
        logger.info(f"Milvus connected: {MILVUS_HOST}:{MILVUS_PORT}")

    def close(self):
        if self._connected:
            connections.disconnect("default")
            self._connected = False

    def _ensure_collection(self, collection_name: str, dim: int = EMBEDDING_DIM) -> Collection:
        if collection_name in self._collections:
            return self._collections[collection_name]

        self.connect()

        if utility.has_collection(collection_name):
            coll = Collection(collection_name)
            coll.load()
            self._collections[collection_name] = coll
            return coll

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535),
        ]
        schema = CollectionSchema(fields=fields, description=collection_name)
        coll = Collection(name=collection_name, schema=schema)
        coll.create_index(field_name="vector", index_params={
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "params": {"nlist": 1024},
        })
        coll.load()
        self._collections[collection_name] = coll
        logger.info(f"Created collection: {collection_name} (dim={dim})")
        return coll

    def insert(self, collection_name: str, vectors: list, texts: list[str], metadatas: Optional[list[dict]] = None):
        coll = self._ensure_collection(collection_name)
        entities = [
            vectors,
            texts,
            [json.dumps(m or {}, ensure_ascii=False) for m in (metadatas or [{}] * len(texts))],
        ]
        mr = coll.insert(entities)
        coll.flush()
        logger.info(f"Inserted {len(texts)} entities into {collection_name}")
        return mr

    def search(self, collection_name: str, query_vector: list, top_k: int = 5) -> list[dict]:
        coll = self._ensure_collection(collection_name)
        coll.load()

        results = coll.search(
            data=[query_vector],
            anns_field="vector",
            param={"metric_type": "COSINE", "params": {"nprobe": 16}},
            limit=top_k,
            output_fields=["content", "metadata"],
        )

        hits = []
        for hits_row in results:
            for hit in hits_row:
                hits.append({
                    "id": hit.id,
                    "score": round(hit.score, 4),
                    "content": hit.entity.get("content"),
                    "metadata": json.loads(hit.entity.get("metadata") or "{}"),
                })

        return hits

    def count(self, collection_name: str) -> int:
        coll = self._ensure_collection(collection_name)
        return coll.num_entities


# 全局单例
milvus_client = MilvusClient()
