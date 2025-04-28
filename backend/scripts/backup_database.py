#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de backup automatizado para o banco de dados do Sistema de Protesto

Este script realiza o backup do banco de dados PostgreSQL e pode ser configurado
para execução automática via cron ou agendador de tarefas do Windows.

Uso:
    python backup_database.py [--config CONFIG_FILE]

Argumentos opcionais:
    --config CONFIG_FILE    Caminho para o arquivo de configuração (padrão: config.json)
"""

import os
import sys
import json
import time
import shutil
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("backup")

# Configurações padrão
DEFAULT_CONFIG = {
    "backup_dir": "../backups",
    "db_name": "protest_db",
    "db_user": "postgres",
    "db_host": "localhost",
    "db_port": "5432",
    "retention_days": 30,
    "compression": True,
    "notify_email": "",
    "s3_backup": False,
    "s3_bucket": "",
    "s3_prefix": "backups/"
}

def parse_args():
    """Analisa os argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description="Script de backup do banco de dados")
    parser.add_argument(
        "--config", 
        default="config.json", 
        help="Caminho para o arquivo de configuração (padrão: config.json)"
    )
    return parser.parse_args()

def load_config(config_file):
    """Carrega a configuração do arquivo JSON"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Mesclar com configurações padrão
                return {**DEFAULT_CONFIG, **config}
        else:
            logger.warning(f"Arquivo de configuração {config_file} não encontrado. Usando configurações padrão.")
            return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Erro ao carregar configuração: {str(e)}")
        return DEFAULT_CONFIG

def create_backup_dir(backup_dir):
    """Cria o diretório de backup se não existir"""
    try:
        os.makedirs(backup_dir, exist_ok=True)
        logger.info(f"Diretório de backup: {backup_dir}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar diretório de backup: {str(e)}")
        return False

def generate_backup_filename(db_name):
    """Gera um nome de arquivo para o backup com timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{db_name}_{timestamp}.sql"

def run_pg_dump(config, backup_file):
    """Executa o pg_dump para criar o backup"""
    try:
        # Construir comando pg_dump
        cmd = [
            "pg_dump",
            "-h", config["db_host"],
            "-p", config["db_port"],
            "-U", config["db_user"],
            "-d", config["db_name"],
            "-f", backup_file,
            "-v",  # Verbose
            "--format=c"  # Formato personalizado (comprimido)
        ]
        
        # Configurar variável de ambiente para senha
        env = os.environ.copy()
        if "db_password" in config:
            env["PGPASSWORD"] = config["db_password"]
        
        # Executar comando
        logger.info(f"Iniciando backup do banco {config['db_name']}...")
        process = subprocess.run(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode == 0:
            logger.info(f"Backup concluído com sucesso: {backup_file}")
            return True
        else:
            logger.error(f"Erro ao executar pg_dump: {process.stderr}")
            return False
    except Exception as e:
        logger.error(f"Erro durante o backup: {str(e)}")
        return False

def compress_backup(backup_file):
    """Comprime o arquivo de backup usando gzip"""
    try:
        # Se já estiver usando formato personalizado do pg_dump, não precisa comprimir
        if backup_file.endswith('.sql'):
            compressed_file = f"{backup_file}.gz"
            logger.info(f"Comprimindo backup: {backup_file} -> {compressed_file}")
            
            with open(backup_file, 'rb') as f_in:
                import gzip
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remover arquivo original após compressão
            os.remove(backup_file)
            logger.info("Compressão concluída")
            return compressed_file
        return backup_file
    except Exception as e:
        logger.error(f"Erro ao comprimir backup: {str(e)}")
        return backup_file

def upload_to_s3(backup_file, config):
    """Faz upload do backup para o Amazon S3"""
    if not config["s3_backup"] or not config["s3_bucket"]:
        return False
    
    try:
        import boto3
        s3 = boto3.client('s3')
        
        # Nome do objeto S3 (key)
        filename = os.path.basename(backup_file)
        s3_key = f"{config['s3_prefix']}{filename}"
        
        logger.info(f"Iniciando upload para S3: {config['s3_bucket']}/{s3_key}")
        s3.upload_file(backup_file, config['s3_bucket'], s3_key)
        logger.info("Upload para S3 concluído com sucesso")
        return True
    except ImportError:
        logger.warning("Biblioteca boto3 não encontrada. Instale com 'pip install boto3' para habilitar backup no S3.")
        return False
    except Exception as e:
        logger.error(f"Erro ao fazer upload para S3: {str(e)}")
        return False

def cleanup_old_backups(backup_dir, retention_days):
    """Remove backups antigos com base na política de retenção"""
    try:
        now = time.time()
        count = 0
        
        for f in os.listdir(backup_dir):
            if f.endswith(".sql") or f.endswith(".sql.gz") or f.endswith(".dump"):
                file_path = os.path.join(backup_dir, f)
                file_age = now - os.path.getmtime(file_path)
                # Converter dias para segundos
                if file_age > (retention_days * 86400):
                    os.remove(file_path)
                    count += 1
                    logger.info(f"Backup antigo removido: {f}")
        
        if count > 0:
            logger.info(f"Limpeza concluída: {count} backups antigos removidos")
        else:
            logger.info("Nenhum backup antigo para remover")
        return True
    except Exception as e:
        logger.error(f"Erro ao limpar backups antigos: {str(e)}")
        return False

def send_notification(success, backup_file, config):
    """Envia notificação por e-mail sobre o resultado do backup"""
    if not config.get("notify_email"):
        return
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        # Configurações de e-mail
        smtp_server = config.get("smtp_server", "localhost")
        smtp_port = config.get("smtp_port", 25)
        smtp_user = config.get("smtp_user", "")
        smtp_password = config.get("smtp_password", "")
        from_email = config.get("from_email", "backup@protestsystem.com")
        
        # Preparar mensagem
        subject = f"{'✅ Sucesso' if success else '❌ Falha'} - Backup do Banco de Dados {config['db_name']}"
        body = f"""Status do backup do banco de dados:

Banco de dados: {config['db_name']}
Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {'Sucesso' if success else 'Falha'}
"""
        
        if success:
            body += f"Arquivo de backup: {os.path.basename(backup_file)}\nTamanho: {os.path.getsize(backup_file) / (1024*1024):.2f} MB\n"
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = config["notify_email"]
        
        # Enviar e-mail
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Notificação enviada para {config['notify_email']}")
    except ImportError:
        logger.warning("Não foi possível enviar notificação por e-mail. Verifique se as bibliotecas necessárias estão instaladas.")
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {str(e)}")

def main():
    """Função principal do script de backup"""
    args = parse_args()
    config = load_config(args.config)
    
    # Criar diretório de backup
    backup_dir = os.path.abspath(config["backup_dir"])
    if not create_backup_dir(backup_dir):
        return 1
    
    # Gerar nome do arquivo de backup
    backup_filename = generate_backup_filename(config["db_name"])
    backup_file = os.path.join(backup_dir, backup_filename)
    
    # Executar backup
    success = run_pg_dump(config, backup_file)
    
    if success and config["compression"]:
        backup_file = compress_backup(backup_file)
    
    # Upload para S3 se configurado
    if success and config["s3_backup"]:
        upload_to_s3(backup_file, config)
    
    # Limpar backups antigos
    cleanup_old_backups(backup_dir, config["retention_days"])
    
    # Enviar notificação
    send_notification(success, backup_file, config)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())