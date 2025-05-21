#!/usr/bin/env python3

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('/home/ubuntu/Prostest-System/.env')

# Configurações do banco de dados
db_config = {
    'dbname': os.getenv('POSTGRES_DB', 'protest_system'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'host': 'db',  # Usando o hostname 'db' do docker-compose
    'port': os.getenv('POSTGRES_PORT', '5432')
}

def check_column_exists(conn, table, column):
    """Verifica se uma coluna existe na tabela"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        """, (table, column))
        return cur.fetchone() is not None

def add_column(conn, table, column, data_type):
    """Adiciona uma coluna à tabela se ela não existir"""
    with conn.cursor() as cur:
        if not check_column_exists(conn, table, column):
            print(f"Adicionando coluna {column} à tabela {table}...")
            cur.execute(
                sql.SQL("ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} {}").format(
                    sql.Identifier(table),
                    sql.Identifier(column),
                    sql.SQL(data_type)
                )
            )
            conn.commit()
            print(f"Coluna {column} adicionada com sucesso!")
            return True
        else:
            print(f"Coluna {column} já existe na tabela {table}.")
            return False

def main():
    """Função principal para aplicar a migração"""
    try:
        # Conectar ao banco de dados
        print("Conectando ao banco de dados...")
        print(f"Configurações: {db_config}")
        conn = psycopg2.connect(**db_config)
        
        # Adicionar coluna task_id à tabela remessas
        add_column(conn, 'remessas', 'task_id', 'VARCHAR(50)')
        
        # Fechar conexão
        conn.close()
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro ao aplicar migração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
