from bs4 import BeautifulSoup
from .. import rdb
import requests
import re
import time

base_url = 'http://202.116.41.246:8080/reader'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'
}


def get_code():
    url = base_url + '/captcha.php'
    resp = requests.get(url, headers=headers)
    cookie = resp.cookies.get('PHPSESSID')
    return resp.content, cookie


def get_renew_code(cookie):
    url = base_url + '/captcha.php'
    resp = requests.get(url, headers=headers, cookies={'PHPSESSID': cookie})
    return resp.content


def login(cookie, username, password, code):
    url = base_url + '/redr_verify.php'
    form = {
        'number': username,
        'passwd': password,
        'captcha': code,
        'select': 'bar_no',
        'returnUrl': ''
    }
    resp = requests.post(url, headers=headers, data=form, cookies={'PHPSESSID': cookie})
    content = resp.content.decode('utf-8')
    if '密码错误' in content:
        return '密码错误'
    elif '验证码错误' in content:
        return '验证码错误'
    elif '请输入正确的读者证件号' in content:
        return '用请输入正确的读者证件号'
    rdb.hset('lib:' + cookie, 'foo', 'foo')
    rdb.expire('lib:' + cookie, 3600)
    return '登录成功'


def get_info(cookie):
    url = base_url + '/redr_info.php'
    resp = requests.get(url, headers=headers, cookies={'PHPSESSID': cookie})
    bs = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    reader_name = bs.select('#mylib_info > table > tr:nth-of-type(1) > td:nth-of-type(2)')[0];
    reader_id = bs.select('#mylib_info > table > tr:nth-of-type(1) > td:nth-of-type(3)')[0];
    reader_type = bs.select('#mylib_info > table > tr:nth-of-type(4) > td:nth-of-type(1)')[0];
    reader_unit = bs.select('#mylib_info > table > tr:nth-of-type(7) > td:nth-of-type(1)')[0];
    info = {
        'name': reader_name.get_text().split('：')[-1],
        'identifier': reader_id.get_text().split('：')[-1],
        'type': reader_type.get_text().split('：')[-1],
        'unit': reader_unit.get_text().split('：')[-1]
    }
    rdb.hmset('lib:' + cookie, info)
    return info


def get_books(cookie):
    books = []
    url = base_url + '/book_lst.php'
    resp = requests.get(url, headers=headers, cookies={'PHPSESSID': cookie})
    bs = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    items = bs.select('#mylib_content > .table_line > tr')
    for item in items[1:]:
        books.append({
            'barcode': item.select('td:nth-of-type(1)')[0].get_text(),
            'title': item.select('td:nth-of-type(2)')[0].get_text().rsplit('/', maxsplit=1)[0].strip(),
            'author': item.select('td:nth-of-type(2)')[0].get_text().rsplit('/', maxsplit=1)[-1].strip(),
            'borrow': item.select('td:nth-of-type(3)')[0].get_text(),
            'return': item.select('td:nth-of-type(4)')[0].get_text(),
            'renew': item.select('td:nth-of-type(5)')[0].get_text(),
            'place': item.select('td:nth-of-type(6)')[0].get_text(),
            'check': item.select('div > input')[0].get('onclick').split("'")[3]
        })
    return books


def renew(cookie, barcode, code, check):
    url = base_url + '/ajax_renew.php?bar_code={}&captcha={}&check={}&time={}'.format(barcode, code, check, int(time.time() * 1000))
    resp = requests.get(url, headers=headers, cookies={'PHPSESSID': cookie})
    bs = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    return bs.get_text()
