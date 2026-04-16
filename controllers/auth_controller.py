from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime # <--- IMPORTANT pour vérifier la date
import models, schemas
from services.services import FaceService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login-biometric")
async def login(
    email: str = Form(...), 
    image: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. Rechercher l'utilisateur
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # 2. Vérification de la Licence (État + Date)
    if not user.license:
        raise HTTPException(status_code=403, detail="Licence introuvable.")

    # Vérification si l'admin a activé le compte
    if not user.license.is_active:
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé : Votre licence est inactive ou bloquée par l'administration."
        )

    # VÉRIFICATION DE LA DATE D'EXPIRATION (L'ajout crucial)
    if user.license.expiry_date and user.license.expiry_date < datetime.utcnow():
        raise HTTPException(
            status_code=403, 
            detail=f"Accès refusé : Votre licence a expiré le {user.license.expiry_date.strftime('%d/%m/%Y')}."
        )
    
    # 3. Vérification biométrique
    image.file.seek(0)
    is_valid = FaceService.verify_face(user.face_encoding, image.file)
    
    if is_valid:
        return {
            "status": "success", 
            "message": f"Accès autorisé. Bienvenue {user.full_name}",
            "user_id": user.id,
            # On renvoie la liste de tous ses comptes pour plus de clarté
            "accounts": [acc.account_number for acc in user.accounts]
        }
    
    raise HTTPException(status_code=401, detail="Échec de la reconnaissance par image")