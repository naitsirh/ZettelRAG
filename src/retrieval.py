"""
retrieval.py

Módulo de recuperación de contexto para el sistema ZettelRAG.

Responsabilidades:
- Consultar la base vectorial (ChromaDB) para una recuperación inicial
- Aplicar reranking semántico mediante similitud coseno
- Retornar los chunks más relevantes junto con sus scores y fuentes

Este módulo es utilizado por el pipeline RAG y por el orquestador
para obtener el contexto a inyectar en el prompt del LLM.
"""


import chromadb
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity










# =========================
# Configuración
# =========================

CHROMA_PATH = r"C:\ruta\al\directorio\ZettelRAG\vectorstore"
COLLECTION_NAME = "zettelrag_notes"

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

TOP_K_INITIAL = 15
TOP_K_FINAL = 3










# =========================
# Inicialización
# =========================

# Inicializar Chroma / Cliente persistente de ChromaDB
chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


try:
    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )
except Exception as e:
    raise RuntimeError(
        f"La colección '{COLLECTION_NAME}' no existe. "
        "¿Ejecutaste ingestion.py?"
    ) from e


# Modelo de embeddings (debe coincidir con el usado en ingestión)
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)










# =========================
# Función principal
# =========================

def retrieve_context(query: str):
    """
    Recupera contexto relevante desde la base vectorial y aplica reranking.

    Flujo:
    1. Recuperación primaria desde ChromaDB (TOP_K_INITIAL)
    2. Reranking semántico usando similitud coseno
    3. Selección de los TOP_K_FINAL chunks más relevantes

    Args:
        query (str): Consulta del usuario.

    Returns:
        dict: Diccionario con:
            - chunks (list[str]): Textos más relevantes
            - scores (list[float]): Similitudes normalizadas
            - sources (list[str]): Archivos de origen
    """

    # -------------------------
    # 1. Recuperación primaria
    # -------------------------
    results = collection.query(
        query_texts=[query],
        n_results=TOP_K_INITIAL
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "chunks": [],
            "scores": [],
            "sources": []
        }

    # -------------------------
    # 2. Reranking
    # -------------------------
    query_embedding = embedding_model.encode(query)
    doc_embeddings = embedding_model.encode(documents)

    similarities = cosine_similarity(
        [query_embedding],
        doc_embeddings
    )[0]

    # -------------------------
    # 3. Ordenar y cortar
    # -------------------------
    ranked_results = sorted(
        zip(documents, similarities, metadatas),
        key=lambda x: x[1],
        reverse=True
    )

    top_results = ranked_results[:TOP_K_FINAL]

    # -------------------------
    # 4. Formato de salida
    # -------------------------
    return {
        "chunks": [item[0] for item in top_results],
        "scores": [round(float(item[1]), 4) for item in top_results],
        "sources": [item[2]["source_file"] for item in top_results]
    }
