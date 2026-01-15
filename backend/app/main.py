from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager

from app.routers import films, customers, staff, rentals, reports
from app.database import connection_pool

# Lifespan context manager para startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Iniciando DVD Rental API...")
    print(f"📊 Conectando a PostgreSQL: {os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 5432)}")
    yield
    # Shutdown
    print("🛑 Cerrando conexiones de base de datos...")
    connection_pool.closeall()
    print("👋 DVD Rental API cerrada")

# Crear aplicación FastAPI
app = FastAPI(
    title="DVD Rental API",
    description="API REST para gestión de rentas de DVDs",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(films.router, prefix="/api/films", tags=["Films"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(rentals.router, prefix="/api/rentals", tags=["Rentals"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

# Endpoint raíz
@app.get("/")
async def root():
    return {
        "message": "DVD Rental API con FastAPI",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "films": "/api/films",
            "customers": "/api/customers",
            "staff": "/api/staff",
            "rentals": "/api/rentals",
            "reports": "/api/reports",
            "docs": "/docs"
        }
    }

# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "error": str(exc)
        }
    )

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )