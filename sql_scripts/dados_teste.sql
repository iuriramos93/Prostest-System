-- Dados de teste para o Sistema de Protesto
-- PostgreSQL

-- Inserir usuários
INSERT INTO users (username, email, password_hash, nome_completo, cargo, ativo, admin, ultimo_acesso)
VALUES
('admin', 'admin@protestosystem.com', 'pbkdf2:sha256:150000$abc123$abcdef1234567890abcdef1234567890', 'Administrador Sistema', 'Administrador', TRUE, TRUE, CURRENT_TIMESTAMP),
('maria.silva', 'maria.silva@protestosystem.com', 'pbkdf2:sha256:150000$def456$abcdef1234567890abcdef1234567890', 'Maria Silva', 'Analista', TRUE, FALSE, CURRENT_TIMESTAMP),
('joao.santos', 'joao.santos@protestosystem.com', 'pbkdf2:sha256:150000$ghi789$abcdef1234567890abcdef1234567890', 'João Santos', 'Operador', TRUE, FALSE, CURRENT_TIMESTAMP),
('ana.oliveira', 'ana.oliveira@protestosystem.com', 'pbkdf2:sha256:150000$jkl012$abcdef1234567890abcdef1234567890', 'Ana Oliveira', 'Gerente', TRUE, FALSE, CURRENT_TIMESTAMP),
('carlos.pereira', 'carlos.pereira@protestosystem.com', 'pbkdf2:sha256:150000$mno345$abcdef1234567890abcdef1234567890', 'Carlos Pereira', 'Supervisor', TRUE, FALSE, CURRENT_TIMESTAMP);

-- Inserir credores
INSERT INTO credores (nome, documento, endereco, cidade, uf, cep)
VALUES
('Banco Nacional S.A.', '60.701.190/0001-04', 'Av. Paulista, 1000', 'São Paulo', 'SP', '01310-100'),
('Financeira Crédito Rápido', '33.052.953/0001-75', 'Rua da Quitanda, 50', 'Rio de Janeiro', 'RJ', '20091-005'),
('Cooperativa de Crédito Central', '45.283.524/0001-09', 'Av. Getúlio Vargas, 500', 'Belo Horizonte', 'MG', '30112-020'),
('Banco Investimentos S.A.', '17.351.180/0001-59', 'Av. Brigadeiro Faria Lima, 3500', 'São Paulo', 'SP', '04538-132'),
('Factoring Express Ltda.', '22.761.413/0001-60', 'Rua XV de Novembro, 200', 'Curitiba', 'PR', '80020-310');

-- Inserir devedores
INSERT INTO devedores (nome, documento, endereco, cidade, uf, cep)
VALUES
('Comércio de Eletrônicos Ltda.', '12.345.678/0001-90', 'Rua Augusta, 1500', 'São Paulo', 'SP', '01304-001'),
('João Carlos da Silva', '123.456.789-00', 'Av. Rio Branco, 156', 'Rio de Janeiro', 'RJ', '20040-901'),
('Supermercado Economia Ltda.', '98.765.432/0001-10', 'Av. Amazonas, 2000', 'Belo Horizonte', 'MG', '30180-001'),
('Maria Aparecida Santos', '987.654.321-00', 'Rua Padre Chagas, 79', 'Porto Alegre', 'RS', '90570-080'),
('Indústria Metalúrgica Nacional', '45.678.901/0001-23', 'Av. Industrial, 1000', 'São Bernardo do Campo', 'SP', '09696-000'),
('Pedro Henrique Oliveira', '456.789.012-34', 'Rua das Palmeiras, 500', 'Salvador', 'BA', '40150-120'),
('Distribuidora Alimentos Ltda.', '78.901.234/0001-56', 'Av. Cristiano Machado, 3000', 'Belo Horizonte', 'MG', '31910-800'),
('Ana Paula Ferreira', '567.890.123-45', 'Rua Oscar Freire, 123', 'São Paulo', 'SP', '01426-001'),
('Construtora Horizonte S.A.', '34.567.890/0001-78', 'Av. Afonso Pena, 1500', 'Belo Horizonte', 'MG', '30130-921'),
('Carlos Eduardo Martins', '678.901.234-56', 'Av. Boa Viagem, 1000', 'Recife', 'PE', '51011-000');

