import chromadb
import os


def get_collection():
    # Путь к базе — от корня проекта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chroma_path = os.path.join(base_dir, "chroma_storage")

    client = chromadb.PersistentClient(path=chroma_path)

    try:
        collection = client.get_collection("banks")
        print(f"✓ Chroma: {collection.count()} продуктов в базе")
        return collection
    except Exception:
        raise RuntimeError(
            "База банков не найдена. Запусти: python scraper/ingest.py"
        )