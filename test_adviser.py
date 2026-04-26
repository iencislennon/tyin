from dotenv import load_dotenv
from agent.advisor import advise

load_dotenv()

loan = {
    "bank": "Kaspi",
    "sum": 1_500_000,
    "annual_rate": 26.0,
    "months": 24,
}

analysis = {
    "monthly_payment": 80811.85,
    "total_payment": 1_939_484.41,
    "overpayment": 439_484.41,
    "similar_offers": [
        "Банк: Jusan Bank, Ставка: 21.8% - 37.0%, Сумма: до 8 000 000 тенге, Срок: до 60 месяцев",
        "Банк: Nurbank, Ставка: 23.5% - 38.2%, Сумма: до 7 000 000 тенге, Срок: до 60 месяцев",
        "Банк: Bank RBK, Ставка: 11% - 37%, Сумма: до 8 000 000 тенге, Срок: до 84 месяцев",
    ]
}

result = advise(loan, analysis)
print(result)