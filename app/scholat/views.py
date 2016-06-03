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
        g.cookie = request.cookies['SCHCOOKIE']


@scholat.route('/')
def index():
    courses = hget_decode(rdb, 'sch:' + g.cookie, 'courses')
    if not courses:
        courses = function.get_list(g.cookie)
    else:
        courses = json.loads(courses)
    return render_template('scholat.html', courses=courses, info=None)


@scholat.route('/course/<int:cid>')
@scholat.route('/course/<int:cid>/<int:cur>')
def course(cid, cur=1):
    courses = hget_decode(rdb, 'sch:' + g.cookie, 'courses')
    if not courses:
        courses = function.get_list(g.cookie)
    else:
        courses = json.loads(courses)
    items, title, page, sid = function.get_homework(g.cookie, cid, cur)
    info = {
        'title': title,
        'page': page,
        'cid': cid,
        'sid': sid,
        'cur': cur
    }
    return render_template('scholat.html', courses=courses, homework=items, info=info)


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
    rdb.delete('sch:' + g.cookie)
    return redirect(url_for('.login'))


@scholat.route('/homework')
def homework():
    cid = request.args.get('cid', None)
    sid = request.args.get('sid', None)
    hid = request.args.get('hid', None)
    if None in (cid, sid, hid):
        abort(404)
    content, hdr = function.download_homework(g.cookie, cid, sid, hid)
    if not content:
        abort(404)
    resp = make_response(content)
    resp.headers['Content-Disposition'] = hdr['Content-Disposition']
    resp.headers['Content-Type'] = hdr['Content-Type']
    resp.headers['Connection'] = 'Keep-Alive'
    return resp


@scholat.route('/details')
def details():
    cid = request.args.get('cid', None)
    hid = request.args.get('hid', None)
    if None in (cid, hid):
        abort(404)
    content, items = function.get_details(g.cookie, cid, hid)
    if not content:
        abort(404)
    footer = ''
    for item in items:
        footer += '<p><a href="{}">{}</a></p>'.format(url_for('.attach', cid=cid, lid=item['lid']), item['title'])
    return json.dumps({
        'content': content,
        'footer': footer
    })


@scholat.route('/attach')
def attach():
    cid = request.args.get('cid', None)
    lid = request.args.get('lid', None)
    if None in (cid, lid):
        abort(404)
    content, hdr = function.download_attach(g.cookie, cid, lid)
    if not content:
        abort(404)
    resp = make_response(content)
    resp.headers['Content-Disposition'] = hdr['Content-Disposition']
    resp.headers['Content-Type'] = hdr['Content-Type']
    resp.headers['Connection'] = 'Keep-Alive'
    return resp


@scholat.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    cid = request.form['cid']
    sid = request.form['sid']
    hid = request.form['hid']
    rs = function.upload_homework(g.cookie, cid, sid, hid, file.stream, file.filename)
    return 'success' if rs else 'failed'
