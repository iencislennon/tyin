from dotenv import load_dotenv
from agent.analyst import analyze

load_dotenv()

test_cases = [
    {
        "bank": "Kaspi",
        "sum": 1_500_000,
        "annual_rate": 26.0,
        "months": 24,
        "collateral": False,
        "income_proof": None,
        "purpose": None,
    },
    {
        "bank": None,
        "sum": 3_000_000,
        "annual_rate": None,
        "months": 24,
        "collateral": False,
        "online": True,
        "purpose": None,
    },
    {
        "bank": None,
        "sum": None,
        "annual_rate": None,
        "months": None,
        "purpose": "ипотека",
        "collateral": None,
        "income_proof": False,
        "deposit": 20.0,
        "age": 28,
    },
]

for loan in test_cases:
    print(f"Входные данные: {loan}")
    result = analyze(loan)
    print(f"  Ежемесячный платёж: {result.get('monthly_payment')} тенге")
    print(f"  Общая сумма:        {result.get('total_payment')} тенге")
    print(f"  Переплата:          {result.get('overpayment')} тенге")
    print(f"  Похожие предложения:")
    for offer in result.get('similar_offers', []):
        print(f"    - {offer[:80]}...")
    print()