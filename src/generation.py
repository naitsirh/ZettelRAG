"""
generation.py

Módulo de generación de respuestas mediante un modelo de lenguaje (Cohere).

Responsabilidades:
- Definir el sistema de prompts y reglas de comportamiento del asistente
- Construir el mensaje final a partir de la consulta y el contexto recuperado
- Invocar al LLM para generar una respuesta controlada y consistente

Este módulo asume que todo el conocimiento relevante ya fue recuperado
y preparado previamente (RAG). El modelo no debe inferir ni inventar
información fuera del contexto proporcionado.
"""


from dotenv import load_dotenv
import cohere
import os

load_dotenv()  # Cargar variables de entorno (incluye COHERE_API_KEY)
co = cohere.ClientV2()



SYSTEM_PROMPT = """Eres un asistente intelectual que responde utilizando exclusivamente el contenido proporcionado.

REGLAS OBLIGATORIAS:
- Responde siempre en español.
- No utilices emojis.
- Usa únicamente la información del CONTEXTO.
- No inventes información.
- Si el contexto no es suficiente, indícalo claramente.
- La misma pregunta debe generar la misma respuesta.
- Sé claro, preciso y sobrio.
"""

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



def generate_answer(query, context, mode="consulta", temperature=0.2):
    """
    Genera una respuesta del LLM a partir de una consulta y un contexto dado.

    La función utiliza un sistema de prompts restrictivo para garantizar que
    la respuesta:
    - se base exclusivamente en el contexto proporcionado
    - no introduzca información inventada
    - sea reproducible para la misma entrada

    Args:
        query (str): Pregunta del usuario.
        context (str): Contexto textual construido a partir del retrieval.
        mode (str, optional): Modo de generación.
            - "consulta": respuesta directa y sintética
            - "autor": organización conceptual para escritura
        temperature (float, optional): Nivel de aleatoriedad del modelo.

    Returns:
        str: Respuesta generada por el modelo de lenguaje.
    """

    if mode == "autor":
        mode_prompt = PROMPT_AUTOR
    else:
        mode_prompt = PROMPT_CONSULTA

    user_content = (
        "CONTEXTO:\n"
        f"{context}\n\n"
        "PREGUNTA:\n"
        f"{query}\n\n"
        f"{mode_prompt}"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content}
    ]

    response = co.chat(
        model="command-r-plus-08-2024",
        messages=messages,
        temperature=temperature
    )

    return response.message.content[0].text.strip()