-- Inserir remessas
INSERT INTO remessas (nome_arquivo, status, uf, tipo, quantidade_titulos, usuario_id, data_processamento)
VALUES
('REMESSA_20230501.txt', 'PROCESSADA', 'SP', 'ENVIO', 3, 1, CURRENT_TIMESTAMP - INTERVAL '30 days'),
('REMESSA_20230515.txt', 'PROCESSADA', 'RJ', 'ENVIO', 2, 2, CURRENT_TIMESTAMP - INTERVAL '15 days'),
('REMESSA_20230601.txt', 'PROCESSADA', 'MG', 'ENVIO', 2, 3, CURRENT_TIMESTAMP - INTERVAL '7 days'),
('REMESSA_20230615.txt', 'EM_PROCESSAMENTO', 'SP', 'ENVIO', 2, 4, NULL),
('REMESSA_20230620.txt', 'ERRO', 'PR', 'ENVIO', 1, 5, NULL);

-- Inserir títulos
INSERT INTO titulos (numero, protocolo, valor, data_emissao, data_vencimento, data_protesto, status, remessa_id, credor_id, devedor_id, especie, aceite, nosso_numero)
VALUES
('12345', 'PROT-001-2023', 1500.00, CURRENT_DATE - INTERVAL '60 days', CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE - INTERVAL '15 days', 'PROTESTADO', 1, 1, 1, 'DMI', TRUE, '001001'),
('23456', 'PROT-002-2023', 2300.50, CURRENT_DATE - INTERVAL '55 days', CURRENT_DATE - INTERVAL '25 days', CURRENT_DATE - INTERVAL '10 days', 'PROTESTADO', 1, 1, 2, 'CBI', FALSE, '001002'),
('34567', 'PROT-003-2023', 5000.00, CURRENT_DATE - INTERVAL '50 days', CURRENT_DATE - INTERVAL '20 days', NULL, 'EM_CARTORIO', 1, 2, 3, 'DMI', TRUE, '002001'),
('45678', 'PROT-004-2023', 1200.75, CURRENT_DATE - INTERVAL '45 days', CURRENT_DATE - INTERVAL '15 days', NULL, 'ENVIADO', 2, 2, 4, 'NP', TRUE, '002002'),
('56789', 'PROT-005-2023', 3450.25, CURRENT_DATE - INTERVAL '40 days', CURRENT_DATE - INTERVAL '10 days', NULL, 'ENVIADO', 2, 3, 5, 'DMI', FALSE, '003001'),
('67890', 'PROT-006-2023', 7800.00, CURRENT_DATE - INTERVAL '35 days', CURRENT_DATE - INTERVAL '5 days', NULL, 'AGUARDANDO_ENVIO', 3, 3, 6, 'CBI', TRUE, '003002'),
('78901', 'PROT-007-2023', 950.30, CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE, NULL, 'AGUARDANDO_ENVIO', 3, 4, 7, 'DMI', FALSE, '004001'),
('89012', 'PROT-008-2023', 2100.00, CURRENT_DATE - INTERVAL '25 days', CURRENT_DATE + INTERVAL '5 days', NULL, 'REGISTRADO', 4, 4, 8, 'NP', TRUE, '004002'),
('90123', 'PROT-009-2023', 4300.80, CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE + INTERVAL '10 days', NULL, 'REGISTRADO', 4, 5, 9, 'DMI', TRUE, '005001'),
('01234', 'PROT-010-2023', 1750.45, CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE + INTERVAL '15 days', NULL, 'ERRO', 5, 5, 10, 'CBI', FALSE, '005002');

-- Inserir desistências
INSERT INTO desistencias (titulo_id, motivo, observacoes, status, data_solicitacao, data_processamento, usuario_id, usuario_processamento_id)
VALUES
(1, 'PAGAMENTO', 'Devedor efetuou o pagamento integral', 'PROCESSADA', CURRENT_TIMESTAMP - INTERVAL '14 days', CURRENT_TIMESTAMP - INTERVAL '13 days', 2, 1),
(2, 'ACORDO', 'Acordo firmado entre as partes', 'PROCESSADA', CURRENT_TIMESTAMP - INTERVAL '9 days', CURRENT_TIMESTAMP - INTERVAL '8 days', 3, 1),
(3, 'ERRO_CADASTRO', 'Título cadastrado com valor incorreto', 'EM_PROCESSAMENTO', CURRENT_TIMESTAMP - INTERVAL '5 days', NULL, 4, NULL),
(5, 'PAGAMENTO', 'Pagamento realizado em atraso', 'PENDENTE', CURRENT_TIMESTAMP - INTERVAL '2 days', NULL, 5, NULL);

