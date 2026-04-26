from langchain.chat_models import init_chat_model
from pydantic import BaseModel
from typing import Optional

class LoanData(BaseModel):
    # Основные параметры — парсятся из текста пользователя
    bank: Optional[str] = None
    product_name: Optional[str] = None
    purpose: Optional[str] = None
    sum: Optional[float] = None
    annual_rate: Optional[float] = None
    months: Optional[int] = None

    # Дополнительные параметры
    collateral: Optional[bool] = None        # есть залог или нет
    income_proof: Optional[bool] = None      # нужна справка о доходах
    deposit: Optional[float] = None          # первоначальный взнос в %
    age: Optional[int] = None                # возраст заёмщика
    online: Optional[bool] = None            # хочет оформить онлайн
    early_repayment: Optional[bool] = None   # планирует досрочное погашение

def extract_loan_data(user_text: str) -> LoanData:
    model = init_chat_model("gpt-4o-mini").with_structured_output(LoanData, method="function_calling")
    result = model.invoke([
        {"role": "system", "content": """Извлеки параметры кредита из текста пользователя и верни JSON.

Правила извлечения:
- bank: название банка если упомянуто
- sum: сумма кредита в числовом виде (1.5M = 1500000, 2 миллиона = 2000000)
- annual_rate: годовая ставка в процентах
- months: срок в месяцах (2 года = 24, 5 лет = 60)
- purpose: цель кредита — например "ипотека", "автокредит", "рефинансирование", "наличные"
- collateral: true если есть залог или упомянута недвижимость/авто как залог, false если "без залога"
- income_proof: false если "без справки", "без подтверждения дохода", true если упомянута справка
- deposit: первоначальный взнос в процентах если упомянут
- age: возраст заёмщика если упомянут
- online: true если хочет оформить онлайн
- early_repayment: true если планирует досрочное погашение

Если поле не упомянуто — верни null.
"""},
        {"role": "user", "content": user_text}
    ])
    return result