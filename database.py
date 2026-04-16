
import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURATION DE L'URL ---

# 1. Récupération de l'URL depuis l'environnement (Render)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Configuration locale (si DATABASE_URL n'est pas définie)
if not SQLALCHEMY_DATABASE_URL:
    password = "password" 
    encoded_password = urllib.parse.quote_plus(password)
    SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:{encoded_password}@localhost:5432/api_banque"

# 3. Correction impérative pour SQLAlchemy et compatibilité Neon/Render
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- INITIALISATION ---

# AJUSTEMENT POUR LE POOLING : 
# Si tu utilises l'URL de pooling de Neon, SQLAlchemy doit être configuré
# pour gérer les connexions de manière plus flexible lors des tests de charge.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,          # Nombre de connexions maintenues ouvertes
    max_overflow=30,       # Connexions supplémentaires autorisées en cas de pic
    pool_recycle=3600,     # Recycle les connexions toutes les heures
    pool_pre_ping=True     # Vérifie si la connexion est encore vivante avant de l'utiliser
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()










"""
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

        """