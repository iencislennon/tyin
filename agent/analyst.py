from agent.tools import calc_annuity_payment, calc_full_payment, calc_overpayment
from data.bank_documents import all_banks

def _get_all_products():
    products = []
    
    # Сначала пробуем спаршенные данные
    try:
        from data.scraped_banks import scraped_banks
        for p in scraped_banks:
            products.append({"bank": p, "products": [p]})
    except ImportError:
        pass
    
    # Всегда добавляем ручные данные
    from data.bank_documents import all_banks
    products.extend(all_banks)
    
    return products

def _keyword_search(loan: dict, n: int = 3) -> list[str]:
    """Простой keyword поиск по банкам без векторной модели"""
    purpose = (loan.get("purpose") or "").lower()
    collateral = loan.get("collateral")
    max_sum = loan.get("sum") or 0
    max_months = loan.get("months") or 0

    scored = []
    for bank in all_banks:
        for product in bank["products"]:
            score = 0
            name = product["name"].lower()
            notes = (product.get("notes") or "").lower()

            # Совпадение по цели
            if purpose:
                if purpose in name or purpose in notes:
                    score += 3
                if "ипотек" in purpose and "ипотек" in name:
                    score += 5
                if "рефинансир" in purpose and "рефинансир" in name:
                    score += 5
                if "авто" in purpose and "авто" in name:
                    score += 5

            # Совпадение по залогу
            if collateral is not None:
                if product.get("collateral") == collateral:
                    score += 2

            # Совпадение по сумме
            if max_sum and product.get("max_sum"):
                if product["max_sum"] >= max_sum:
                    score += 1

            # Совпадение по сроку
            if max_months and product.get("max_months"):
                if product["max_months"] >= max_months:
                    score += 1

            doc_text = f"""Банк: {bank['bank']}
Продукт: {product['name']}
Ставка: {product['annual_rate_min']}% - {product['annual_rate_max']}%
Сумма: до {product['max_sum']} тенге
Срок: до {product['max_months']} месяцев
Залог: {'нет' if not product['collateral'] else 'требуется'}
{product.get('notes', '')}""".strip()

            scored.append((score, doc_text))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:n]]


def analyze(loan: dict) -> dict:
    result = {}

    if loan.get("sum") and loan.get("annual_rate") and loan.get("months"):
        monthly = calc_annuity_payment.invoke({
            "credit_sum": loan["sum"],
            "annual_rate": loan["annual_rate"],
            "months": loan["months"]
        })
        total = calc_full_payment.invoke({
            "principal": loan["sum"],
            "annual_rate": loan["annual_rate"],
            "months": loan["months"]
        })
        overpayment = calc_overpayment.invoke({
            "principal": loan["sum"],
            "annual_rate": loan["annual_rate"],
            "months": loan["months"]
        })
        result["monthly_payment"] = round(monthly, 2)
        result["total_payment"] = round(total, 2)
        result["overpayment"] = round(overpayment, 2)
    else:
        result["monthly_payment"] = None
        result["total_payment"] = None
        result["overpayment"] = None

    result["similar_offers"] = _keyword_search(loan)
    return result