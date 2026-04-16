from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import uuid, secrets, os, shutil
from datetime import datetime
from database import get_db
import models, schemas
from services.services import FaceService
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

# --- CONFIGURATION DU STOCKAGE ---
UPLOAD_DIR = "uploads/cni"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- 1. INSCRIPTION (Crée l'utilisateur + 1er compte + Licence inactive) ---
@router.post("/register", response_model=schemas.UserOut)
async def register(
    full_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    address: str = Form(...),
    account_type: str = Form("COURANT"), 
    image: UploadFile = File(...),     
    cni_file: UploadFile = File(...),  
    db: Session = Depends(get_db)
):
    # Vérification email
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà")

    # Sauvegarde CNI
    file_extension = os.path.splitext(cni_file.filename)[1]
    cni_filename = f"cni_{uuid.uuid4().hex}{file_extension}"
    cni_path = os.path.join(UPLOAD_DIR, cni_filename)
    
    with open(cni_path, "wb") as buffer:
        shutil.copyfileobj(cni_file.file, buffer)

    # Encodage facial
    image.file.seek(0)
    face_encoding = FaceService.encode_face(image.file)
    
    if not face_encoding:
        if os.path.exists(cni_path):
            os.remove(cni_path)
        raise HTTPException(status_code=400, detail="Visage non détecté sur la photo")

    # Création User
    new_user = models.User(
        full_name=full_name, 
        email=email, 
        phone_number=phone_number, 
        address=address, 
        cni_path=cni_path, 
        face_encoding=face_encoding
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Création du premier compte
    new_acc = models.Account(
        account_number=uuid.uuid4().hex[:10].upper(), 
        user_id=new_user.id,
        account_type=account_type, 
        balance=0.0
    )
    
    # Création de la licence (BLOQUÉE par défaut)
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
    """
    Permet à un utilisateur existant d'ouvrir un nouveau compte (ex: ajouter un compte Épargne).
    """
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