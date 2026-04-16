import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURATION DE L'URL ---

# 1. On cherche d'abord si Render a fourni une URL (variable DATABASE_URL)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Si on est sur ton PC (la variable est vide), on utilise ta configuration locale
if not SQLALCHEMY_DATABASE_URL:
    password = "password"  # Ton mot de passe local
    encoded_password = urllib.parse.quote_plus(password)
    # Ton URL locale pointant vers api_banque
    SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{encoded_password}@localhost:5432/api_banque"

# 3. Correction de compatibilité pour Render/Neon
# Render utilise parfois 'postgres://' mais SQLAlchemy exige 'postgresql://'
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- INITIALISATION ---

# Création de l'engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Configuration de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles
Base = declarative_base()

# Dépendance pour les controllers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()