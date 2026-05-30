import chromadb
import os

def get_collection():
    # На Railway используем in-memory, локально persistent
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        client = chromadb.EphemeralClient()
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chroma_path = os.path.join(base_dir, "chroma_storage")
        client = chromadb.PersistentClient(path=chroma_path)

    try:
        collection = client.get_collection("banks")
        print(f"✓ Chroma: {collection.count()} продуктов в базе")
        return collection
    except Exception:
        print("⚡ Создаём базу банков...")
        collection = client.create_collection("banks")
        _load_banks(collection)
        print(f"✓ Chroma: {collection.count()} продуктов загружено")
        return collection

def _load_banks(collection):
    from data.bank_documents import all_banks
    documents, metadatas, ids = [], [], []

    for bank in all_banks:
        for i, product in enumerate(bank["products"]):
            doc_text = f"""
Банк: {bank['bank']}
Продукт: {product['name']}
Ставка: {product['annual_rate_min']}% - {product['annual_rate_max']}%
Сумма: от {product['min_sum']} до {product['max_sum']} тенге
Срок: от {product['min_months']} до {product['max_months']} месяцев
Залог: {'нет' if not product['collateral'] else 'требуется'}
{product['notes']}""".strip()

            metadata = {
                "bank": bank["bank"],
                "product_name": product["name"],
                "annual_rate_min": float(product["annual_rate_min"] or 0),
                "annual_rate_max": float(product["annual_rate_max"] or 0),
                "max_sum": float(product["max_sum"] or 0),
                "max_months": int(product["max_months"] or 0),
                "collateral": bool(product["collateral"]),
                "income_proof": bool(product.get("income_proof") or False),
                "online": bool(product.get("online") or False),
            }

            documents.append(doc_text)
            metadatas.append(metadata)
            ids.append(f"{bank['bank']}_{i}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)