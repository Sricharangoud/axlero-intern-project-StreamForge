from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.sensors import router as sensors_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.dashboard import router as dashboard_router

api_v1_router = APIRouter()

# Register sub-routers
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(sensors_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(dashboard_router)
