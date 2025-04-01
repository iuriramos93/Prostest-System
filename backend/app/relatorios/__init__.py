from flask import Blueprint

relatorios = Blueprint('relatorios', __name__)

from . import routes