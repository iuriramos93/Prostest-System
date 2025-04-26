from flask import Blueprint

protestos = Blueprint('protestos', __name__)

from . import routes