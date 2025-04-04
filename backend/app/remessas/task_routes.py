from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.async_tasks import get_task_status
from app.utils.task_utils import list_tasks, get_pending_tasks
from app.models import Remessa, User
from app import db
from . import remessas

@remessas.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Obtém o status de uma tarefa assíncrona
    ---
    tags:
      - Remessas
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
        description: ID da tarefa
    security:
      - JWT: []
    responses:
      200:
        description: Status da tarefa
      404:
        description: Tarefa não encontrada
    """
    # Verifica se a tarefa existe
    task_status = get_task_status(task_id)
    if not task_status:
        return jsonify({'message': 'Tarefa não encontrada'}), 404
    
    # Retorna o status da tarefa
    return jsonify({
        'task': task_status
    }), 200

@remessas.route('/by-task/<task_id>', methods=['GET'])
@jwt_required()
def get_remessa_by_task(task_id):
    """Obtém uma remessa pelo ID da tarefa
    ---
    tags:
      - Remessas
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
        description: ID da tarefa
    security:
      - JWT: []
    responses:
      200:
        description: Remessa encontrada
      404:
        description: Remessa não encontrada
    """
    # Busca a remessa pelo ID da tarefa
    remessa = Remessa.query.filter_by(task_id=task_id).first()
    if not remessa:
        return jsonify({'message': 'Remessa não encontrada'}), 404
    
    # Retorna a remessa
    return jsonify({
        'remessa': remessa.to_dict()
    }), 200

@remessas.route('/tasks', methods=['GET'])
@jwt_required()
def list_all_tasks():
    """Lista todas as tarefas assíncronas
    ---
    tags:
      - Remessas
    parameters:
      - name: status
        in: query
        type: string
        required: false
        description: Filtro de status (pending, running, completed, failed)
      - name: limit
        in: query
        type: integer
        required: false
        description: Limite de tarefas a serem retornadas
    security:
      - JWT: []
    responses:
      200:
        description: Lista de tarefas
    """
    # Obtém os parâmetros da requisição
    status = request.args.get('status')
    limit = request.args.get('limit')
    
    # Converte o limite para inteiro, se especificado
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return jsonify({'message': 'Limite inválido'}), 400
    
    # Lista as tarefas
    tasks = list_tasks(status_filter=status, limit=limit)
    
    # Retorna a lista de tarefas
    return jsonify({
        'tasks': tasks,
        'count': len(tasks)
    }), 200

@remessas.route('/tasks/pending', methods=['GET'])
@jwt_required()
def list_pending_tasks():
    """Lista todas as tarefas pendentes ou em execução
    ---
    tags:
      - Remessas
    security:
      - JWT: []
    responses:
      200:
        description: Lista de tarefas pendentes
    """
    # Obtém as tarefas pendentes
    tasks = get_pending_tasks()
    
    # Retorna a lista de tarefas
    return jsonify({
        'tasks': tasks,
        'count': len(tasks)
    }), 200