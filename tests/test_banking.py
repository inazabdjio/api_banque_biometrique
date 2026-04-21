import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Ajout de la racine pour permettre l'import de 'main'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

client = TestClient(app)

def test_full_banking_workflow():
    # CT-000: Initialisation Admin
    # Si le test échoue en 400, vide simplement ta base manuellement avant de relancer
    admin_res = client.post("/admin/create", json={
        "username": "superadmin", 
        "password": "AdminPassword123", 
        "role": "MANAGER"
    })
    assert admin_res.status_code == 200

    # CT-001: Inscription Utilisateur
    user_res = client.post("/users/create", json={
        "full_name": "Ina Zabdjio", 
        "email": "test@yaounde.cm", 
        "password": "Password123", 
        "phone_number": "690000000", 
        "address": "Yaoundé",
        "account_type": "COURANT" 
    })
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    # CT-002: Validation par Admin
    expiry = (datetime.utcnow() + timedelta(days=30)).isoformat()
    val_res = client.put(f"/admin/validate-user/{user_id}", json={"expiry_date": expiry})
    assert val_res.status_code == 200

    # CT-003: Auth Utilisateur
    login_res = client.post("/auth/login", json={
        "email": "test@yaounde.cm", 
        "password": "Password123"
    })
    assert login_res.status_code == 200

    # CT-004: Créer Compte additionnel
    acc_res = client.post("/accounts/create", json={
        "user_id": user_id, 
        "account_type": "COURANT"
    })
    assert acc_res.status_code == 200
    account_number = acc_res.json()["account_number"]

    # CT-005: Dépôt
    dep_res = client.post(f"/transactions/deposit?account_number={account_number}&amount=1000")
    assert dep_res.status_code == 200

    # CT-006: Virement (vers un second compte)
    acc2 = client.post("/accounts/create", json={"user_id": user_id, "account_type": "EPARGNE"})
    acc2_num = acc2.json()["account_number"]
    
    trans_res = client.post("/transactions/transfer", json={
        "sender_account": account_number,
        "receiver_account": acc2_num,
        "amount": 200
    })
    assert trans_res.status_code == 200