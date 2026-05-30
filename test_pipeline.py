from dotenv import load_dotenv
from agent.pipeline import run_pipeline

load_dotenv()

test_cases = [
    "Kaspi предлагает 1.5M на 24 мес под 26%, стоит брать?",
    "Хочу взять ипотеку без справки о доходах, первоначальный взнос 20%",
    "Стоит ли брать кредит?",  # не хватает данных
]

for text in test_cases:
    print(f"Вопрос: {text}")
    print(f"Ответ: {run_pipeline(text)}")
    print("-" * 60)
    print("111")