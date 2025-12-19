import os
import markdown
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
from cohere import Client
import chromadb
from dotenv import load_dotenv


load_dotenv()  # Para cargar las claves de Cohere
print('hola')
