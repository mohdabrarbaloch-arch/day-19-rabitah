"""Public routes: profile page + click redirect + QR code.

The click redirect (GET /go/{link_id}) is the workhorse: it counts the
click, records a ClickEvent, and redirects the visitor to the target URL.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import ClickEvent, Link, User
from app.schemas import PublicPage
from app.services.qr import qr_png

router = APIRouter(tags=["public"])


@router.get("/api/page/{username}", response_model=PublicPage)
def get_public_page_json(username: str, db: Session = Depends(get_db)):
    return _build_page(username, db)


@router.get("/{username}", response_model=PublicPage)
def get_public_page(username: str, db: Session = Depends(get_db)):
    return _build_page(username, db)


def _build_page(username: str, db: Session) -> PublicPage:
    user = db.query(User).filter(User.username == username.lower()).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=404, detail="Page not found")
    links = [link for link in user.links if link.is_active]
    return PublicPage(
        username=user.username,
        display_name=user.display_name or user.username,
        bio=user.bio,
        avatar_url=user.avatar_url,
        theme=user.theme,
        links=links,
    )


@router.get("/go/{link_id}")
def redirect_and_count(
    link_id: int,
    referrer: str = "",
    user_agent: str = "",
    db: Session = Depends(get_db),
):
    link = db.get(Link, link_id)
    if link is None or not link.is_active:
        raise HTTPException(status_code=404, detail="Link not found")
    link.click_count += 1
    event = ClickEvent(
        link_id=link.id,
        user_id=link.user_id,
        referrer=referrer[:500],
        user_agent=user_agent[:500],
    )
    db.add(event)
    db.commit()
    return RedirectResponse(url=link.url, status_code=302)


@router.get("/qr/{link_id}")
def link_qr(link_id: int, db: Session = Depends(get_db)):
    link = db.get(Link, link_id)
    if link is None or not link.is_active:
        raise HTTPException(status_code=404, detail="Link not found")
    return qr_png(link.url)
