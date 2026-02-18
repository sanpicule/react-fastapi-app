from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.middleware import AuditLogMiddleware

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:5173",  # Frontend origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Audit log middleware
app.add_middleware(AuditLogMiddleware)

app.include_router(router)
