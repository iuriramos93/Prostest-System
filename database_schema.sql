-- Esquema do Banco de Dados para o Sistema de Protesto
-- PostgreSQL

-- Criação do banco de dados
CREATE DATABASE protest_system;

-- Conectar ao banco de dados
\c protest_system

-- Tabela de usuários
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    nome_completo VARCHAR(100) NOT NULL,
    cargo VARCHAR(50),
    ativo BOOLEAN DEFAULT TRUE,
    admin BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso TIMESTAMP
);

-- Índices para a tabela users
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Tabela de credores
CREATE TABLE credores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    documento VARCHAR(20) NOT NULL,
    endereco VARCHAR(255),
    cidade VARCHAR(100),
    uf VARCHAR(2),
    cep VARCHAR(10)
);

-- Índices para a tabela credores
CREATE INDEX idx_credores_documento ON credores(documento);

-- Tabela de devedores
CREATE TABLE devedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    documento VARCHAR(20) NOT NULL,
    endereco VARCHAR(255),
    cidade VARCHAR(100),
    uf VARCHAR(2),
    cep VARCHAR(10)
);

-- Índices para a tabela devedores
CREATE INDEX idx_devedores_documento ON devedores(documento);

-- Tabela de remessas
CREATE TABLE remessas (
    id SERIAL PRIMARY KEY,
    nome_arquivo VARCHAR(255) NOT NULL,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    uf VARCHAR(2),
    tipo VARCHAR(20) NOT NULL,
    quantidade_titulos INTEGER DEFAULT 0,
    usuario_id INTEGER REFERENCES users(id),
    data_processamento TIMESTAMP
);

-- Índices para a tabela remessas
CREATE INDEX idx_remessas_status ON remessas(status);
CREATE INDEX idx_remessas_usuario_id ON remessas(usuario_id);

-- Tabela de títulos
CREATE TABLE titulos (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) NOT NULL,
    protocolo VARCHAR(50) UNIQUE NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    data_emissao DATE,
    data_vencimento DATE,
    data_protesto DATE,
    status VARCHAR(20) NOT NULL,
    remessa_id INTEGER REFERENCES remessas(id),
    credor_id INTEGER REFERENCES credores(id),
    devedor_id INTEGER REFERENCES devedores(id),
    especie VARCHAR(50),
    aceite BOOLEAN DEFAULT FALSE,
    nosso_numero VARCHAR(50),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para a tabela titulos
CREATE INDEX idx_titulos_numero ON titulos(numero);
CREATE INDEX idx_titulos_protocolo ON titulos(protocolo);
CREATE INDEX idx_titulos_status ON titulos(status);
CREATE INDEX idx_titulos_remessa_id ON titulos(remessa_id);
CREATE INDEX idx_titulos_credor_id ON titulos(credor_id);
CREATE INDEX idx_titulos_devedor_id ON titulos(devedor_id);

-- Tabela de desistências
CREATE TABLE desistencias (
    id SERIAL PRIMARY KEY,
    titulo_id INTEGER REFERENCES titulos(id),
    motivo VARCHAR(255) NOT NULL,
    observacoes TEXT,
    status VARCHAR(20) NOT NULL,
    data_solicitacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_processamento TIMESTAMP,
    usuario_id INTEGER REFERENCES users(id),
    usuario_processamento_id INTEGER REFERENCES users(id)
);

-- Índices para a tabela desistencias
CREATE INDEX idx_desistencias_titulo_id ON desistencias(titulo_id);
CREATE INDEX idx_desistencias_status ON desistencias(status);
CREATE INDEX idx_desistencias_usuario_id ON desistencias(usuario_id);

-- Tabela de erros
CREATE TABLE erros (
    id SERIAL PRIMARY KEY,
    remessa_id INTEGER REFERENCES remessas(id),
    titulo_id INTEGER REFERENCES titulos(id),
    tipo VARCHAR(50) NOT NULL,
    mensagem TEXT NOT NULL,
    data_ocorrencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolvido BOOLEAN DEFAULT FALSE,
    data_resolucao TIMESTAMP,
    usuario_resolucao_id INTEGER REFERENCES users(id)
);

-- Índices para a tabela erros
CREATE INDEX idx_erros_remessa_id ON erros(remessa_id);
CREATE INDEX idx_erros_titulo_id ON erros(titulo_id);
CREATE INDEX idx_erros_resolvido ON erros(resolvido);

