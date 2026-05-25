from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine

# import models so SQLAlchemy registers tables
from app.models import user as _u  # noqa
from app.models import report as _r  # noqa
from app.models import chat as _c  # noqa

from app.api.routes.auth import router as auth_router, users_router
from app.api.routes.reports import router as reports_router
from app.api.routes.chat import router as chat_router
from app.api.routes.recommendations import router as reco_router
from app.api.routes.analysis import router as analysis_router

# dev only — prod uses alembic
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.env}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(reports_router)
app.include_router(chat_router)
app.include_router(reco_router)
app.include_router(analysis_router)
