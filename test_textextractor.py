from dotenv import load_dotenv
from agent.extractor import extract_loan_data

load_dotenv()

test_cases = [
    "Kaspi предлагает 1.5M на 24 мес под 26%, стоит брать?",
    "Хочу взять ипотеку без справки о доходах, первоначальный взнос 20%, мне 28 лет",
    "Ищу кредит онлайн без залога на 2 года, сумма 3 миллиона",
    "Halyk даёт кредит под 17.5% на 5 лет, сумма 2 миллиона, планирую досрочно погасить",
    "Хочу рефинансировать кредит другого банка, сумма 5 млн, справки о доходах нет",
    "Стоит ли брать кредит?",  # не хватает данных
]

for text in test_cases:
    print(f"Вопрос: {text}")
    result = extract_loan_data(text)
    print(f"  bank:           {result.bank}")
    print(f"  sum:            {result.sum}")
    print(f"  annual_rate:    {result.annual_rate}")
    print(f"  months:         {result.months}")
    print(f"  purpose:        {result.purpose}")
    print(f"  collateral:     {result.collateral}")
    print(f"  income_proof:   {result.income_proof}")
    print(f"  deposit:        {result.deposit}")
    print(f"  age:            {result.age}")
    print(f"  online:         {result.online}")
    print(f"  early_repayment:{result.early_repayment}")
    print()