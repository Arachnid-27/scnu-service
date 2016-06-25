from bs4 import BeautifulSoup, SoupStrainer
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


def get_courses(cookie):
    url = host + '/getAllCourses.html'
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    items = json.loads(resp.content.decode('utf-8'))[0]['加入的课程']
    courses = [{
        'title': item['title'],
        'cid': item['id']
    } for item in items]
    rdb.hset('sch:' + cookie, 'courses', json.dumps(courses))
    return courses


def get_info(cookie, cid):
    url = host + '/course/ml_course.html?courseId={}'.format(cid)
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    info = {
        'title': bs.title.get_text(),
        'teacher': bs.find(class_='am-icon-user').find_next().get_text()
    }
    rdb.hset('sch:' + cookie, 'info:' + str(cid), json.dumps(info))
    return info


def get_homework(cookie, cid, cur=1):
    status_map = {
        '已截止': -1,
        '未截止': 0,
        '按时提交': 1,
        '延时提交': 2
    }
    homework = []
    url = host + '/course/S_homeworkList.html?courseId={}&cpage={}'.format(cid, cur)
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    parse_only = SoupStrainer(class_='underContent')
    bs = BeautifulSoup(resp.text, 'lxml', parse_only=parse_only)
    rs = bs.find(class_='page')
    page = 1 if not rs else int(re.search(r'\d+', rs.get_text()).group())
    for item in bs(class_='altrow'):
        td = item('td')
        homework.append({
            'title': td[0].find('a').get('title').strip(),
            'deadline': td[2].get_text(strip=True),
            'handin': td[3].get_text(strip=True),
            'status': status_map.get(td[4].get_text(strip=True), -2),
            'hid': int(re.search(r'homeworkId=(\d+)', td[0].find('a').get('href')).group(1))
        })
    rs = bs.find(id='studentId')
    sid = None if not rs else int(rs.get('value'))
    return homework, int(page), sid


def download_homework(cookie, cid, sid, hid):
    url = host + '/course/S_downloadStudentHomework.html?courseId={}&studentId={}&homeworkId={}'.format(cid, sid, hid)
    return download_url({'JSESSIONID': cookie}, url)


def get_details(cookie, cid, hid):
    url = host + '/course/S_oneHomework.html?courseId={}&homeworkId={}'.format(cid, hid)
    resp = requests.get(url, headers=headers, cookies={'JSESSIONID': cookie})
    bs = BeautifulSoup(resp.text, 'lxml')
    content = bs.find('div', class_='notice_content').prettify()
    titles = bs.select('.cont > div > p > span')
    links = bs.select('.cont > div > a')
    attach = [{
        'title': title.get('title'),
        'lid': re.search(r'homeworkLinkId=(\d+)', link.get('href')).group(1)
    } for title, link in zip(titles, links)]
    return content, attach


def download_attach(cookie, cid, lid):
    url = host + '/course/S_downloadHomeworkLink.html?courseId={}&homeworkLinkId={}'.format(cid, lid)
    return download_url({'JSESSIONID': cookie}, url)


def upload_homework(cookie, cid, sid, hid, file, filename):
    url = host + '/course/S_uploadHomework.html?studentId={}&courseId={}&homeworkId={}'.format(sid, cid, hid)
    files = {
        'Filename': (None, filename),
        'file': (urllib.parse.quote(filename, encoding='gb2312'), file, 'application/octet-stream'),
        'Upload': (None, 'Submit Query')
    }
    resp = requests.post(url, headers=headers, files=files, cookies={'JSESSIONID': cookie})
    return True if 'homework' in resp.text else False


def download_url(cookies, url):
    resp = requests.get(url, headers=headers, cookies=cookies)
    if 'Content-Disposition' not in resp.headers:
        return None, None
    disposition = resp.headers['Content-Disposition'].encode('iso-8859-1').decode('gb2312')
    return resp.content, {
        'Content-Disposition': urllib.parse.quote(disposition, safe='/=;'),
        'Content-Type': resp.headers['Content-Type']
    }

