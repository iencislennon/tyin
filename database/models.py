from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(String(100), nullable=False)
    role       = Column(String(20), nullable=False)
    message    = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class RealCase(Base):
    __tablename__ = "real_cases"
    id           = Column(Integer, primary_key=True)
    user_id      = Column(String(100))
    bank         = Column(String(100))
    requested_sum= Column(Integer)
    approved     = Column(String(10))
    real_rate    = Column(String(20))
    created_at   = Column(DateTime, default=datetime.now)

DATABASE_URL = os.getenv("DATABASE_URL")
engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_message(user_id: str, role: str, message: str):
    db = SessionLocal()
    try:
        db.add(ChatHistory(user_id=user_id, role=role, message=message))
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()

def get_history(user_id: str, limit: int = 6) -> list[dict]:
    db = SessionLocal()
    try:
        rows = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
            .all()
        )
        return [{"role": r.role, "content": r.message} for r in reversed(rows)]
    finally:
        db.close()