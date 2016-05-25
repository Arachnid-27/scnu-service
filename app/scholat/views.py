from flask import render_template, request, redirect, url_for, g, make_response
from .. import rdb
from ..utils import hmget_decode
from . import scholat


@scholat.before_request
def before_request():
    pass


@scholat.route('/')
def index():
    pass


@scholat.route('/course/<name>')
def course(name):
    pass


@scholat.route('/login')
def login():
    pass


@scholat.route('/logout')
def logout():
    pass