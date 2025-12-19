import sys
from pathlib import Path

# Agregar root del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.generation import generate_answer


if __name__ == "__main__":
    query = "¿Qué ideas aparecen sobre el método socrático?"

    context = """
The Socratic ethic can also help explain a certain kind of life story.
Some people spend years struggling with hard questions and never quite
find peace about them.
"""

    answer = generate_answer(
        query=query,
        context=context,
        mode="consulta",
        temperature=0.2
    )

    print("\n=== RESPUESTA ===\n")
    print(answer)