-- Inserir erros
INSERT INTO erros (remessa_id, titulo_id, tipo, mensagem, data_ocorrencia, resolvido, data_resolucao, usuario_resolucao_id)
VALUES
(5, 10, 'VALIDACAO', 'Documento do devedor inválido', CURRENT_TIMESTAMP - INTERVAL '15 days', TRUE, CURRENT_TIMESTAMP - INTERVAL '14 days', 1),
(4, 9, 'PROCESSAMENTO', 'Falha na comunicação com o cartório', CURRENT_TIMESTAMP - INTERVAL '10 days', TRUE, CURRENT_TIMESTAMP - INTERVAL '9 days', 1),
(3, 7, 'VALIDACAO', 'Data de vencimento inválida', CURRENT_TIMESTAMP - INTERVAL '7 days', TRUE, CURRENT_TIMESTAMP - INTERVAL '6 days', 2),
(2, 5, 'SISTEMA', 'Erro interno no processamento', CURRENT_TIMESTAMP - INTERVAL '5 days', FALSE, NULL, NULL),
(1, 3, 'VALIDACAO', 'Valor do título zerado ou negativo', CURRENT_TIMESTAMP - INTERVAL '3 days', FALSE, NULL, NULL);

-- Inserir autorizações de cancelamento
INSERT INTO autorizacoes_cancelamento (arquivo_nome, codigo_apresentante, nome_apresentante, data_movimento, quantidade_solicitacoes, sequencia_registro, data_processamento, status, usuario_id)
VALUES
('CANC_20230510.txt', '001', 'Banco Nacional S.A.', CURRENT_DATE - INTERVAL '20 days', 2, '00001', CURRENT_TIMESTAMP - INTERVAL '19 days', 'PROCESSADA', 1),
('CANC_20230525.txt', '002', 'Financeira Crédito Rápido', CURRENT_DATE - INTERVAL '15 days', 1, '00002', CURRENT_TIMESTAMP - INTERVAL '14 days', 'PROCESSADA', 2),
('CANC_20230605.txt', '003', 'Cooperativa de Crédito Central', CURRENT_DATE - INTERVAL '10 days', 1, '00003', NULL, 'PENDENTE', 3),
('CANC_20230615.txt', '004', 'Banco Investimentos S.A.', CURRENT_DATE - INTERVAL '5 days', 1, '00004', NULL, 'ERRO', 4);

-- Inserir transações de autorização de cancelamento
INSERT INTO transacoes_autorizacao_cancelamento (autorizacao_id, titulo_id, numero_protocolo, data_protocolizacao, numero_titulo, nome_devedor, valor_titulo, solicitacao_cancelamento, agencia_conta, carteira_nosso_numero, numero_controle, sequencia_registro, status, data_processamento)
VALUES
(1, 1, '0000000001', CURRENT_DATE - INTERVAL '25 days', '00000012345', 'Comércio de Eletrônicos Ltda.', 1500.00, 'S', '0001/123456', '001/001001', '000001', '00001', 'PROCESSADA', CURRENT_TIMESTAMP - INTERVAL '19 days'),
(1, 2, '0000000002', CURRENT_DATE - INTERVAL '25 days', '00000023456', 'João Carlos da Silva', 2300.50, 'S', '0001/123456', '001/001002', '000002', '00002', 'PROCESSADA', CURRENT_TIMESTAMP - INTERVAL '19 days'),
(2, 4, '0000000004', CURRENT_DATE - INTERVAL  '20 days', '00000045678', 'Maria Aparecida Santos', 1200.75, 'S', '0002/234567', '002/002002', '000003', '00003', 'PROCESSADA', CURRENT_TIMESTAMP - INTERVAL '14 days'),
(3, 6, '0000000006', CURRENT_DATE - INTERVAL '15 days', '00000067890', 'Pedro Henrique Oliveira', 7800.00, 'S', '0003/345678', '003/003002', '000004', '00004', 'PENDENTE', NULL),
(4, 8, '0000000008', CURRENT_DATE - INTERVAL '10 days', '00000089012', 'Ana Paula Ferreira', 2100.00, 'S', '0004/456789', '004/004002', '000005', '00005', 'ERRO', NULL);