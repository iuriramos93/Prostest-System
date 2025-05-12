# Mapeamento de Funcionalidades: Backend JS para Python/Flask

Este documento detalha o plano de migração das funcionalidades do backend existente em JavaScript (Node.js/Express) para Python/Flask.

## 1. Análise dos Componentes JS Originais

### 1.1. `server.js`

*   **Framework:** Express.js
*   **Middlewares Principais:**
    *   `cors`: Tratamento de Cross-Origin Resource Sharing.
        *   **Flask Equivalente:** `Flask-CORS` (já configurado no projeto Flask existente).
    *   `bodyParser.json()` e `bodyParser.urlencoded()`: Parsing de corpos de requisição JSON e URL encoded.
        *   **Flask Equivalente:** `request.get_json()` para JSON, `request.form` para URL encoded (nativo do Flask/Werkzeug).
    *   Middleware de Autenticação (Simulado): Verificava `Authorization: Bearer <token>` e simulava um `req.user`.
        *   **Flask Equivalente:** Substituído pelo `basic_auth_required` decorador implementado em `backend/app/auth/middleware.py`, que lida com Basic Auth HTTP, conforme solicitado e validado.
*   **Estrutura de Rotas:**
    *   `/remessas`: Delegado para `remessasRoutes` (`./routes/remessas.js`).
    *   `/desistencias`: Redirecionado internamente para `/remessas/desistencias` e também delegado para `remessasRoutes`.
        *   **Flask Equivalente:** Será um endpoint distinto ou tratado dentro do blueprint de remessas.
    *   `/`: Rota de teste.
*   **Tratamento de Erros:** Middleware genérico para erros 500.
    *   **Flask Equivalente:** Flask possui manipuladores de erro (`@app.errorhandler`) que podem ser usados para comportamento similar.
*   **Servidor:** `app.listen(PORT)`.
    *   **Flask Equivalente:** Gerenciado pelo Gunicorn em produção ou pelo servidor de desenvolvimento do Flask.

### 1.2. `routes/remessas.js`

*   **Conexão com Banco (PostgreSQL):** Usa a biblioteca `pg` (Pool de conexões).
    *   **Flask Equivalente:** SQLAlchemy com `psycopg2-binary` (já configurado no projeto Flask). Os modelos de dados (`Remessa`, `Titulo`, etc.) já existem em `backend/app/models.py`.
*   **Upload de Arquivos (XML):** Usa `multer` para lidar com uploads `multipart/form-data`.
    *   Configuração de destino: `../../uploads` (relativo ao arquivo `remessas.js`).
    *   Nome do arquivo: `fieldname-timestamp-random.ext`.
    *   Filtro de arquivo: Apenas `.xml`.
    *   **Flask Equivalente:**
        *   Acesso ao arquivo: `request.files['arquivo']`.
        *   Salvar arquivo: `file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))`.
        *   Validação de extensão: Verificar `file.filename.endswith('.xml')`.
        *   Geração de nome de arquivo seguro: `werkzeug.utils.secure_filename`.
*   **Parsing de XML:** Usa `xml2js`.
    *   **Flask Equivalente:** `xmltodict` (já no `requirements.txt`) é uma boa opção para converter XML para dicionário Python, similar ao `xml2js`. Alternativamente, `xml.etree.ElementTree` (nativo).

#### Endpoints em `routes/remessas.js`:

1.  **`POST /` (Enviar Nova Remessa)**
    *   **JS:** Recebe `tipo`, `uf`, `descricao` (opcional) no corpo e `arquivo` (XML) via upload.
    *   **Lógica JS:**
        1.  Valida campos obrigatórios.
        2.  Conecta ao DB, inicia transação (`BEGIN`).
        3.  Insere na tabela `remessas` com status 'Pendente'.
        4.  Atualiza `descricao` se fornecida.
        5.  Lê o arquivo XML, parseia com `xml2js`.
        6.  (Lógica de processamento do XML e salvamento de títulos é simplificada/comentada no JS).
        7.  Atualiza status da remessa para 'Processado' e `data_processamento`.
        8.  `COMMIT` ou `ROLLBACK`.
    *   **Flask Mapeamento:**
        *   Rota: `POST /api/remessas/` (seguindo o padrão do backend Flask).
        *   Blueprint: `remessas_blueprint` em `backend/app/remessas/routes.py`.
        *   Receber dados: `request.form.get('tipo')`, `request.form.get('uf')`, `request.form.get('descricao')`, `request.files.get('arquivo')`.
        *   Validação: Similar.
        *   DB: Usar `db.session` do SQLAlchemy.
        *   Inserção: `remessa = Remessa(...)`, `db.session.add(remessa)`, `db.session.commit()`.
        *   Processamento XML: Ler `arquivo.read()`, parsear com `xmltodict.parse()`.
        *   Lógica de títulos: Iterar sobre os dados parseados, criar instâncias do modelo `Titulo` e associá-las à `Remessa`.
        *   Transações: SQLAlchemy gerencia transações por sessão, `db.session.commit()` e `db.session.rollback()`.