-- Tabela de autorizações de cancelamento
CREATE TABLE autorizacoes_cancelamento (
    id SERIAL PRIMARY KEY,
    arquivo_nome VARCHAR(255) NOT NULL,
    codigo_apresentante VARCHAR(3) NOT NULL,
    nome_apresentante VARCHAR(45) NOT NULL,
    data_movimento DATE NOT NULL,
    quantidade_solicitacoes INTEGER DEFAULT 0,
    sequencia_registro VARCHAR(5),
    data_processamento TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    usuario_id INTEGER REFERENCES users(id),
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para a tabela autorizacoes_cancelamento
CREATE INDEX idx_autorizacoes_status ON autorizacoes_cancelamento(status);
CREATE INDEX idx_autorizacoes_usuario_id ON autorizacoes_cancelamento(usuario_id);

-- Tabela de transações de autorização de cancelamento
CREATE TABLE transacoes_autorizacao_cancelamento (
    id SERIAL PRIMARY KEY,
    autorizacao_id INTEGER REFERENCES autorizacoes_cancelamento(id),
    titulo_id INTEGER REFERENCES titulos(id),
    numero_protocolo VARCHAR(10) NOT NULL,
    data_protocolizacao DATE NOT NULL,
    numero_titulo VARCHAR(11) NOT NULL,
    nome_devedor VARCHAR(45) NOT NULL,
    valor_titulo NUMERIC(14, 2) NOT NULL,
    solicitacao_cancelamento VARCHAR(1) NOT NULL,
    agencia_conta VARCHAR(12),
    carteira_nosso_numero VARCHAR(12),
    numero_controle VARCHAR(6),
    sequencia_registro VARCHAR(5),
    status VARCHAR(20) NOT NULL,
    data_processamento TIMESTAMP
);
-- Índices para a tabela transacoes_autorizacao_cancelamento
CREATE INDEX idx_transacoes_autorizacao_id ON transacoes_autorizacao_cancelamento(autorizacao_id);
CREATE INDEX idx_transacoes_titulo_id ON transacoes_autorizacao_cancelamento(titulo_id);
CREATE INDEX idx_transacoes_status ON transacoes_autorizacao_cancelamento(status);

-- Trigger para atualizar data_atualizacao em titulos
CREATE OR REPLACE FUNCTION update_data_atualizacao_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_atualizacao = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_titulos_data_atualizacao
BEFORE UPDATE ON titulos
FOR EACH ROW
EXECUTE FUNCTION update_data_atualizacao_column();

-- Função para atualizar quantidade_titulos em remessas
CREATE OR REPLACE FUNCTION update_quantidade_titulos()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE remessas SET quantidade_titulos = quantidade_titulos + 1 WHERE id = NEW.remessa_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE remessas SET quantidade_titulos = quantidade_titulos - 1 WHERE id = OLD.remessa_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_remessas_quantidade_titulos
AFTER INSERT OR DELETE ON titulos
FOR EACH ROW
EXECUTE FUNCTION update_quantidade_titulos();

-- Comentários nas tabelas
COMMENT ON TABLE users IS 'Usuários do sistema';
COMMENT ON TABLE credores IS 'Credores dos títulos';
COMMENT ON TABLE devedores IS 'Devedores dos títulos';
COMMENT ON TABLE remessas IS 'Remessas de títulos enviadas';
COMMENT ON TABLE titulos IS 'Títulos de protesto';
COMMENT ON TABLE desistencias IS 'Solicitações de desistência de protesto';
COMMENT ON TABLE erros IS 'Erros de processamento';
COMMENT ON TABLE autorizacoes_cancelamento IS 'Autorizações de cancelamento de protesto';
COMMENT ON TABLE transacoes_autorizacao_cancelamento IS 'Transações de autorização de cancelamento';

-- Criação de usuário para a aplicação (altere a senha conforme necessário)
CREATE USER protest_app WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE protest_system TO protest_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO protest_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO protest_app;

-- Instruções para backup e restauração
-- Para fazer backup:
-- pg_dump -U postgres protest_system > backup_protest_system.sql

-- Para restaurar:
-- psql -U postgres -d protest_system -f backup_protest_system.sql
