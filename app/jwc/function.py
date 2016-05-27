from bs4 import BeautifulSoup
from .. import rdb
from ..utils import hmget_decode
import requests
import re

base_url = 'http://jwc.scnu.edu.cn/'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36',
    'Referer': base_url
}

score_view = 'dDw2NDI3MTcwOTk7dDxwPGw8U29ydEV4cHJlcztzZmRjYms7ZGczO2R5YnlzY2o7U29ydERpcmU7eGg7c3RyX3RhYl9' \
             'iamc7Y2pjeF9sc2I7enhjamN4eHM7PjtsPGtjbWM7XGU7YmpnO1xlO2FzYzsyMDE0MjAwNTAyNzt6Zl9jeGNqdGpfMj' \
             'AxNDIwMDUwMjc7OzA7Pj47bDxpPDE+Oz47bDx0PDtsPGk8ND47aTwxMD47aTwxOT47aTwyND47aTwzMj47aTwzND47a' \
             'TwzNj47aTwzOD47aTw0MD47aTw0Mj47aTw0ND47aTw0Nj47aTw0OD47aTw1Mj47aTw1ND47aTw1Nj47PjtsPHQ8dDxw' \
             'PHA8bDxEYXRhVGV4dEZpZWxkO0RhdGFWYWx1ZUZpZWxkOz47bDxYTjtYTjs+Pjs+O3Q8aTwzPjtAPFxlOzIwMTUtMjA' \
             'xNjsyMDE0LTIwMTU7PjtAPFxlOzIwMTUtMjAxNjsyMDE0LTIwMTU7Pj47Pjs7Pjt0PHQ8cDxwPGw8RGF0YVRleHRGaW' \
             'VsZDtEYXRhVmFsdWVGaWVsZDs+O2w8a2N4em1jO2tjeHpkbTs+Pjs+O3Q8aTw5PjtAPOW/heS/ruivvjvpgInkv67or' \
             '7476ZmQ6YCJ6K++O+S7u+mAieivvjvlhazpgInor7475a6e6Le15pWZ5a2mO+i+heS/ruivvjvlm73lpJbkuqTmjaLo' \
             'r77nqIs7XGU7PjtAPDAxOzAyOzAzOzA0OzA1OzA2OzA3OzE3O1xlOz4+Oz47Oz47dDxwPHA8bDxWaXNpYmxlOz47bDx' \
             'vPGY+Oz4+Oz47Oz47dDxwPHA8bDxWaXNpYmxlOz47bDxvPGY+Oz4+Oz47Oz47dDxwPHA8bDxWaXNpYmxlOz47bDxvPG' \
             'Y+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDxcZTs+Pjs+Ozs+O3Q8cDxwPGw8VGV4dDtWaXNpYmxlOz47bDzlrablj' \
             '7fvvJoyMDE0MjAwNTAyNztvPHQ+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0O1Zpc2libGU7PjtsPOWnk+WQje+8muWQtOWu' \
             'j+WFtDtvPHQ+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0O1Zpc2libGU7PjtsPOWtpumZou+8mui9r+S7tuWtpumZojtvPHQ' \
             '+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0O1Zpc2libGU7PjtsPOS4k+S4mu+8mjtvPHQ+Oz4+Oz47Oz47dDxwPHA8bDxUZX' \
             'h0O1Zpc2libGU7PjtsPOi9r+S7tuW3peeoiztvPHQ+Oz4+Oz47Oz47dDxwPHA8bDxUZXh0Oz47bDzkuJPkuJrmlrnlk' \
             'JE6Oz4+Oz47Oz47dDxwPHA8bDxUZXh0O1Zpc2libGU7PjtsPOihjOaUv+ePre+8mjE06L2v5Lu25bel56iLMeePrTtv' \
             'PHQ+Oz4+Oz47Oz47dDxAMDxwPHA8bDxWaXNpYmxlOz47bDxvPGY+Oz4+Oz47Ozs7Ozs7Ozs7Pjs7Pjt0PDtsPGk8MT4' \
             '7aTwzPjtpPDU+O2k8Nz47aTw5PjtpPDEzPjtpPDE1PjtpPDE5PjtpPDIxPjtpPDIyPjtpPDIzPjtpPDI1PjtpPDI3Pj' \
             'tpPDI5PjtpPDMxPjtpPDMzPjtpPDQxPjtpPDQ3PjtpPDQ5PjtpPDUwPjs+O2w8dDxwPHA8bDxWaXNpYmxlOz47bDxvP' \
             'GY+Oz4+Oz47Oz47dDxAMDxwPHA8bDxWaXNpYmxlOz47bDxvPGY+Oz4+O3A8bDxzdHlsZTs+O2w8RElTUExBWTpub25l' \
             'Oz4+Pjs7Ozs7Ozs7Ozs+Ozs+O3Q8O2w8aTwxMz47PjtsPHQ8QDA8Ozs7Ozs7Ozs7Oz47Oz47Pj47dDxwPHA8bDxUZXh' \
             '0O1Zpc2libGU7PjtsPOiHs+S7iuacqumAmui/h+ivvueoi+aIkOe7qe+8mjtvPHQ+Oz4+Oz47Oz47dDxAMDxwPHA8bD' \
             'xQYWdlQ291bnQ7XyFJdGVtQ291bnQ7XyFEYXRhU291cmNlSXRlbUNvdW50O0RhdGFLZXlzOz47bDxpPDE+O2k8MD47a' \
             'TwwPjtsPD47Pj47cDxsPHN0eWxlOz47bDxESVNQTEFZOmJsb2NrOz4+Pjs7Ozs7Ozs7Ozs+Ozs+O3Q8QDA8cDxwPGw8' \
             'VmlzaWJsZTs+O2w8bzxmPjs+PjtwPGw8c3R5bGU7PjtsPERJU1BMQVk6bm9uZTs+Pj47Ozs7Ozs7Ozs7Pjs7Pjt0PEA' \
             'wPHA8cDxsPFZpc2libGU7PjtsPG88Zj47Pj47cDxsPHN0eWxlOz47bDxESVNQTEFZOm5vbmU7Pj4+Ozs7Ozs7Ozs7Oz' \
             '47Oz47dDxAMDw7Ozs7Ozs7Ozs7Pjs7Pjt0PEAwPHA8cDxsPFZpc2libGU7PjtsPG88Zj47Pj47cDxsPHN0eWxlOz47b' \
             'DxESVNQTEFZOm5vbmU7Pj4+Ozs7Ozs7Ozs7Oz47Oz47dDxAMDxwPHA8bDxWaXNpYmxlOz47bDxvPGY+Oz4+O3A8bDxz' \
             'dHlsZTs+O2w8RElTUExBWTpub25lOz4+Pjs7Ozs7Ozs7Ozs+Ozs+O3Q8QDA8cDxwPGw8VmlzaWJsZTs+O2w8bzxmPjs' \
             '+Pjs+Ozs7Ozs7Ozs7Oz47Oz47dDxAMDxwPHA8bDxWaXNpYmxlOz47bDxvPGY+Oz4+O3A8bDxzdHlsZTs+O2w8RElTUE' \
             'xBWTpub25lOz4+Pjs7Ozs7Ozs7Ozs+Ozs+O3Q8QDA8cDxwPGw8VmlzaWJsZTs+O2w8bzxmPjs+PjtwPGw8c3R5bGU7P' \
             'jtsPERJU1BMQVk6bm9uZTs+Pj47Ozs7Ozs7Ozs7Pjs7Pjt0PEAwPDtAMDw7O0AwPHA8bDxIZWFkZXJUZXh0Oz47bDzl' \
             'iJvmlrDlhoXlrrk7Pj47Ozs7PjtAMDxwPGw8SGVhZGVyVGV4dDs+O2w85Yib5paw5a2m5YiGOz4+Ozs7Oz47QDA8cDx' \
             'sPEhlYWRlclRleHQ7PjtsPOWIm+aWsOasoeaVsDs+Pjs7Ozs+Ozs7Pjs7Ozs7Ozs7Oz47Oz47dDxwPHA8bDxUZXh0O1' \
             'Zpc2libGU7PjtsPOacrOS4k+S4muWFsTc45Lq6O288Zj47Pj47Pjs7Pjt0PHA8cDxsPFZpc2libGU7PjtsPG88Zj47P' \
             'j47Pjs7Pjt0PHA8cDxsPFZpc2libGU7PjtsPG88Zj47Pj47Pjs7Pjt0PHA8cDxsPFZpc2libGU7PjtsPG88Zj47Pj47' \
             'Pjs7Pjt0PHA8cDxsPFRleHQ7PjtsPFNDTlU7Pj47Pjs7Pjt0PHA8cDxsPEltYWdlVXJsOz47bDwuL2V4Y2VsLzIwMTQ' \
             'yMDA1MDI3LmpwZzs+Pjs+Ozs+Oz4+O3Q8O2w8aTwzPjs+O2w8dDxAMDw7Ozs7Ozs7Ozs7Pjs7Pjs+Pjs+Pjs+Pjs+U6' \
             'Rj9ArPkGA3xNS/xAo95A5ZwO4='


