# Testes do Sistema de Protesto

Este diretório contém os testes automatizados para o backend do Sistema de Protesto. Os testes foram desenvolvidos para identificar bugs e garantir o correto funcionamento da aplicação.

## Estrutura de Testes

Os testes estão organizados em módulos que correspondem às principais funcionalidades do sistema:

- `test_auth.py`: Testes para o módulo de autenticação
- `test_titulos.py`: Testes para o módulo de títulos
- `test_remessas.py`: Testes para o módulo de remessas
- `test_desistencias.py`: Testes para o módulo de desistências
- `test_erros.py`: Testes para o módulo de análise de erros
- `test_relatorios.py`: Testes para o módulo de relatórios
- `test_models.py`: Testes para os modelos de dados

## Configuração

O arquivo `conftest.py` contém as fixtures do pytest que configuram o ambiente de teste, incluindo:

- Criação de uma instância de aplicação Flask para testes
- Configuração do banco de dados de teste
- Criação de dados iniciais para os testes
- Geração de tokens JWT para autenticação

## Como Executar os Testes

### Usando o script run_tests.py

A maneira mais fácil de executar os testes é usando o script `run_tests.py` na raiz do diretório backend:

```bash
python run_tests.py
```

Este script oferece um menu interativo para escolher quais testes executar.

### Usando o pytest diretamente

Você também pode executar os testes diretamente com o pytest:

```bash
# Executar todos os testes
pytest

# Executar testes com relatório de cobertura
pytest --cov=app

# Executar um módulo específico de testes
pytest tests/test_auth.py

# Executar testes com marcadores específicos
pytest -m "auth or titulos"
```

## Marcadores

Os testes estão organizados com os seguintes marcadores:

- `unit`: Testes unitários
- `integration`: Testes de integração
- `auth`: Testes de autenticação
- `titulos`: Testes de títulos
- `remessas`: Testes de remessas
- `desistencias`: Testes de desistências
- `erros`: Testes de erros
- `relatorios`: Testes de relatórios
- `models`: Testes de modelos

## Ambiente de Teste

Os testes são executados em um banco de dados PostgreSQL separado (`protest_system_test`), que é criado e destruído durante a execução dos testes. Isso garante que os testes não afetem o banco de dados de desenvolvimento ou produção.

## Adicionando Novos Testes

Ao adicionar novos testes:

1. Siga o padrão de nomenclatura: `test_*.py` para arquivos e `test_*` para funções
2. Use as fixtures existentes em `conftest.py` para configurar o ambiente
3. Adicione marcadores apropriados para categorizar os testes
4. Mantenha os testes independentes uns dos outros

## Relatórios de Cobertura

Para gerar um relatório de cobertura detalhado em HTML:

```bash
pytest --cov=app --cov-report=html
```

O relatório será gerado no diretório `htmlcov/`.