from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, Integer

from app.routes import chat
from app.db.database import init_db, get_db, LogEntry
from app.core.logger import get_logger

app = FastAPI(title="AegisAI Firewall", version="0.2.0")

# Include Routers
app.include_router(chat.router)

logger = get_logger()

@app.on_event("startup")
async def on_startup():
    logger.info("AegisAI Firewall starting up...")
    await init_db()

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "firewall", "mode": "rule-based"}

# Dashboard Aggregation Endpoints

@app.get("/logs")
async def get_logs(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """Return latest logs"""
    result = await db.execute(
        select(LogEntry).order_by(desc(LogEntry.timestamp)).limit(limit)
    )
    logs = result.scalars().all()
    return logs

@app.get("/sessions")
async def get_sessions_summary(db: AsyncSession = Depends(get_db)):
    """Group by session_id with stats"""
    # SQLite aggregation
    # Select session_id, count(*), avg(risk), sum(blocked)
    
    stmt = (
        select(
            LogEntry.session_id,
            func.count(LogEntry.id).label("total_requests"),
            func.avg(LogEntry.final_risk).label("average_risk"),
            func.sum(func.cast(LogEntry.blocked, Integer)).label("blocked_count") # cast bool to numeric for sum in sqlite
        )
        .group_by(LogEntry.session_id)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    sessions = []
    for row in rows:
        sessions.append({
            "session_id": row.session_id,
            "total_requests": row.total_requests,
            "average_risk": round(row.average_risk, 2) if row.average_risk else 0.0,
            "blocked_count": int(row.blocked_count) if row.blocked_count else 0
        })
        
    return sessions

@app.get("/risk-summary")
async def get_risk_summary(db: AsyncSession = Depends(get_db)):
    """Global risk stats"""
    
    # Calculate totals
    stmt = select(
        func.count(LogEntry.id).label("total"),
        func.sum(func.cast(LogEntry.blocked, Integer)).label("blocked"),
        func.avg(LogEntry.final_risk).label("avg_risk")
    )
    result = await db.execute(stmt)
    total, blocked, avg_risk = result.one()
    
    # Highest risk session
    # Select session_id ordered by avg(risk) desc limit 1
    stmt_high = (
        select(LogEntry.session_id)
        .group_by(LogEntry.session_id)
        .order_by(desc(func.avg(LogEntry.final_risk)))
        .limit(1)
    )
    res_high = await db.execute(stmt_high)
    highest_risk_session = res_high.scalar_one_or_none()
    
    return {
        "total_requests": total or 0,
        "total_blocked": int(blocked) if blocked else 0,
        "average_risk": round(avg_risk, 2) if avg_risk else 0.0,
        "highest_risk_session": highest_risk_session
    }
