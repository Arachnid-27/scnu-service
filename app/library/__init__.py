from flask import Blueprint

library = Blueprint('library', __name__)

from . import views
