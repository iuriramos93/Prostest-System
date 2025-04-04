from flask import Blueprint

autorizacoes = Blueprint('autorizacoes', __name__)

from . import routes