import requests
import re
import json


class dgutLogin(object):
    '''
    登录类
    username: str => dgut中央认证用户名
    password: str => 密码
    '''

    def __init__(self, username: str, password: str):
        '''
        构造函数
        '''
        # 检测用户名密码
        self.username = str(username)
        self.password = str(password)

        # 创建一个会话
        self.session = requests.Session()

        '''
        登录headers和url
        学工系统：xgxtt
        教务网络管理系统：jwyd
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
        # 目前收录的系统名
        self.sys = ['xgxtt', 'jwyd', 'illness', 'stuaffair']

        # 设置请求超时时间
        self.timeout = 15

    def signin(self, sys_name: str = None):
        '''
        登录函数
        sys_name => 系统名 | None=="xgxtt"
        '''
        if not sys_name:
            url = self.login['xgxtt']['url']
            sys_name = 'xgxtt'
        if not sys_name in self.sys:
            return {'message': '参数错误：系统名', 'code': 2}
        url = self.login[sys_name]['url']

        all_response = []
        try:
            # 获取登录token
            response = self.session.get(
                url, headers=self.login['headers'], timeout=self.timeout)
            all_response.append(response)
            if response.status_code != 200:
                self.login[sys_name]['response'].append(all_response)
                return {'message': f'页面{url}请求失败', 'code': 300}

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
                all_response.append(response)
                result = json.loads(response.text)
                if result['code'] == 1:
                    # 认证
                    auth_url = result['info']
                    auth = self.session.get(
                        auth_url, headers=self.login['headers'])
                    all_response.append(auth)
                    self.login[sys_name]['response'].append(all_response)
                    if auth.status_code == 200:
                        return result
                    else:
                        return {'message': f'认证{auth_url}失败', 'code': 302}
                else:
                    self.login[sys_name]['response'].append(all_response)
                    if result['code'] == 8:
                        return {'message': '密码错误', 'code': 400}
                    elif result['code'] == 15:
                        return {'message': '不存在该用户', 'code': 401}
                    else:
                        return {'message': '未知的登录错误', 'code': 402}

            else:
                # 已登陆过，只需要获取认证
                self.login[sys_name]['response'].append(all_response)
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
        except:
            # 未知的错误
            return {'message': '未知的错误', 'code': 5}
