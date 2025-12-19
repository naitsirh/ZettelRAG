import sys
from pathlib import Path

# Agregar root del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.retrieval import retrieve_context
from src.build_context import build_context
from src.generation import generate_answer



if __name__ == "__main__":
    query = "ideas sobre conocimiento y escritura"

    retrieval_result = retrieve_context(query)
    context = build_context(retrieval_result)

    answer = generate_answer(
        query=query,
        context=context,
        mode="consulta",
        temperature=0.2
    )

    print("\n=== RESPUESTA ===\n")
    print(answer)
