import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "faiss_index")

print("🔄 Initializing RAG...")

db = None
embeddings = None


def load_rag():
    global db, embeddings

    # If already loaded, return immediately
    if db is not None:
        return db

    try:
        print("⏳ Loading RAG model...")

        # Load embedding model
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        # Load FAISS database
        db = FAISS.load_local(
            DB_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

        print("✅ RAG Model Loaded")

    except Exception as e:
        print("⚠️ RAG Load Failed (will retry later):", e)
        db = None

    return db


def query_rag(query):
    try:
        db_instance = load_rag()

        if db_instance is None:
            return None

        # Perform similarity search
        results = db_instance.similarity_search(query, k=1)

        if results:
            return results[0].page_content.strip()

        return None

    except Exception as e:
        print("❌ RAG Error:", e)
        return None