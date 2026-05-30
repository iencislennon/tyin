# tyin.ai — Кредитный AI-советник для Казахстана

Независимый финансовый советник на базе AI. Анализирует кредитные предложения банков РК, считает платежи и переплату, сравнивает с рынком.

---

## Живой URL

```
https://web-production-b601d.up.railway.app
```

---

## Архитектура

### Multi-agent pipeline

```
Запрос пользователя
        ↓
  [Extractor]         — понимает текст, извлекает параметры кредита
        ↓
  [Analyst]           — считает аннуитет, ищет похожие предложения
        ↓
  [Advisor]           — GPT-4 формирует финальный совет
        ↓
    Ответ (streaming)
```

### Стек

| Компонент | Технология |
|-----------|-----------|
| API | FastAPI + uvicorn |
| AI | OpenAI GPT-4 Turbo |
| LLM Framework | LangChain |
| База данных | PostgreSQL (SQLAlchemy) |
| Поиск по банкам | Keyword search (без векторной БД) |
| Деплой | Railway |
| Автопарсер | GitHub Actions (каждый понедельник) |
| Мониторинг | Sentry |
| Rate limiting | slowapi (15 req/min) |

### Структура проекта

```
creditagent/
├── api.py                    # FastAPI приложение, endpoints
├── index.html                # Веб-интерфейс чата
├── Procfile                  # web: uvicorn api:app --host 0.0.0.0 --port $PORT
├── requirements.txt
├── .env                      # локальные переменные (не в git)
│
├── agent/
│   ├── pipeline.py           # оркестрация агентов, история чатов
│   ├── extractor.py          # Агент 1: извлечение параметров кредита
│   ├── analyst.py            # Агент 2: расчёты + поиск по банкам
│   ├── advisor.py            # Агент 3: GPT-4 советник
│   └── tools.py              # калькуляторы аннуитета, переплаты
│
├── database/
│   ├── __init__.py
│   └── models.py             # SQLAlchemy модели + функции save/get
│
├── data/
│   ├── bank_documents.py     # ручные данные 10 банков
│   └── scraped_banks.py      # автогенерируется парсером (не редактировать)
│
├── scraper/
│   ├── base.py               # базовый класс парсера
│   ├── forte.py              # парсер ForteBank
│   ├── halyk.py              # парсер Halyk Bank (Playwright)
│   ├── cleaner.py            # очистка данных
│   ├── runner.py             # запуск всех парсеров
│   ├── ingest.py             # загрузка в базу
│   └── update_bank_docs.py   # обновление scraped_banks.py
│
├── db/
│   └── chromadb.py           # (устарел, не используется)
│
└── .github/
    └── workflows/
        └── update_banks.yml  # GitHub Actions автопарсер
```

---

## API

### POST /ask

Основной эндпоинт. Возвращает streaming SSE ответ.

**Request:**
```json
{
  "text": "Kaspi предлагает 1.5M на 24 мес под 26%, стоит брать?",
  "user_id": "user_abc123"
}
```

**Response (Server-Sent Events):**
```
data: {"chunk": "Ежемесячный платёж"}
data: {"chunk": " составит 80,811 тг..."}
data: [DONE]
```

**Пример curl:**
```bash
curl -X POST https://web-production-b601d.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"text": "Kaspi 1.5M на 24 мес под 26%", "user_id": "test"}'
```

### GET /health

Проверка работоспособности.

**Response:**
```json
{"status": "ok", "version": "1.0.0"}
```

---

## База данных

### Таблицы PostgreSQL

**chat_history**
```sql
id          SERIAL PRIMARY KEY
user_id     VARCHAR(100)
role        VARCHAR(20)    -- 'user' или 'assistant'
message     TEXT
created_at  TIMESTAMP
```

**real_cases** (для будущей монетизации)
```sql
id              SERIAL PRIMARY KEY
user_id         VARCHAR(100)
bank            VARCHAR(100)
requested_sum   INTEGER
approved        VARCHAR(10)   -- 'yes' / 'no'
real_rate       VARCHAR(20)
created_at      TIMESTAMP
```

---

## Деплой

### Railway

Проект: `enthusiastic-achievement`
Сервисы: `web` (FastAPI) + `Postgres`

**Переменные окружения (web сервис):**
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:PORT/railway
SENTRY_DSN=https://...@sentry.io/...   (опционально)
```

**Автодеплой:** при каждом `git push origin main` Railway автоматически пересобирает и деплоит.

**Procfile:**
```
web: uvicorn api:app --host 0.0.0.0 --port $PORT
```

### Локальный запуск

```bash
# 1. Клонировать репо
git clone https://github.com/iencislennon/tyin.git
cd tyin

# 2. Создать виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# 3. Установить зависимости
pip install -r requirements.txt
playwright install chromium

# 4. Создать .env
cat > .env << EOF
OPENAI_API_KEY=sk-твой_ключ
DATABASE_URL=postgresql://postgres:пароль@localhost:5433/tyinDB
EOF

# 5. Инициализировать БД
python -c "from database.models import init_db; init_db()"

# 6. Запустить сервер
uvicorn api:app --reload
```

---

## Автопарсер банков

GitHub Actions запускает парсер каждый **понедельник в 6:00 UTC**.

**Что происходит:**
1. Playwright парсит сайты ForteBank и Halyk Bank
2. Данные сохраняются в `data/scraped_banks.py`
3. Коммит пушится в репо
4. Railway автоматически передеплоится с новыми данными

**Запустить вручную:**
GitHub → Actions → Update Bank Data → Run workflow

**Локальный запуск парсера:**
```bash
python scraper/runner.py
```

---

## Данные банков

Сейчас в базе **10 банков, 18+ продуктов**:

| Банк | Источник | Тип |
|------|----------|-----|
| ForteBank | Автопарсер | Потреб, ипотека, авто |
| Halyk Bank | Автопарсер | Потреб, ипотека, рефинанс |
| Kaspi Bank | Ручные данные | Потреб |
| Jusan Bank | Ручные данные | Потреб |
| Bank RBK | Ручные данные | Потреб |
| Bereke Bank | Ручные данные | Потреб |
| Nurbank | Ручные данные | Потреб |
| Home Credit | Ручные данные | Потреб |
| VTB Kazakhstan | Ручные данные | Потреб |
| Alatau City Bank | Ручные данные | Потреб |

---

## Что осталось сделать

```
☐ Flutter мобильное приложение
☐ Кнопка "Одобрили / Отказали" → запись в real_cases
☐ Kaspi данные — обновить вручную (сайт не парсится)
☐ ГЭСВ в расчётах — добавить в tools.py
☐ Партнёрские ссылки на заявки в банки
☐ Подписка / монетизация
```

---

## Контакты

Разработчик AI части: Ansar Tleubayev
Репо: https://github.com/iencislennon/tyin
