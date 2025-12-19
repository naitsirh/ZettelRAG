import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.retrieval import retrieve_context


if __name__ == "__main__":
    query = "ideas sobre conocimiento y escritura"
    result = retrieve_context(query)

    for i, chunk in enumerate(result["chunks"], 1):
        print(f"\n--- Chunk {i} ---")
        print(chunk[:300])
        print("Score:", result["scores"][i-1])
        print("Source:", result["sources"][i-1])
