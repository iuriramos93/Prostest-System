from typing import Dict, List, Any
from app.utils.async_tasks import task_status, TaskStatus

def list_tasks(status_filter=None, limit=None) -> List[Dict[str, Any]]:
    """Lista todas as tarefas, opcionalmente filtradas por status
    
    Args:
        status_filter: Filtro de status (opcional)
        limit: Limite de tarefas a serem retornadas (opcional)
        
    Returns:
        List[Dict[str, Any]]: Lista de tarefas
    """
    tasks = []
    
    # Converte o dicionário de tarefas em uma lista
    for task_id, task in task_status.items():
        # Filtra por status, se especificado
        if status_filter and task.status != status_filter:
            continue
        
        # Adiciona a tarefa à lista
        tasks.append(task.to_dict())
    
    # Ordena as tarefas por tempo de início (mais recentes primeiro)
    tasks.sort(key=lambda x: x.get('start_time', 0) or 0, reverse=True)
    
    # Limita o número de tarefas, se especificado
    if limit and isinstance(limit, int) and limit > 0:
        tasks = tasks[:limit]
    
    return tasks

def get_pending_tasks() -> List[Dict[str, Any]]:
    """Obtém todas as tarefas pendentes ou em execução
    
    Returns:
        List[Dict[str, Any]]: Lista de tarefas pendentes ou em execução
    """
    pending_tasks = []
    
    for task_id, task in task_status.items():
        if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            pending_tasks.append(task.to_dict())
    
    # Ordena as tarefas por tempo de início (mais recentes primeiro)
    pending_tasks.sort(key=lambda x: x.get('start_time', 0) or 0, reverse=True)
    
    return pending_tasks

def clear_completed_tasks(older_than=None):
    """Remove tarefas concluídas ou falhas do dicionário de status
    
    Args:
        older_than: Tempo em segundos para considerar uma tarefa antiga (opcional)
    """
    import time
    current_time = time.time()
    
    to_remove = []
    for task_id, task in task_status.items():
        # Verifica se a tarefa está concluída ou falhou
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            # Verifica se a tarefa é antiga o suficiente para ser removida
            if older_than and task.end_time:
                if current_time - task.end_time > older_than:
                    to_remove.append(task_id)
            # Se não foi especificado um tempo, remove todas as tarefas concluídas
            elif not older_than:
                to_remove.append(task_id)
    
    # Remove as tarefas do dicionário
    for task_id in to_remove:
        del task_status[task_id]
    
    return len(to_remove)