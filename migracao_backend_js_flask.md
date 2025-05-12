# Documentação da Migração do Backend: JS para Python/Flask

## 1. Visão Geral

Este documento descreve as alterações realizadas durante a migração de funcionalidades do backend originalmente implementado em JavaScript (Node.js/Express) para Python/Flask no projeto Prostest-System. O objetivo principal foi consolidar o backend em Python/Flask, aproveitando a estrutura existente e as bibliotecas do ecossistema Python.

As funcionalidades migradas referem-se principalmente ao gerenciamento de **Remessas** e **Desistências**, incluindo upload de arquivos XML, processamento desses arquivos e interações com o banco de dados PostgreSQL.

## 2. Arquitetura e Estrutura de Arquivos (Pós-Migração)

As funcionalidades migradas foram integradas ao backend Flask existente, localizado em `/home/ubuntu/Prostest-System/backend/`.

*   **Módulo Principal das Funcionalidades Migradas:** `backend/app/remessas/`
    *   `routes.py`: Contém os endpoints Flask para `/api/remessas/` e `/api/remessas/desistencias/`, bem como a rota de estatísticas `/api/remessas/estatisticas`.
        *   Este arquivo agora lida com o upload de arquivos XML, validação, parsing (usando `xmltodict`), interação com o banco de dados (via SQLAlchemy) e enfileiramento de tarefas assíncronas para processamento de remessas/desistências.
    *   `__init__.py`: Define o Blueprint `remessas` para este módulo.
*   **Modelos de Dados:** `backend/app/models.py`
    *   Os modelos `Remessa`, `Titulo`, `User`, `Erro`, etc., foram utilizados e são a base para a persistência dos dados.
*   **Autenticação:** `backend/app/auth/middleware.py`
    *   O decorador `basic_auth_required` implementado anteriormente é utilizado para proteger os endpoints de remessas e desistências.
*   **Tarefas Assíncronas:** `backend/app/utils/async_tasks.py` (e o sistema de filas configurado, ex: Redis/Celery)
    *   O processamento dos arquivos XML de remessa e desistência foi projetado para ser executado de forma assíncrona para não bloquear as requisições HTTP. As funções `processar_remessa` e `processar_desistencia` (esta última adicionada/adaptada em `backend/app/remessas/routes.py` ou em um arquivo de `services.py` se separado) são enfileiradas.
*   **Configuração de Upload:** A pasta de uploads é gerenciada pela configuração `UPLOAD_FOLDER` da aplicação Flask.

## 3. Endpoints Implementados/Migrados (em `backend/app/remessas/routes.py`)

Todos os endpoints estão sob o prefixo `/api` e são protegidos por Basic Auth.

1.  **`POST /api/remessas/upload`** (Anteriormente `POST /remessas/` no JS)
    *   **Funcionalidade:** Envio de um novo arquivo de remessa XML.
    *   **Corpo da Requisição:** `multipart/form-data` com os campos `file` (arquivo XML), `uf` (string), `tipo` (string, "Remessa"), `descricao` (string, opcional).
    *   **Lógica:**
        *   Valida o arquivo e os campos.
        *   Salva o arquivo XML no servidor.
        *   Cria um registro `Remessa` no banco com status "Pendente".
        *   Enfileira uma tarefa assíncrona (`processar_remessa`) para o processamento do XML.
    *   **Resposta:** JSON com mensagem de sucesso e detalhes da remessa criada.

2.  **`POST /api/remessas/desistencias`** (Anteriormente `POST /remessas/desistencias/` no JS)
    *   **Funcionalidade:** Envio de um novo arquivo de desistência XML.
    *   **Corpo da Requisição:** `multipart/form-data` com os campos `file` (arquivo XML), `uf` (string), `descricao` (string, opcional). O tipo é internamente definido como "Desistência".
    *   **Lógica:** Similar ao envio de remessa, mas cria um registro `Remessa` com `tipo="Desistência"` e enfileira uma tarefa `processar_desistencia`.
    *   **Resposta:** JSON com mensagem de sucesso e detalhes da remessa (desistência) criada.

3.  **`GET /api/remessas/`** (Anteriormente `GET /remessas/` no JS)
    *   **Funcionalidade:** Lista todas as remessas com filtros opcionais.
    *   **Query Params:** `tipo`, `uf`, `status`, `dataInicio`, `dataFim`.
    *   **Lógica:** Constrói uma query SQLAlchemy dinâmica para filtrar e ordenar as remessas.
    *   **Resposta:** JSON com uma lista de objetos de remessa.

4.  **`GET /api/remessas/<int:id>`** (Anteriormente `GET /remessas/:id` no JS)
    *   **Funcionalidade:** Obtém detalhes de uma remessa específica, incluindo os títulos associados.
    *   **Path Param:** `id` da remessa.
    *   **Lógica:** Busca a remessa e seus títulos relacionados no banco.
    *   **Resposta:** JSON com os detalhes da remessa e uma lista de seus títulos.

5.  **`GET /api/remessas/estatisticas`** (Nova rota adicionada durante a migração para Flask)
    *   **Funcionalidade:** Fornece estatísticas agregadas sobre as remessas.
    *   **Lógica:** Realiza contagens e agregações no banco de dados (total por status, tipo, UF, total de títulos).
    *   **Resposta:** JSON com as estatísticas.

## 4. Principais Mudanças e Melhorias em Relação ao Backend JS

*   **Tipagem e Estrutura:** Python com Flask oferece uma estrutura mais robusta e tipada (com uso de type hints, embora não totalmente obrigatório) em comparação com o JavaScript do exemplo.
*   **ORM (SQLAlchemy):** A interação com o banco de dados é feita através do SQLAlchemy ORM, o que proporciona uma camada de abstração mais segura e manutenível em comparação com queries SQL raw diretamente no código das rotas, como no exemplo JS.
*   **Processamento Assíncrono:** A arquitetura Flask existente já previa o uso de tarefas assíncronas (indicado pela presença de `app.utils.async_tasks` e `redis` no `requirements.txt`). O processamento dos arquivos XML foi integrado a este sistema, melhorando a responsividade da API para uploads.
*   **Autenticação Consolidada:** A autenticação Basic Auth implementada anteriormente agora protege os novos endpoints de remessas.
*   **Validação:** Embora não explicitamente detalhado no código JS, a implementação Flask deve incluir validação de dados mais robusta (ex: usando Marshmallow ou validações manuais) para os inputs e o conteúdo XML.
*   **Tratamento de Erros:** O Flask oferece mecanismos mais estruturados para tratamento de erros específicos e globais.

## 5. Considerações para o Futuro

*   **Testes Abrangentes:** Continuar a expandir a suíte de testes unitários e de integração para cobrir todos os cenários das funcionalidades migradas.
*   **Validação de XML:** Implementar validação de schema XML (XSD) se disponível, para garantir a integridade dos arquivos enviados.
*   **Monitoramento e Logging:** Expandir o logging para fornecer mais detalhes sobre o processamento de remessas e possíveis erros.

Esta documentação serve como um guia inicial para as funcionalidades migradas. Recomenda-se a consulta direta ao código-fonte para detalhes de implementação específicos.
