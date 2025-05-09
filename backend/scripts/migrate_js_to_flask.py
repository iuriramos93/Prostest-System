#!/usr/bin/env python
"""
Script para migrar dados do servidor Node.js para o servidor Flask.
Este script lê os dados do banco de dados PostgreSQL usado pelo servidor Node.js
e os importa para o banco de dados usado pelo servidor Flask.
"""
import os
import sys
import json
import psycopg2
from datetime import datetime

# Adicionar o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Remessa, Titulo, Credor, Devedor, User, Erro

def connect_to_nodejs_db():
    """Conecta ao banco de dados do Node.js."""
    print("Conectando ao banco de dados do Node.js...")
    
    # Configurações de conexão - ajuste conforme necessário
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="protest_system",
        user="protest_app",
        password="senha_segura",
        port=5432
    )
    
    print("Conexão estabelecida com sucesso!")
    return conn

def migrate_remessas(nodejs_conn, flask_app):
    """Migra as remessas do Node.js para o Flask."""
    print("Migrando remessas...")
    
    # Obter remessas do banco de dados do Node.js
    cursor = nodejs_conn.cursor()
    cursor.execute("SELECT id, nome_arquivo, status, uf, tipo, data_envio, usuario_id, descricao FROM remessas")
    remessas_data = cursor.fetchall()
    
    # Mapear status do Node.js para o Flask
    status_map = {
        'Pendente': 'Pendente',
        'Processado': 'Processado',
        'Erro': 'Erro'
    }
    
    # Mapear tipo do Node.js para o Flask
    tipo_map = {
        'remessa': 'Remessa',
        'desistencia': 'Desistência'
    }
    
    with flask_app.app_context():
        # Criar um mapeamento de IDs do Node.js para IDs do Flask
        remessa_id_map = {}
        
        # Migrar cada remessa
        for remessa_data in remessas_data:
            nodejs_id, nome_arquivo, status, uf, tipo, data_envio, usuario_id, descricao = remessa_data
            
            # Criar nova remessa no Flask
            remessa = Remessa(
                nome_arquivo=nome_arquivo,
                status=status_map.get(status, 'Pendente'),
                uf=uf,
                tipo=tipo_map.get(tipo, 'Remessa'),
                data_envio=data_envio,
                usuario_id=usuario_id,  # Assumindo que os IDs de usuário são os mesmos
                descricao=descricao
            )
            
            db.session.add(remessa)
            db.session.flush()  # Para obter o ID gerado
            
            # Armazenar o mapeamento de IDs
            remessa_id_map[nodejs_id] = remessa.id
        
        # Commit para salvar as remessas
        db.session.commit()
        
        print(f"Migradas {len(remessas_data)} remessas com sucesso!")
        return remessa_id_map

def migrate_titulos(nodejs_conn, flask_app, remessa_id_map):
    """Migra os títulos do Node.js para o Flask."""
    print("Migrando títulos...")
    
    # Obter títulos do banco de dados do Node.js
    cursor = nodejs_conn.cursor()
    cursor.execute("""
        SELECT id, numero, protocolo, valor, data_emissao, data_vencimento, 
               data_protesto, status, remessa_id, credor_id, devedor_id, 
               especie, aceite, nosso_numero
        FROM titulos
    """)
    titulos_data = cursor.fetchall()
    
    # Mapear status do Node.js para o Flask
    status_map = {
        'Pendente': 'Pendente',
        'Protestado': 'Protestado',
        'Pago': 'Pago',
        'Desistido': 'Desistido'
    }
    
    with flask_app.app_context():
        # Criar um mapeamento de IDs do Node.js para IDs do Flask
        titulo_id_map = {}
        
        # Migrar cada título
        for titulo_data in titulos_data:
            (nodejs_id, numero, protocolo, valor, data_emissao, data_vencimento, 
             data_protesto, status, remessa_id, credor_id, devedor_id, 
             especie, aceite, nosso_numero) = titulo_data
            
            # Mapear IDs de remessa
            flask_remessa_id = remessa_id_map.get(remessa_id)
            
            if not flask_remessa_id:
                print(f"Aviso: Remessa ID {remessa_id} não encontrada no mapeamento. Pulando título {nodejs_id}.")
                continue
            
            # Criar novo título no Flask
            titulo = Titulo(
                numero=numero,
                protocolo=protocolo,
                valor=valor,
                data_emissao=data_emissao,
                data_vencimento=data_vencimento,
                data_protesto=data_protesto,
                status=status_map.get(status, 'Pendente'),
                remessa_id=flask_remessa_id,
                credor_id=credor_id,  # Assumindo que os IDs de credor são os mesmos
                devedor_id=devedor_id,  # Assumindo que os IDs de devedor são os mesmos
                especie=especie,
                aceite=aceite == 'S' if aceite else False,
                nosso_numero=nosso_numero
            )
            
            db.session.add(titulo)
            db.session.flush()  # Para obter o ID gerado
            
            # Armazenar o mapeamento de IDs
            titulo_id_map[nodejs_id] = titulo.id
        
        # Commit para salvar os títulos
        db.session.commit()
        
        print(f"Migrados {len(titulo_id_map)} títulos com sucesso!")
        return titulo_id_map

def migrate_data():
    """Migra todos os dados do Node.js para o Flask."""
    print("Iniciando migração de dados do Node.js para o Flask...")
    
    # Conectar ao banco de dados do Node.js
    nodejs_conn = connect_to_nodejs_db()
    
    # Criar a aplicação Flask
    flask_app = create_app()
    
    try:
        # Migrar remessas
        remessa_id_map = migrate_remessas(nodejs_conn, flask_app)
        
        # Migrar títulos
        titulo_id_map = migrate_titulos(nodejs_conn, flask_app, remessa_id_map)
        
        # Aqui você poderia adicionar mais migrações conforme necessário
        # Por exemplo, migrar desistências, erros, etc.
        
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        
    finally:
        # Fechar conexão com o banco de dados do Node.js
        nodejs_conn.close()

if __name__ == "__main__":
    migrate_data() 