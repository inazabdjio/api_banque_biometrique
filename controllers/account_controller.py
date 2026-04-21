from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import uuid
from typing import List

router = APIRouter(prefix="/accounts", tags=["Accounts"])

# --- 1. CRÉER UN COMPTE ---
@router.post("/create", response_model=schemas.AccountOut)
def create_account(account_data: schemas.AccountCreate, db: Session = Depends(get_db)):
    # Vérification que l'utilisateur existe
    user = db.query(models.User).filter(models.User.id == account_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    new_account = models.Account(
        account_number=uuid.uuid4().hex[:10].upper(), # Génération automatique d'un numéro unique
        account_type=account_data.account_type,
        balance=0.0,
        user_id=account_data.user_id
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

# --- 2. LIRE LES INFOS D'UN COMPTE ---
@router.get("/{account_id}", response_model=schemas.AccountOut)
def read_account(account_id: int, db: Session = Depends(get_db)):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Compte introuvable")
    return db_account

# --- 3. LISTER TOUS LES COMPTES D'UN UTILISATEUR ---
@router.get("/user/{user_id}", response_model=List[schemas.AccountOut])
def get_user_accounts(user_id: int, db: Session = Depends(get_db)):
    accounts = db.query(models.Account).filter(models.Account.user_id == user_id).all()
    # Retourne une liste vide si l'utilisateur n'a pas encore de compte
    return accounts

# --- 4. SUPPRIMER UN COMPTE ---
@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Compte introuvable")
    
    # Règle métier : Interdiction de supprimer un compte non vide
    if db_account.balance != 0:
        raise HTTPException(status_code=400, detail="Impossible de supprimer un compte non vide")

    db.delete(db_account)
    db.commit()
    return None