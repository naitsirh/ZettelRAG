"""
ingestion.py

Módulo de ingestión de notas tipo Zettelkasten (Obsidian vault).

Responsabilidades:
- Leer recursivamente archivos Markdown (.md) desde un vault
- Dividir el contenido en chunks
- Generar embeddings localmente
- Persistir los embeddings y metadatos en ChromaDB

Este script se ejecuta de forma independiente para poblar o actualizar
la base vectorial utilizada por el sistema RAG.
"""


import os
import uuid
from dotenv import load_dotenv

import chromadb
from chromadb.config import Settings

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer










# =========================
# Configuración
# =========================

load_dotenv()

VAULT_PATH = r"C:\ruta\al\directorio\louis"

CHROMA_PATH = r"C:\ruta\al\directorio\ZettelRAG\vectorstore"

EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

CHUNK_SIZE = 2000
CHUNK_OVERLAP = 200
EMBED_BATCH_SIZE = 32










# =========================
# Inicialización
# =========================

print("Cargando modelo de embeddings...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_or_create_collection(
    name="zettelrag_notes"
)










# =========================
# Funciones
# =========================

def read_markdown_files(vault_path: str):
    """
    Lee recursivamente todos los archivos Markdown (.md) de un vault.

    Args:
        vault_path (str): Ruta al vault de Obsidian.

    Returns:
        list[tuple[str, str]]: Lista de tuplas (ruta_archivo, contenido).
    """
    notes = []

    for root, _, files in os.walk(vault_path):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        notes.append((file_path, f.read()))
                except Exception as e:
                    print(f"⚠️ Error leyendo {file_path}: {e}")

    print(f"📄 Notas encontradas: {len(notes)}")
    return notes




def process_and_store_notes(notes):
    """
    Procesa las notas del vault y las persiste en la base vectorial.

    Pasos:
    - Divide cada nota en chunks
    - Genera embeddings locales por batch
    - Almacena documentos, embeddings y metadatos en ChromaDB

    Args:
        notes (list[tuple[str, str]]): Lista de notas (ruta, contenido).
    """
    total_chunks = 0

    for note_path, note_text in notes:
        chunks = text_splitter.split_text(note_text)

        if not chunks:
            continue

        # Embeddings por batch
        embeddings = embedding_model.encode(
            chunks,
            batch_size=EMBED_BATCH_SIZE,
            show_progress_bar=False,
        ).tolist()

        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{
            "source_file": note_path
        } for _ in chunks]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

        total_chunks += len(chunks)
        print(f"✅ {note_path} → {len(chunks)} chunks")

    print(f"\n📦 Total chunks almacenados: {total_chunks}")










# =========================
# Main
# =========================

def main():
    """
    Punto de entrada del script de ingestión.

    Ejecuta la lectura del vault, el procesamiento de notas
    y la persistencia en la base vectorial.
    """
    notes = read_markdown_files(VAULT_PATH)
    process_and_store_notes(notes)

    print("\nVector store persistido correctamente.")
    print(f"Embedding model: {EMBEDDING_MODEL_NAME} ({EMBEDDING_DIM} dims)")


if __name__ == "__main__":
    main()
