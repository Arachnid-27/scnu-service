from flask import render_template, request, redirect, url_for, g, make_response, jsonify
from .. import rdb
from ..utils import hmget_decode
from . import jwc, function
import json


@jwc.before_request
def before_request():
    if request.endpoint not in ['jwc.login', 'jwc.verify']:
        if 'JWCCOOKIE' not in request.cookies or not rdb.exists('jwc:' + request.cookies['JWCCOOKIE']):
            return redirect(url_for('.login'))
        g.cookie = request.cookies['JWCCOOKIE']
        g.name = 'jwc:' + g.cookie


@jwc.route('/')
def index():
    years, terms, selected_year, selected_term, table = hmget_decode(
        rdb, g.name, ['years', 'terms', 'selected_year', 'selected_term', 'table'])
    if None in (years, terms, selected_year, selected_term, table):
        years, terms, selected_year, selected_term, table = function.init_schedule(g.cookie)
    return render_template('jwc.html', table=table, years=years.split(','), terms=terms.split(','),
                           selected_year=selected_year, selected_term=selected_term)


@jwc.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if 'JWCCOOKIE' in request.cookies and rdb.exists('jwc:' + request.cookies['JWCCOOKIE']):
            return redirect(url_for('.index'))
        return render_template('login.html', entry='教务处')
    else:
        username = request.form['username']
        password = request.form['password']
        code = request.form['code']
        if not username.strip() or not password.strip() or not code.strip():
            return render_template('login.html', entry='教务处', msg='帐号/密码/验证码为空')
        cookie = request.cookies.get('JWCCOOKIE')
        msg = function.login(username, password, code, cookie)
        if msg:
            return render_template('login.html', entry='教务处', msg=msg)
        return redirect(url_for('.index'))


@jwc.route('/code')
def verify():
    content, cookie = function.get_code()
    resp = make_response(content)
    resp.set_cookie('JWCCOOKIE', cookie)
    resp.mimetype = 'image/gif'
    return resp


@jwc.route('/score', methods=['POST'])
def score():
    year = request.form['year']
    term = request.form['term']
    items = function.get_score(g.cookie, year, term)
    total, gpa, credit = [], [], []
    for item in items:
        total.append(int(item['total']))
        gpa.append(float(item['gpa']))
        credit.append(float(item['credit']))
    info = None
    if items:
        info = {
            'sum': sum(credit),
            'max': max(total),
            'min': min(total),
            'ave': round(sum([c * p for c, p in zip(credit, gpa)]) / sum(credit), 2)
        }
    return jsonify({
        'items': items,
        'info': info
    })


@jwc.route('/schedule', methods=['POST'])
def schedule():
    year = request.form['year']
    term = request.form['term']
    table = function.get_schedule(g.cookie, year, term)
    return jsonify({
        'table': table
    })