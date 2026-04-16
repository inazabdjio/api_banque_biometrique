from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid, secrets
from database import get_db
import models, schemas
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

# --- 1. INSCRIPTION (Version allégée sans images) ---
@router.post("/register", response_model=schemas.UserOut)
async def register(
    user_data: schemas.UserCreate, # On utilise maintenant le schéma JSON
    db: Session = Depends(get_db)
):
    # Vérification si l'email existe déjà
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà")

    # Création de l'utilisateur (uniquement avec les champs textuels)
    new_user = models.User(
        full_name=user_data.full_name, 
        email=user_data.email, 
        phone_number=user_data.phone_number, 
        address=user_data.address
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Création automatique du premier compte (selon le choix de l'utilisateur)
    new_acc = models.Account(
        account_number=uuid.uuid4().hex[:10].upper(), 
        user_id=new_user.id,
        account_type=user_data.account_type, 
        balance=0.0
    )
    
    # Création de la licence (Inactive par défaut jusqu'à validation admin)
    new_lic = models.License(
        license_key=secrets.token_urlsafe(16), 
        is_active=False,
        expiry_date=None,
        user_id=new_user.id
    )
    
    db.add(new_acc)
    db.add(new_lic)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# --- 2. AJOUTER UN COMPTE SUPPLÉMENTAIRE ---
@router.post("/add-account/{user_id}", response_model=schemas.AccountOut)
def add_new_account(user_id: int, account_type: str = "EPARGNE", db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    new_acc = models.Account(
        account_number=uuid.uuid4().hex[:10].upper(),
        user_id=user.id,
        account_type=account_type,
        balance=0.0
    )
    
    db.add(new_acc)
    db.commit()
    db.refresh(new_acc)
    return new_acc

# --- 3. CONSULTER LE PROFIL ---
@router.get("/me/{user_id}", response_model=schemas.UserOut)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user