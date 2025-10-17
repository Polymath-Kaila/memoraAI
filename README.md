
# MemoraAI — Cross‑Conversation Memory Engine (Elastic + Vertex AI)

A production‑ready scaffold for a context memory layer that augments LLMs (Gemini, GPT, etc.) with
**cross‑chat, project‑persistent memory** using **Elastic hybrid search** and **Vertex AI** embeddings / generation.

## Why this scaffold?
- Clean FastAPI layout (health checks, typed models, routers)
- Elastic **dense_vector** + hybrid (kNN + lexical) retrieval
- Simple **MMR** reranker for diversity
- Token‑budget aware prompt builder
- Environment‑driven config with sane defaults
- Docker optional; local `uvicorn` works out of the box

## Quick start

1) **Create env file**

Copy `.env.example` → `.env` and fill in values:

```bash
cp .env.example .env
# edit .env
```

2) **Install**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

3) **Run**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000/docs

## Key endpoints

- `GET /health` — liveness & dependency checks
- `POST /ingest` — ingest raw text into a project memory
- `POST /ask` — query with automatic retrieval + Gemini/Vertex generation

## Notes

- This repo **does not** hard‑pin versions; if you prefer reproducibility, add exact versions later.
- Vertex AI calls use the official SDK. Authenticate with a service account (ADC) or set `GOOGLE_APPLICATION_CREDENTIALS`.
- Elastic index is created on demand with a `dense_vector` mapping (768 dims by default).

## Security
- Never commit `.env` or service account JSON.
- Restrict Elastic API keys to your index; rotate regularly.

## License
Apache-2.0
