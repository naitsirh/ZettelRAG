import sys
from pathlib import Path

# Agregar root del proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.build_context import build_context



if __name__ == "__main__":
    fake_retrieval_result = {
        "chunks": [
            "El conocimiento se construye a través de la escritura reflexiva.",
            "La toma de notas mejora la comprensión profunda."
        ],
        "scores": [0.42, 0.37],
        "sources": [
            "nota_conocimiento.md",
            "nota_escritura.md"
        ]
    }

    context = build_context(fake_retrieval_result)
    print(context)
