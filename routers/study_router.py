# backend/routers/study_router.py
from fastapi import APIRouter, Depends, HTTPException, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from db.database import get_db
from db.models import StudyLog
from utils.security import verify_token
from sqlalchemy import func
from pydantic import BaseModel

router = APIRouter()
bearer_scheme = HTTPBearer()

class StudyTimeRequest(BaseModel):
    minutes: int

@router.post("/api/study_logs")
def add_study_time(
    req: StudyTimeRequest,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    today = date.today()
    log = db.query(StudyLog).filter(StudyLog.user_id == user_id, StudyLog.date == today).first()

    if log:
        log.minutes += req.minutes
    else:
        log = StudyLog(user_id=user_id, date=today, minutes=req.minutes)
        db.add(log)

    db.commit()
    db.refresh(log)
    return {"message": "Study time added", "date": str(today), "minutes": log.minutes}


@router.get("/api/study_logs")
def get_study_logs_for_week(
    week_start: str = Query(None),
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    if week_start:
        try:
            start_date = datetime.strptime(week_start, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid week_start format. Use YYYY-MM-DD.")
    else:
        # week_startが無い場合、今日を含む過去7日間
        today = date.today()
        start_date = today - timedelta(days=6)

    end_date = start_date + timedelta(days=6)

    logs = db.query(StudyLog).filter(
        StudyLog.user_id == user_id,
        StudyLog.date >= start_date,
        StudyLog.date <= end_date
    ).all()

    # 期間中の日付をすべてキーとして0で初期化
    result = {}
    for i in range(7):
        d = start_date + timedelta(days=i)
        result[str(d)] = 0

    for l in logs:
        result[str(l.date)] = l.minutes

    total_minutes = sum(result.values())

    return {"week_start": str(start_date), "logs": result, "total_minutes": total_minutes}
