from flask import Blueprint

score = Blueprint('score', __name__)

from . import views
