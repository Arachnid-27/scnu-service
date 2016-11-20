from flask import render_template, request, url_for, jsonify
from . import main
from .. import rdb


@main.route('/')
def index():
    return render_template('index.html')


@main.app_template_filter('ellipsis')
def filter_ellipsis(s):
    return s[:35] + '..' if len(s) > 35 else s


@main.route('/account')
def account():
    data = {
        'sch': {
            'status': 'SCHCOOKIE' in request.cookies and rdb.exists('sch:' + request.cookies['SCHCOOKIE'])
        },
        'lib': {
            'status': 'LIBCOOKIE' in request.cookies and rdb.exists('lib:' + request.cookies['LIBCOOKIE'])
        },
        'sco': {
            'status': 'SCOCOOKIE' in request.cookies and rdb.exists('sco:' + request.cookies['SCOCOOKIE'])
        }
    }
    data['sch']['url'] = url_for('scholat.logout') if data['sch']['status'] else url_for('scholat.login')
    data['lib']['url'] = url_for('library.logout') if data['lib']['status'] else url_for('library.login')
    data['sco']['url'] = url_for('score.logout') if data['sco']['status'] else url_for('score.login')
    return jsonify(data)

