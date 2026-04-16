from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
# Importation des contrôleurs
from controllers import user_controller, transaction_controller, admin_controller, auth_controller

# --- CRÉATION DES TABLES ---
# SQLAlchemy va créer les tables dans Neon en suivant ton nouveau models.py (sans CNI)
models.Base.metadata.create_all(bind=engine)

# --- INITIALISATION DE L'API ---
app = FastAPI(
    title="Système de Gestion Bancaire Numérique", # Titre mis à jour (plus de "Biométrique")
    description="API de gestion bancaire simplifiée et sécurisée",
    version="1.1.0"
)

# --- CONFIGURATION CORS ---
# Permet à ton futur frontend (ou Postman/Swagger) de communiquer avec l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUSION DES ROUTEURS ---
# Ces routeurs connectent tes fonctions logiques à des URLs précises
app.include_router(user_controller.router)
app.include_router(auth_controller.router)        
app.include_router(transaction_controller.router)
app.include_router(admin_controller.router)       

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur l'API de la Banque Numérique",
        "status": "Opérationnel",
        "documentation": "/docs"
    }