from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt  # Importation directe de bcrypt
from database import get_db
import models, schemas
import uuid 

router = APIRouter(prefix="/users", tags=["Users"])

# --- CREATE: Créer un utilisateur ---
@router.post("/create", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur avec un mot de passe haché et son compte initial."""
    # 1. Vérifier si l'email existe déjà
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cet email est déjà utilisé"
        )
    
    # 2. Hacher le mot de passe avec bcrypt nativement
    # On encode le mot de passe en bytes, on génère un sel, et on hache
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8')
    
    # 3. Préparer les données
    user_data = user.model_dump()
    user_data.pop("password") # On retire le mot de passe en clair
    
    # Extraction et retrait du champ account_type
    account_type = user_data.pop("account_type", "COURANT")
    
    user_data["password_hash"] = hashed_password
    
    # 4. Créer l'utilisateur
    new_user = models.User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 5. Création automatique du compte associé
    new_account = models.Account(
        account_number=uuid.uuid4().hex[:10].upper(),
        account_type=account_type,
        balance=0.0,
        user_id=new_user.id
    )
    db.add(new_account)
    
    # 6. Création automatique d'une licence par défaut
    new_license = models.License(
        license_key=uuid.uuid4().hex[:16],
        is_active=False,
        user_id=new_user.id
    )
    db.add(new_license)
    
    db.commit()
    db.refresh(new_user)
    
    return new_user

# --- READ: Lire un utilisateur par son ID ---
@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Utilisateur non trouvé"
        )
    return db_user

# --- UPDATE: Mettre à jour les infos d'un utilisateur ---
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Utilisateur non trouvé"
        )
    
    # 1. Convertir les données en dictionnaire
    update_data = user_update.model_dump(exclude_unset=True)
    
    # 2. Sécurité : Empêcher explicitement la modification du mot de passe
    # On retire le mot de passe s'il est présent dans la requête
    update_data.pop("password", None)
    update_data.pop("password_hash", None)
    
    # 3. Appliquer les changements sur les champs autorisés
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# --- DELETE: Supprimer un utilisateur ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Utilisateur non trouvé"
        )
    
    db.delete(db_user)
    db.commit()
    return None