from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# --- CONFIGURATION DE BASE ---
class BaseSchema(BaseModel):
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

class AdminUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# --- VALIDATION ADMINISTRATIVE ---
class LicenseValidation(BaseModel):
    expiry_date: datetime

# --- TRANSACTION ---
class TransactionCreate(BaseModel):
    sender_account: str
    receiver_account: str
    amount: float = Field(gt=0) 

# Nouveau schéma pour éviter l'erreur de validation
class AccountRefOut(BaseSchema):
    account_number: str

class TransactionOut(BaseSchema):
    id: int
    amount: float
    timestamp: datetime
    # On utilise Optional car le dépôt/retrait peut avoir sender/receiver à None
    sender: Optional[AccountRefOut] = None
    receiver: Optional[AccountRefOut] = None

# --- ACCOUNT ---
class AccountCreate(BaseModel):
    user_id: int
    account_type: str = Field(default="COURANT", pattern="^(COURANT|EPARGNE)$")

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
    password: str
    account_type: str = Field(default="COURANT", pattern="^(COURANT|EPARGNE)$")

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None # Ajouté pour permettre la modif du mot de passe

class UserOut(UserBase, BaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    accounts: List[AccountOut] = []
    license: Optional[LicenseOut] = None

# --- AUTHENTIFICATION ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str