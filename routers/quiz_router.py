from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Quiz
from typing import List
from pydantic import BaseModel, validator
from datetime import datetime, date
import json

router = APIRouter()

class QuizOut(BaseModel):
    id: int
    question_text: str
    options: List[str]
    correct_index: int
    explanation: str
    category: str
    date: date

    class Config:
        orm_mode = True

    @validator('options', pre=True)
    def parse_options(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v

@router.get("/get_all_dates", response_model=List[str])
def get_all_dates(db: Session = Depends(get_db)):
    dates = db.query(Quiz.date).distinct().all()
    return [date_tuple[0].isoformat() for date_tuple in dates]

@router.get("/get_questions_by_date/{selected_date}", response_model=List[QuizOut])
def get_questions_by_date(selected_date: str, db: Session = Depends(get_db)):
    try:
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    questions = db.query(Quiz).filter(Quiz.date == date_obj).all()

    return questions