2.  **`POST /desistencias` (Enviar Nova Desistência)**
    *   **JS:** Similar à remessa, mas `tipo` é fixado como 'desistência'.
    *   **Lógica JS:** Praticamente idêntica à remessa, mas com `tipo = 'desistencia'` e a lógica de processamento XML de desistência é comentada.
    *   **Flask Mapeamento:**
        *   Rota: `POST /api/remessas/desistencias/` ou um endpoint dedicado se a lógica for muito diferente.
        *   Lógica: Similar à remessa, mas o campo `tipo` na tabela `remessas` será 'desistencia'. O processamento do XML de desistência precisará ser implementado.

3.  **`GET /` (Listar Remessas)**
    *   **JS:** Aceita query params: `tipo`, `uf`, `status`, `dataInicio`, `dataFim`.
    *   **Lógica JS:** Constrói uma query SQL dinâmica para filtrar `remessas`.
    *   **Flask Mapeamento:**
        *   Rota: `GET /api/remessas/`.
        *   Receber query params: `request.args.get('param')`.
        *   DB: Construir query com SQLAlchemy ORM: `query = Remessa.query` e aplicar filtros dinamicamente: `query = query.filter(Remessa.tipo == tipo_param)` etc.
        *   Ordenação: `query.order_by(Remessa.data_envio.desc())`.

4.  **`GET /:id` (Detalhes da Remessa)**
    *   **JS:** Recebe `id` da remessa como path param.
    *   **Lógica JS:**
        1.  Busca remessa pelo ID.
        2.  Busca títulos associados à remessa (`WHERE remessa_id = $1`).
        3.  Retorna remessa com os títulos aninhados.
    *   **Flask Mapeamento:**
        *   Rota: `GET /api/remessas/<int:id>`.
        *   DB: `remessa = Remessa.query.get_or_404(id)`. Os títulos podem ser acessados via relacionamento `remessa.titulos` (se o backref estiver configurado corretamente no modelo `Titulo`).

## 2. Estrutura Proposta no Backend Flask

*   **Localização Principal:** As funcionalidades de remessas e desistências serão implementadas principalmente no módulo `backend/app/remessas/`.
    *   `backend/app/remessas/routes.py`: Conterá os endpoints Flask para `/api/remessas/*`.
    *   `backend/app/remessas/services.py` (Novo arquivo, opcional): Pode conter a lógica de negócios mais complexa (processamento de XML, interação detalhada com DB) para manter as rotas mais limpas.
    *   `backend/app/models.py`: Os modelos `Remessa` e `Titulo` já existem e serão utilizados. Poderão ser necessários ajustes ou novos modelos dependendo da complexidade do XML.
*   **Uploads:** A pasta de uploads configurada no Flask (`app.config['UPLOAD_FOLDER']`) será utilizada.

## 3. Bibliotecas Python Adicionais

*   `xmltodict`: Já está no `requirements.txt`. Confirmar se atende a todas as necessidades de parsing. Caso contrário, `lxml` é uma alternativa mais poderosa, mas `xmltodict` deve ser suficiente para a maioria dos casos.
*   Nenhuma outra biblioteca nova parece ser imediatamente necessária com base na análise dos arquivos JS.

## 4. Considerações Adicionais

*   **Segurança de Uploads:** Garantir validação robusta de arquivos XML (tamanho, tipo, conteúdo malicioso potencial) além da extensão.
*   **Processamento Assíncrono:** O processamento de XML e a interação com o banco podem ser demorados para arquivos grandes. Considerar o uso de tarefas assíncronas (ex: Celery com Redis/RabbitMQ, que já tem indícios no `requirements.txt` com `redis`) para as rotas `POST /` e `POST /desistencias` para melhorar a responsividade da API. O backend JS não implementa isso, mas é uma melhoria a ser considerada no Flask.
*   **Validação de Dados:** Implementar validação robusta para os dados recebidos no corpo da requisição e nos arquivos XML usando, por exemplo, Marshmallow (já no `requirements.txt`).
*   **Testes:** Escrever testes unitários e de integração para todas as novas funcionalidades.

Este mapeamento servirá como guia para a fase de reescrita do código.
