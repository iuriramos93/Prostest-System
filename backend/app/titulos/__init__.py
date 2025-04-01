from flask import Blueprint

titulos = Blueprint('titulos', __name__)

from . import routes