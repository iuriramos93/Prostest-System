#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Credor, Devedor, Remessa, Titulo, Desistencia, Erro

def inserir_dados_teste():
    """
    Script para inserir dados de teste no banco de dados.
    Útil para desenvolvimento e testes da integração frontend-backend.
    """
    try:
        print("Iniciando inserção de dados de teste...")
        
        # Verificar se já existem dados
        if User.query.count() > 0:
            print("Banco de dados já possui usuários. Verificando outros dados...")
        else:
            # Inserir usuário admin
            admin = User(
                nome_completo="Administrador",
                email="admin@example.com",
                senha_hash="pbkdf2:sha256:150000$nMmI0PVR$a5cb5707c9b0b6e89a1b5d3a7e4a0b8f9c5d6e3f2a1b0c9d8e7f6a5b4c3d2e1f",  # senha: admin
                ativo=True,
                admin=True
            )
            db.session.add(admin)
            print("Usuário administrador criado.")
        
        # Verificar se já existem credores
        if Credor.query.count() > 0:
            print("Banco de dados já possui credores.")
        else:
            # Inserir credores
            credor1 = Credor(nome="Banco Nacional", cnpj="12345678901234")
            credor2 = Credor(nome="Financeira Crédito Fácil", cnpj="56789012345678")
            credor3 = Credor(nome="Cooperativa Financeira", cnpj="90123456789012")
            db.session.add_all([credor1, credor2, credor3])
            print("Credores criados.")
        
        # Verificar se já existem devedores
        if Devedor.query.count() > 0:
            print("Banco de dados já possui devedores.")
        else:
            # Inserir devedores
            devedor1 = Devedor(nome="João da Silva", cpf_cnpj="12345678901")
            devedor2 = Devedor(nome="Maria Oliveira", cpf_cnpj="98765432109")
            devedor3 = Devedor(nome="Empresa ABC Ltda", cpf_cnpj="12345678901234")
            devedor4 = Devedor(nome="Carlos Pereira", cpf_cnpj="45678912301")
            devedor5 = Devedor(nome="Ana Souza", cpf_cnpj="78901234567")
            db.session.add_all([devedor1, devedor2, devedor3, devedor4, devedor5])
            print("Devedores criados.")
        
        # Commit para garantir que os IDs estejam disponíveis
        db.session.commit()
        
        # Obter IDs para referências
        admin = User.query.filter_by(email="admin@example.com").first()
        credores = Credor.query.all()
        devedores = Devedor.query.all()
        
        # Verificar se já existem remessas
        if Remessa.query.count() > 0:
            print("Banco de dados já possui remessas.")
        else:
            # Inserir remessas
            hoje = datetime.utcnow()
            
            # Remessa 1 - Processada com sucesso
            remessa1 = Remessa(
                nome_arquivo="remessa_protesto_01.xml",
                status="Processado",
                tipo="Protesto",
                quantidade_titulos=5,
                data_envio=hoje - timedelta(days=30),
                data_processamento=hoje - timedelta(days=29),
                usuario_id=admin.id
            )
            
            # Remessa 2 - Com alguns erros
            remessa2 = Remessa(
                nome_arquivo="remessa_protesto_02.xml",
                status="Erro",
                tipo="Protesto",
                quantidade_titulos=3,
                data_envio=hoje - timedelta(days=20),
                data_processamento=hoje - timedelta(days=19),
                usuario_id=admin.id
            )
            
            # Remessa 3 - Mais recente
            remessa3 = Remessa(
                nome_arquivo="remessa_protesto_03.xml",
                status="Processado",
                tipo="Protesto",
                quantidade_titulos=4,
                data_envio=hoje - timedelta(days=10),
                data_processamento=hoje - timedelta(days=9),
                usuario_id=admin.id
            )
            
            # Remessa 4 - Mês anterior
            remessa4 = Remessa(
                nome_arquivo="remessa_protesto_04.xml",
                status="Processado",
                tipo="Protesto",
                quantidade_titulos=6,
                data_envio=hoje - timedelta(days=45),
                data_processamento=hoje - timedelta(days=44),
                usuario_id=admin.id
            )
            
            db.session.add_all([remessa1, remessa2, remessa3, remessa4])
            db.session.commit()
            print("Remessas criadas.")
        
        # Verificar se já existem títulos
        if Titulo.query.count() > 0:
            print("Banco de dados já possui títulos.")
        else:
            # Obter remessas
            remessas = Remessa.query.all()
            
            # Inserir títulos para a remessa 1
            titulos_remessa1 = []
            for i in range(5):
                titulo = Titulo(
                    numero=f"TIT{100+i}",
                    protocolo=f"PROT{100+i}",
                    valor=1000.0 + (i * 500),
                    data_emissao=datetime.utcnow() - timedelta(days=60),
                    data_vencimento=datetime.utcnow() - timedelta(days=30),
                    status="Protestado" if i < 3 else "Pago",
                    devedor_id=devedores[i % len(devedores)].id,
                    credor_id=credores[i % len(credores)].id,
                    remessa_id=remessas[0].id,
                    data_protesto=datetime.utcnow() - timedelta(days=25) if i < 3 else None,
                    data_pagamento=datetime.utcnow() - timedelta(days=20) if i >= 3 else None
                )
                titulos_remessa1.append(titulo)
            
            # Inserir títulos para a remessa 2
            titulos_remessa2 = []
            for i in range(3):
                titulo = Titulo(
                    numero=f"TIT{200+i}",
                    protocolo=f"PROT{200+i}",
                    valor=2000.0 + (i * 750),
                    data_emissao=datetime.utcnow() - timedelta(days=50),
                    data_vencimento=datetime.utcnow() - timedelta(days=20),
                    status="Pendente",
                    devedor_id=devedores[(i+2) % len(devedores)].id,
                    credor_id=credores[(i+1) % len(credores)].id,
                    remessa_id=remessas[1].id
                )
                titulos_remessa2.append(titulo)
            
            # Inserir títulos para a remessa 3
            titulos_remessa3 = []
            for i in range(4):
                titulo = Titulo(
                    numero=f"TIT{300+i}",
                    protocolo=f"PROT{300+i}",
                    valor=1500.0 + (i * 600),
                    data_emissao=datetime.utcnow() - timedelta(days=40),
                    data_vencimento=datetime.utcnow() - timedelta(days=10),
                    status="Protestado" if i % 2 == 0 else "Pendente",
                    devedor_id=devedores[(i+1) % len(devedores)].id,
                    credor_id=credores[(i+2) % len(credores)].id,
                    remessa_id=remessas[2].id,
                    data_protesto=datetime.utcnow() - timedelta(days=5) if i % 2 == 0 else None
                )
                titulos_remessa3.append(titulo)
            
            # Inserir títulos para a remessa 4
            titulos_remessa4 = []
            for i in range(6):
                titulo = Titulo(
                    numero=f"TIT{400+i}",
                    protocolo=f"PROT{400+i}",
                    valor=3000.0 + (i * 1000),
                    data_emissao=datetime.utcnow() - timedelta(days=70),
                    data_vencimento=datetime.utcnow() - timedelta(days=40),
                    status="Protestado" if i < 4 else "Pago",
                    devedor_id=devedores[i % len(devedores)].id,
                    credor_id=credores[i % len(credores)].id,
                    remessa_id=remessas[3].id,
                    data_protesto=datetime.utcnow() - timedelta(days=35) if i < 4 else None,
                    data_pagamento=datetime.utcnow() - timedelta(days=30) if i >= 4 else None
                )
                titulos_remessa4.append(titulo)
            
            db.session.add_all(titulos_remessa1 + titulos_remessa2 + titulos_remessa3 + titulos_remessa4)
            db.session.commit()
            print("Títulos criados.")
        
        # Verificar se já existem erros
        if Erro.query.count() > 0:
            print("Banco de dados já possui erros.")
        else:
            # Obter remessas e títulos
            remessa_com_erro = Remessa.query.filter_by(status="Erro").first()
            titulos = Titulo.query.filter_by(remessa_id=remessa_com_erro.id).all()
            
            # Inserir erros
            erros = []
            for i, titulo in enumerate(titulos):
                erro = Erro(
                    tipo="Validação" if i == 0 else "Processamento",
                    mensagem=f"Erro ao processar título {titulo.numero}: {'Documento inválido' if i == 0 else 'Falha na comunicação com o cartório'}",
                    data_ocorrencia=remessa_com_erro.data_processamento,
                    resolvido=i == 0,  # Primeiro erro já resolvido
                    data_resolucao=datetime.utcnow() - timedelta(days=15) if i == 0 else None,
                    remessa_id=remessa_com_erro.id,
                    titulo_id=titulo.id,
                    usuario_resolucao_id=admin.id if i == 0 else None
                )
                erros.append(erro)
            
            # Erro de sistema
            erro_sistema = Erro(
                tipo="Sistema",
                mensagem="Falha na conexão com o banco de dados",
                data_ocorrencia=datetime.utcnow() - timedelta(days=5),
                resolvido=True,
                data_resolucao=datetime.utcnow() - timedelta(days=4),
                usuario_resolucao_id=admin.id
            )
            erros.append(erro_sistema)
            
            db.session.add_all(erros)
            db.session.commit()
            print("Erros criados.")
        
        # Verificar se já existem desistências
        if Desistencia.query.count() > 0:
            print("Banco de dados já possui desistências.")
        else:
            # Obter títulos protestados
            titulos_protestados = Titulo.query.filter_by(status="Protestado").limit(3).all()
            
            # Inserir desistências
            desistencias = []
            for i, titulo in enumerate(titulos_protestados):
                status = ["Aprovada", "Pendente", "Rejeitada"][i]
                desistencia = Desistencia(
                    titulo_id=titulo.id,
                    motivo=f"Desistência do protesto do título {titulo.numero} - {'Pagamento realizado' if i == 0 else 'Acordo firmado' if i == 1 else 'Erro no cadastro'}",
                    status=status,
                    usuario_id=admin.id,
                    data_solicitacao=datetime.utcnow() - timedelta(days=15-i*5),
                    data_processamento=datetime.utcnow() - timedelta(days=14-i*5) if status != "Pendente" else None,
                    usuario_processamento_id=admin.id if status != "Pendente" else None
                )
                desistencias.append(desistencia)
            
            db.session.add_all(desistencias)
            db.session.commit()
            print("Desistências criadas.")
        
        print("Dados de teste inseridos com sucesso!")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inserir dados de teste: {str(e)}")
        return False

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        inserir_dados_teste()
