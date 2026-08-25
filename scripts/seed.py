"""Seed script: create a demo user with links and sample clicks.

Usage: python -m scripts.seed
"""

import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import ClickEvent, Link, User  # noqa: E402

DEMO_EMAIL = "demo@rabitah.pk"
DEMO_PASSWORD = "demo12345"


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == DEMO_EMAIL).first():
            print("Demo user already exists — skipping.")
            return
        user = User(
            email=DEMO_EMAIL,
            username="demo",
            hashed_password=hash_password(DEMO_PASSWORD),
            display_name="Abrar Demo",
            bio="Growth hacker, creator & builder. Check out my latest work!",
            theme="midnight",
        )
        db.add(user)
        db.flush()

        links_data = [
            ("My Portfolio", "https://github.com/mohdabrarbaloch-arch", "github", 0),
            ("Latest YouTube Video", "https://youtube.com", "youtube", 1),
            ("Fiverr Gig", "https://fiverr.com", "briefcase", 2),
            ("TikTok", "https://tiktok.com", "video", 3),
            ("Book a Call", "https://calendly.com", "calendar", 4),
        ]
        links = []
        for title, url, icon, order in links_data:
            link = Link(user_id=user.id, title=title, url=url, icon=icon, sort_order=order)
            db.add(link)
            links.append(link)
        db.flush()

        # ~60 days of plausible click history
        today = datetime.now(UTC).date()
        for link in links:
            for offset in range(60):
                day = today - timedelta(days=offset)
                for _ in range(random.randint(0, 6)):
                    click_time = datetime.combine(day, datetime.min.time(), tzinfo=UTC) + timedelta(
                        hours=random.randint(8, 23), minutes=random.randint(0, 59)
                    )
                    db.add(
                        ClickEvent(
                            link_id=link.id,
                            user_id=user.id,
                            referrer=random.choice(
                                ["instagram.com", "tiktok.com", "youtube.com", "direct"]
                            ),
                            user_agent="Mozilla/5.0 (demo)",
                            clicked_at=click_time,
                        )
                    )
        db.commit()
        print(f"Seeded demo user: {DEMO_EMAIL} / {DEMO_PASSWORD} — public page at /demo")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
