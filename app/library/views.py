from flask import render_template, request, redirect, url_for, g, make_response, jsonify
from .. import rdb
from ..utils import hmget_decode
from . import library, function


@library.before_request
def before_request():
    if  request.endpoint not in ['library.login', 'library.verify']:
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
    code = request.form['code']
    if not username.strip() or not password.strip() or not code.strip():
        return render_template('login.html', entry='图书馆', msg='帐号/密码/验证码为空')
    cookie = request.cookies.get('LIBCOOKIE')
    msg = function.login(cookie, username, password, code)
    if msg != '登录成功':
        return render_template('login.html', entry='图书馆', msg=msg)
    resp = make_response(redirect(url_for('.index')))
    return resp


@library.route('/code')
def verify():
    content, cookie = function.get_code()
    resp = make_response(content)
    resp.set_cookie('LIBCOOKIE', cookie)
    resp.mimetype = 'image/jpeg'
    return resp


@library.route('/renew_code')
def renew_verify():
    content = function.get_renew_code(g.cookie)
    resp = make_response(content)
    resp.mimetype = 'image/jpeg'
    return resp


@library.route('/renew')
def renew():
    barcode = request.args.get('barcode', None)
    code = request.args.get('code', None)
    check = request.args.get('check', None)
    if not code:
        return jsonify({'success': False, 'msg': '验证码不能为空'})
    elif not barcode or not check:
        return jsonify({'success': False, 'msg': '未知错误'})
    msg = function.renew(g.cookie, barcode, code, check)
    if '成功' in msg:
        return jsonify({'success': True})
    return jsonify({'success': False, 'msg': msg})


@library.route('/logout')
def logout():
    rdb.delete('lib:' + g.cookie)
    return redirect(url_for('.login'))
