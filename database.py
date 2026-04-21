import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env
load_dotenv()

# Récupérer l'URL depuis l'environnement
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Correction obligatoire pour les URL de base de données (Neon/Heroku utilisent souvent postgres://)
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Initialisation du moteur avec configuration optimisée pour Neon
# pool_pre_ping=True est vital pour vérifier que la connexion n'est pas "endormie"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # Augmentation des timeouts pour gérer la latence serverless si nécessaire
    pool_size=10, 
    max_overflow=20,
    pool_recycle=300, # Plus court que 3600 pour éviter les fermetures de connexions inactives
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Fonction dépendance pour FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()