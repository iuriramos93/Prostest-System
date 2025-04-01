from flask import Blueprint

remessas = Blueprint('remessas', __name__)

from . import routes