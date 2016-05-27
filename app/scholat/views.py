from flask import render_template, request, redirect, url_for, g, make_response, abort
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
    courses = hget_decode(rdb, g.name, 'courses')
    if not courses:
        courses = function.get_list(g.cookie)
    else:
        courses = json.loads(courses)
    return render_template('scholat.html', courses=courses, info=None)


@scholat.route('/course/<int:cid>')
@scholat.route('/course/<int:cid>/<int:cur>')
def course(cid, cur=1):
    courses = hget_decode(rdb, g.name, 'courses')
    if not courses:
        courses = function.get_list(g.cookie)
    else:
        courses = json.loads(courses)
    homework, title, page = function.get_homework(g.cookie, cid, cur)
    info = {
        'title': title,
        'page': page,
        'cid': cid,
        'cur': cur
    }
    return render_template('scholat.html', courses=courses, homework=homework, info=info)


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


@scholat.route('/download')
def download():
    hid = request.args.get('hid', None)
    cid = request.args.get('cid', None)
    sid = request.args.get('sid', None)
    if None in (hid, cid, sid):
        abort(404)
    content, hdr = function.download_homework(g.cookie, cid, sid, hid)
    if not content:
        abort(404)
    resp = make_response(content)
    resp.headers['Content-Disposition'] = hdr['Content-Disposition']
    resp.headers['Content-Type'] = hdr['Content-Type']
    resp.headers['Connection'] = 'Keep-Alive'
    return resp

