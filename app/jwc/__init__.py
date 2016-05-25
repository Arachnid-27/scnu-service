from flask import Blueprint

jwc = Blueprint('jwc', __name__)

from . import views
