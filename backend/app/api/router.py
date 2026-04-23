from fastapi import APIRouter

from app.api.routes import campaigns, seed, system, turns

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(turns.router, prefix="/campaigns", tags=["turns"])
api_router.include_router(seed.router, prefix="/seed", tags=["seed"])
