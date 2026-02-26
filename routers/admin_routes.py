from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def require_admin(request: Request, db: Session):
    user = get_current_user(request, db)
    if not user:
        return None, RedirectResponse("/login", status_code=303)
    if not user.is_admin:
        return None, HTMLResponse("<h1>403 Forbidden</h1>", status_code=403)
    return user, None


@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
    user, err = require_admin(request, db)
    if err:
        return err

    pending = db.query(User).filter(User.is_approved == False).all()
    approved = db.query(User).filter(User.is_approved == True).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "user": user, "pending": pending, "approved": approved},
    )


@router.post("/admin/approve")
def approve_user(
    request: Request,
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    _, err = require_admin(request, db)
    if err:
        return err

    target = db.query(User).filter(User.id == user_id).first()
    if target:
        target.is_approved = True
        db.commit()
    return RedirectResponse("/admin", status_code=303)


@router.post("/admin/reject")
def reject_user(
    request: Request,
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    _, err = require_admin(request, db)
    if err:
        return err

    target = db.query(User).filter(User.id == user_id).first()
    if target:
        db.delete(target)
        db.commit()
    return RedirectResponse("/admin", status_code=303)
