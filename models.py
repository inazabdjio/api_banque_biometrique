from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="MANAGER")
    created_at = Column(DateTime, default=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String)
    address = Column(String)
    # AJOUT ESSENTIEL : Stockage du mot de passe haché
    password_hash = Column(String, nullable=False) 
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    accounts = relationship("Account", back_populates="owner", cascade="all, delete-orphan")
    license = relationship("License", back_populates="owner", uselist=False, cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True)
    account_type = Column(String, default="COURANT") 
    balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="accounts")
    sent_transactions = relationship("Transaction", foreign_keys="[Transaction.sender_id]", back_populates="sender")
    received_transactions = relationship("Transaction", foreign_keys="[Transaction.receiver_id]", back_populates="receiver")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    
    sender_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    receiver_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    sender = relationship("Account", foreign_keys=[sender_id], back_populates="sent_transactions")
    receiver = relationship("Account", foreign_keys=[receiver_id], back_populates="received_transactions")

class License(Base):
    __tablename__ = "licenses"
    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=False) 
    expiry_date = Column(DateTime, nullable=True) 
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="license")