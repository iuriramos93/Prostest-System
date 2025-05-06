-- Criar tabela users
CREATE TABLE IF NOT EXISTS users (
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

-- Inserir usuário admin
INSERT INTO users (username, email, password_hash, nome_completo, cargo, ativo, admin)
VALUES (
    'admin',
    'admin@protestsystem.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQN3J9.5KJHy',
    'Administrador',
    'Administrador',
    true,
    true
); 