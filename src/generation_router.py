"""
generation_router.py

Router de generación de respuestas mediante LLM.

Responsabilidades:
- Centralizar la interacción con el modelo de lenguaje
- Seleccionar dinámicamente el system prompt según el contexto de uso
- Permitir overrides explícitos del system prompt (ej. clasificación de intención)
- Unificar generación directa y generación basada en RAG

Este módulo actúa como capa intermedia entre el orquestador
y el modelo de lenguaje.
"""


import cohere
from dotenv import load_dotenv




# =========================
# Inicialización
# =========================

load_dotenv()  # Cargar variables de entorno (incluye COHERE_API_KEY)
co = cohere.ClientV2()




# =========================
# System prompts
# =========================

SYSTEM_PROMPT_BASE = """Eres un asistente intelectual que responde utilizando exclusivamente el contenido proporcionado.

REGLAS OBLIGATORIAS:
- Responde siempre en español.
- No utilices emojis.
- No inventes información.
- Sé claro y preciso.
"""

SYSTEM_PROMPT_RAG = SYSTEM_PROMPT_BASE + """
- Usa únicamente la información del CONTEXTO.
- Si el contexto no es suficiente, indícalo claramente.
- La misma pregunta debe generar la misma respuesta.
"""




# =========================
# User prompts
# =========================

PROMPT_CONSULTA = """Tu tarea es responder la pregunta del usuario de forma clara y sintética.

- Resume las ideas relevantes.
- No extiendas innecesariamente la respuesta.
"""

PROMPT_AUTOR = """Tu tarea es ayudar a organizar el conocimiento para la escritura de un libro.

- Agrupa las ideas presentes en el contexto.
- Propón una posible estructura de capítulos.
- Para cada capítulo, redacta un breve resumen.
- No escribas texto final de libro.
- No agregues ideas que no estén en el contexto.
"""










# =========================
# Función principal
# =========================

def generate_answer(
    query: str,
    context: str = "",
    mode: str = "consulta",
    temperature: float = 0.2,
    system_override: str | None = None,
):
    """
    Genera una respuesta utilizando un modelo de lenguaje, con soporte
    para generación directa o basada en RAG.

    Comportamiento:
    - Si `system_override` está presente, se utiliza como system prompt
      y se ignoran los prompts estándar.
    - Si no hay override, se aplica el sistema de prompts RAG
      y el modo de generación ("consulta" o "autor").

    Args:
        query (str): Consulta del usuario.
        context (str, optional): Contexto textual (RAG).
        mode (str, optional): Modo de generación ("consulta" o "autor").
        temperature (float, optional): Nivel de aleatoriedad del modelo.
        system_override (str | None, optional): Prompt de sistema alternativo.

    Returns:
        str: Texto generado por el modelo de lenguaje.
    """

    # --------------------------
    # Selección de system prompt
    # --------------------------
    if system_override:
        system_prompt = system_override
        mode_prompt = ""
    else:
        system_prompt = SYSTEM_PROMPT_RAG
        mode_prompt = PROMPT_AUTOR if mode == "autor" else PROMPT_CONSULTA

    # ----------------------------
    # Construcción del user prompt
    # ----------------------------
    if context:
        user_content = (
            "CONTEXTO:\n"
            f"{context}\n\n"
            "PREGUNTA:\n"
            f"{query}\n\n"
            f"{mode_prompt}"
        )
    else:
        user_content = query

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    response = co.chat(
        model="command-r-plus-08-2024",
        messages=messages,
        temperature=temperature,
    )

    return response.message.content[0].text.strip()
