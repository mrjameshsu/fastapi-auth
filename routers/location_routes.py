from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from models import UserLocation
from utils import geocode_address

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/location", response_class=HTMLResponse)
def location_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        "location.html",
        {"request": request, "user": user, "location": user.location},
    )


@router.post("/location")
def update_location(
    request: Request,
    address: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    coords = geocode_address(address)
    if not coords:
        return templates.TemplateResponse(
            "location.html",
            {
                "request": request,
                "user": user,
                "location": user.location,
                "error": "Address not found. Please try a more specific address.",
            },
        )

    lat, lon = coords
    if user.location:
        user.location.latitude = lat
        user.location.longitude = lon
        user.location.display_address = address
        user.location.last_updated = datetime.utcnow()
    else:
        loc = UserLocation(
            user_id=user.id,
            latitude=lat,
            longitude=lon,
            display_address=address,
            last_updated=datetime.utcnow(),
        )
        db.add(loc)

    db.commit()
    return RedirectResponse("/location", status_code=303)


@router.get("/map", response_class=HTMLResponse)
def shared_map(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)

    locations_raw = db.query(UserLocation).all()
    locations = [
        {
            "email": loc.owner.email,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "display_address": loc.display_address,
            "last_updated": loc.last_updated.strftime("%Y-%m-%d %H:%M UTC") if loc.last_updated else "",
        }
        for loc in locations_raw
    ]
    return templates.TemplateResponse(
        "map.html",
        {"request": request, "user": user, "locations": locations},
    )
