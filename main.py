from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse  # <--- Ajout de l'import pour la redirection
import models
from database import engine
# Importation des contrôleurs
from controllers import user_controller, transaction_controller, admin_controller, auth_controller

# --- CRÉATION DES TABLES ---
models.Base.metadata.create_all(bind=engine)

# --- INITIALISATION DE L'API ---
app = FastAPI(
    title="Système de Gestion Bancaire Numérique",
    description="API de gestion bancaire simplifiée et sécurisée",
    version="1.1.0"
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
app.include_router(user_controller.router)
app.include_router(auth_controller.router)        
app.include_router(transaction_controller.router)
app.include_router(admin_controller.router)       

# --- ROUTE RACINE (REDIRECTION) ---
@app.get("/")
async def root():
    """
    Redirige automatiquement les visiteurs vers la documentation interactive.
    """
    return RedirectResponse(url="/docs")