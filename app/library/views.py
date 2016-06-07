from flask import render_template, request, redirect, url_for, g, make_response
from .. import rdb
from ..utils import hmget_decode
from . import library, function
import json


@library.before_request
def before_request():
    if not request.endpoint == 'library.login':
        if 'LIBCOOKIE' not in request.cookies or not rdb.exists('lib:' + request.cookies['LIBCOOKIE']):
            return redirect(url_for('.login'))
        g.cookie = request.cookies['LIBCOOKIE']


@library.route('/')
def index():
    keys = ['name', 'identifier', 'type', 'unit']
    values = hmget_decode(rdb, 'lib:' + g.cookie, keys)
    if None in values:
        info = function.get_info(g.cookie)
    else:
        info = dict(zip(keys, values))
    books = function.get_books(g.cookie)
    return render_template('library.html', books=books, info=info)


@library.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'LIBCOOKIE' in request.cookies and rdb.exists('lib:' + request.cookies['LIBCOOKIE']):
            return redirect(url_for('.index'))
        return render_template('login.html', entry='图书馆')
    username = request.form['username']
    password = request.form['password']
    msg, cookie = function.login(username, password)
    if not cookie:
        return render_template('login.html', entry='图书馆', msg=msg)
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('LIBCOOKIE', cookie)
    return resp


@library.route('/renew')
def renew():
    barcode = request.args.get('barcode', None)
    if not barcode:
        return json.dumps({'success': False, 'msg': '条形码不能为空'})
    msg = function.renew(g.cookie, barcode)
    if '成功' in msg:
        return json.dumps({'success': True})
    return json.dumps({'success': False, 'msg': msg})


@library.route('/logout')
def logout():
    rdb.delete('lib:' + g.cookie)
    return redirect(url_for('.login'))
