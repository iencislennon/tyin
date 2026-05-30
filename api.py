import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from agent.pipeline import run_pipeline
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging

load_dotenv()

from fastapi.responses import StreamingResponse
import json

import sentry_sdk




# ── Rate limiter ──
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def root():
    return FileResponse("index.html")
# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на проде заменить на конкретный домен
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup():
    from database.models import init_db
    init_db()
    logging.info("✓ БД инициализирована")
    
# ── Автообновление базы ──
def update_banks():
    try:
        logging.info("Обновление базы банков...")
        from scraper.ingest import ingest_to_chroma
        ingest_to_chroma()
        logging.info("✓ База обновлена")
    except Exception as e:
        logging.error(f"Ошибка обновления: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(update_banks, 'interval', days=7)
scheduler.start()

# ── Models ──
class Query(BaseModel):
    text: str
    user_id: str = "default"

    @validator('text')
    def text_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Текст не может быть пустым')
        if len(v) > 2000:
            raise ValueError('Слишком длинный запрос (макс 2000 символов)')
        return v

    @validator('user_id')
    def user_id_valid(cls, v):
        if len(v) > 100:
            raise ValueError('user_id слишком длинный')
        return v

# ── Endpoints ──
@app.post("/ask")
@limiter.limit("15/minute")
async def ask(request: Request, query: Query):
    try:
        response = run_pipeline(query.text, query.user_id)
        return {"response": response}
    except Exception as e:
        logging.error(f"API error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Внутренняя ошибка сервера"}
        )

@app.on_event("startup")
async def startup():
    from database.models import init_db
    init_db()
    logging.info("✓ БД инициализирована")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/ask")
@limiter.limit("15/minute")
async def ask(request: Request, query: Query):
    try:
        def generate():
            from agent.pipeline import run_pipeline_stream
            for chunk in run_pipeline_stream(query.text, query.user_id):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        logging.error(f"API error: {e}")
        return JSONResponse(status_code=500, content={"error": "Ошибка сервера"})

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN", ""),
    traces_sample_rate=0.1,
)

