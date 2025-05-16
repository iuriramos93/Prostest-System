from flask import Blueprint

desistencias = Blueprint('desistencias', __name__)

from . import routes
from . import routes_upload