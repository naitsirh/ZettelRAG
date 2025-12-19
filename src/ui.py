"""
ui.py

Interfaz gráfica de usuario (UI) para el sistema ZettelRAG.

Responsabilidades:
- Proveer una interfaz web simple para interactuar con la API FastAPI
- Enviar consultas al endpoint /query
- Mostrar la respuesta generada junto con información de grounding y fuentes

Esta UI no contiene lógica de negocio: actúa únicamente como cliente
de la API principal del sistema.
"""


import gradio as gr
import requests




# =========================
# Configuración
# =========================

API_URL = "http://127.0.0.1:8000/query"










# =========================
# Cliente de la API
# =========================

def query_api(question, mode, temperature):
    """
    Envía una consulta a la API FastAPI y retorna la respuesta formateada.

    Args:
        question (str): Pregunta del usuario.
        mode (str): Modo de generación ("consulta" o "autor").
        temperature (float): Nivel de aleatoriedad del modelo.

    Returns:
        str: Respuesta del sistema, incluyendo metadata de grounding.
    """

    payload = {
        "question": question,
        "mode": mode,
        "temperature": temperature
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        answer = data["answer"]
        sources = data.get("sources", [])
        grounded = data.get("grounded", False)

        sources_text = (
            "\n".join(f"- {s}" for s in sources)
            if sources else "Sin fuentes"
        )

        footer = (
            f"\n\n---\n"
            f"Grounded: {grounded}\n"
            f"Fuentes:\n{sources_text}"
        )

        return answer + footer

    except requests.exceptions.RequestException as e:
        return f"Error al consultar la API:\n{e}"










# =========================
# Construcción UI
# =========================

with gr.Blocks(title="ZettelRAG") as demo:
    gr.Markdown("# 🧠 ZettelRAG")
    gr.Markdown("Interfaz gráfica que consume la API FastAPI")

    question = gr.Textbox(
        label="Pregunta",
        placeholder="Escribí tu pregunta aquí...",
        lines=3
    )

    with gr.Row():
        mode = gr.Radio(
            choices=["consulta", "autor"],
            value="consulta",
            label="Modo"
        )
        temperature = gr.Slider(
            0.0, 1.0,
            value=0.2,
            step=0.05,
            label="Temperatura"
        )

    submit = gr.Button("Consultar")

    answer = gr.Textbox(
        label="Respuesta",
        lines=15
    )

    submit.click(
        fn=query_api,
        inputs=[question, mode, temperature],
        outputs=answer
    )




# =========================
# Entry point
# =========================

if __name__ == "__main__":
    demo.launch()
