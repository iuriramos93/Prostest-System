from datetime import datetime

from app import db

class User(db.Model):
    """Modelo para usuários do sistema"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nome_completo = db.Column(db.String(100))
    cargo = db.Column(db.String(50))
    ativo = db.Column(db.Boolean, default=True)
    admin = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, username, email, password, nome_completo, cargo=None, admin=False):
        self.username = username
        self.email = email
        self.password = password
        self.nome_completo = nome_completo
        self.cargo = cargo
        self.admin = admin
    
    @property
    def password(self):
        raise AttributeError('password não é um atributo legível')
    
    @password.setter
    def password(self, password):
        # Usando bcrypt para gerar hash seguro da senha
        from flask_bcrypt import Bcrypt
        from flask import current_app
        bcrypt = Bcrypt(current_app)
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        # Verificação usando bcrypt para comparar a senha com o hash armazenado
        from flask_bcrypt import Bcrypt
        from flask import current_app
        bcrypt = Bcrypt(current_app)
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nome_completo': self.nome_completo,
            'cargo': self.cargo,
            'admin': self.admin,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None
        }

class Titulo(db.Model):
    """Modelo para títulos de protesto"""
    __tablename__ = 'titulos'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), index=True)
    protocolo = db.Column(db.String(50), unique=True, index=True)
    valor = db.Column(db.Numeric(10, 2))
    data_emissao = db.Column(db.Date)
    data_vencimento = db.Column(db.Date)
    data_protesto = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), index=True)  # Protestado, Pendente, Pago
    
    # Relacionamentos
    remessa_id = db.Column(db.Integer, db.ForeignKey('remessas.id'))
    credor_id = db.Column(db.Integer, db.ForeignKey('credores.id'))
    devedor_id = db.Column(db.Integer, db.ForeignKey('devedores.id'))
    
    # Dados adicionais
    especie = db.Column(db.String(50))
    aceite = db.Column(db.Boolean, default=False)
    nosso_numero = db.Column(db.String(50))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'protocolo': self.protocolo,
            'valor': float(self.valor) if self.valor else None,
            'data_emissao': self.data_emissao.isoformat() if self.data_emissao else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'data_protesto': self.data_protesto.isoformat() if self.data_protesto else None,
            'status': self.status,
            'remessa_id': self.remessa_id,
            'credor_id': self.credor_id,
            'devedor_id': self.devedor_id,
            'especie': self.especie,
            'aceite': self.aceite,
            'nosso_numero': self.nosso_numero,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

class Remessa(db.Model):
    """Modelo para remessas de títulos"""
    __tablename__ = 'remessas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(100))
    status = db.Column(db.String(20), index=True)  # Processado, Pendente, Erro
    uf = db.Column(db.String(2))
    tipo = db.Column(db.String(20))  # Remessa, Confirmação, Retorno
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    quantidade_titulos = db.Column(db.Integer, default=0)
    task_id = db.Column(db.String(50), nullable=True)  # ID da tarefa assíncrona
    
    # Relacionamentos
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    titulos = db.relationship('Titulo', backref='remessa', lazy='dynamic')
    erros = db.relationship('Erro', backref='remessa', lazy='dynamic')
    
    # Metadados
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    data_processamento = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_arquivo': self.nome_arquivo,
            'data_envio': self.data_envio.isoformat() if self.data_envio else None,
            'status': self.status,
            'uf': self.uf,
            'tipo': self.tipo,
            'quantidade_titulos': self.quantidade_titulos,
            'usuario_id': self.usuario_id,
            'data_processamento': self.data_processamento.isoformat() if self.data_processamento else None,
            'titulos_count': self.titulos.count(),
            'erros_count': self.erros.count()
        }

class Credor(db.Model):
    """Modelo para credores"""
    __tablename__ = 'credores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    documento = db.Column(db.String(20), index=True)  # CNPJ/CPF
    endereco = db.Column(db.String(255))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    
    # Relacionamentos
    titulos = db.relationship('Titulo', backref='credor', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'documento': self.documento,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'uf': self.uf,
            'cep': self.cep
        }

class Devedor(db.Model):
    """Modelo para devedores"""
    __tablename__ = 'devedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    documento = db.Column(db.String(20), index=True)  # CNPJ/CPF
    endereco = db.Column(db.String(255))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    
    # Relacionamentos
    titulos = db.relationship('Titulo', backref='devedor', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'documento': self.documento,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'uf': self.uf,
            'cep': self.cep
        }

class Desistencia(db.Model):
    """Modelo para solicitações de desistência"""
    __tablename__ = 'desistencias'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo_id = db.Column(db.Integer, db.ForeignKey('titulos.id'))
    motivo = db.Column(db.String(255))
    observacoes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), index=True)  # Aprovada, Pendente, Rejeitada
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_processamento = db.Column(db.DateTime, nullable=True)
    
    # Metadados
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    usuario_processamento_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relacionamentos
    titulo = db.relationship('Titulo', backref='desistencias')
    usuario = db.relationship('User', foreign_keys=[usuario_id], backref='desistencias_solicitadas')
    usuario_processamento = db.relationship('User', foreign_keys=[usuario_processamento_id], backref='desistencias_processadas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo_id': self.titulo_id,
            'motivo': self.motivo,
            'observacoes': self.observacoes,
            'status': self.status,
            'data_solicitacao': self.data_solicitacao.isoformat() if self.data_solicitacao else None,
            'data_processamento': self.data_processamento.isoformat() if self.data_processamento else None,
            'usuario_id': self.usuario_id,
            'usuario_processamento_id': self.usuario_processamento_id
        }

class Erro(db.Model):
    """Modelo para erros de processamento"""
    __tablename__ = 'erros'
    
    id = db.Column(db.Integer, primary_key=True)
    remessa_id = db.Column(db.Integer, db.ForeignKey('remessas.id'))
    titulo_id = db.Column(db.Integer, db.ForeignKey('titulos.id'), nullable=True)
    tipo = db.Column(db.String(50))  # Validação, Processamento, Sistema
    mensagem = db.Column(db.Text)
    data_ocorrencia = db.Column(db.DateTime, default=datetime.utcnow)
    resolvido = db.Column(db.Boolean, default=False)
    data_resolucao = db.Column(db.DateTime, nullable=True)
    
    # Metadados
    usuario_resolucao_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relacionamentos
    titulo = db.relationship('Titulo', backref='erros')
    usuario_resolucao = db.relationship('User', backref='erros_resolvidos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'remessa_id': self.remessa_id,
            'titulo_id': self.titulo_id,
            'tipo': self.tipo,
            'mensagem': self.mensagem,
            'data_ocorrencia': self.data_ocorrencia.isoformat() if self.data_ocorrencia else None,
            'resolvido': self.resolvido,
            'data_resolucao': self.data_resolucao.isoformat() if self.data_resolucao else None,
            'usuario_resolucao_id': self.usuario_resolucao_id
        }

class AutorizacaoCancelamento(db.Model):
    """Modelo para autorizações de cancelamento de protesto"""
    __tablename__ = 'autorizacoes_cancelamento'
    
    id = db.Column(db.Integer, primary_key=True)
    arquivo_nome = db.Column(db.String(255))
    codigo_apresentante = db.Column(db.String(3))
    nome_apresentante = db.Column(db.String(45))
    data_movimento = db.Column(db.Date)
    quantidade_solicitacoes = db.Column(db.Integer, default=0)
    sequencia_registro = db.Column(db.String(5), nullable=True)
    data_processamento = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), index=True)  # Processado, Erro, Pendente
    
    # Metadados
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('User', backref='autorizacoes_cancelamento')
    transacoes = db.relationship('TransacaoAutorizacaoCancelamento', backref='autorizacao', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'arquivo_nome': self.arquivo_nome,
            'codigo_apresentante': self.codigo_apresentante,
            'nome_apresentante': self.nome_apresentante,
            'data_movimento': self.data_movimento.isoformat() if self.data_movimento else None,
            'quantidade_solicitacoes': self.quantidade_solicitacoes,
            'sequencia_registro': self.sequencia_registro,
            'data_processamento': self.data_processamento.isoformat() if self.data_processamento else None,
            'status': self.status,
            'usuario_id': self.usuario_id,
            'data_upload': self.data_upload.isoformat() if self.data_upload else None,
            'transacoes_count': self.transacoes.count()
        }

class TransacaoAutorizacaoCancelamento(db.Model):
    """Modelo para transações de autorização de cancelamento"""
    __tablename__ = 'transacoes_autorizacao_cancelamento'
    
    id = db.Column(db.Integer, primary_key=True)
    autorizacao_id = db.Column(db.Integer, db.ForeignKey('autorizacoes_cancelamento.id'))
    titulo_id = db.Column(db.Integer, db.ForeignKey('titulos.id'), nullable=True)
    numero_protocolo = db.Column(db.String(10))
    data_protocolizacao = db.Column(db.Date)
    numero_titulo = db.Column(db.String(11))
    nome_devedor = db.Column(db.String(45))
    valor_titulo = db.Column(db.Numeric(14, 2))
    solicitacao_cancelamento = db.Column(db.String(1))  # Fixo 'A'
    agencia_conta = db.Column(db.String(12), nullable=True)
    carteira_nosso_numero = db.Column(db.String(12), nullable=True)
    numero_controle = db.Column(db.String(6), nullable=True)
    sequencia_registro = db.Column(db.String(5), nullable=True)
    status = db.Column(db.String(20), index=True)  # Processado, Pendente, Erro
    data_processamento = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    titulo = db.relationship('Titulo', backref='autorizacoes_cancelamento')
    
    def to_dict(self):
        return {
            'id': self.id,
            'autorizacao_id': self.autorizacao_id,
            'titulo_id': self.titulo_id,
            'numero_protocolo': self.numero_protocolo,
            'data_protocolizacao': self.data_protocolizacao.isoformat() if self.data_protocolizacao else None,
            'numero_titulo': self.numero_titulo,
            'nome_devedor': self.nome_devedor,
            'valor_titulo': float(self.valor_titulo) if self.valor_titulo else None,
            'solicitacao_cancelamento': self.solicitacao_cancelamento,
            'agencia_conta': self.agencia_conta,
            'carteira_nosso_numero': self.carteira_nosso_numero,
            'numero_controle': self.numero_controle,
            'sequencia_registro': self.sequencia_registro,
            'status': self.status,
            'data_processamento': self.data_processamento.isoformat() if self.data_processamento else None
        }