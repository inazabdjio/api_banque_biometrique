from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="MANAGER")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    accounts = relationship("Account", back_populates="owner", cascade="all, delete-orphan")
    license = relationship("License", back_populates="owner", uselist=False, cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True)
    account_type = Column(String, default="COURANT") 
    balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="accounts")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    sender_account = Column(String)
    receiver_account = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class License(Base):
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String, unique=True)
    # L'utilisateur est bloqué par défaut à l'inscription
    is_active = Column(Boolean, default=False) 
    # Pas de date par défaut, l'admin la fixera à l'activation
    expiry_date = Column(DateTime, nullable=True) 
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="license")