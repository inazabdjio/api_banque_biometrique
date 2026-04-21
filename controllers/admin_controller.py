from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from typing import List
from datetime import datetime
import models, schemas

router = APIRouter(prefix="/admin", tags=["Administration"])

# --- 1. GESTION DES ADMINS ---

@router.post("/create", response_model=schemas.AdminOut)
def create_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    
    # Stockage du mot de passe (Note: en production, il faudrait le hasher avec bcrypt)
    new_admin = models.Admin(
        username=admin.username,
        password_hash=admin.password, 
        role=admin.role
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.get("/all", response_model=List[schemas.AdminOut])
def get_all_admins(db: Session = Depends(get_db)):
    return db.query(models.Admin).all()

@router.get("/{admin_id}", response_model=schemas.AdminOut)
def read_admin(admin_id: int, db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Administrateur non trouvé")
    return db_admin

@router.put("/{admin_id}", response_model=schemas.AdminOut)
def update_admin(admin_id: int, admin_update: schemas.AdminUpdate, db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Administrateur non trouvé")
    
    # Mise à jour dynamique
    update_data = admin_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_admin, key, value)
        
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Administrateur non trouvé")
    db.delete(db_admin)
    db.commit()
    return None

# --- 2. GESTION DES UTILISATEURS PAR L'ADMIN ---

@router.get("/users-report", response_model=List[schemas.UserOut]) # Utilisation de UserOut
def get_all_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@router.delete("/delete-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db.delete(db_user)
    db.commit()
    return None

# --- 3. GESTION DES LICENCES ---

@router.put("/validate-user/{user_id}")
def validate_user_license(user_id: int, data: schemas.LicenseValidation, db: Session = Depends(get_db)):
    user_license = db.query(models.License).filter(models.License.user_id == user_id).first()
    if not user_license:
        raise HTTPException(status_code=404, detail="Licence introuvable")
    user_license.is_active = True
    user_license.expiry_date = data.expiry_date
    db.commit()
    return {"message": "Utilisateur validé", "expire_le": user_license.expiry_date}

@router.put("/license-status/{user_id}")
def update_license_status(user_id: int, is_active: bool, db: Session = Depends(get_db)):
    user_license = db.query(models.License).filter(models.License.user_id == user_id).first()
    if not user_license:
        raise HTTPException(status_code=404, detail="Licence non trouvée")
    user_license.is_active = is_active
    db.commit()
    return {"message": f"Licence {'activée' if is_active else 'bloquée'}."}