def get_code():
    url = base_url + 'CheckCode.aspx'
    resp = requests.get(url, headers=headers, allow_redirects=False)
    print(resp.request.headers)
    cookie = resp.cookies.get('ASP.NET_SessionId')
    return resp.content, cookie


def login(username, password, code, cookie):
    url = base_url + 'default2.aspx'
    form = {
        '__VIEWSTATE': 'dDwyODE2NTM0OTg7Oz4W5FwUsee1KqGNW4fFCJkBIcFXCQ==',
        'txtUserName': username,
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
    alert = re.search(r"alert\('(.*?)'\)", bs.select('script[defer]')[0].get_text())
    if alert:
        return alert.group(1)
    href = bs.select('#headDiv > ul > li:nth-of-type(2) > ul > li:nth-of-type(1) > a')[0].get('href')
    rs = re.split(r'=|&', href)
    rdb.hmset('jwc:' + cookie, {'xh': rs[1], 'xm': rs[3]})
    rdb.expire('jwc:' + cookie, 1800)
    return None


def init_schedule(cookie, name):
    xh, xm = hmget_decode(rdb, name, ['xh', 'xm'])
    url = base_url + 'xskbcx.aspx?xh=' + xh + '&xm=' + xm + '&gnmkdm=N121603'
    resp = requests.get(url, headers=headers, cookies={'ASP.NET_SessionId': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    xnd, xqd = bs.select('#xnd')[0], bs.select('#xqd')[0]
    years = ','.join([option.get('value') for option in xnd.select('option')])
    terms = ','.join([option.get('value') for option in xqd.select('option')])
    table = re.sub(r'<table.*?>', '<table id="Table" class="table table-bordered">', bs.find(id='Table1').prettify())
    selected_year = xnd.select('option[selected]')[0].get('value')
    selected_term = xqd.select('option[selected]')[0].get('value')
    rdb.hmset(name, {
        'years': years,
        'terms': terms,
        'selected_year': selected_year,
        'selected_term': selected_term,
        'table': table,
        'view': bs.select('#xskb_form > input:nth-of-type(3)')[0].get('value')
    })
    return years, terms, selected_year, selected_term, table


def get_schedule(cookie, name, year, term):
    view, xh, xm = hmget_decode(rdb, name, ['view', 'xh', 'xm'])
    url = base_url + 'xskbcx.aspx?xh=' + xh + '&xm=' + xm + '&gnmkdm=N121603'
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
    rdb.hmset(name, {
        'selected_year': year,
        'selected_term': term,
        'table': table,
        'view': bs.select('#xskb_form > input:nth-of-type(3)')[0].get('value')
    })
    return table


def get_score(cookie, name, year, term):
    xh, xm = hmget_decode(rdb, name, ['xh', 'xm'])
    url = base_url + 'xscjcx.aspx?xh={}&xm={}&gnmkdm=N121605'.format(xh, xm)
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
    items = bs.select('#Datagrid1 > tr')
    for item in items[1:]:
        score.append({
            'name': item.select('td:nth-of-type(4)')[0].get_text().strip(),
            'credit': item.select('td:nth-of-type(7)')[0].get_text().strip(),
            'gpa': item.select('td:nth-of-type(8)')[0].get_text().strip(),
            'performance': item.select('td:nth-of-type(9)')[0].get_text().strip(),
            'exam': item.select('td:nth-of-type(11)')[0].get_text().strip(),
            'total': item.select('td:nth-of-type(13)')[0].get_text().strip()
        })
    return score

