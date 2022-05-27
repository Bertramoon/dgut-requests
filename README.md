[![dugt-requests](https://img.shields.io/pypi/v/dgut-requests?color=blue)](https://pypi.org/project/dgut-requests)
[![Build Status](https://travis-ci.org/BertraMoon/dgut-requests.svg?branch=master)](https://travis-ci.org/BertraMoon/dgut-requests)
[![README](https://img.shields.io/badge/README-Chinese-brightgreen)](https://github.com/BertraMoon/dgut-requests/blob/master/README.md)
[![GitHub](https://img.shields.io/github/license/bertramoon/dgut-requests)](https://github.com/BertraMoon/dgut-requests/blob/master/LICENSE)  


# 0. 前言

dgut-requests是一款适用于东莞理工学院系统的Python库（要求Python3.7及以上版本），主要基于requests库进行再抽象并实现所需功能，采用面向切面编程(AOP)，目前基于该库已做出勤工俭学自动考勤、疫情防控自动打卡、出入校快速申请等小应用。 

这是一篇面向编程新手的帮助文档，我会通过例子向你展示这个库的功能。如果你不熟悉dgut-requests库，请从头开始完整阅读本文档，并在自己的电脑上尝试运行一下（PS：演示所使用的操作系统是windows 10）。如果你有编程基础，并且对Python语言比较熟悉，那可以直接阅读[说明文档](#4-说明文档)。 

# 1. 安装
请先确保自己已经安装了pip

```
pip install dgut-requests
```


如果安装得很慢，甚至报错的话，很可能是网速问题，这时候可以使用镜像源进行下载。我个人比较推荐的镜像源是清华镜像源，我们可以将上面的cmd命令改成这样：  

```
pip install -i "https://pypi.tuna.tsinghua.edu.cn/simple/" dgut-requests
```

在Python交互界面环境下，输入`import dgut_requests`没有报错即成功安装了dgut-requests库。  
```
Python 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 23:11:46) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import dgut_requests
>>>
```

# 2. 基本用法
## 2.1. 导入

- 旧版

```
>>> from dgut_requests.dgut import dgutUser, dgutXgxt, dgutIllness
>>> dgutUser
<class 'dgut_requests.dgut.dgutUser'>
>>> dgutXgxt
<class 'dgut_requests.dgut.dgutXgxt'>
>>> dgutIllness
<class 'dgut_requests.dgut.dgutIllness'>
>>>
```
- 但是更建议使用新版接口

```
>>> from dgut_requests import DgutUser, DgutXgxt, DgutIllness
>>> DgutUser
<class 'dgut_requests.dgut.DgutUser'>
>>> DgutXgxt
<class 'dgut_requests.dgut.DgutXgxt'>
>>> DgutIllness
<class 'dgut_requests.dgut.DgutIllness'>
>>>
```
如果想要更加方便的话，可以这样
```
>>> from dgut_requests.dgut *
>>> DgutUser
<class 'dgut_requests.dgut.DgutUser'>
>>> DgutXgxt
<class 'dgut_requests.dgut.DgutXgxt'>
>>>
```

## 2.2. 构建账号，实现登录
```python
from dgut_requests import DgutUser

u = DgutUser("201841312111", "123456") # DgutUser(username, password)

response = u.signin("https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html") # 登录学工系统, signin(login_url: str)
print(response)
# <Response [200]>
print(response.text)
"""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">
<html>
<head>
<title>学生信息管理系统</title>
<meta http-equiv="refresh" content="0;URL=homepage.jsp">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body>
正在进入首页
</body>
</html>
"""



response = u.session.get("http://stu.dgut.edu.cn/student/basicinfo/basicInfo.jsp")
print(response)
# <Response [200]>
print(response.text)
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>学生基本信息</title>
<link href="/css/main.css" rel="stylesheet" type="text/css">
<script type="text/javascript">
function submitTo(formId, url) {
        var form = document.getElementById("" + formId);
        form.action = url;
        form.submit();
}
function SubmitToBlank(formId, url) {
        var form = document.getElementById("" + formId);
        form.action = url;
        form.target = "_blank";
        form.submit();
        form.action = '';
        form.target = "_self";
}
</script>
</head>
<body>
……
"""
```


## 2.3. 获取考勤职位信息 & 学工系统考勤
```python
from dgut_requests import DgutXgxt

u = DgutXgxt("201841312111", "123456") # DgutUser(username, password)

# get_workAssignment()方法获取考勤职位信息，返回一个包含二元组的列表，每一个二元组包含考勤职位ID和考勤职位名。当你没有任何职位时，返回空列表[]
print(u.get_workAssignment())
# [('9000', 'XXX学生助理'), ('9001', 'xxx办公室助理')]


# attendance(flag: int, workAssignmentId: int = None)
# flag=1表示签到，flag=2表示签退
# workAssignmentId为None或者缺省时，表示调用get_workAssignment()方法并获取第一个职位信息的ID作为该参数
print(u.attendance(1))
# {'message': '签到成功', 'code': 1, 'info': {'data': {'action_name': 'beginWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1619157009355', 'backUrl': '', 'workAssignmentId': '9000'}, 'time': datetime.datetime(2021, 4, 23, 13, 50, 9, 542232)}}
print(u.attendance(2))
# {'message': '签退成功', 'code': 1, 'info': {'data': {'action_name': 'endWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1619157045726', 'backUrl': '', 'workAssignmentId': '9000'}, 'time': datetime.datetime(2021, 4, 23, 13, 50, 45, 960229)}}


print(u.attendance(1, 9001))
# {'message': '签到成功', 'code': 1, 'info': {'data': {'action_name': 'beginWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1619157089460', 'backUrl': '', 'workAssignmentId': '9001'}, 'time': datetime.datetime(2021, 4, 23, 13, 51, 29, 618113)}}
print(u.attendance(2, 9001))
# {'message': '签退成功', 'code': 1, 'info': {'data': {'action_name': 'endWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1619157094360', 'backUrl': '', 'workAssignmentId': '9001'}, 'time': datetime.datetime(2021, 4, 23, 13, 51, 34, 492294)}}
```

细心的读者可能已经发现了，上面的代码中，构建账号后并没有调用`signin(login_url: str)`方法，而是直接调用两个功能方法。  
这是因为DgutXgxt类中使用python的装饰函数实现AOP面向切面编程，在调用`get_workAssignment()`和`attendance(flag: int, workAssignmentId: int = None)`方法时会自动判断是否已登录、未登录则会先调用`signin(login_url: str)`方法进行登录认证。


## 2.4. 实现每日疫情打卡
```python
from dgut_requests import DgutIllness

u = dgutIllness("201841312111", "123456")
print(u.report())
# {'message': '您今天已打卡成功！已连续打卡688天！'}
```

与前面一样，先构造一个`DgutIllness`对象，然后调用`report()`方法即可完成打卡。该功能仅用于爬虫学习及防止忘记打卡，疫情期间切勿轻视打卡。  

因为有些字段（如最后一次核酸时间）学校系统会过几天清空一次，所以会出现打卡成功之后这些字段是空的情况。为了解决这个情况，我们可以自定义字段

```python
from dgut_requests import DgutIllness

data = {
    "latest_acid_test": "2022-05-26"
}

u = DgutIllness("201841312111", "123456")
print(u.report(custom_data=data))
# {'message': '您今天已打卡成功！已连续打卡688天！'}
```

## 2.5. 获取个人成绩
```python
from dgut_requests import DgutJwxt

u = DgutJwxt("201841312111", "123456")

# 获取本学期的原始成绩
# 现在是2022年5月，即2021-2022学年第二学期
for item in u.get_score():
    print(*item)
"""
[0710010]形势与政策 2.0 12 公共课/必修课 初修 考试 初修取得 xx
[4100088]毕业实习 2.0 0 实习 初修 初修取得 xx
...
"""


# 获取2020-2021学年第一学期的原始成绩
# xn=2020代表2020-2021学年
# xq=1代表第一学期，xq=2代表第二学期
for item in u.get_score(xn=2020, xq=1):
    print(*item)
"""
[0710007]形势与政策5 0.0 公共课/必修课 初修 考试 初修取得 xx
[1310006]体育5 0.5 公共课/必修课 初修 考试 初修取得 xx
[0410084]PHP程序设计 3.0 专业课/任选课 初修 考查 初修取得 xx
...
"""


# 获取2020-2021学年第一学期的有效成绩
for item in u.get_score(score_type=2, xn=2020, xq=1):
    print(*item)
"""
[0710007]形势与政策5 0.0 公共课/必修课 初修 考试 xx 0.0 xx xx
[1310006]体育5 0.5 公共课/必修课 初修 考试 xx 0.5 xx xx
[0410084]PHP程序设计 3.0 专业课/任选课 初修 考查 xx 3.0 xx xx
...
"""

    

# 获取2019-2020学年的原始成绩
# time_range=2代表按学年查询（1：入学以来 | 2：按学年 | 3：按学期）
# xn=2019代表2019-2020学年
for item in u.get_score(time_range=2, xn=2019):
    print(*item)
"""
[14510300]计算机组成原理 4.0 专业基础课/必修课 初修 考试 初修取得 xx
[14540011]JAVA语言程序设计 3.0 专业基础课/必修课 初修 考试 初修取得 xx
[048774]离散数学 4.0 专业基础课/必修课 初修 考试 初修取得 xx
[0710002]马克思主义基本原理 3.0 公共课/必修课 初修 考试 初修取得 xx
[0710005]形势与政策3 0.0 公共课/必修课 初修 考试 初修取得 xx
[1010005]应用英语A 2.0 公共课/必修课 初修 考试 初修取得 xx
[1310004]体育3 0.5 公共课/必修课 初修 考查 初修取得 xx
[0410032]概率论与数理统计 3.5 专业基础课/必修课 初修 考试 初修取得 xx
[379925]算法与数据结构 5.0 专业基础课/必修课 初修 考试 初修取得 xx
...
"""
    
    

# 获取入学以来的有效成绩
for item in u.get_score(time_range=1, score_type=2):
    print(*item)
"""
[19510070]中国近现代史纲要 2.0 公共课/必修课 初修 考试 xx 2.0 xx xx
[0710003]形势与政策1 0.0 公共课/必修课 初修 考试 xx 0.0 xx xx
[1010001]大学英语1 3.0 公共课/必修课 初修 考试 xx 3.0 xx xx
[1010003]英语口语1 1.0 公共课/必修课 初修 考试 xx 1.0 xx xx
[0810001]管理学概论 2.0 公共课/必修课 初修 考查 xx 2.0 xx xx
[1310001]大学生心理健康教育 1.0 公共课/必修课 初修 考查 xx 1.0 xx xx
[1310002]体育1 1.0 公共课/必修课 初修 考查 xx 1.0 xx xx
[1710001]军事训练与教育 3.0 军训 初修 xx 3.0 xx xx
[0410029]高等数学C(I) 5.0 专业基础课/必修课 初修 考试 xx 5.0 xx xx
[0410069]网络空间安全专业导论与职业生涯规划 1.0 专业基础课/必修课 初修 考查 xx 1.0 xx xx
[0410073]程序设计基础 5.0 专业基础课/必修课 初修 考试 xx 5.0 xx xx
[0710001]思想道德修养与法律基础 3.0 公共课/必修课 初修 考试 xx 3.0 xx xx
[0710004]形势与政策2 0.0 公共课/必修课 初修 考试 xx 0.0 xx xx
[078645]“思政课”社会实践1 1.0 社会实践 初修 xx 1.0 xx xx
...
[0410084]PHP程序设计 3.0 专业课/任选课 初修 考查 xx 3.0 xx xx
...
[4100088]毕业实习 2.0 0 实习 初修 初修取得 xx
"""
    
    

# get_score(score_type: int = 1, course_type: int = 3, time_range: int = 3, **kwargs)
# score_type: 成绩类型: 1=>原始成绩（默认） | 2=>有效成绩
# course_type: 课程类型: 1=>主修 | 2=>辅修 | 3=>主修和辅修（默认）
# time_range: 时间范围选择: 1=>入学以来 | 2=>学年 | 3=>学期（默认）
# **kwargs: 补充参数，有xn和xq两个参数，都是int类型
    # xn: 学年: [1970, 9999]
    # xq: 学期: 1 | 2
```

首先创建一个`DgutJwxt`对象，然后调用`get_score`方法返回一个成绩结果的生成器，该生成器的每个元素对应着一条记录。  
有兴趣的朋友可以研究一下openpyxl库，制作一个生成学年综测excel表格的脚本。

# 3. 高级用法

## 3.1. session会话管理
`dgutUser`类及其子类(`dgutXgxt`、`dgutIllness`)的构造函数中定义了一个`requests.Session()`对象session进行会话管理，它会自动保存cookies信息，并且每次发起http请求都会使用该对象的headers和cookies属性作为http包的头部。因此，我们使用其来发起请求，可以更加轻松方便。

```python
from dgut_requests import DgutUser


u = DgutUser("201841312111", "123456")
u.signin("https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html")

# 使用session进行会话管理
print("对象u的cookies有：")
for key, value in u.session.cookies.items():
    print(f"{key}={value}")
"""
PHPSESSID=f6e8e2ue5qqn8qu7kjq1abmhf1
last_oauth_appid=xgxtt
JSESSIONID=1811A6B611868FA3529A18214A263E1B.sms9011
"""


# 我们再登录一下教务服务平台试试，并查看登录之后cookies有什么变化
print("对象u当前的cookies有：")
u.session.get("https://cas.dgut.edu.cn/home/Oauth/getToken/appid/jwyd.html")
for key, value in u.session.cookies.items():
    print(f"{key}={value}")
"""
PHPSESSID=f6e8e2ue5qqn8qu7kjq1abmhf1
last_oauth_appid=jwyd
JSESSIONID=6FBE069884CCAFB6D26E69DC237686E7
JSESSIONID=1811A6B611868FA3529A18214A263E1B.sms9011
"""
```

## 3.2. 使用cookies进行管理
当账号很多并且操作很多的时候，如果每一次都需要进行登录，那么效率就会很低。此外，如果短时间内需要重复登录的话，可能需要重复输入账号密码。  
有一个比较好的方案就是可以使用cookies。cookies一般会有一定时长的有效期，在有效期内我们可以把账号密码置空，直接将cookies信息添加到空账号中。这样，当我们模拟访问网页的时候也可以畅行无阻。

```python
from dgut_requests import *
import re
import os
import json
import requests

path = 'cookies.json'

def cookies_is_expires(path: str, url: str, pattern: re.compile):
    '''
    判断cookies是否过期（过期或不存在该文件都视为过期）
    '''
    if not os.path.exists(path):
        return True
    with open(path, 'r') as f:
        cookie = json.loads(f.read())
    headers = {
        "cookie": ";".join([f"{k}={v}" for k,v in cookie.items()])
    }
    response = requests.get(url, headers=headers)
    if pattern.search(response.text, re.S):
        return True
    return False


if not os.path.exists(path) or cookies_is_expires(path, "http://stu.dgut.edu.cn/homepage.jsp", re.compile(r'token = ".*?"')):
    u = DgutXgxt("201841312111", "123456")
    print(u.get_workAssignment())
    cookie = requests.utils.dict_from_cookiejar(u.session.cookies)
    print(cookie)
    with open(path, 'w') as f:
        f.write(json.dumps(cookie))
else:
    print("has cookies")
    with open(path, 'r') as f:
        cookies = json.loads(f.read())
    u = DgutXgxt('', '')
    requests.utils.add_dict_to_cookiejar(u.session.cookies, cookies)
    print(u.get_workAssignment())
    print(u.session.cookies)
```

第一次输出结果
```
[('9000', 'xxx学生助理')]
{'JSESSIONID': '88847A3F393EB86DEC60ECDE60007533.sms9011', 'PHPSESSID': '8qahsd5f8gocuqdpddkq5vghg0', 'last_oauth_appid': 'xgxtt'}
```

第二次输出结果
```
has cookies
[('9000', 'xxx学生助理')]
<RequestsCookieJar[<Cookie JSESSIONID=88847A3F392EB86DEC60ECDE66007533.sms9011 for />, <Cookie PHPSESSID=8qahsd5f8gocuqdpddkq5vghg0 for />, <Cookie last_oauth_appid=xgxtt for />]>
```

## 3.3. 基于DgutUser开发新系统，基于现有系统开发新功能
开发者可基于`DgutUser`及其子类进行新功能的开发，继承`DugtUser`及其子类，然后用装饰函数`DgutUser.decorator_signin`装饰新功能函数。这样，开发者只需要关心功能的实现而不需要关心登录功能。

# 4. 说明文档
## 4.1. class AuthError
认证错误类，在认证失败时会抛出该异常。
```python
from dgut_requests import DgutUser, AuthError

try:
    u = DgutUser('123', '456')
    u.signin("https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html")
except AuthError as e:
    print(e)
```

## 4.2. class DgutUser
|                                                属性/方法 | 说明                                                         |
| -------------------------------------------------------: | :----------------------------------------------------------- |
|                                            username: str | DGUT中央认证账号                                             |
|                                          __password: str | DGUT中央认证密码                                             |
|                       session: requests.sessions.Session | 会话                                                         |
| \_\_init\_\_(self, username: str, password: str) -> None | 构造函数<br />username: DGUT中央认证账号<br />__password: DGUT中央认证密码 |
|        signin(self, login_url: str) -> requests.Response | 登录函数，返回结果响应<br />login_url: 登录url，以http://或https://开头 |
|   decorator_signin(url: str)(func: function) -> function | 登录装饰器                                                   |


## 4.3. class DgutXgxt
继承自[4.2](#42-class DgutUser)

|                                                    属性/方法 | 说明                                                         |
| -----------------------------------------------------------: | :----------------------------------------------------------- |
|                          xgxt_login: str & 学工系统登录: str | 学工系统的登录url                                            |
|                             get_workAssignment(self) -> list | 获取考勤职位信息，返回一个列表                               |
| attendance(self, flag: int, workAssignmentId: int=None) -> dict | 考勤函数，返回一个字典结果<br />flag: 1表示签到，2表示签退<br>workAssignmentId: 考勤职位ID，缺省或None时自动调用get_workAssignment(self)获取第一个职位信息作为参数，若没有任何职位信息则抛出ValueError异常 |

## 4.4. class DgutIllness

继承自[4.2](#42-class DgutUser)

|                                                                属性/方法 | 说明                            |
| -----------------------------------------------------------------------: | :-------------------------------- |
| illness_login: str & 疫情防控系统登录: str | 疫情防控系统的登录url |
| report(self, custom_data: dict=None, priority: bool=False) -> dict | 进行疫情防控每日打卡，返回字典结果<br />custom_data: 用户自定义数据，用于自定义字段（如最后一次核酸时间latest_acid_test）<br />priority: 用户自定义数据是否具有更高优先级。为True时用户自定义数据将覆盖云端数据，为False时相反。默认为False |

其他方法同[4.2.2](#422-方法method)

## 4.5. class DgutJwxt

继承自[4.2](#42-class DgutUser)

|                                                    属性/方法 | 说明                                                         |
| -----------------------------------------------------------: | :----------------------------------------------------------- |
|                          jwxt_login: str & 教务系统登录: str | 教务系统的登录url                                            |
| get_score(self, score_type: int = 1, course_type: int = 3, time_range: int = 3, **kwargs) -> Generator | 查询成绩，返回一个生成器对象<br />score_type: 成绩类型: 1=>原始成绩（默认） / 2=>有效成绩<br>course_type: 课程类型: 1=>主修 / 2=>辅修 / 3=>主修和辅修（默认）<br>time_range: 时间范围选择: 1=>入学以来 / 2=>学年 / 3=>学期（默认）<br>**kwargs: 补充参数，有xn和xq两个参数，都是int类型。xn: 学年，取值[1970, 9999]; xq: 学期，取值1或2 |

# 5. 目前已有的项目示例
- 勤工俭学自动考勤助手  
  - [github仓库](https://github.com/Bertramoon/DGUT-Auto-Attendance)  
  - [gitee仓库](https://gitee.com/bertramoon/Auto_Attendance)  

- 疫情防控自动打卡  
  - [github仓库](https://github.com/Bertramoon/DGUT-Auto-Report)  
  - [gitee仓库](https://gitee.com/bertramoon/dgut-autoreport-configure)  
  
- ~~出入校快速申请~~
  - 目前基于QT5和dgut-requests开发了PC端的GUI程序，具有记住账号密码和表单的功能，可用于快速申请，[gitee仓库地址](https://gitee.com/bertramoon/dgut-leave-application)  

- 有需求或技术方面的问题请联系作者Email：bertramoon@126.com


# 6. 更新日志

## v2.0.1 - 2022-5-28

- 修改依赖库lxml和requests的版本限制

## v2.0.0 - 2022-5-27

- 启用x.x.x的版本号，第一个数表示主版本号，往往意味着接口可能会有不兼容的修改。第二个数表示次版本号，一般是一些改变内部实现的更新、优化等。最后一个数则是对内容进行小幅度的修改或对bug的修复
- 对README文档进行更新，将多余的废话去除，只留下核心文档
- 对模块文件的结构进行修改，将其中类的名字也进行了修改，更加符合Python的命名规范（虽然是主版本更新，但诸多原因下还是对接口进行了兼容）

## v1.2 - 2022-1-4

- `dgutIllness`的`report`方法有点小问题，在提交数据前不小心删除了最后一次核酸检测时间选项，本次是修复该小bug

## v1.1 - 2021-12-22

- `dgutIllness`的`report`方法代码微修改

## v1.0 - 2021-12-21

- 疫情防控打卡系统更新。注意，因接口改变，`dgutIllness`的`report`方法有所变化，不再接收任何参数
- 随着版本更新，将版本号正式定为1.0，此后每次小的迭代增加0.1，大的更新向上取整

## v0.1.5 - 2021-12-18

- 疫情防控打卡时会检测是否已打卡，已打卡则返回打卡成功的信息`{'code': 400, 'message': message, 'info': []}`，减少无故提交次数，避免被检测

## v0.1.4 - 2021-9-5

- 将返回成绩结果改为生成器
- 修正了部分注释
- 稍微修改了一下代码中不够简洁的部分

## v0.1.3 - 2021-7-1
修复了显示`{'code': 400, 'message': '选定的 核酸检测结果 是无效的', 'info': []}`的问题

## v0.1.2 - 2021-5-19
修改了上次更新时代码错误产生的无法正常打卡的问题，并更新了README.md。

## v0.1.1 - 2021-5-16
主要解决了调用dgutIllness中report()方法出现提交异常的情况。此外，对READEME.md文档也进行了部分更新。

## v0.1.0 - 2021-4-24
重大更新，重构代码。具体请查看`5. 相比0.0.x版本的改动`