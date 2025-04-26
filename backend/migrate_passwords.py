import os
import sys
from flask import Flask
from flask_bcrypt import Bcrypt
from app import create_app, db
from app.models import User

# Criar uma aplicação Flask para o contexto
app = create_app('development')
bcrypt = Bcrypt(app)

def migrate_passwords():
    """Migra senhas em texto puro para hash bcrypt"""
    with app.app_context():
        users = User.query.all()
        count = 0
        
        print(f"Encontrados {len(users)} usuários para migração de senhas.")
        
        for user in users:
            # Verificar se a senha já está em formato hash (mais de 50 caracteres)
            if user.password_hash and len(user.password_hash) < 50:
                # Senha em texto puro, precisa ser convertida
                plain_password = user.password_hash
                user.password_hash = bcrypt.generate_password_hash(plain_password).decode('utf-8')
                count += 1
        
        if count > 0:
            db.session.commit()
            print(f"Migração concluída! {count} senhas foram convertidas para formato seguro.")
        else:
            print("Nenhuma senha precisou ser migrada.")

if __name__ == '__main__':
    migrate_passwords()