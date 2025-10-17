
from elasticsearch import Elasticsearch
from typing import List, Dict, Any
from .settings import get_settings
import numpy as np

S = get_settings()

es = Elasticsearch(
    S.elastic_url,
    api_key=S.elastic_api_key,
    request_timeout=30,
)

def ensure_index():
    mapping = {
        "mappings": {
            "properties": {
                "project_id": {"type": "keyword"},
                "text": {"type": "text"},
                "chunk_id": {"type": "keyword"},
                "tags": {"type": "keyword"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": S.embed_dims,
                    "index": True,
                    "similarity": "cosine"
                },
                "created_at": {"type": "date"}
            }
        }
    }
    if not es.indices.exists(index=S.elastic_index):
        es.indices.create(index=S.elastic_index, body=mapping)

def upsert_chunk(project_id: str, text: str, embedding: List[float], tags: List[str] = None) -> str:
    ensure_index()
    doc = {
        "project_id": project_id,
        "text": text,
        "tags": tags or [],
        "embedding": embedding,
    }
    res = es.index(index=S.elastic_index, document=doc)
    return res["_id"]

def knn_search(project_id: str, query_vec: List[float], k: int = 8) -> List[Dict[str, Any]]:
    ensure_index()
    body = {
        "size": k,
        "query": {
            "bool": {
                "filter": [{"term": {"project_id": project_id}}],
                "must": [
                    {
                        "knn": {
                            "field": "embedding",
                            "query_vector": query_vec,
                            "k": k,
                            "num_candidates": max(20, k*5)
                        }
                    }
                ]
            }
        }
    }
    res = es.search(index=S.elastic_index, body=body)
    hits = res["hits"]["hits"]
    return [{"text": h["_source"]["text"], "score": h["_score"]} for h in hits]

def hybrid_search(project_id: str, query_text: str, query_vec: List[float], k: int = 8) -> List[Dict[str, Any]]:
    # Combine lexical and vector signals
    ensure_index()
    body = {
        "size": max(k, 8),
        "query": {
            "bool": {
                "filter": [{"term": {"project_id": project_id}}],
                "should": [
                    {"match": {"text": {"query": query_text, "boost": 2.0}}},
                    {
                        "knn": {
                            "field": "embedding",
                            "query_vector": query_vec,
                            "k": max(k,8),
                            "num_candidates": max(40, k*8),
                            "boost": 1.0
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    }
    res = es.search(index=S.elastic_index, body=body)
    hits = res["hits"]["hits"]
    return [{"text": h["_source"]["text"], "score": h["_score"]} for h in hits]
