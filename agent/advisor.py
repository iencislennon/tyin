from langchain.chat_models import init_chat_model

def advise(loan: dict, analysis: dict, original_question: str = "", history: list = []) -> str:
    model = init_chat_model("gpt-4-turbo")

    # Форматируем историю для контекста
    history_text = ""
    if history:
        history_text = "\nИстория разговора:\n"
        for msg in history:
            role = "Пользователь" if msg["role"] == "user" else "Ассистент"
            history_text += f"{role}: {msg['content']}\n"

    prompt = f"""Ты — tyin.ai, независимый финансовый советник по кредитам Казахстана.
Твоя цель — защищать интересы пользователя, а не банков.
{history_text}
ВОПРОС ПОЛЬЗОВАТЕЛЯ: "{original_question}"

ДАННЫЕ ДЛЯ АНАЛИЗА:
- Параметры займа: {loan}
- Расчёты: ежемесячный платёж {analysis.get('monthly_payment')} тг, переплата {analysis.get('overpayment')} тг
- Похожие предложения банков: {analysis.get('similar_offers', [])}

ИНСТРУКЦИИ:

Если это КРЕДИТНЫЙ ЗАПРОС (есть сумма/ставка/банк):
— Начни с конкретных цифр: платёж X тг/мес, переплата Y тг
— Оцени выгодность: сравни ставку со средней по рынку РК (20-30% потреб, 7-15% ипотека)
— Найди лучшую альтернативу из похожих предложений и назови конкретный банк
— Дай чёткую рекомендацию: БРАТЬ / НЕ БРАТЬ / СРАВНИТЬ С X
— Укажи на что обратить внимание: ГЭСВ, комиссии, досрочное погашение

Если это ОБЩИЙ ФИНАНСОВЫЙ ВОПРОС (про банки, кредиты, ипотеку, ГЭСВ и т.д.):
— Дай развёрнутый полезный ответ с примерами
— Используй знания о рынке Казахстана (ставки, банки, программы 7-20-25, Отбасы)
— Будь конкретным, избегай общих фраз

Если НЕРЕЛЕВАНТНЫЙ ВОПРОС (не про финансы):
— Одно предложение: объясни специализацию
— Предложи финансовый вопрос

СТИЛЬ:
— Русский язык, без воды
— Цифры выделяй жирным (**80,811 тг**)
— Максимум 3-4 абзаца
— Заканчивай конкретным советом или вопросом"""
    response = model.invoke([{"role": "user", "content": prompt}])
    return response.content

def advise_stream(loan: dict, analysis: dict, original_question: str = "", history: list = []):
    from langchain_openai import ChatOpenAI
    
    model = ChatOpenAI(model="gpt-4-turbo", streaming=True)
    
    history_text = ""
    if history:
        history_text = "\nИстория разговора:\n"
        for msg in history:
            role = "Пользователь" if msg["role"] == "user" else "Ассистент"
            history_text += f"{role}: {msg['content']}\n"

    prompt = f"""Ты — финансовый AI-ассистент tyin.ai для рынка кредитов Казахстана.
{history_text}
Текущий вопрос: "{original_question}"
Параметры займа: {loan}
Финансовый анализ: {analysis}
Похожие предложения: {analysis.get('similar_offers', [])}

Правила:
1. КРЕДИТНЫЙ ЗАПРОС — конкретный анализ с цифрами, сравни с альтернативами
2. ОБЩИЙ ФИНАНСОВЫЙ ВОПРОС — развёрнутый ответ про рынок Казахстана
3. НЕРЕЛЕВАНТНЫЙ ВОПРОС — коротко объясни специализацию

Отвечай на русском языке."""

    for chunk in model.stream([{"role": "user", "content": prompt}]):
        if chunk.content:
            yield chunk.content