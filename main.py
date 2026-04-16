from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
# AJOUT : On importe tous les contrôleurs nécessaires
from controllers import user_controller, transaction_controller, admin_controller, auth_controller

# --- CRÉATION DES TABLES ---
models.Base.metadata.create_all(bind=engine)

# --- INITIALISATION DE L'API ---
app = FastAPI(
    title="Système de Banque Biométrique",
    description="API de gestion bancaire",
    version="1.0.0"
)

# --- CONFIGURATION CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSION DES ROUTEURS ---
# AJOUT : On inclut les 4 routeurs pour que tout soit visible dans Swagger
app.include_router(user_controller.router)
app.include_router(auth_controller.router)        # <--- IMPORTANT : Pour le login
app.include_router(transaction_controller.router)
app.include_router(admin_controller.router)       # <--- IMPORTANT : Pour la gestion admin
# ----------------------------

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur l'API de la Banque Biométrique",
        "status": "Opérationnel",
        "documentation": "/docs"
    }