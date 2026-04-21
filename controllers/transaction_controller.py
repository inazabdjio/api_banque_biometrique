from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from typing import List
from datetime import datetime
import models, schemas

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# --- 1. DÉPÔT ---
@router.post("/deposit")
def deposit_money(account_number: str, amount: float, db: Session = Depends(get_db)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Le montant doit être positif")
    
    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    try:
        account.balance += amount
        new_tx = models.Transaction(
            receiver_id=account.id, 
            amount=amount,
            timestamp=datetime.utcnow()
        )
        db.add(new_tx)
        db.commit()
        db.refresh(account)
        return {"message": f"Dépôt réussi. Nouveau solde : {account.balance} FCFA"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors du dépôt")

# --- 2. RETRAIT ---
@router.post("/withdraw")
def withdraw_money(account_number: str, amount: float, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable")
    
    if account.balance < amount:
        raise HTTPException(status_code=400, detail="Solde insuffisant")

    try:
        account.balance -= amount
        new_tx = models.Transaction(
            sender_id=account.id,
            amount=amount,
            timestamp=datetime.utcnow()
        )
        db.add(new_tx)
        db.commit()
        return {"message": "Retrait réussi"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors du retrait")

# --- 3. VIREMENT ---
@router.post("/transfer")
def transfer_money(data: schemas.TransactionCreate, db: Session = Depends(get_db)):
    if data.sender_account == data.receiver_account:
        raise HTTPException(status_code=400, detail="Comptes identiques")

    sender = db.query(models.Account).filter(models.Account.account_number == data.sender_account).first()
    receiver = db.query(models.Account).filter(models.Account.account_number == data.receiver_account).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="L'un des comptes n'existe pas")

    if sender.balance < data.amount:
        raise HTTPException(status_code=400, detail="Solde insuffisant")

    try:
        sender.balance -= data.amount
        receiver.balance += data.amount
        
        new_tx = models.Transaction(
            sender_id=sender.id,
            receiver_id=receiver.id,
            amount=data.amount,
            timestamp=datetime.utcnow()
        )
        db.add(new_tx)
        db.commit()
        return {"message": "Virement effectué avec succès"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Échec de la transaction")

# --- 4. HISTORIQUE ---
@router.get("/history/{account_number}", response_model=List[schemas.TransactionOut])
def get_history(account_number: str, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable")
        
    # CORRECTION : Utilisation des noms de relations 'sender' et 'receiver'
    # tels qu'ils sont définis dans models.py
    return db.query(models.Transaction).options(
        joinedload(models.Transaction.sender),
        joinedload(models.Transaction.receiver)
    ).filter(
        (models.Transaction.sender_id == account.id) | 
        (models.Transaction.receiver_id == account.id)
    ).order_by(models.Transaction.timestamp.desc()).all()