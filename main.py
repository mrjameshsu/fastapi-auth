from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from database import engine, Base
from routers import auth_routes, dashboard_routes, location_routes, admin_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Auth App")

app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(location_routes.router)
app.include_router(admin_routes.router)


@app.get("/")
def root():
    return RedirectResponse("/dashboard")


if __name__ == "__main__":
    import logging
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
