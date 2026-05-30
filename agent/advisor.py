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

    prompt = f"""
Ты — финансовый AI-ассистент tyin.ai для рынка кредитов Казахстана.
{history_text}
Текущий вопрос: "{original_question}"

Параметры займа: {loan}
Финансовый анализ: {analysis}
Похожие предложения: {analysis.get('similar_offers', [])}

Правила:
1. КРЕДИТНЫЙ ЗАПРОС — конкретный анализ с цифрами, сравни с альтернативами
2. ОБЩИЙ ФИНАНСОВЫЙ ВОПРОС — развёрнутый ответ про рынок Казахстана
3. НЕРЕЛЕВАНТНЫЙ ВОПРОС — коротко объясни специализацию, предложи финансовый вопрос
4. Учитывай контекст предыдущих вопросов если он есть

Отвечай на русском языке.
"""
    response = model.invoke([{"role": "user", "content": prompt}])
    return response.content