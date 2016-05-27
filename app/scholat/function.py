from bs4 import BeautifulSoup
from .. import rdb
import requests
import re
import json

host = 'http://www.scholat.com'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'
}


def login(username, password):
    form = {
        'j_username': username,
        'j_password': password
    }
    url = host + '/Auth.html'
    resp = requests.post(url, headers=headers, data=form)
    if '登录信息错误' in resp.text:
        return '登录信息错误', None
    cookie = resp.request.headers['Cookie'].split('=')[-1]
    rdb.hset('sch:' + cookie, 'foo', 'foo')
    rdb.expire('sch:' + cookie, '3600')
    return '登录成功', cookie


# 获取课程列表
def get_list(cookie):
    url = host + '/getAllCourses.html'
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    resp.encoding = 'utf-8'
    items = json.loads(resp.text)[0]['加入的课程']
    courses = [{
            'title': item['title'],
            'cid': item['id']
    } for item in items]
    rdb.hset('sch:' + cookie, 'courses', json.dumps(courses))
    return courses


def get_homework(cookie, cid, cur=1):
    homework = []
    url = host + '/course/S_homeworkList.html?courseId={}&cpage={}'.format(cid, cur)
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    page = 1
    temp = bs.select('div.page')
    if temp:
        page = re.search(r'\d+', temp[0].get_text()).group(0)
    for item in bs.select('.altrow'):
        info = item.select('td:nth-of-type(6) > a')
        rs = re.search(r'homeworkId=(\d+)', info[0].get('href'))
        hid = None if not rs else int(rs.group(1))
        rs = re.search(r'studentId=(\d+)', info[1].get('href'))
        sid = None if not rs else int(rs.group(1))
        homework.append({
            'title': item.select('td:nth-of-type(1) > a')[0].get('title').strip(),
            'deadline': item.select('td:nth-of-type(3)')[0].get_text().strip(),
            'handin': item.select('td:nth-of-type(4)')[0].get_text().strip(),
            'status': item.select('td:nth-of-type(5)')[0].get_text().strip(),
            'hid': hid,
            'sid': sid
        })
    title = bs.select('.head-title')[0].get_text()
    return homework, title, int(page)


def download_homework(cookie, cid, sid, hid):
    url = host + '/course/S_downloadStudentHomework.html?courseId={}&studentId={}&homeworkId={}'.format(cid, sid, hid)
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    if 'Content-Disposition' not in resp.headers:
        return None, None
    return resp.content, {
        'Content-Disposition': resp.headers['Content-Disposition'],
        'Content-Type': resp.headers['Content-Type']
    }


