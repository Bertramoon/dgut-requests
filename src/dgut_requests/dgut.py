# coding=utf-8
import requests
import re
import json
from lxml import etree
import datetime

xgxt_login = 学工系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html"


def decorator_signin(url):
    '''
    定义一个登录装饰器
    '''
    def decorator(func):
        def wrapper(self, *args, **kargs):
            self.signin(url)
            return func(self, *args, **kargs)
        return wrapper
    return decorator


class UrlFormatError(Exception):
    def __init__(self, url):
        self.url = url

    def __str__(self):
        print(f"<{self.url}>不符合url的正确格式")


class AuthError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        print(f"认证失败,失败原因:{self.reason}")


class dgut(object):
    '''
    登录类

    username : 中央认证账号用户名

    password : 中央认证账号密码
    '''

    def __init__(self, username: str, password: str):
        '''
        构造函数__init__(self, username, password)

        username : 中央认证账号用户名

        password : 中央认证账号密码
        '''
        self.username = str(username)
        self.__password = str(password)

        # 创建一个会话
        self.session = requests.Session()
        # 设置请求超时时间
        self.timeout = 20

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }

    def __str__(self):
        addr = hex(id(self))
        return f"<dgutLogin at 0x{addr[2:].upper().zfill(16)} username is {self.username}>"

    def signin(self, login_url: str):
        '''
        登录函数

        signin(self, login_url)
        login_url : 系统登录url
        '''
        # 检查url
        if not isinstance(login_url, str):
            raise TypeError("login_url参数应为str类型")
        if not re.match("^https?://.*?", str(login_url)):
            raise UrlFormatError(login_url)
        # 获取登录token
        response = self.session.get(
            login_url, timeout=self.timeout)
        if re.search('token = \".*?\"', response.text):
            # 如果获取到登录token，说明还未登录
            __token__ = re.search(
                'token = \"(.*?)\"', response.text).group(1)
            # 发送登录请求
            data = {
                'username': self.username,
                'password': self.__password,
                '__token__': __token__
            }
            response = self.session.post(
                login_url, data=data, timeout=self.timeout)
            result = json.loads(response.text)
            if result['code'] == 1:
                # 登录成功
                # 认证
                auth_url = result['info']
                response = self.session.get(auth_url, timeout=self.timeout)
                if response.status_code == 200:
                    # 认证成功
                    return response
                else:
                    raise AuthError(f'认证{auth_url}失败')
            else:
                if result['code'] == 8:
                    raise AuthError("密码错误")
                if result['code'] == 15:
                    raise AuthError('不存在该用户')

        else:
            return response

    @decorator_signin(xgxt_login)
    def get_workAssignment(self):
        '''
        获取考勤职位信息
        '''
        # 请求考勤页职位信息
        response = self.session.get(
            "http://stu.dgut.edu.cn/student/partwork/attendance.jsp", timeout=self.timeout)
        html = etree.HTML(response.text)
        result = html.xpath('//div[@class="searchTitle"]')
        works = result[0].xpath('./select/option[position()>1]')
        workAssignment = []
        if not len(works):
            return list()
        for item in works:
            id_ = item.xpath('./@value')
            name = item.xpath('./text()')
            workAssignment.append((id_[0], name[0]))
        return workAssignment

    @decorator_signin(xgxt_login)
    def attendance(self, flag: int, workAssignmentId: int = None):
        '''
        学工系统考勤

        attendance(self, flag[, workAssignmentId])
        flag : 1->签到 / 2->签退
        workAssignmentId : 职位id，为None时自动获取当前的首个职位
        '''
        if not flag in [1, 2]:
            raise ValueError("参数flag只能是1或2")
        if flag == 1:
            action_name = 'beginWork'
            s = '签到'
        if flag == 2:
            action_name = 'endWork'
            s = '签退'

        # 如果没有传递workAssignmentId，自动获取可考勤的第一个职位作为考勤职位
        if not workAssignmentId:
            workAssignment = self.get_workAssignment()
            if len(workAssignment) < 1:
                raise ValueError("没有可考勤的职位")
            workAssignmentId = workAssignment[0][0]

        # 请求考勤界面
        response = self.session.get(
            "http://stu.dgut.edu.cn/student/partwork/attendance.jsp", timeout=self.timeout)

        # 获取session_token
        session_token = re.search(
            r'session_token.*?value="(.*?)"/>', response.text, re.S).group(1)

        # 提交表单数据
        data = {
            'action_name': action_name,
            'modifying': 'true',
            'salaryInfoId': '',
            'session_token': session_token,
            'backUrl': '',
            'workAssignmentId': workAssignmentId
        }

        # 发送请求
        response = self.session.post(
            "http://stu.dgut.edu.cn/student/partwork/attendance.jsp", data=data, timeout=self.timeout)
        attendance_time = datetime.datetime.now()
        return {
            'message': f'{s}成功',
            'code': 1,
            'info': {
                'data': data,
                'time': attendance_time,
            }
        }
