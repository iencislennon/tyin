from agent.tools import calc_annuity_payment, calc_full_payment, calc_overpayment
from db.chromadb import get_collection

def analyze(loan: dict) -> dict:
    collection = get_collection()
    result = {}

    # считаем метрики только если есть все нужные данные
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

    # поиск в сhroma строим запрос из того что есть
    query_parts = []
    if loan.get("purpose") == "ипотека":
        query_text = "ипотека покупка жилья первоначальный взнос"
    elif loan.get("purpose") == "рефинансирование":
        query_text = "рефинансирование кредитов других банков"
    if loan.get("purpose"):
        query_parts.append(loan["purpose"])
    if loan.get("sum"):
        query_parts.append(f"сумма {loan['sum']} тенге")
    if loan.get("months"):
        query_parts.append(f"срок {loan['months']} месяцев")
    if loan.get("annual_rate"):
        query_parts.append(f"ставка {loan['annual_rate']}%")

    query_text = " ".join(query_parts) if query_parts else "кредит наличными"

    # фильтр по метаданным из того что есть
    where = {}
    if loan.get("collateral") is not None:
        where["collateral"] = loan["collateral"]

    results = collection.query(
        query_texts=[query_text],
        n_results=3,
        where=where if where else None
    )

    result["similar_offers"] = results["documents"][0]
    return result