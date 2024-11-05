from fastapi import FastAPI
from app.routes.user import auth_router
from app.routes.vehicle import vehicle_router
from app.init_db import init_db
from app.middleware import register_middleware

app = FastAPI()

register_middleware(app)

# Include router for authentication
app.include_router(auth_router)

app.include_router(vehicle_router)


'''
@app.on_event("startup")
async def startup_event():
    await init_db()
'''