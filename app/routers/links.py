"""Link management routes (authenticated)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Link, User
from app.schemas import LinkCreate, LinkOut, LinkUpdate

router = APIRouter(prefix="/api/links", tags=["links"])


def _get_owned_link(link_id: int, user: User, db: Session) -> Link:
    link = db.get(Link, link_id)
    if link is None or link.user_id != user.id:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.get("", response_model=list[LinkOut])
def list_links(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Link).filter(Link.user_id == user.id).order_by(Link.sort_order, Link.id).all()


@router.post("", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
def create_link(
    payload: LinkCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    link = Link(
        user_id=user.id,
        title=payload.title.strip(),
        url=payload.url,
        icon=payload.icon,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.patch("/{link_id}", response_model=LinkOut)
def update_link(
    link_id: int,
    payload: LinkUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    link = _get_owned_link(link_id, user, db)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(link, key, value)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(
    link_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    link = _get_owned_link(link_id, user, db)
    db.delete(link)
    db.commit()
    return None
