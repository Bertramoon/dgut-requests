[![dugt-requests](https://img.shields.io/pypi/v/dgut-requests?color=blue)](https://pypi.org/project/dgut-requests)
[![Build Status](https://travis-ci.org/BertraMoon/dgut-requests.svg?branch=master)](https://travis-ci.org/BertraMoon/dgut-requests)
[![README](https://img.shields.io/badge/README-Chinese-brightgreen)](https://github.com/BertraMoon/dgut-requests/blob/master/README.md)
[![GitHub](https://img.shields.io/github/license/bertramoon/dgut-requests)](https://github.com/BertraMoon/dgut-requests/blob/master/LICENSE)  

# 0. 前言

dgut-requests是一款适用于东莞理工学院系统的Python库（要求Python3.7及以上版本），主要基于requests库进行再抽象并实现所需功能，采用面向切面编程(AOP)，目前基于该库已做出勤工俭学自动考勤、~~疫情防控自动打卡~~、出入校快速申请等小应用。 

这是一篇面向编程新手的帮助文档，我会通过例子向你展示这个库的功能。如果你不熟悉dgut-requests库，请从头开始完整阅读本文档，并在自己的电脑上尝试运行一下（PS：演示所使用的操作系统是windows 10）。如果你有编程基础，并且对Python语言比较熟悉，那可以直接阅读[3. 说明文档](#3-说明文档)。 

# 1. 安装
请先确保自己已经安装了pip，并且Python版本大于等于3.7

```
pip install dgut-requests
```

如果安装得很慢，甚至报错的话，很可能是网速问题，这时候可以使用镜像源进行下载：  

```
pip install dgut-requests -i https://mirrors.aliyun.com/pypi/simple/
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

## 2.2. 构建账号，实现登录
```python
from dgut_requests import DgutUser

u = DgutUser("201841312111", "123456")  # DgutUser(username, password)

response = u.login()  # 登录学工系统
print(response)
# <Response [200]>
print(response.url)
# https://auth.dgut.edu.cn/personalInfo/personCenter/index.html
print(u.session.cookies)
"""
[
    ('EncryptKey', '****************'),
    ('MOD_AUTH_CAS', 'MOD_AUTH_ST-******-***************************************-**-**-***'),
    ('REFERERCE_TOKEN', '********-****-****-****-*************'),
    ('CASTGC', 'TGT-******-*************************-********************************************-**-**-***'),
    ('JSESSIONID', '********************************'),
    ('route', '********************************'),
    ('JSESSIONID', '********************************'),
    ('happyVoyagePersonal', '****************************************************************************************************************************************************************************'),
    ('route', '********************************')
]
"""
```

## 2.3. 获取考勤职位信息 & 学工系统考勤
```python
from dgut_requests import DgutXgxt

u = DgutXgxt("201841312111", "123456") # DgutUser(username, password)

# get_work_assignment()方法获取考勤职位信息，返回一个包含二元组的列表，每一个二元组包含考勤职位ID和考勤职位名。当你没有任何职位时，返回空列表[]
print(u.get_work_assignment())
# [('9000', 'XXX学生助理'), ('9001', 'xxx办公室助理')]


# attendance(flag: int, work_assignment_id: int = None)
# flag=1表示签到，flag=2表示签退
# work_assignment_id为None或者缺省时，表示调用get_work_assignment()方法并获取第一个职位信息的ID作为该参数
print(u.attendance(1))
# {'message': '签到成功', 'code': 1, 'info': {'data': {'action_name': 'beginWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1619157009355', 'backUrl': '', 'workAssignmentId': '9000'}, 'time': datetime.datetime(2021, 4, 23, 13, 50, 9, 542232)}}
print(u.attendance(2))
# {'message': '签退成功', 'code': 1, 'info': {'data': {'action_name': 'endWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1619157045726', 'backUrl': '', 'workAssignmentId': '9000'}, 'time': datetime.datetime(2021, 4, 23, 13, 50, 45, 960229)}}


print(u.attendance(1, 9001))
# {'message': '签到成功', 'code': 1, 'info': {'data': {'action_name': 'beginWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1619157089460', 'backUrl': '', 'workAssignmentId': '9001'}, 'time': datetime.datetime(2021, 4, 23, 13, 51, 29, 618113)}}
print(u.attendance(2, 9001))
# {'message': '签退成功', 'code': 1, 'info': {'data': {'action_name': 'endWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1619157094360', 'backUrl': '', 'workAssignmentId': '9001'}, 'time': datetime.datetime(2021, 4, 23, 13, 51, 34, 492294)}}
```

细心的读者可能已经发现了，上面的代码中，构建账号后并没有调用`login`方法，而是直接调用两个功能方法。  
这是因为DgutXgxt类中使用python的装饰函数实现AOP面向切面编程，在调用`get_work_assignment()`和`attendance(flag: int, work_assignment_id: int = None)`方法时会自动判断是否已登录、未登录则会先调用`login`方法进行登录认证。


## 2.4. 获取个人成绩
```python
from dgut_requests import DgutJwxt

u = DgutJwxt("201841312111", "123456")

# 获取本学期的原始成绩
# 现在是2022年10月，即2022-2023学年第一学期的成绩
for score in u.get_score():
    print(*score)
"""
[0710010]形势与政策 2.0 12 公共课/必修课 初修 考试 初修取得 xx
[4100088]毕业实习 2.0 0 实习 初修 初修取得 xx
...
"""

# 获取2020-2021学年第一学期的原始成绩
# xn=2020代表2020-2021学年
# xq=0代表第一学期，xq=1代表第二学期
for score in u.get_score(xn=2020, xq=1):
    print(*score)
"""
[0710007]形势与政策5 0.0 公共课/必修课 初修 考试 初修取得 xx
[1310006]体育5 0.5 公共课/必修课 初修 考试 初修取得 xx
[0410084]PHP程序设计 3.0 专业课/任选课 初修 考查 初修取得 xx
...
"""


# 获取2020-2021学年第一学期的有效成绩
for score in u.get_score(score_type=2, xn=2020, xq=0):
    print(*score)
"""
[0710007]形势与政策5 0.0 公共课/必修课 初修 考试 xx 0.0 xx xx
[1310006]体育5 0.5 公共课/必修课 初修 考试 xx 0.5 xx xx
[0410084]PHP程序设计 3.0 专业课/任选课 初修 考查 xx 3.0 xx xx
...
"""

    

# 获取2019-2020学年的原始成绩
# time_range=2代表按学年查询（1：入学以来 | 2：按学年 | 3：按学期）
# xn=2019代表2019-2020学年
for score in u.get_score(time_range=2, xn=2019):
    print(*score)
"""
[14510300]计算机组成原理 4.0 专业基础课/必修课 初修 考试 初修取得 xx
[14540011]JAVA语言程序设计 3.0 专业基础课/必修课 初修 考试 初修取得 xx
[048774]离散数学 4.0 专业基础课/必修课 初修 考试 初修取得 xx
[0710002]马克思主义基本原理 3.0 公共课/必修课 初修 考试 初修取得 xx
[0710005]形势与政策3 0.0 公共课/必修课 初修 考试 初修取得 xx
[1010005]应用英语A 2.0 公共课/必修课 初修 考试 初修取得 xx
...
"""
    
    

# 获取入学以来的有效成绩
for score in u.get_score(time_range=1, score_type=2):
    print(*score)
"""
[19510070]中国近现代史纲要 2.0 公共课/必修课 初修 考试 xx 2.0 xx xx
[0710003]形势与政策1 0.0 公共课/必修课 初修 考试 xx 0.0 xx xx
[1010001]大学英语1 3.0 公共课/必修课 初修 考试 xx 3.0 xx xx
[1010003]英语口语1 1.0 公共课/必修课 初修 考试 xx 1.0 xx xx
...
[0410084]PHP程序设计 3.0 专业课/任选课 初修 考查 xx 3.0 xx xx
...
[4100088]毕业实习 2.0 0 实习 初修 初修取得 xx
"""
```

首先创建一个`DgutJwxt`对象，然后调用`get_score`方法返回一个成绩结果列表。有兴趣的朋友可以研究一下openpyxl库，制作一个生成学年综测excel表格的脚本。


开发者可基于`DgutUser`及其子类进行新功能的开发，继承`DugtUser`及其子类，然后用装饰函数`DgutUser.login_decorator`装饰新功能函数。这样，开发者只需要关心功能的实现而不需要关心登录功能。

# 3. 说明文档
## 3.1. 异常类
|                         异常类类名 | 说明                                              |
|------------------------------:|:------------------------------------------------|
|                    LoginError | 登录失败时抛出（可能是账号/密码错误，可能是学校服务器崩了，也可能是学校更换接口导致登录失败） |
|                     AuthError | 认证失败时抛出（失败原因主要是学校接口更换导致，其他原因同上）                 |
|               ObjectTypeError | 对象类型错误时抛出，用于校验目标对象是否符合要求                        |
|                GetAesKeyError | 当从登录界面解析不到密钥时抛出                                 |
|               AESEncryptError | 当使用AES加密密码失败时抛出                                 |


## 3.2. class DgutUser
|                                                                       属性/方法 | 说明                                                                            |
|----------------------------------------------------------------------------:|:------------------------------------------------------------------------------|
|                                                              LOGIN_URL: str | 登录URL，https://auth.dgut.edu.cn/authserver/login                               |
|                                                               AUTH_URL: str | 认证URL                                                                         |
|                                                               username: str | DGUT中央认证账号                                                                    |
|                                                             __password: str | DGUT中央认证密码                                                                    |
|                                                                timeout: int | 请求超时时间                                                                        |
|                                                             _aes_key: bytes | AES加密密钥                                                                       |
|                                                        _aes_password: bytes | AES加密密码                                                                       |
|                                                      is_authenticated: bool | 是否已认证                                                                         |
|                                          session: requests.sessions.Session | 会话                                                                            |
| \_\_init\_\_(self, username: str, password: str, timeout: int = 30) -> None | 构造函数<br />username: DGUT中央认证账号<br />password: DGUT中央认证密码<br />timeout: 请求超时时间 |
|                                            login(self) -> requests.Response | 登录函数，调用LOGIN_URL进行登录，返回结果响应                                                   |
|                                                                 _auth(self) | 认证方法，调用AUTH_URL进行认证。若AUTH_URL存在则发送请求返回结果，否则直接返回                               |
|                                    _encrypt(text: str, key: bytes) -> bytes | 静态方法，传入明文text和密钥key，返回AES加密结果(128位CBC，明文为随机64个字符+text，iv为随机16个字符)             |
|                                 login_decorator(func: Callable) -> Callable | 登录装饰器                                                                         |


## 3.3. class DgutXgxt
继承自[3.2](#32-class-DgutUser)

|                                                               属性/方法 | 说明                                                                                                                                             |
|--------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------|
|                                   get_work_assignment(self) -> list | 获取考勤职位信息，返回一个列表                                                                                                                                |
| attendance(self, flag: int, work_assignment_id: int = None) -> dict | 考勤函数，返回一个字典结果<br />flag: 1表示签到，2表示签退<br>work_assignment_id: 考勤职位ID，缺省或None时自动调用get_work_assignment(self)获取第一个职位信息作为参数，若没有任何职位信息则抛出ValueError异常 |

## 3.4. class DgutIllness
继承自[3.2](#32-class-dgutuser)

|                                                                  属性/方法 | 说明                                                                                                                                                     |
|-----------------------------------------------------------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------|
|                                           REPORT_POP_LIST: list\[str\] | 获取云端数据时会返回多余无用的数据，`get_record`方法会迭代该列表，将多余字段删去                                                                                                         |
|                                               _set_authorization(self) | 设置Authorization                                                                                                                                        |
|                                         get_authorization(self) -> str | 获取Authorization                                                                                                                                        |
|                                               get_record(self) -> dict | 获取疫情打卡云端表单记录                                                                                                                                           |
| report(self, custom_data: dict = None, priority: bool = False) -> dict | 进行疫情防控每日打卡，返回字典结果<br />custom_data: 用户自定义数据，用于自定义字段（如最后一次核酸时间latest_acid_test）<br />priority: 用户自定义数据是否具有更高优先级。为True时用户自定义数据将覆盖云端数据，为False时相反。默认为False |


## 3.5. class DgutJwxt
继承自[3.2](#32-class-DgutUser)

|                                                                                              属性/方法 | 说明                                                                                                                                                                                                                                       |
|---------------------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  get_score(self, score_type: int = 1, course_type: int = 3, time_range: int = 3, **kwargs) -> list | 查询成绩，返回一个列表对象<br />score_type: 成绩类型: 1=>原始成绩（默认） / 2=>有效成绩<br>course_type: 课程类型: 1=>主修 / 2=>辅修 / 3=>主修和辅修（默认）<br>time_range: 时间范围选择: 1=>入学以来 / 2=>学年 / 3=>学期（默认）<br>**kwargs: 补充参数，有xn和xq两个参数，都是int类型。xn: 学年，取值[1970, now]; xq: 学期，取值0或1 |


# 4. 目前已有的项目示例
- 勤工俭学自动考勤助手  
  - [github仓库](https://github.com/Bertramoon/DGUT-Auto-Attendance)  
  - [gitee仓库](https://gitee.com/bertramoon/Auto_Attendance)  

- 疫情防控自动打卡  
  - [github仓库](https://github.com/Bertramoon/DGUT-Auto-Report)  
  - [gitee仓库](https://gitee.com/bertramoon/dgut-autoreport-configure)  
  
- ~~出入校快速申请~~
  - ~~目前基于QT5和dgut-requests开发了PC端的GUI程序，具有记住账号密码和表单的功能，可用于快速申请，[gitee仓库地址](https://gitee.com/bertramoon/dgut-leave-application)~~

- 有需求或技术方面的问题请联系作者Email：bertramoon@126.com


# 6. 更新日志

## v2.1.1 - 2022-12-17

- 移除疫情打卡类

## v2.1.0 - 2022-10-5

- 对学校新登录接口进行重写，登录方法signin改名login，登录装饰器decorator_signin改名login_decorator，其余接口基本保持不变
- 按照Python安全编码规范，对之前不符合规范的部分进行修正

## v2.0.2 - 2022-9-17

- 修正了`DgutIllness.report`中用户自定义数据添加的问题，现在只需要以`{ key: value }`方式传入即可

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