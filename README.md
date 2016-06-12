# SCNU Service
- 聚集校内常用的三个网站，便利生活
- 开发采用 `Flask` 框架

## 功能介绍
[学者网](http://www.scholat.com)
- 查看作业详情
- 下载作业附件
- 上交作业
- 下载作业

[图书馆](http://lib.scnu.edu.cn)
- 查询当前借阅
- 续借书籍

[教务系统](http://jwc.scnu.edu.cn)
- 查询个人成绩
- 查询个人课表

## 应用截图
![image](https://github.com/Arachnid-27/scnu-service/raw/master/screenshots/index.png)
![image](https://github.com/Arachnid-27/scnu-service/raw/master/screenshots/login.png)
![image](https://github.com/Arachnid-27/scnu-service/raw/master/screenshots/scholat.png)
![image](https://github.com/Arachnid-27/scnu-service/raw/master/screenshots/library.png)
![image](https://github.com/Arachnid-27/scnu-service/raw/master/screenshots/score.png)
![image](https://github.com/Arachnid-27/scnu-service/raw/master/screenshots/manager.png)

## 使用说明
- 安装 `Python3`
- 安装 `Redis` 作为数据缓存
- 执行 `pip install -r requirements.txt` 安装所需依赖
- 执行 `python scnu.py` 或 `gunicorn -c gunicorn.conf scnu:app` 运行应用
