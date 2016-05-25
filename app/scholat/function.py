from bs4 import BeautifulSoup
from .. import rdb
from ..utils import hmget_decode
import requests
import re
import json


base_url = 'http://www.scholat.com/'

headers_mb = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/48.0.2564.23 Mobile Safari/537.36'
}

headers_pc = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'
}


def login(username, password):
    form = {
        'j_username': username,
        'j_password': password
    }
    url = base_url + 'Auth.html'
    resp = requests.post(url, headers=headers_pc, data=form)
    if '登录信息错误' in resp.text:
        return '登录信息错误', None
    cookie = resp.request.headers['Cookie'].split('=')[-1]
    rdb.hset('sch:' + cookie, 'foo', 'foo')
    rdb.expire('sch:' + cookie, '3600')
    return '登录成功', cookie


# 获取课程列表
def get_list(cookie):
    url = base_url + 'getAllCourses.html'
    resp = requests.get(url, headers=headers_mb, cookies={'JSESSIONID': cookie})
    resp.encoding = 'utf-8'
    items = json.loads(resp.text)[0]['加入的课程']
    courses = [{
            'title': item['title'],
            'cid': item['id']
    } for item in items]
    rdb.hset('sch:' + cookie, 'courses', json.dumps(courses))
    print(courses)
    return courses


def get_homework(cookie, cid):
    homework = []
    url = base_url + 'course/S_homeworkList.html?courseId={}'.format(cid)
    resp = requests.get(url, headers=headers_pc, cookies={'JSESSIONID': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    page = 1
    temp = bs.select('div.page')
    if temp:
        page = re.search(r'\d+', temp[0].get_text())
    for item in bs.select('.altrow'):
        info = item.select('td:nth-of-type(1) > a')[0]
        title = info.get('title')
        title = title[:30] + '..' if len(title) > 30 else title
        '''
            if href == '#':
                href = None
            else:
                args = re.split(r'\?|&', href)
                href = 'http://www.scholat.com/course/S_downloadStudentHomework.html?' \
                       + args[1] + '&' + args[4] + '&' + args[2]
        '''
        homework.append({
            'title': title,
            'deadline': item.select('td:nth-of-type(3)')[0].get_text(),
            'handin': item.select('td:nth-of-type(4)')[0].get_text(),
            'status': item.select('td:nth-of-type(5)')[0].get_text(),
            'id': info.get('href').split('=')[-1]
        })
    title = bs.select('.head-title')[0].get_text()
    return homework, title


