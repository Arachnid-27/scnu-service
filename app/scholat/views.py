from flask import render_template, request, redirect, url_for, g, make_response
from .. import rdb
from ..utils import hget_decode
from . import scholat, function
import json


@scholat.before_request
def before_request():
    if not request.endpoint == 'scholat.login':
        if 'SCHCOOKIE' not in request.cookies or not rdb.exists('sch:' + request.cookies['SCHCOOKIE']):
            return redirect(url_for('.login'))
        g.name = 'sch:' + request.cookies['SCHCOOKIE']
        g.cookie = request.cookies['SCHCOOKIE']


@scholat.route('/')
def index():
    courses = function.get_list(g.cookie)
    return render_template('scholat.html', courses=courses)


@scholat.route('/course/<cid>')
def course(cid):
    courses = json.loads(hget_decode(rdb, g.name, 'courses'))
    homework, title = function.get_homework(g.cookie, cid)
    return render_template('scholat.html', courses=courses, homework=homework, title=title)


@scholat.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'SCHCOOKIE' in request.cookies and rdb.exists('sch:' + request.cookies['SCHCOOKIE']):
            return redirect(url_for('.index'))
        return render_template('login.html', entry='学者网')
    username = request.form['username']
    password = request.form['password']
    msg, cookie = function.login(username, password)
    if not cookie:
        return render_template('login.html', entry='学者网', msg=msg)
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('SCHCOOKIE', cookie)
    return resp


@scholat.route('/logout')
def logout():
    pass
