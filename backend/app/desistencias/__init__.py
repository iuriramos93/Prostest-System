from flask import Blueprint

desistencias = Blueprint('desistencias', __name__)

from . import routes