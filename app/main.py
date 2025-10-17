
from fastapi import FastAPI, HTTPException
from .settings import get_settings
from .models import IngestRequest, AskRequest, AskResponse
from .elastic_memory import upsert_chunk, hybrid_search
from .retriever import mmr
from .utils import chunk_text, approx_token_count
from .vertex_ai import get_embedding, generate_text

S = get_settings()
app = FastAPI(title=S.app_name)

@app.get("/health")
def health():
    # minimal liveness check
    return {"status": "ok", "app": S.app_name, "elastic_index": S.elastic_index, "location": S.gcp_location}

@app.post("/ingest")
def ingest(req: IngestRequest):
    chunks = chunk_text(req.text)
    for ch in chunks:
        emb = get_embedding(ch)
        upsert_chunk(req.project_id, ch, emb, req.tags or [])
    return {"ingested_chunks": len(chunks)}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    # embed query
    q_vec = get_embedding(req.query)
    # retrieve hybrid results
    hits = hybrid_search(req.project_id, req.query, q_vec, k=req.k)
    docs = [h["text"] for h in hits]
    if not docs:
        context = ""
        used = 0
    else:
        # for MMR we need doc vectors again; recompute (tradeoff simplicity vs storage)
        doc_vecs = [get_embedding(d) for d in docs]
        sel_idx = mmr(q_vec, docs, doc_vecs, k=min(req.k, len(docs)))
        selected_docs = [docs[i] for i in sel_idx]
        used = len(selected_docs)
        # token-budget aware join
        context_parts = []
        budget = S.token_budget
        for d in selected_docs:
            t = approx_token_count(d)
            if t + approx_token_count("\n".join(context_parts)) < budget:
                context_parts.append(d)
            else:
                break
        context = "\n\n".join(context_parts)

    prompt = f"""{S.system_preamble}

Relevant context:
{context}

User question: {req.query}

Answer clearly and cite which context snippets you used when appropriate.
"""
    try:
        text = generate_text(prompt).strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}")
    return AskResponse(response=text, used_snippets=used, tokens_estimate=approx_token_count(prompt))
