from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# --- CONFIGURATION DE BASE ---
class BaseSchema(BaseModel):
    """Active la compatibilité avec les objets SQLAlchemy (ORM)"""
    model_config = ConfigDict(from_attributes=True)

# --- ADMIN ---
class AdminCreate(BaseModel):
    username: str
    password: str
    role: str = "MANAGER"
    
class AdminOut(BaseSchema):
    id: int
    username: str
    role: str

# --- VALIDATION ADMINISTRATIVE ---
class LicenseValidation(BaseModel):
    """Utilisé par l'admin pour fixer une date d'expiration précise lors de l'activation"""
    expiry_date: datetime

# --- TRANSACTION ---
class TransactionCreate(BaseModel):
    sender_account: str
    receiver_account: str
    amount: float = Field(gt=0) # Montant strictement positif

class TransactionOut(BaseSchema):
    id: int
    sender_account: str
    receiver_account: str
    amount: float
    timestamp: datetime

# --- ACCOUNT ---
class AccountOut(BaseSchema):
    id: int
    account_number: str
    account_type: str
    balance: float

# --- LICENSE ---
class LicenseOut(BaseSchema):
    license_key: str
    is_active: bool
    expiry_date: Optional[datetime] = None

# --- USER ---
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str
    address: str

class UserCreate(UserBase):
    """
    Schéma utilisé lors de l'inscription. 
    L'utilisateur choisit son type de compte.
    """
    account_type: str = Field(default="COURANT", pattern="^(COURANT|EPARGNE)$")

class UserOut(UserBase, BaseSchema):
    id: int
    # MODIFICATION : cni_path a été supprimé ici
    created_at: datetime
    accounts: List[AccountOut] = []
    license: Optional[LicenseOut] = None

# --- AUTHENTIFICATION ---
class LoginRequest(BaseModel):
    email: str