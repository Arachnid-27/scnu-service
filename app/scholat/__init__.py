from flask import Blueprint

scholat = Blueprint('scholat', __name__)

from . import views
