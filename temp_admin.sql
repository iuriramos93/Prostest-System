-- Remover usuário admin existente
DELETE FROM users WHERE email = 'admin@protestsystem.com';

-- Inserir novo usuário admin
INSERT INTO users (username, email, password_hash, nome_completo, cargo, ativo, admin)
VALUES (
    'admin',
    'admin@protestsystem.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBAQN3J9.5KJHy', -- senha: admin123
    'Administrador',
    'Administrador',
    true,
    true
); 