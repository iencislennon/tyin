from agent.extractor import extract_loan_data
from agent.analyst import analyze
from agent.advisor import advise
from database.models import save_message, get_history
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
) # 1 more time?
def run_pipeline(user_text: str, user_id: str = "default") -> str:

    # История из PostgreSQL
    history = get_history(user_id, limit=6)

    try:
        loan = extract_loan_data(user_text)
        loan_dict = loan.model_dump()
    except Exception as e:
        logging.error(f"Extractor error: {e}")
        loan_dict = {}

    try:
        has_enough = any([
            loan_dict.get("sum"),
            loan_dict.get("annual_rate"),
            loan_dict.get("purpose"),
            loan_dict.get("collateral") is not None,
            loan_dict.get("income_proof") is not None,
            loan_dict.get("deposit"),
            loan_dict.get("bank"),
        ])
        analysis = analyze(loan_dict) if has_enough else {
            "monthly_payment": None,
            "total_payment": None,
            "overpayment": None,
            "similar_offers": []
        }
    except Exception as e:
        logging.error(f"Analyst error: {e}")
        analysis = {"monthly_payment": None, "total_payment": None, "overpayment": None, "similar_offers": []}

    try:
        advice = advise(loan_dict, analysis, user_text, history)
    except Exception as e:
        logging.error(f"Advisor stream error: {e}")
        yield "Сервис временно недоступен. Попробуйте через несколько минут."

    # Сохраняем в PostgreSQL
    save_message(user_id, "user", user_text)
    save_message(user_id, "assistant", advice)

    logging.info(f"user={user_id} q={user_text[:50]}")

    return advice


def run_pipeline_stream(user_text: str, user_id: str = "default"):
    history = get_history(user_id, limit=6)

    try:
        loan = extract_loan_data(user_text)
        loan_dict = loan.model_dump()
    except Exception as e:
        logging.error(f"Extractor error: {e}")
        loan_dict = {}

    try:
        has_enough = any([
            loan_dict.get("sum"), loan_dict.get("annual_rate"),
            loan_dict.get("purpose"), loan_dict.get("bank"),
        ])
        analysis = analyze(loan_dict) if has_enough else {
            "monthly_payment": None, "total_payment": None,
            "overpayment": None, "similar_offers": []
        }
    except Exception as e:
        logging.error(f"Analyst error: {e}")
        analysis = {"monthly_payment": None, "total_payment": None,
                    "overpayment": None, "similar_offers": []}

    full_response = ""
    try:
        for chunk in advise_stream(loan_dict, analysis, user_text, history):
            full_response += chunk
            yield chunk
    except Exception as e:
        logging.error(f"Advisor stream error: {e}")
        yield "Произошла ошибка. Попробуйте ещё раз."
        return

    save_message(user_id, "user", user_text)
    save_message(user_id, "assistant", full_response)
    logging.info(f"user={user_id} q={user_text[:50]}")