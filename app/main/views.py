from flask import render_template
from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.app_template_filter('ellipsis')
def filter_ellipsis(s):
    return s[:30] + '..' if len(s) > 30 else s