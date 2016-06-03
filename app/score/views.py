from flask import render_template, request, redirect, url_for, g, make_response
from .. import rdb
from ..utils import hmget_decode
from . import score, function
import json


@score.before_request
def before_request():
    if request.endpoint not in ['score.login', 'score.verify']:
        if 'SCOCOOKIE' not in request.cookies or not rdb.exists('sco:' + request.cookies['SCOCOOKIE']):
            return redirect(url_for('.login'))
        g.cookie = request.cookies['SCOCOOKIE']


@score.route('/')
def index():
    keys = ['info', 'terms']
    info, terms = hmget_decode(rdb, 'sco:' + g.cookie, keys)
    return render_template('score.html', info=json.loads(info), terms=json.loads(terms))


@score.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if 'SCOCOOKIE' in request.cookies and rdb.exists('sco:' + request.cookies['SCOCOOKIE']):
            return redirect(url_for('.index'))
        return render_template('login.html', entry='校园网')
    else:
        username = request.form['username']
        password = request.form['password']
        code = request.form['code']
        cookie = request.cookies.get('SCOCOOKIE')
        if not function.check(cookie, code):
            return render_template('login.html', entry='校园网', msg='验证码错误')
        cookie = function.login(cookie, username, password, code)
        if not cookie:
            return render_template('login.html', entry='校园网', msg='用户名或密码错误')
        resp = make_response(redirect(url_for('.index')))
        resp.set_cookie('SCOCOOKIE', cookie)
        return resp


@score.route('/code')
def verify():
    content, cookie = function.get_code()
    resp = make_response(content)
    resp.set_cookie('SCOCOOKIE', cookie)
    resp.mimetype = 'image/jpeg'
    return resp


@score.route('/get', methods=['POST'])
def get():
    year = request.form['year']
    term = request.form['term']
    info, items = function.get_score(g.cookie, year, term)
    body, statistics = '', ''
    if items:
        for item in items:
            body += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                item['name'], item['credit'], item['usual'], item['final'], item['total']
            )
        statistics = '<p>绩点： {}</p><p>共修科目数： {}</p><p>未通过科目数： {}</p>'.format(
            info['points'], info['all'], info['unpass']
        )
    return json.dumps({
        'body': body,
        'statistics': statistics
    })


@score.route('/logout')
def logout():
    rdb.delete('sco:' + g.cookie)
    return redirect(url_for('.login'))
