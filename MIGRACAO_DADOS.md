# Plano de Migração de Dados para o Sistema de Protesto

Este documento descreve o processo de migração de dados de sistemas legados para o Sistema de Protesto.

## Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Etapas da Migração](#etapas-da-migração)
4. [Mapeamento de Dados](#mapeamento-de-dados)
5. [Scripts de Migração](#scripts-de-migração)
6. [Validação e Verificação](#validação-e-verificação)
7. [Rollback](#rollback)
8. [Cronograma](#cronograma)

## Visão Geral

A migração de dados é um processo crítico para garantir a continuidade das operações ao migrar de sistemas legados para o novo Sistema de Protesto. Este documento fornece um guia detalhado para realizar essa migração de forma segura e eficiente.

## Pré-requisitos

### Ambiente

- Sistema de Protesto instalado e configurado
- Acesso ao banco de dados do sistema legado
- Permissões adequadas para leitura/escrita em ambos os sistemas
- Espaço em disco suficiente para backups e arquivos temporários

### Ferramentas

- Scripts de migração Python (disponíveis em `/backend/app/scripts/migracao/`)
- Utilitários de exportação do banco de dados legado
- Ferramentas de validação de dados

## Etapas da Migração

### 1. Análise e Planejamento

- Identificar todas as entidades de dados no sistema legado
- Mapear entidades para o esquema do novo sistema
- Identificar transformações necessárias
- Definir ordem de migração considerando dependências entre entidades

### 2. Extração de Dados

- Exportar dados do sistema legado em formato CSV ou SQL
- Documentar a estrutura dos dados exportados
- Verificar integridade dos arquivos exportados

### 3. Transformação

- Limpar dados (remover duplicatas, corrigir inconsistências)
- Converter formatos de dados conforme necessário
- Aplicar regras de negócio para adequação ao novo sistema

### 4. Carregamento

- Carregar dados no banco de dados do novo sistema
- Seguir a ordem definida no planejamento
- Registrar logs detalhados do processo

### 5. Validação

- Verificar contagens de registros
- Validar integridade referencial
- Executar testes funcionais com os dados migrados

## Mapeamento de Dados

### Entidades Principais

| Sistema Legado | Sistema Novo | Transformações Necessárias |
|----------------|--------------|----------------------------|
| Titulos        | Titulo       | Normalizar status, ajustar formatos de data |
| Devedores      | Devedor      | Validar documentos, normalizar endereços |
| Credores       | Credor       | Validar documentos, normalizar razão social |
| Protestos      | Titulo (status=Protestado) | Consolidar informações de protesto |
| Usuarios       | User         | Converter senhas para formato bcrypt |
| Remessas       | Remessa      | Ajustar metadados e relacionamentos |

### Campos Específicos

Para cada entidade, os campos devem ser mapeados individualmente. Exemplo para a entidade Título:

| Campo Legado | Campo Novo | Transformação |
|--------------|------------|---------------|
| num_titulo   | numero     | Direto |
| valor        | valor      | Converter para decimal |
| dt_emissao   | data_emissao | Converter formato de data |
| dt_vencimento | data_vencimento | Converter formato de data |
| situacao     | status     | Mapear valores (ex: 'P' → 'Protestado') |
| id_devedor   | devedor_id | Relacionamento |
| id_credor    | credor_id  | Relacionamento |

## Scripts de Migração

Os scripts de migração estão localizados em `/backend/app/scripts/migracao/` e incluem:

### 1. Exportadores

- `exportar_sistema_legado.py`: Conecta ao sistema legado e exporta dados em formato CSV

### 2. Transformadores

- `transformar_titulos.py`: Aplica transformações aos dados de títulos
- `transformar_devedores.py`: Aplica transformações aos dados de devedores
- `transformar_credores.py`: Aplica transformações aos dados de credores
- `transformar_usuarios.py`: Aplica transformações aos dados de usuários

### 3. Importadores

- `importar_devedores.py`: Importa devedores para o novo sistema
- `importar_credores.py`: Importa credores para o novo sistema
- `importar_titulos.py`: Importa títulos para o novo sistema
- `importar_usuarios.py`: Importa usuários para o novo sistema

### 4. Validadores

- `validar_migracao.py`: Verifica a integridade dos dados migrados

### Exemplo de Uso

```bash
# Exportar dados do sistema legado
python -m app.scripts.migracao.exportar_sistema_legado --config=config/legado.json --output=dados_exportados/

# Transformar dados
python -m app.scripts.migracao.transformar_titulos --input=dados_exportados/titulos.csv --output=dados_transformados/titulos.csv

# Importar dados
python -m app.scripts.migracao.importar_devedores --input=dados_transformados/devedores.csv
python -m app.scripts.migracao.importar_credores --input=dados_transformados/credores.csv
python -m app.scripts.migracao.importar_titulos --input=dados_transformados/titulos.csv

# Validar migração
python -m app.scripts.migracao.validar_migracao --config=config/validacao.json
```

## Validação e Verificação

### Verificações Quantitativas

- Contagem de registros em cada tabela
- Somas de controle (ex: total de valores de títulos)
- Verificação de registros órfãos

### Verificações Qualitativas

- Amostragem de registros para verificação manual
- Validação de regras de negócio
- Testes funcionais com dados migrados

### Relatórios de Validação

O script `validar_migracao.py` gera relatórios detalhados incluindo:

- Resumo da migração (contagens, status)
- Lista de problemas encontrados
- Recomendações para correção

## Rollback

### Plano de Rollback

Em caso de problemas graves durante a migração, o seguinte plano de rollback deve ser seguido:

1. Interromper todos os processos de migração
2. Restaurar backup do banco de dados do novo sistema
3. Documentar os problemas encontrados
4. Corrigir os scripts de migração
5. Reiniciar o processo após correções

### Backups

Antes de iniciar a migração, os seguintes backups devem ser realizados:

- Backup completo do banco de dados do sistema legado
- Backup completo do banco de dados do novo sistema (se já contiver dados)
- Backup dos arquivos exportados em cada etapa

## Cronograma

| Etapa | Duração Estimada | Dependências |
|-------|------------------|-------------|
| Análise e Planejamento | 1 semana | - |
| Desenvolvimento de Scripts | 2 semanas | Análise e Planejamento |
| Migração de Teste | 3 dias | Desenvolvimento de Scripts |
| Validação da Migração de Teste | 2 dias | Migração de Teste |
| Correções e Ajustes | 1 semana | Validação da Migração de Teste |
| Migração Final | 1-2 dias | Correções e Ajustes |
| Validação Final | 2 dias | Migração Final |

### Janela de Migração

A migração final deve ser realizada durante um período de baixa utilização do sistema, preferencialmente em um final de semana. Um período de indisponibilidade de 24-48 horas deve ser planejado e comunicado a todos os usuários.

---

## Apêndices

### A. Consultas SQL para Extração

Exemplos de consultas SQL para extração de dados do sistema legado:

```sql
-- Extração de títulos
SELECT 
    id as id_legado,
    num_titulo,
    valor,
    dt_emissao,
    dt_vencimento,
    situacao,
    id_devedor,
    id_credor
FROM titulos;

-- Extração de devedores
SELECT 
    id as id_legado,
    nome,
    documento,
    endereco,
    cidade,
    uf,
    cep
FROM devedores;
```

### B. Mapeamento de Códigos de Status

| Código Legado | Descrição Legado | Status Novo |
|---------------|------------------|-------------|
| P | Protestado | Protestado |
| A | Aguardando | Pendente |
| C | Cancelado | Cancelado |
| L | Liquidado | Pago |
| D | Devolvido | Devolvido |

### C. Tratamento de Exceções

Procedimentos para lidar com casos especiais durante a migração:

1. Registros duplicados: Identificar por chaves naturais e manter apenas o mais recente
2. Dados inválidos: Corrigir manualmente ou aplicar valores padrão
3. Relacionamentos quebrados: Criar entidades temporárias ou marcar para revisão manual

---

Este plano de migração deve ser revisado e aprovado por todas as partes interessadas antes do início do processo de migração. Quaisquer alterações devem ser documentadas e comunicadas adequadamente.