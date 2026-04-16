from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from typing import List
from datetime import datetime
import models, schemas

router = APIRouter(prefix="/admin", tags=["Administration"])

# --- 1. CRÉER UN ADMIN ---
@router.post("/create", response_model=schemas.AdminOut)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    
    new_admin = models.Admin(
        username=admin.username,
        password_hash=admin.password, # Note: Dans un vrai projet, on hacherait ce MDP
        role=admin.role
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# --- 2. VOIR TOUS LES ADMINS (Nouvelle fonctionnalité) ---
@router.get("/all", response_model=List[schemas.AdminOut])
def get_all_admins(db: Session = Depends(get_db)):
    """Récupère la liste de tous les administrateurs du système"""
    return db.query(models.Admin).all()

# --- 3. VOIR TOUS LES UTILISATEURS ---
@router.get("/users-report", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    """L'admin consulte la liste des clients inscrits (version numérique)"""
    return db.query(models.User).all()

# --- 4. VALIDER AVEC UNE DATE PRÉCISE ---
@router.put("/validate-user/{user_id}")
def validate_user_license(user_id: int, data: schemas.LicenseValidation, db: Session = Depends(get_db)):
    """
    Active le compte et définit la date d'expiration exacte choisie par l'admin.
    """
    user_license = db.query(models.License).filter(models.License.user_id == user_id).first()
    
    if not user_license:
        raise HTTPException(status_code=404, detail="Licence introuvable")

    user_license.is_active = True
    user_license.expiry_date = data.expiry_date
    
    db.commit()
    return {
        "message": "Utilisateur validé avec succès",
        "nouveau_statut": "Actif",
        "expire_le": user_license.expiry_date
    }

# --- 5. BLOQUER / DÉBLOQUER RAPIDEMENT ---
@router.put("/license-status/{user_id}")
def update_license_status(user_id: int, is_active: bool, db: Session = Depends(get_db)):
    user_license = db.query(models.License).filter(models.License.user_id == user_id).first()
    
    if not user_license:
        raise HTTPException(status_code=404, detail="Licence non trouvée")
    
    user_license.is_active = is_active
    db.commit()
    
    statut = "activée" if is_active else "bloquée"
    return {"message": f"La licence de l'utilisateur {user_id} a été {statut}."}