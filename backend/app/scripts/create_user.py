import sys
import os

# Adiciona o diretório principal do backend ao sys.path
# O script está em backend/app/scripts/create_user.py
# O diretório do pacote 'app' é 'backend/app', então o 'backend' precisa estar no path
path_to_add = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if path_to_add not in sys.path:
    sys.path.insert(0, path_to_add)

from app import create_app, db
from app.models import User # Garanta que User está em app.models

app = create_app("default") # Ou sua configuração específica

def create_or_update_admin_user():
    with app.app_context():
        email_to_check = "admin@protestsystem.com"
        user = User.query.filter_by(email=email_to_check).first()
        
        if user:
            print(f"Usuário {email_to_check} já existe. Atualizando senha e garantindo que está ativo e é admin.")
            user.password = "admin123" # Usa o password.setter
            user.ativo = True # Definido diretamente no objeto, não no construtor
            user.admin = True # Definido diretamente no objeto, não no construtor se não for argumento
        else:
            print(f"Criando novo usuário: {email_to_check}")
            admin_username = "adminprotestsystem"
            existing_username = User.query.filter_by(username=admin_username).first()
            if existing_username and existing_username.email != email_to_check:
                print(f"AVISO: Username {admin_username} já existe para outro usuário. Tentando com email como username.")
                admin_username = email_to_check 
                existing_username_check = User.query.filter_by(username=admin_username).first()
                if existing_username_check and existing_username_check.email != email_to_check:
                     print(f"ERRO: Username {admin_username} (email) também já existe para outro usuário. Não é possível criar o admin.")
                     return

            # Corrigido: 'ativo' não é um argumento do construtor, é definido internamente ou após a criação.
            # 'admin' é um argumento do construtor.
            user = User(
                username=admin_username, 
                email=email_to_check,
                password="admin123",
                nome_completo="Administrador do Sistema Protesto",
                cargo="Administrador",
                admin=True # 'admin' é aceito pelo construtor
            )
            # 'ativo' é True por padrão no __init__ do modelo User, então não precisa ser passado aqui
            # e nem setado explicitamente após, a menos que o padrão mude ou queira garantir.
            db.session.add(user)
        
        try:
            db.session.commit()
            print(f"Usuário {email_to_check} salvo/atualizado com sucesso.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar/atualizar usuário {email_to_check}: {str(e)}")

if __name__ == "__main__":
    create_or_update_admin_user()

