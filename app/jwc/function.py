from bs4 import BeautifulSoup
from .. import rdb
from ..utils import hmget_decode, hget_decode
import requests
import re

host = 'http://jwc.scnu.edu.cn'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36',
    'Referer': host
}

def get_code():
    url = host + '/CheckCode.aspx'
    resp = requests.get(url, headers=headers)
    cookie = resp.cookies.get('ASP.NET_SessionId')
    return resp.content, cookie


def login(username, password, code, cookie):
    url = host + '/default2.aspx'
    form = {
        '__VIEWSTATE': 'dDwtNTE2MjI4MTQ7Oz5O1VSr99LahyNHrIGlotpJ441TCA==',
        'txtUserName': username,
        'Textbox1': '',
        'TextBox2': password,
        'txtSecretCode': code,
        'RadioButtonList1': '学生',
        'Button1': '',
        'lbLanguage': '',
        'hidPdrs': '',
        'hidsc': ''
    }
    resp = requests.post(url, headers=headers, data=form, cookies={'ASP.NET_SessionId': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    alert = bs.select('script[defer]')
    alert = re.search(r"alert\('(.*?)'\)", alert[0].get_text())
    if alert:
        return alert.group(1)
    href = bs.select('#headDiv > ul > li:nth-of-type(2) > ul > li:nth-of-type(1) > a')[0].get('href')
    rs = re.split(r'=|&', href)
    rdb.hmset('jwc:' + cookie, {'xh': rs[1], 'xm': rs[3]})
    rdb.expire('jwc:' + cookie, 1800)
    return None


def init_schedule(cookie):
    xh, xm = hmget_decode(rdb, 'jwc:' + cookie, ['xh', 'xm'])
    url = host + '/xskbcx.aspx?xh=' + xh + '&xm=' + xm + '&gnmkdm=N121603'
    resp = requests.get(url, headers=headers, cookies={'ASP.NET_SessionId': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    xnd, xqd = bs.select('#xnd')[0], bs.select('#xqd')[0]
    years = ','.join([option.get('value') for option in xnd.select('option')])
    terms = ','.join([option.get('value') for option in xqd.select('option')])
    table = re.sub(r'<table.*?>', '<table id="Table" class="table table-bordered">', bs.find(id='Table1').prettify())
    selected_year = xnd.select('option[selected]')[0].get('value')
    selected_term = xqd.select('option[selected]')[0].get('value')
    rdb.hmset('jwc:' + cookie, {
        'years': years,
        'terms': terms,
        'selected_year': selected_year,
        'selected_term': selected_term,
        'table': table,
        'view': bs.select('#xskb_form > input:nth-of-type(3)')[0].get('value')
    })
    return years, terms, selected_year, selected_term, table


def get_schedule(cookie, year, term):
    view, xh, xm = hmget_decode(rdb, 'jwc:' + cookie, ['view', 'xh', 'xm'])
    url = host + '/xskbcx.aspx?xh=' + xh + '&xm=' + xm + '&gnmkdm=N121603'
    form = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': view,
        'xnd': year,
        'xqd': term
    }
    resp = requests.post(url, headers=headers, data=form, cookies={'ASP.NET_SessionId': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    table = re.sub(r'<table.*?>', '<table id="Table" class="table table-bordered">', bs.find(id='Table1').prettify())
    rdb.hmset('jwc:' + cookie, {
        'selected_year': year,
        'selected_term': term,
        'table': table,
        'view': bs.select('#xskb_form > input:nth-of-type(3)')[0].get('value')
    })
    return table


def get_score(cookie, year, term):
    xh, xm = hmget_decode(rdb, 'jwc:' + cookie, ['xh', 'xm'])
    score_view = hget_decode(rdb, 'jwc:' + cookie, 'score_view')
    if not score_view:
        score_view = get_score_view(cookie, xh, xm)
    url = host + '/xscjcx.aspx?xh={}&xm={}&gnmkdm=N121605'.format(xh, xm)
    score = []
    form = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': score_view,
        'hidLanguage': '',
        'ddlXN': year,
        'ddlXQ': term,
        'ddl_kcxz': '',
        'btn_xq': '学期成绩'
    }
    resp = requests.post(url, headers=headers, data=form, cookies={'ASP.NET_SessionId': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    items = bs.find(id='Datagrid1')('tr')
    for item in items[1:]:
        td = item('td')
        score.append({
            'name': td[3].get_text(strip=True),
            'credit': td[6].get_text(strip=True),
            'gpa': td[7].get_text(strip=True),
            'usual': td[8].get_text(strip=True),
            'exam': td[10].get_text(strip=True),
            'total': td[12].get_text(strip=True),
        })
    return score

def get_score_view(cookie, xh, xm):
    url = host + '/xscjcx.aspx?xh={}&xm={}&gnmkdm=N121605'.format(xh, xm)
    resp = requests.get(url, headers=headers, cookies={'ASP.NET_SessionId': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    result = bs.find(id='Form1').select('input')[2]['value']
    rdb.hset('jwc:' + cookie, 'score_view', result)
    return result
