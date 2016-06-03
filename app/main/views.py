from flask import render_template, request, url_for
from . import main
from .. import rdb
import json


@main.route('/')
def index():
    return render_template('index.html')


@main.app_template_filter('ellipsis')
def filter_ellipsis(s):
    return s[:30] + '..' if len(s) > 30 else s


@main.route('/account')
def account():
    data = {'sch': {}, 'lib': {}, 'sco': {}}
    span_success = '<span class="label label-success label-align">已登录</span>'
    span_info = '<span class="label label-info label-align">未登录</span>'
    button = '<button type="button" class="btn btn-default btn-xs" onclick="location.href=\'{}\'">' \
             '<span class="glyphicon glyphicon-{}"></span> {}</button>'
    if 'SCHCOOKIE' in request.cookies and rdb.exists('sch:' + request.cookies['SCHCOOKIE']):
        data['sch']['status'] = span_success
        data['sch']['operate'] = button.format(url_for('scholat.logout'), 'send', '登出')
    else:
        data['sch']['status'] = span_info
        data['sch']['operate'] = button.format(url_for('scholat.login'), 'user', '登陆')
    if 'LIBCOOKIE' in request.cookies and rdb.exists('lib:' + request.cookies['LIBCOOKIE']):
        data['lib']['status'] = span_success
        data['lib']['operate'] = button.format(url_for('library.logout'), 'send', '登出')
    else:
        data['lib']['status'] = span_info
        data['lib']['operate'] = button.format(url_for('library.login'), 'user', '登陆')
    if 'SCOCOOKIE' in request.cookies and rdb.exists('sco:' + request.cookies['SCOCOOKIE']):
        data['sco']['status'] = span_success
        data['sco']['operate'] = button.format(url_for('score.logout'), 'send', '登出')
    else:
        data['sco']['status'] = span_info
        data['sco']['operate'] = button.format(url_for('score.login'), 'user', '登陆')
    return json.dumps(data)

