# Système de Gestion Bancaire Numérique


## Prérequis
- Python 3.10+
- PostgreSQL
- `pip`

## Installation
1. Cloner le dépôt : `git clone <https://github.com/inazabdjio/api_banque_biometrique>`
2. Créer l'environnement : `python3 -m venv venv && source venv/bin/activate`
3. Installer les dépendances : `pip install -r requirements.txt`

## Lancement des tests
Pour exécuter la suite de tests unitaires et d'intégration :
Taper dans le terminal:

DATABASE_URL="postgresql://user:ton_mon_passe@localhost:5432/ta_base_donnees_test" pytest tests/test_banking.py -v --html=rapport_test.html
