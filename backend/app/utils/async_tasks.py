import threading
import time
import queue
import logging
from typing import Callable, Dict, Any, Optional
from flask import current_app

# Fila global para tarefas assíncronas
task_queue = queue.Queue()

# Flag para controlar o worker
should_stop = False

# Dicionário para armazenar o status das tarefas
task_status = {}


class TaskStatus:
    """Classe para armazenar o status de uma tarefa"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'

    def __init__(self, task_id: str, description: str):
        self.task_id = task_id
        self.description = description
        self.status = self.PENDING
        self.result = None
        self.error = None
        self.progress = 0
        self.start_time = None
        self.end_time = None

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'description': self.description,
            'status': self.status,
            'progress': self.progress,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'error': self.error
        }


def worker():
    """Worker para processar tarefas da fila"""
    global should_stop
    
    while not should_stop:
        try:
            # Tenta obter uma tarefa da fila (timeout para permitir verificar should_stop)
            try:
                task_id, task_func, args, kwargs = task_queue.get(timeout=1)
            except queue.Empty:
                continue
            
            # Atualiza o status da tarefa
            if task_id in task_status:
                task_status[task_id].status = TaskStatus.RUNNING
                task_status[task_id].start_time = time.time()
            
            # Executa a tarefa
            try:
                result = task_func(*args, **kwargs)
                
                # Atualiza o status da tarefa
                if task_id in task_status:
                    task_status[task_id].status = TaskStatus.COMPLETED
                    task_status[task_id].result = result
                    task_status[task_id].end_time = time.time()
                    task_status[task_id].progress = 100
            except Exception as e:
                # Registra o erro
                logging.error(f"Erro ao executar tarefa {task_id}: {str(e)}")
                
                # Atualiza o status da tarefa
                if task_id in task_status:
                    task_status[task_id].status = TaskStatus.FAILED
                    task_status[task_id].error = str(e)
                    task_status[task_id].end_time = time.time()
            
            # Marca a tarefa como concluída na fila
            task_queue.task_done()
        except Exception as e:
            logging.error(f"Erro no worker: {str(e)}")


def start_worker():
    """Inicia o worker em uma thread separada"""
    global should_stop
    should_stop = False
    
    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()
    
    return worker_thread


def stop_worker():
    """Para o worker"""
    global should_stop
    should_stop = True


def enqueue_task(task_func: Callable, description: str, *args, **kwargs) -> str:
    """Adiciona uma tarefa à fila para execução assíncrona
    
    Args:
        task_func: Função a ser executada
        description: Descrição da tarefa
        *args: Argumentos posicionais para a função
        **kwargs: Argumentos nomeados para a função
        
    Returns:
        str: ID da tarefa
    """
    # Gera um ID para a tarefa
    task_id = f"task_{int(time.time())}_{threading.get_ident()}"
    
    # Cria um objeto de status para a tarefa
    task_status[task_id] = TaskStatus(task_id, description)
    
    # Adiciona a tarefa à fila
    task_queue.put((task_id, task_func, args, kwargs))
    
    return task_id


def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Obtém o status de uma tarefa
    
    Args:
        task_id: ID da tarefa
        
    Returns:
        Dict[str, Any]: Status da tarefa ou None se a tarefa não existir
    """
    if task_id in task_status:
        return task_status[task_id].to_dict()
    return None


def update_task_progress(task_id: str, progress: int):
    """Atualiza o progresso de uma tarefa
    
    Args:
        task_id: ID da tarefa
        progress: Progresso da tarefa (0-100)
    """
    if task_id in task_status:
        task_status[task_id].progress = progress


# Inicia o worker quando o módulo é carregado
worker_thread = start_worker()


# Função para inicializar o sistema de tarefas assíncronas
def init_async_tasks(app):
    """Inicializa o sistema de tarefas assíncronas
    
    Args:
        app: Aplicação Flask
    """
    @app.teardown_appcontext
    def shutdown_worker(exception=None):
        """Para o worker quando a aplicação é encerrada"""
        stop_worker()