"""
app.py

API REST principal del sistema ZettelRAG.

Características:
- Punto de entrada único para consultas del usuario
- Delegación completa de la lógica al orquestador
- Soporte para múltiples modos de generación
- Logging estructurado para observabilidad
- Endpoint de health check

Esta API representa la versión final del sistema, donde las decisiones
de flujo (RAG vs generación directa) se realizan dinámicamente mediante
el orquestador.
"""


import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from orchestrator import run_pipeline




# ===============================
# Configuración básica de logging
# ===============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="zettelrag.log",
)

logger = logging.getLogger(__name__)


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
    Modelo de entrada para una consulta al sistema ZettelRAG.
    """
    question: str = Field(..., description="Pregunta del usuario")
    mode: str = Field("consulta", description="consulta | autor")
    temperature: float = Field(
        0.2,
        ge=0.0,
        le=1.0
    )


class QueryResponse(BaseModel):
    """
    Modelo de salida unificado del pipeline orquestado.
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
    Ejecuta el pipeline orquestado completo para una consulta del usuario.

    Flujo:
    1. Validaciones básicas de la entrada
    2. Log de la consulta recibida
    3. Ejecución del orquestador (clasificación + RAG si aplica)
    4. Retorno de la respuesta unificada

    Args:
        request (QueryRequest): Parámetros de la consulta.

    Returns:
        QueryResponse: Resultado del pipeline, incluyendo grounding y fuentes.
    """

    # Log de entrada (truncado para evitar logs excesivos)
    logger.info(
        f"Query recibida | question='{request.question[:100]}...' | mode={request.mode} | temperature={request.temperature}"
        )

    # -------------------------
    # Validaciones básicas
    # -------------------------
    if not request.question.strip():
        logger.warning("Query rechazada: pregunta vacía")
        raise HTTPException(
            status_code=400,
            detail="La pregunta no puede estar vacía."
        )

    if request.mode not in ("consulta", "autor"):
        logger.warning(f"Query rechazada: modo inválido '{request.mode}'")
        raise HTTPException(
            status_code=400,
            detail="El modo debe ser 'consulta' o 'autor'."
        )

    # -------------------------
    # Orquestación completa
    # -------------------------
    try:
        logger.info("Ejecutando pipeline...")
        result = run_pipeline(
            query=request.question,
            mode=request.mode,
            temperature=request.temperature
        )
        logger.info("Pipeline completado exitosamente")
        return QueryResponse(**result)
    
    except Exception as e:
        logger.error(f"Error en pipeline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )










# =========================
# Endpoint health
# =========================

@app.get("/health")
def health_check():
    """
    Endpoint de health check para monitoreo del servicio.
    """
    logger.info("Health check ejecutado OK")
    return {
        "status": "ok",
        "service": "ZettelRAG"
    }

