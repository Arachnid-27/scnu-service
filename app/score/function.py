from .. import rdb
import requests
import re
import json

host = 'https://sso.scnu.edu.cn'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'
}


def get_code():
    url = host + '/AccountService/user/rancode.jpg'
    resp = requests.get(url, headers=headers)
    cookie = resp.cookies.get('JSESSIONID')
    return resp.content, cookie


def check(cookie, code):
    url = host + '/AccountService/user/checkrandom.html'
    resp = requests.post(url, headers=headers, data={'random': code}, cookies={'JSESSIONID': cookie})
    if resp.text == 'false':
        return False
    return True


def login(cookie, username, password, code):
    url = host + '/AccountService/openapi/auth'
    form = {
        'account': username,
        'password': password,
        'rancode': code,
        'client_id': auth(),
        'response_type': 'code',
        'redirect_url': 'http://app.scnu.edu.cn/score/index.html',
        'jump': ''
    }
    resp = requests.post(url, headers=headers, data=form, cookies={'JSESSIONID': cookie})
    if '统一身份认证' in resp.text:
        return None
    terms_data = json.loads(re.search(r'terms_data = (.*?);', resp.text).group(1))
    score_data = json.loads(re.search(r'score_data = (.*?);', resp.text).group(1))
    cookie = resp.cookies.get('JSESSIONID')
    terms = [{'year': item['academicYear'], 'term': item['term']} for item in terms_data['data']['terms']]
    rdb.hmset('sco:' + cookie, {
        'info': json.dumps(score_data['data']),
        'terms': json.dumps(terms)
    })
    rdb.expire('sco:' + cookie, 3600)
    return cookie


def auth():
    url = 'http://app.scnu.edu.cn/score/oauth.html'
    resp = requests.get(url, headers=headers, allow_redirects=False)
    return re.search(r'client_id=(.*?)&', resp.headers['location']).group(1)


def get_score(cookie, year, term):
    url = 'http://app.scnu.edu.cn/score/term.html?academicYear={}&term={}'.format(year, term)
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    term_data = json.loads(re.search(r'term_data = (.*?);', resp.text).group(1))
    grade = [{
        'name': item.get('lessionName', '-'),
        'final': item.get('finalGrade', '-'),
        'usual': item.get('usualGrade', '-'),
        'credit': item.get('credit', '-'),
        'total': item.get('grade', '-')
    } for item in term_data['data']['gradeList']]
    info = {
        'all': term_data['data']['passCount'],
        'unpass': term_data['data']['unPassCount'],
        'points': term_data['data']['points']
    }
    return info, grade
