# Dados de Teste para o Sistema de Protesto

## Visão Geral

Este documento descreve os dados de teste criados para o Sistema de Protesto. Os dados foram projetados para cobrir diversos cenários de uso e testar todas as funcionalidades do sistema.

## Arquivo de Dados

Os dados de teste estão disponíveis no arquivo `dados_teste.sql` na raiz do projeto. Este arquivo contém comandos SQL para inserir dados em todas as tabelas do sistema.

## Como Utilizar

Para carregar os dados de teste no banco de dados:

1. Certifique-se de que o banco de dados PostgreSQL esteja em execução
2. Execute o comando:
   ```
   psql -U postgres -f dados_teste.sql
   ```

## Dados Disponíveis

### Usuários (5)
- Administrador do sistema
- Analista
- Operador
- Gerente
- Supervisor

### Credores (5)
- Instituições financeiras diversas com dados completos

### Devedores (10)
- Pessoas físicas e jurídicas com diferentes perfis

### Remessas (5)
- Remessas em diferentes estados: processada, em processamento e com erro
- Distribuídas por diferentes UFs

### Títulos (10)
- Títulos em diversos estados: protestado, em cartório, enviado, aguardando envio, registrado e com erro
- Diferentes tipos de espécies: DMI, CBI, NP
- Valores variados

### Desistências (4)
- Motivos diversos: pagamento, acordo, erro de cadastro
- Estados diferentes: processada, em processamento, pendente

### Erros (5)
- Tipos variados: validação, processamento, sistema
- Alguns resolvidos e outros pendentes

### Autorizações de Cancelamento (4)
- Estados diferentes: processada, pendente, erro

### Transações de Autorização de Cancelamento (5)
- Relacionadas às autorizações de cancelamento
- Estados diferentes: processada, pendente, erro

## Cenários de Teste

Os dados foram criados para permitir testar os seguintes cenários:

1. **Consulta de Remessas**: Filtrar remessas por status, UF, período
2. **Consulta de Títulos**: Buscar títulos por protocolo, devedor, valor
3. **Processamento de Desistências**: Aprovar/rejeitar solicitações pendentes
4. **Análise de Erros**: Visualizar e resolver erros pendentes
5. **Autorizações de Cancelamento**: Processar autorizações pendentes
6. **Relatórios**: Gerar relatórios com base nos dados existentes

## Observações

- As datas foram configuradas relativamente à data atual para manter a relevância dos dados
- Os valores dos títulos variam de R$ 950,30 a R$ 7.800,00
- Foram criadas relações entre todas as tabelas para garantir a integridade referencial