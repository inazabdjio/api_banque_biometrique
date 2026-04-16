from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime
import models, schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login") # On a renommé la route (plus de "-biometric")
async def login(
    login_data: schemas.LoginRequest, # On utilise le schéma qu'on a créé
    db: Session = Depends(get_db)
):
    # 1. Rechercher l'utilisateur par email
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    
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

    # VÉRIFICATION DE LA DATE D'EXPIRATION
    if user.license.expiry_date and user.license.expiry_date < datetime.utcnow():
        raise HTTPException(
            status_code=403, 
            detail=f"Accès refusé : Votre licence a expiré le {user.license.expiry_date.strftime('%d/%m/%Y')}."
        )
    
    # 3. Plus de vérification biométrique ! 
    # L'accès est autorisé si l'email existe et que la licence est valide.
    return {
        "status": "success", 
        "message": f"Accès autorisé. Bienvenue {user.full_name}",
        "user_id": user.id,
        "accounts": [
            {
                "number": acc.account_number, 
                "type": acc.account_type, 
                "balance": acc.balance
            } for acc in user.accounts
        ]
    }