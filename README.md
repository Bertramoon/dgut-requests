# dgut-requests
[![dugt-requests](https://img.shields.io/pypi/v/dgut-requests?color=blue)](https://pypi.org/project/dgut-requests)
[![Build Status](https://travis-ci.org/BertraMoon/dgut-requests.svg?branch=master)](https://travis-ci.org/BertraMoon/dgut-requests)
[![README](https://img.shields.io/badge/README-English-brightgreen.svg)](https://github.com/BertraMoon/dgut-requests/blob/master/README.md)
[![LICENSE](https://img.shields.io/pypi/l/dgut-requests)](https://github.com/BertraMoon/dgut-requests/blob/master/LICENSE)
# 0. 前言

这是一篇面向编程新手的说明文档，我会通过例子向你展示这个库的功能。如果你不熟悉dgut-requests库，请你一步步跟着文档自己做，并在自己的电脑上尝试运行一下（PS：演示所使用的操作系统是windows 10）。  

dgut-requests是本人开发的一款适用于东莞理工学院系统的Python库（要求Python3.7及以上版本），是对基本请求库进行再抽象并实现所需功能，目前基于该库已做出勤工俭学自动考勤、疫情防控自动打卡、出入校快速申请等小应用。  

目前设想的模型框架是：dgutLogin类对requests等请求库进行抽象，实现登录功能，简单易用，是莞工各个系统的登录接口。dgutXgxtt等类继承dgutLogin类，基于dgutLogin类开发各个系统功能。各位如果想练手的话也可以基于dgutLogin类进行开发。

# 1. 安装
请先确保自己已经安装了pip。如果你不确定是否安装了pip，请打开cmd命令窗口并输入`pip`，如果像下面这样，说明你已安装pip。  
```
C:\Users\bertr>pip

Usage:
  pip <command> [options]

Commands:
  install                     Install packages.
  download                    Download packages.
  uninstall                   Uninstall packages.
  freeze                      Output installed packages in requirements format.
  list                        List installed packages.
  show                        Show information about installed packages.
  check                       Verify installed packages have compatible dependencies.
  config                      Manage local and global configuration.
  search                      Search PyPI for packages.
  cache                       Inspect and manage pip's wheel cache.
  wheel                       Build wheels from your requirements.
  hash                        Compute hashes of package archives.
  completion                  A helper command used for command completion.
  debug                       Show information useful for debugging.
  help                        Show help for commands.

General Options:
  -h, --help                  Show help.
  --isolated                  Run pip in an isolated mode, ignoring environment variables and user configuration.
  -v, --verbose               Give more output. Option is additive, and can be used up to 3 times.
  -V, --version               Show version and exit.
  -q, --quiet                 Give less output. Option is additive, and can be used up to 3 times (corresponding to
                              WARNING, ERROR, and CRITICAL logging levels).
  --log <path>                Path to a verbose appending log.
  --no-input                  Disable prompting for input.
  --proxy <proxy>             Specify a proxy in the form [user:passwd@]proxy.server:port.
  --retries <retries>         Maximum number of retries each connection should attempt (default 5 times).
  --timeout <sec>             Set the socket timeout (default 15 seconds).
  --exists-action <action>    Default action when a path already exists: (s)witch, (i)gnore, (w)ipe, (b)ackup,
                              (a)bort.
  --trusted-host <hostname>   Mark this host or host:port pair as trusted, even though it does not have valid or any
                              HTTPS.
  --cert <path>               Path to alternate CA bundle.
  --client-cert <path>        Path to SSL client certificate, a single file containing the private key and the
                              certificate in PEM format.
  --cache-dir <dir>           Store the cache data in <dir>.
  --no-cache-dir              Disable the cache.
  --disable-pip-version-check
                              Don't periodically check PyPI to determine whether a new version of pip is available for
                              download. Implied with --no-index.
  --no-color                  Suppress colored output.
  --no-python-version-warning
                              Silence deprecation warnings for upcoming unsupported Pythons.
  --use-feature <feature>     Enable new functionality, that may be backward incompatible.
  --use-deprecated <feature>  Enable deprecated functionality, that will be removed in the future.
```

如果你已安装pip，请跳到1.2.

# 1.1. 安装pip
安装方法可以参考这篇博客：[windows下 python安装pip 简易教程](https://blog.csdn.net/qq_37176126/article/details/72824404)。如果环境变量不知道怎么设置的话，可以重新[下载Python](https://www.python.org/downloads/)，并在安装时勾选添加Python到PATH变量。  


# 1.2. 更新pip
还是打开cmd命令窗口，输入`pip install --upgrade pip`  
```
C:\Users\bertr>pip install --upgrade pip
```

# 1.3. 安装dgut-requests
打开cmd命令窗口，输入`pip install dgut-requests`  
```
C:\Users\bertr\Desktop>pip install dgut-requests
Looking in indexes: https://pypi.org/simple/
Collecting dgut-requests
  Using cached dgut_requests-0.0.1-py3-none-any.whl (6.3 kB)
Collecting requests
  Using cached requests-2.25.1-py2.py3-none-any.whl (61 kB)
Collecting lxml
  Using cached lxml-4.6.3-cp38-cp38-win_amd64.whl (3.5 MB)
Collecting idna<3,>=2.5
  Using cached idna-2.10-py2.py3-none-any.whl (58 kB)
Collecting urllib3<1.27,>=1.21.1
  Using cached urllib3-1.26.4-py2.py3-none-any.whl (153 kB)
Collecting chardet<5,>=3.0.2
  Using cached chardet-4.0.0-py2.py3-none-any.whl (178 kB)
Collecting certifi>=2017.4.17
  Using cached certifi-2020.12.5-py2.py3-none-any.whl (147 kB)
Installing collected packages: urllib3, idna, chardet, certifi, requests, lxml, dgut-requests
Successfully installed certifi-2020.12.5 chardet-4.0.0 dgut-requests-0.0.1 idna-2.10 lxml-4.6.3 requests-2.25.1 urllib3-1.26.4
```
最后面是Successfully installed...说明安装成功。  
如果安装得很慢，甚至报错的话，很可能是网速问题，这时候可以使用镜像源进行下载。我个人比较推荐的镜像源是清华镜像源，我们可以将上面的cmd命令改成这样：  
```
pip install "https://pypi.tuna.tsinghua.edu.cn/simple/" dgut-requests
```

# 1.4. 确认成功安装
在Python交互界面环境下，输入`import dgut_requests`没有报错即成功安装了dgut-requests库。  
```
Python 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 23:11:46) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import dgut_requests
>>>
```

# 2. class dgutLogin
## 2.1. 导入
```
Python 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 23:11:46) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from dgut_requests.dgutLogin import dgutLogin
>>> dgutLogin
<class 'dgut_requests.dgutLogin.dgutLogin'>
>>>
```

## 2.2. dgutLogin(username: str, password: str)
dgutLogin类的构造函数是`__init__(self, username: str, password: str)`，构造dgutLogin对象需要输入中央认证账号用户名*username*和密码*password*，示例如下。  
```
Python 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 23:11:46) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from dgut_requests.dgutLogin import dgutLogin
>>> u = dgutLogin("202041416100", "123456")
>>> u
<dgut_requests.dgutLogin.dgutLogin object at 0x0000029F40700850>
>>> u.username
'202041416100'
>>>
```

|   参数   |         含义         | 数据类型 |      例      |
| :------: | :------------------: | :------: | :----------: |
| username | DGUT中央认证系统账号 |   str    | 202041416100 |
| password |         密码         |   str    |    123456    |


- PS：构造仅仅是构造，不会验证用户名和密码是否正确  


## 2.3. signin(self, sys_name: str = None)
登录方法包含唯一参数系统名，系统名对应一个登录url，当不传值时默认登录学工系统。库中已初始配置了4个系统，对应关系如下。  

|     系统名      |       含义       |                                         登录url                                         |
| :-------------: | :--------------: | :-------------------------------------------------------------------------------------: |
| xgxtt（默认值） |     学工系统     |              https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html               |
|      jwyd       | 教务网络管理系统 |               https://cas.dgut.edu.cn/home/Oauth/getToken/appid/jwyd.html               |
|     illness     |   疫情防控系统   | https://cas.dgut.edu.cn/home/Oauth/getToken/appid/illnessProtectionHome/state/home.html |
|    stuaffair    |     事务中心     |            https://cas.dgut.edu.cn/home/Oauth/getToken/appid/stuaffair.html             |


我们分别登录学工系统和事务中心尝试一下。  
```
>>> u.signin()
{'message': '验证通过', 'code': 1, 'info': 'http://stu.dgut.edu.cn/caslogin.jsp?token=xgxtt-z-2b0b214fb204f26dd7eb1282e7732da8'}
>>> u.signin("stuaffair")
{'message': '验证通过', 'code': 1, 'info': 'http://sa.dgut.edu.cn/sahWeb/sys/casLogin.do?token=stuaffair-z-a55a89d328bcd4c97a23baf6a12bb477'}
>>>
```
可以看到，返回值是Python的字典类型，共有3个字段，分别是**message**、**code**和**info**。  

info返回认证url及token，message和code对应返回的信息和信息码，它们的对应关系如下。  

|      message      | code  |
| :---------------: | :---: |
|     验证通过      |   1   |
|     参数错误      |   2   |
|   页面请求失败    |  300  |
| 页面token请求失败 |  301  |
|     认证失败      |  302  |
|     请求超时      |  303  |
|  请求的信息为空   |  304  |
|   请求信息失败    |  305  |
|     密码错误      |  400  |
|   不存在该用户    |  401  |
|  未知的登录错误   |  402  |


## 2.4. add_sys(self, sys_name: str, login_url: str)
`signin`方法的局限是只能登录dgut-requests库已经内置的系统。当有新的系统需求或者有自己学院的独立系统需要登录时，我们需要使用`add_sys`方法。该方法有两个参数，分别对应系统名和系统登录url，我们来尝试添加校务服务平台试试吧。  
```
>>> u.add_sys("ibpstest", "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/ibpstest/state/home")
{'url': 'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/ibpstest/state/home', 'response': []}
>>> u.signin("ibpstest")
{'message': '验证通过', 'code': 1, 'info': 'http://e.dgut.edu.cn/api/cas/login?token=ibpstest-z-19e4eabc7c5446ad7537169f68bf1c1f&state=home'}
>>> result = u.add_sys("ibpstest", "abc")
>>> print(result)
None
>>> 
```
该方法会检查参数**login_url**是否合法（即是否以http://或https://开头），当添加成功时返回dict字典类型，失败时返回None。  


## 2.5. 其他
前面就是dgutLogin类的主要功能了，但是该类还有一些属性没有展示，说明附下，可以自己尝试一下，如果有需要的话也可以扩展更多属性或方法。   

|  属性名  |                                                                含义                                                                | 数据类型 |
| :------: | :--------------------------------------------------------------------------------------------------------------------------------: | :------: |
| username |                                                        DGUT中央认证系统账号                                                        |   str    |
| password |                                                                密码                                                                |   str    |
| session  |                                                          该对象开启的会话                                                          | Session  |
| timeout  |                                                          请求超时时间/秒                                                           |   int    |
|   sys    |                                                           已收录的系统名                                                           |   list   |
|  login   | 登录的重要信息<br>login['headers']是发送http request的头部<br>login[sys_name]是个字典，包含该系统的登录url和请求的历史记录response |   dict   |



# 3. class dgutXgxtt
## 3.1. 导入
```
Python 3.8.1 (tags/v3.8.1:1b293b6, Dec 18 2019, 23:11:46) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from dgut_requests.dgutXgxtt import dgutXgxtt
>>> dgutXgxtt
<class 'dgut_requests.dgutXgxtt.dgutXgxtt'>
>>>
```

## 3.2. dgutXgxtt(username: str, password: str)
该方法继承自dgutLogin，参数完全一致，示例如下。  
```
>>> u = dgutXgxtt("202041416100", "123456")
>>> u
<dgut_requests.dgutXgxtt.dgutXgxtt object at 0x000001ADDFFF0850>
>>> u.username
'202041416100'
>>>
```

## 3.3. get_workAssignment(self)
调用该方法可以获取勤工俭学岗位信息。如果没有职位，也会返回相应的信息。   
```
当拥有勤工俭学职位时
>>> u.get_workAssignment()
{'message': '获取职位信息成功', 'code': 1, 'workAssignment': [('9375', '易班平台学生助理')]}
>>> 

当没有勤工俭学任何职位时
>>> u.get_workAssignment()
{'message': '请求的职位信息为空', 'code': 304}
>>> 
```

## 3.4. attendance(self, flag: int, workAssignmentId: int = None)
调用该方法可以实现考勤的签到签退，返回一个dict类型，**code**和**message**的对应关系与[2.3.](#23-signinself-sys_name-str--none)基本一致。  
```
>>> u.attendance(1) 
{'message': '签到成功', 'code': 1, 'info': {'data': {'action_name': 'beginWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1616821236912', 'backUrl': '', 'workAssignmentId': '9375'}, 'time': datetime.datetime(2021, 3, 27, 13, 0, 38, 99590)}}
>>> u.attendance(2)
{'message': '签退成功', 'code': 1, 'info': {'data': {'action_name': 'endWork', 'modifying': 'true', 'salaryInfoId': '', 'session_token': 'token_key_1616821255033', 'backUrl': '', 'workAssignmentId': '9375'}, 'time': datetime.datetime(2021, 3, 27, 13, 0, 56, 281075)}}
>>> 
```  

|         参数          |                                                                        含义                                                                        |
| :-------------------: | :------------------------------------------------------------------------------------------------------------------------------------------------: |
|         flag          |                                               标记，1对应签到，2对应签退，0对应模拟，常用于测试时间                                                |
| workAssignmentId=None | 勤工俭学考勤职位对应的ID，默认值为None，系统自动匹配第一个可以考勤的职位<br>但是，如果你有多个可考勤的职位，或者想要提高运行速度，那么请填写该参数 |


## 3.5. 其他的方法和属性
在dgutXgxtt.py中，有一个装饰函数`xgxtt_decorator_signin(func)`，在调用`attendance(self, flag: int, workAssignmentId: int = None)`等方法时，该函数会验证当前的dgutXgxtt对象是否已经登录，如果没有登录的话会进行自动登录。因此，使用dgutXgxtt类直接调用功能方法即可，不需要手动调用登录方法`signin(self, sys_name: str = None)`。  
在dgutXgxtt中，除了从dgutLogin继承来的属性外，也新增了一个属性**xgxtt: dict**，存储学工系统的一些重要信息，xgxtt['headers']是发送http request的头部，xgxtt['homepage']、xgxtt['attendance']等是字典，存放该系统各界面的url和请求的历史记录response。  


# 4. 目前已有的项目示例
- 勤工俭学自动考勤助手  
  - [github仓库](https://github.com/bertramoon/Auto_Attendance)  
  - [gitee仓库](https://gitee.com/bertramoon/Auto_Attendance)  

- 疫情防控自动打卡  
  - 在github上运行不稳定，目前用在windows本地任务中，有兴趣的可以找我要，应该是可以托管到gitee上面的。  
  
- 出入校快速申请
  - 目前来看已经没有这个必要了，事务中心PC端移动端申请都很快。  

- 有需求或技术方面的问题请联系作者Email：bertramoon@126.com