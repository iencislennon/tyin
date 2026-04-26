from agent.extractor import extract_loan_data
from agent.analyst import analyze
from agent.advisor import advise

def run_pipeline(user_text: str) -> str:
    loan = extract_loan_data(user_text)
    loan_dict = loan.model_dump()

    # Достаточно хотя бы одного значимого поля чтобы продолжить
    has_enough = any([
        loan_dict.get("sum"),
        loan_dict.get("annual_rate"),
        loan_dict.get("purpose"),
        loan_dict.get("collateral") is not None,
        loan_dict.get("income_proof") is not None,
        loan_dict.get("deposit"),
    ])

    if not has_enough:
        return "Расскажите подробнее — какой кредит вас интересует? Укажите сумму, срок, цель или другие параметры."

    analysis = analyze(loan_dict)
    advice = advise(loan_dict, analysis)
    return advice