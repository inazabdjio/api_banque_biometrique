from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from typing import List
import models, schemas
from datetime import datetime

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# --- 1. DÉPÔT ---
@router.post("/deposit")
def deposit_money(account_number: str, amount: float, db: Session = Depends(get_db)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Le montant doit être supérieur à 0")
    
    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    account.balance += amount

    new_tx = models.Transaction(
        sender_account="DEPOT_CASH",
        receiver_account=account_number,
        amount=amount,
        timestamp=datetime.utcnow()
    )
    
    db.add(new_tx)
    db.commit()
    db.refresh(account)
    return {"message": f"Dépôt réussi. Nouveau solde : {account.balance} FCFA"}

# --- 2. RETRAIT ---
@router.post("/withdraw")
def withdraw_money(account_number: str, amount: float, db: Session = Depends(get_db)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Le montant doit être supérieur à 0")

    account = db.query(models.Account).filter(models.Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="Compte introuvable")

    if account.balance < amount:
        raise HTTPException(status_code=400, detail="Solde insuffisant pour ce retrait")

    account.balance -= amount

    new_tx = models.Transaction(
        sender_account=account_number,
        receiver_account="RETRAIT_CASH",
        amount=amount,
        timestamp=datetime.utcnow()
    )

    db.add(new_tx)
    db.commit()
    db.refresh(account)
    return {"message": f"Retrait réussi. Nouveau solde : {account.balance} FCFA"}

# --- 3. VIREMENT (Sécurisé) ---
@router.post("/transfer")
def transfer_money(data: schemas.TransactionCreate, db: Session = Depends(get_db)):
    # AJOUT DE LA SÉCURITÉ : Vérifier si les comptes sont identiques
    if data.sender_account == data.receiver_account:
        raise HTTPException(
            status_code=400, 
            detail="Le compte émetteur et récepteur doivent être différents"
        )

    sender = db.query(models.Account).filter(models.Account.account_number == data.sender_account).first()
    receiver = db.query(models.Account).filter(models.Account.account_number == data.receiver_account).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="L'un des comptes est introuvable")

    if sender.balance < data.amount:
        raise HTTPException(status_code=400, detail="Solde insuffisant pour le virement")

    # Opération atomique (simplifiée)
    sender.balance -= data.amount
    receiver.balance += data.amount

    new_tx = models.Transaction(
        sender_account=data.sender_account,
        receiver_account=data.receiver_account,
        amount=data.amount,
        timestamp=datetime.utcnow()
    )

    db.add(new_tx)
    db.commit()
    return {"message": "Virement effectué avec succès", "montant": data.amount}

# --- 4. HISTORIQUE ---
@router.get("/history/{account_number}", response_model=List[schemas.TransactionOut])
def get_history(account_number: str, db: Session = Depends(get_db)):
    history = db.query(models.Transaction).filter(
        (models.Transaction.sender_account == account_number) | 
        (models.Transaction.receiver_account == account_number)
    ).order_by(models.Transaction.timestamp.desc()).all()
    return history