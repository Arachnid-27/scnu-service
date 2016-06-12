from bs4 import BeautifulSoup
from .. import rdb
import requests
import re

base_url = 'http://202.116.41.246/m/reader'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'
}


def login(username, password):
    url = base_url + '/check_login.action'
    form = {
        'name': username,
        'passwd': password,
        'type': '2'
    }
    resp = requests.post(url, headers=headers, data=form)
    msg = re.search(r"msg:'(.*?)'", resp.text)
    if not msg:
        cookie = resp.cookies.get('JSESSIONID')
        rdb.hset('lib:' + cookie, 'foo', 'foo')
        rdb.expire('lib:' + cookie, 3600)
        return '登录成功', cookie
    return msg.group(1), None


def get_info(cookie):
    url = base_url + '/info.action'
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    rs = bs.find_all('h6')
    info = {
        'name': rs[0].get_text().split(':')[-1],
        'identifier': rs[1].get_text().split(':')[-1],
        'type': rs[3].get_text().split(':')[-1],
        'unit': rs[4].get_text().split(':')[-1]
    }
    rdb.hmset('lib:' + cookie, info)
    return info


def get_books(cookie):
    books = []
    url = base_url + '/lend_list.action'
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    items = bs.select('#lend_list > li')
    for item in items[1:]:
        rs = re.search('^\d+\.(.*)/(.*?)[编著]', item.select('a > h3')[0].get_text().strip())
        books.append({
            'title': rs.group(1),
            'author': rs.group(2),
            'borrow': item.select('a > p:nth-of-type(1)')[0].get_text().strip().split(':')[1],
            'return': item.select('a > p:nth-of-type(2)')[0].get_text().strip().split(':')[1],
            'place': item.select('a > p:nth-of-type(3)')[0].get_text().strip().split(':')[1],
            'barcode': item.select('input[onclick]')[0].get('onclick').split("'")[-2]
        })
    return books


def renew(cookie, barcode):
    url = base_url + '/renew.action?barcode={}'.format(barcode)
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    msg = bs.select('body > div > div:nth-of-type(3) > h3')[0].get_text()
    return msg
