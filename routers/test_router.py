# backend/routers/test_router.py
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from db.database import get_db
from db.models import TestResult, UserMaster, Specialty
from utils.security import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from sqlalchemy import desc
from datetime import datetime
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer()

class TestResultCreate(BaseModel):
    category: str = Field(..., example="Tech")
    correct_answers: int = Field(..., example=2)

class TestResultOut(BaseModel):
    id: int
    user_id: str
    category: str
    correct_answers: int
    created_at: datetime

    class Config:
        from_attributes = True  # 'orm_mode' を 'from_attributes' に変更


@router.post("/api/test_results/", response_model=TestResultOut, status_code=201)
def create_test_result(
    test_result: TestResultCreate,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # カテゴリの存在確認
        category = db.query(Specialty).filter(Specialty.specialty == test_result.category).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid category")

        # テスト結果の作成
        new_test_result = TestResult(
            user_id=user_id,
            category=test_result.category,
            correct_answers=test_result.correct_answers
        )
        db.add(new_test_result)
        db.commit()
        db.refresh(new_test_result)

        return new_test_result

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in create_test_result: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/test_results/", response_model=List[TestResultOut])
def get_user_test_results(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        test_results = db.query(TestResult).filter(TestResult.user_id == user_id).order_by(desc(TestResult.created_at)).all()
        return test_results

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in get_user_test_results: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
