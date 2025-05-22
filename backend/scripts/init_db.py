import sys
import os
from pathlib import Path

# Adicionar o diretório pai ao path para permitir importações relativas
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models import User

def init_db():
    app = create_app()
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        
        # Verificar se já existe um usuário admin
        admin = User.query.filter_by(email='admin@protestsystem.com').first()
        if not admin:
            # Criar usuário admin
            admin = User(
                email='admin@protestsystem.com',
                username='admin',
                nome_completo='Administrador Sistema',
                cargo='Administrador',
                password='admin123',
                admin=True
            )
            # O atributo self.ativo é definido como True por defeito no __init__ do modelo User.
            # Se fosse necessário definir explicitamente, seria aqui: admin.ativo = True
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado com sucesso!")
        else:
            print("Usuário admin já existe!")

if __name__ == '__main__':
    init_db() 
