from time import time 
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def register_middleware(app: FastAPI):
    
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time()  # Call the time function directly

        response = await call_next(request)
        processing_time = time() - start_time

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time:.2f}s"

        print(message)
        return response
    
    origins = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"],
    )