from flask import Blueprint

erros = Blueprint('erros', __name__)

from . import routes