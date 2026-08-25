"""Analytics routes (authenticated): totals, daily clicks, top links."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import ClickEvent, Link, User
from app.schemas import AnalyticsOut, DailyClick

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsOut)
def analytics(
    days: int = 14, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    days = max(1, min(days, 90))
    links = (
        db.query(Link)
        .filter(Link.user_id == user.id)
        .order_by(Link.click_count.desc(), Link.sort_order)
        .all()
    )
    total_clicks = sum(link.click_count for link in links)

    since = datetime.now(UTC) - timedelta(days=days - 1)
    since_midnight = since.replace(hour=0, minute=0, second=0, microsecond=0)

    rows = (
        db.query(func.date(ClickEvent.clicked_at).label("day"), func.count(ClickEvent.id))
        .filter(
            ClickEvent.user_id == user.id,
            ClickEvent.clicked_at >= since_midnight,
        )
        .group_by(func.date(ClickEvent.clicked_at))
        .all()
    )
    counts = {str(day): count for day, count in rows}

    daily: list[DailyClick] = []
    for offset in range(days - 1, -1, -1):
        day = (datetime.now(UTC) - timedelta(days=offset)).date()
        daily.append(DailyClick(date=day.isoformat(), count=counts.get(day.isoformat(), 0)))

    return AnalyticsOut(
        total_clicks=total_clicks,
        total_links=len(links),
        daily=daily,
        top_links=links[:5],
    )
