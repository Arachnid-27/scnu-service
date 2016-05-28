from bs4 import BeautifulSoup
from .. import rdb
import requests
import re
import json
import urllib.parse

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
        tag = item.select('td:nth-of-type(1) > a')[0]
        rs = re.search(r'homeworkId=(\d+)', tag.get('href'))
        homework.append({
            'title': tag.get('title').strip(),
            'deadline': item.select('td:nth-of-type(3)')[0].get_text().strip(),
            'handin': item.select('td:nth-of-type(4)')[0].get_text().strip(),
            'status': item.select('td:nth-of-type(5)')[0].get_text().strip(),
            'hid': int(rs.group(1))
        })
    title = bs.select('.head-title')[0].get_text()
    sid = int(bs.find(id='studentId').get('value'))
    return homework, title, int(page), sid


def download_homework(cookie, cid, sid, hid):
    url = host + '/course/S_downloadStudentHomework.html?courseId={}&studentId={}&homeworkId={}'.format(cid, sid, hid)
    return download_url({'JSESSIONID': cookie}, url)


def get_details(cookie, cid, hid):
    url = host + '/course/S_oneHomework.html?courseId={}&homeworkId={}'.format(cid, hid)
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    content = bs.select('.notice_content')[0].prettify()
    titles = bs.select('.cont > div > p > span')
    links = bs.select('.cont > div > a')
    attach = []
    for title, link in zip(titles, links):
        attach.append({
            'title': title.get('title'),
            'lid': re.search(r'homeworkLinkId=(\d+)', link.get('href')).group(1)
        })
    return content, attach


def download_attach(cookie, cid, lid):
    url = host + '/course/S_downloadHomeworkLink.html?courseId={}&homeworkLinkId={}'.format(cid, lid)
    return download_url({'JSESSIONID': cookie}, url)


def upload_homework(cookie, cid, sid, hid, file, filename):
    url = host + '/course/S_uploadHomework.html?studentId={}&courseId={}&homeworkId={}'.format(sid, cid, hid)
    files = {
        'Filename': (None, filename),
        'file': (urllib.parse.quote(filename), file, 'application/octet-stream'),
        'Upload': (None, 'Submit Query')
    }
    resp = requests.post(url, headers=headers, files=files, cookies={'JSESSIONID': cookie})
    if 'homework' in resp.text:
        return True
    return False


def download_url(cookies, url):
    resp = requests.get(url, headers=headers, cookies=cookies)
    if 'Content-Disposition' not in resp.headers:
        return None, None
    return resp.content, {
        'Content-Disposition': resp.headers['Content-Disposition'],
        'Content-Type': resp.headers['Content-Type']
    }

