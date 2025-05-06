from app import create_app, db
from app.models import User

app = create_app('development')

with app.app_context():
    # Remover usuário admin existente
    User.query.filter_by(email='admin@protestsystem.com').delete()
    
    # Criar novo usuário admin
    admin = User(
        username='admin',
        email='admin@protestsystem.com',
        password='admin123',
        nome_completo='Administrador',
        cargo='Administrador',
        admin=True
    )
    
    db.session.add(admin)
    db.session.commit()
    
    print("Usuário admin criado com sucesso!") 