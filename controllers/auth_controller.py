from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from datetime import datetime
import models, schemas

# Configuration du contexte pour vérifier les mots de passe hachés
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Authentification"])

@router.post("/login")
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Rechercher l'utilisateur par email
    user = db.query(models.User).filter(models.User.email == login_data.email).first()
    
    # 2. Sécurité : Vérification de l'utilisateur ET du mot de passe haché
    # On utilise pwd_context.verify() pour comparer le mot de passe reçu avec le hash stocké
    if not user or not pwd_context.verify(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email ou mot de passe incorrect"
        )
    
    # 3. Vérification de la Licence
    if not user.license or not user.license.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Accès refusé : Licence inactive ou inexistante."
        )

    # 4. Vérification de la date d'expiration
    if user.license.expiry_date and user.license.expiry_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Accès refusé : Votre licence a expiré le {user.license.expiry_date.strftime('%d/%m/%Y')}."
        )
    
    # 5. Retour des informations utilisateur
    return {
        "status": "success", 
        "user_id": user.id,
        "full_name": user.full_name,
        "accounts": [
            {
                "id": acc.id,
                "account_number": acc.account_number, 
                "account_type": acc.account_type, 
                "balance": acc.balance
            } 
            for acc in user.accounts
        ]
    }