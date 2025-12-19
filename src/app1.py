"""
app1.py

API REST (FastAPI) para el sistema ZettelRAG – versión directa sin orquestador.

Características:
- Pipeline RAG lineal (retrieval → build_context → generation)
- No realiza clasificación de intención
- Asume que toda consulta debe resolverse mediante RAG
- Pensada como primera versión funcional del sistema

Esta API expone un único endpoint para consultas y organización de conocimiento
basadas exclusivamente en el contexto recuperado.
"""


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from retrieval import retrieve_context
from build_context import build_context
from generation import generate_answer




# =========================
# Inicialización API
# =========================

app = FastAPI(
    title="ZettelRAG",
    description="RAG personal para consulta y organización de conocimiento",
    version="1.0.0"
)










# =========================
# Modelos de entrada/salida
# =========================

class QueryRequest(BaseModel):
    """
    Modelo de entrada para una consulta al sistema RAG.
    """
    question: str = Field(..., description="Pregunta del usuario")
    mode: str = Field("consulta", description="consulta | autor")
    temperature: float = Field(0.2, ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    """
    Modelo de salida de una consulta al sistema RAG.
    """
    answer: str
    sources: list[str]
    scores: list[float]
    grounded: bool










# =========================
# Endpoint principal
# =========================

@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """
    Ejecuta el pipeline RAG completo para una consulta del usuario.

    Flujo:
    1. Validación de la entrada
    2. Recuperación de contexto desde la base vectorial
    3. Construcción del contexto textual
    4. Generación de la respuesta mediante LLM

    Args:
        request (QueryRequest): Parámetros de la consulta.

    Returns:
        QueryResponse: Respuesta generada, fuentes utilizadas y metadata.
    """

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")

    if request.mode not in ("consulta", "autor"):
        raise HTTPException(
            status_code=400,
            detail="El modo debe ser 'consulta' o 'autor'."
        )

    # -------------------------
    # Retrieval + Reranking
    # -------------------------
    retrieval_result = retrieve_context(request.question)

    # -------------------------
    # Construcción de contexto
    # -------------------------
    context = build_context(retrieval_result)

    # -------------------------
    # Generación
    # -------------------------
    answer = generate_answer(
        query=request.question,
        context=context,
        mode=request.mode,
        temperature=request.temperature
    )

    return QueryResponse(
        answer=answer,
        sources=retrieval_result.get("sources", []),
        scores=retrieval_result.get("scores", []),
        grounded=bool(retrieval_result.get("chunks"))
    )
