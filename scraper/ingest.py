import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from scraper.runner import run_all
from data.bank_documents import (
    kaspi_bank, jusan_bank, bereke_bank,
    bank_rbk, vtb_bank, nurbank,
    alatau_city_bank, home_credit_bank
)


def get_manual_products() -> list[dict]:
    """Банки которые нельзя спарсить — берём из ручной базы"""
    manual_banks = [
        kaspi_bank, jusan_bank, bereke_bank,
        bank_rbk, vtb_bank, nurbank,
        alatau_city_bank, home_credit_bank
    ]
    products = []
    for bank in manual_banks:
        for p in bank["products"]:
            products.append({
                "bank": bank["bank"],
                "name": p["name"],
                "description": p.get("notes", ""),
                "annual_rate_min": p.get("annual_rate_min") or 0.0,
                "annual_rate_max": p.get("annual_rate_max") or 0.0,
                "max_sum": p.get("max_sum") or 0,
                "max_months": p.get("max_months") or 0,
            })
    return products


def ingest_to_chroma():
    print("Парсим ForteBank и Halyk...")
    scraped = run_all()

    print("\nДобавляем ручные данные...")
    manual = get_manual_products()
    print(f"  + {len(manual)} продуктов из ручной базы")

    all_products = scraped + manual
    print(f"\nВсего продуктов: {len(all_products)}")

    # Загружаем в Chroma
    client = chromadb.PersistentClient(path="./chroma_storage")
    try:
        client.delete_collection("banks")
    except:
        pass
    collection = client.create_collection("banks")

    documents, metadatas, ids = [], [], []

    for i, p in enumerate(all_products):
        doc_text = f"""
Банк: {p['bank']}
Продукт: {p['name']}
Ставка: {p.get('annual_rate_min')}% - {p.get('annual_rate_max')}%
Сумма: до {p.get('max_sum')} тенге
Срок: до {p.get('max_months')} месяцев
{p.get('description', '')}
        """.strip()

        metadata = {
            "bank": p["bank"],
            "product_name": p["name"],
            "annual_rate_min": float(p.get("annual_rate_min") or 0),
            "annual_rate_max": float(p.get("annual_rate_max") or 0),
            "max_sum": float(p.get("max_sum") or 0),
            "max_months": int(p.get("max_months") or 0),
        }

        documents.append(doc_text)
        metadatas.append(metadata)
        ids.append(f"product_{i}")

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✓ Загружено в Chroma: {len(documents)} продуктов")


if __name__ == "__main__":
    ingest_to_chroma()