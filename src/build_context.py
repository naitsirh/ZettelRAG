"""
build_context.py

Módulo de construcción de contexto para el sistema ZettelRAG.

Responsabilidad:
- Transformar el resultado estructurado de la recuperación (chunks, scores,
  fuentes) en un bloque de texto coherente que será inyectado en el prompt
  del modelo de lenguaje.

Este módulo actúa como puente entre retrieval y generación, y define
explícitamente el formato del contexto consumido por el LLM.
"""


def build_context(retrieval_result: dict) -> str:
    """
    Construye el contexto textual para el LLM a partir del resultado
    de retrieval + reranking.

    El contexto incluye:
    - Una sección de fuentes
    - Una sección de contenido relevante, con scores de similitud

    Args:
        retrieval_result (dict): Resultado de `retrieve_context`, que contiene
            chunks, scores y fuentes.

    Returns:
        str: Texto formateado listo para ser inyectado en el prompt.
    """

    chunks = retrieval_result.get("chunks", [])
    sources = retrieval_result.get("sources", [])
    scores = retrieval_result.get("scores", [])

    # Caso sin contexto
    if not chunks:
        return (
            "No se encontró información relevante en la base de conocimiento "
            "para responder la pregunta."
        )

    context_lines = []

    # -------------------------
    # Sección fuentes
    # -------------------------
    context_lines.append("FUENTES:")

    for idx, source in enumerate(sources, start=1):
        context_lines.append(f"[{idx}] {source}")

    # -------------------------
    # Sección contenido
    # -------------------------
    context_lines.append("\nCONTENIDO RELEVANTE:")

    for idx, (chunk, score) in enumerate(zip(chunks, scores), start=1):
        context_lines.append(f"[{idx}] (relevancia: {score})")
        context_lines.append(chunk.strip())
        context_lines.append("")  # línea en blanco

    return "\n".join(context_lines)
