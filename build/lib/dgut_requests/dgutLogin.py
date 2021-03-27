import requests
import re
import json


class dgutLogin(object):
    '''
    登录类
    username : 中央认证账号用户名
    password : 中央认证账号密码
    '''

    def __init__(self, username: str, password: str):
        '''
        构造函数

        __init__(self, username, password)
        username : 中央认证账号用户名
        password : 中央认证账号密码
        '''
        self.username = str(username)
        self.password = str(password)

        # 创建一个会话
        self.session = requests.Session()
        # 设置请求超时时间
        self.timeout = 20
        # 目前收录的系统名
        '''
        学工系统：xgxtt
        教务网络管理系统：jwyd
        疫情防控系统：illness
        事务中心：stuaffair
        '''
        self.sys = ['xgxtt', 'jwyd', 'illness', 'stuaffair']
        '''
        login属性，对应登录的各项信息
        headers是http requests的headers
        各系统名对应的字典分别是登录url和存放对象请求记录的response
        '''
        self.login = {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            },
            'xgxtt': {
                'url': r'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html',
                'response': [],
            },
            'jwyd': {
                'url': r'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/jwyd.html',
                'response': [],
            },
            'illness': {
                'url': r'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/illnessProtectionHome/state/home.html',
                'response': [],
            },
            'stuaffair': {
                'url': r'https://cas.dgut.edu.cn/home/Oauth/getToken/appid/stuaffair.html',
                'response': [],
            },
        }

    def __str__(self):
        addr = hex(id(self))
        return f"<dgutLogin at 0x{addr[2:].upper().zfill(16)} username is {self.username}>"

    def signin(self, sys_name: str = None):
        '''
        登录函数

        signin(self[, sys_name])
        sys_name : 系统名 | None=="xgxtt"
        '''
        if not sys_name:
            url = self.login['xgxtt']['url']
            sys_name = 'xgxtt'
        if not sys_name in self.sys:
            return {'message': '参数错误：系统名', 'code': 2}
        url = self.login[sys_name]['url']
        self.login[sys_name]['response'].append(list())
        try:
            # 获取登录token
            response = self.session.get(
                url, headers=self.login['headers'], timeout=self.timeout)
            self.login[sys_name]['response'][-1].append(response)
            if response.status_code != 200:
                return {'message': f'登录页面{url}请求失败', 'code': 300}

            if re.search('token = \".*?\"', response.text):
                # 如果获取到登录token，说明还未登录
                __token__ = re.search(
                    'token = \"(.*?)\"', response.text).group(1)
                # 发送登录请求
                data = {
                    'username': self.username,
                    'password': self.password,
                    '__token__': __token__
                }
                response = self.session.post(
                    url, data=data, headers=self.login['headers'], timeout=self.timeout)
                self.login[sys_name]['response'][-1].append(response)
                result = json.loads(response.text)

                if result['code'] == 1:
                    # 登录成功
                    # 认证
                    auth_url = result['info']
                    response = self.session.get(
                        auth_url, headers=self.login['headers'])
                    self.login[sys_name]['response'][-1].append(response)
                    if response.status_code == 200:
                        # 认证成功
                        return result
                    else:
                        return {'message': f'认证{auth_url}失败', 'code': 302}
                else:
                    if result['code'] == 8:
                        return {'message': '密码错误', 'code': 400}
                    elif result['code'] == 15:
                        return {'message': '不存在该用户', 'code': 401}
                    else:
                        return {'message': '未知的登录错误', 'code': 402, 'info': json.loads(response.text)}

            else:
                # 已登陆过，只需要获取认证
                info = None
                if re.match(r'.*?token.*?', response.url, re.S):
                    info = response.url.strip()
                if info:
                    return {'message': '验证通过', 'code': 1, 'info': info}
                for item in response.history:
                    if re.match(r'.*?token.*?', item.url, re.S):
                        info = item.url.strip()
                if not info:
                    return {'message': f'认证{url}失败', 'code': 302}
                return {'message': '验证通过', 'code': 1, 'info': info}

        except AttributeError:
            # 属性错误
            return {'message': '页面token请求失败', 'code': 301}
        except requests.exceptions.ConnectTimeout:
            # 请求超时
            return {'message': '请求超时', 'code': 303}

    def add_sys(self, sys_name: str, login_url: str):
        '''
        添加系统

        sys_name : 系统名
        login_url: 系统登录url
        '''
        if not re.match("^https?://.*?", str(login_url)):
            return None
        self.sys.append(str(sys_name))
        self.login[str(sys_name)] = {
            'url': str(login_url),
            'response': [],
        }
        return self.login[str(sys_name)]
