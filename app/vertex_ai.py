from typing import List
from .settings import get_settings
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel

S = get_settings()

_initialized = False


def _init():
    """Initialize Vertex AI once globally"""
    global _initialized
    if not _initialized:
        vertexai.init(project=S.gcp_project_id, location=S.gcp_location)
        _initialized = True


def get_embedding(text: str) -> List[float]:
    """Generate a 768-dimensional text embedding using Vertex AI."""
    _init()
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    emb = model.get_embeddings([text])[0].values
    return emb


def generate_text(prompt: str) -> str:
    """Generate a text response using Gemini."""
    _init()
    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text or ""
