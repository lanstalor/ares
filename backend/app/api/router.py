from fastapi import APIRouter

from app.api.routes import campaigns, clarify, media, memories, operator, portraits, seed, system, turns

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(media.file_router, prefix="/media", tags=["media"])
api_router.include_router(portraits.file_router, prefix="/media", tags=["media"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(turns.router, prefix="/campaigns", tags=["turns"])
api_router.include_router(media.router, prefix="/campaigns", tags=["media"])
api_router.include_router(portraits.router, prefix="/campaigns", tags=["portraits"])
api_router.include_router(clarify.router, prefix="/campaigns", tags=["clarify"])
api_router.include_router(memories.router, prefix="/campaigns", tags=["memories"])
api_router.include_router(seed.router, prefix="/seed", tags=["seed"])
api_router.include_router(operator.router, prefix="/operator", tags=["operator"])
