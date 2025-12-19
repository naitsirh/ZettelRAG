"""
orchestrator.py

Módulo de orquestación del sistema ZettelRAG.

Responsabilidades:
- Clasificar la intención del usuario
- Decidir si una consulta requiere RAG o puede resolverse sin contexto
- Coordinar el flujo entre retrieval, construcción de contexto y generación
- Unificar la salida del pipeline en un formato consistente

Este módulo representa la capa de control cognitivo del sistema.
"""


from generation_router import generate_answer
from retrieval import retrieve_context
from build_context import build_context




# =========================
# Prompt de clasificación
# =========================

INTENT_SYSTEM_PROMPT = """Clasifica la intención del usuario.

Devuelve SOLO una palabra:
- chitchat
- consulta
- autor
"""










# =========================
# Clasificación de intención
# =========================

def classify_intent(query: str) -> str:
    """
    Clasifica la intención del usuario utilizando el LLM.

    La clasificación se realiza con temperatura cero para garantizar
    determinismo. El resultado controla el flujo completo del pipeline.

    Args:
        query (str): Consulta del usuario.

    Returns:
        str: Intención detectada ("chitchat", "consulta" o "autor").
    """

    intent = generate_answer(
        query=query,
        system_override=INTENT_SYSTEM_PROMPT,
        temperature=0.0,
    )
    return intent.lower().strip()




# =========================
# Pipeline principal
# =========================

def run_pipeline(query: str, mode: str, temperature: float):
    """
    Ejecuta el pipeline completo de respuesta según la intención detectada.

    Flujo general:
    1. Clasificar intención del usuario
    2. Si es chitchat → generación directa sin RAG
    3. Si no:
        - recuperación de contexto
        - construcción del prompt contextual
        - generación de respuesta grounded

    Args:
        query (str): Consulta del usuario.
        mode (str): Modo de generación ("consulta" o "autor").
        temperature (float): Nivel de aleatoriedad del modelo.

    Returns:
        dict: Resultado del pipeline con:
            - answer (str): Respuesta generada
            - sources (list[str]): Fuentes utilizadas
            - scores (list[float]): Scores de relevancia
            - grounded (bool): Indica si la respuesta está basada en contexto
    """

    intent = classify_intent(query)

    # -------------------------
    # Chitchat (sin RAG)
    # -------------------------
    if intent == "chitchat":
        answer = generate_answer(
            query=query,
            temperature=temperature,
        )
        return {
            "answer": answer,
            "sources": [],
            "scores": [],
            "grounded": False,
        }

    # -------------------------
    # RAG (consulta / autor)
    # -------------------------
    retrieval_result = retrieve_context(query)
    context = build_context(retrieval_result)

    answer = generate_answer(
        query=query,
        context=context,
        mode=mode,
        temperature=temperature,
    )

    return {
        "answer": answer,
        "sources": retrieval_result.get("sources", []),
        "scores": retrieval_result.get("scores", []),
        "grounded": bool(retrieval_result.get("chunks")),
    }
