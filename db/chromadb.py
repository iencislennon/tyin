
import chromadb
from data.bank_documents import all_banks

def get_collection():
    client = chromadb.PersistentClient(path="./chroma_storage")  # сохраняется на диск!
    
    # если коллекция уже есть — просто возвращаем, не пересоздаём
    try:
        return client.get_collection("banks")
    except:
        collection = client.create_collection("banks")
        _load_banks(collection)
        return collection

def _load_banks(collection):
    documents, metadatas, ids = [], [], []
    for bank in all_banks:
        for i, product in enumerate(bank["products"]):  # "products" не "prodcts" — опечатка у тебя
            doc_text = f"""
            Банк: {bank['bank']}
            Продукт: {product['name']}
            Цель: {product['purpose']}
            Ставка: {product['annual_rate_min']}% - {product['annual_rate_max']}%
            ГЭСВ: {product['gesv_min']}% - {product['gesv_max']}%
            Сумма: от {product['min_sum']} до {product['max_sum']} тенге
            Срок: от {product['min_months']} до {product['max_months']} месяцев
            Залог: {'нет' if not product['collateral'] else 'требуется'}
            Справка о доходах: {'не нужна' if not product['income_proof'] else 'нужна'}
            Комиссия: {product['commission']}
            Досрочное погашение: {product['early_repayment']}
            Документы: {', '.join(product['documents'])}
            {product['notes']}"""
        #Метаданные — для точной фильтрации (chroma принимает только str/int/float/bool)
        metadata = {
            "bank": bank["bank"],
            "product_name": product["name"],
            "annual_rate_min": product["annual_rate_min"] or 0.0,
            "annual_rate_max": product["annual_rate_max"] or 0.0,
            "max_sum": product["max_sum"] or 0,
            "max_months": product["max_months"] or 0,
            "collateral": product["collateral"],
            "income_proof": product["income_proof"] or False,
            "online": product["online"],
        }
        documents.append(doc_text.strip())
        metadatas.append(metadata)
        ids.append(f"{bank['bank']}_{i}")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)