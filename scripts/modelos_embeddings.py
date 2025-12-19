# Estructura de modelos para los embeddings:

from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)


"""
{
  "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
  "dim": 384
}
"""
