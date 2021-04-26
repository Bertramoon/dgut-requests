# coding=utf-8
import requests
import re
import json
from lxml import etree
from datetime import datetime, timedelta

xgxt_login = 学工系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html"
illness_login = 疫情防控系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/illnessProtectionHome/state/home.html"
jwxt_login = 教务系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/jwyd.html"


def decorator_signin(url: str):
    '''
    定义一个登录装饰器，url是系统的登录url
    '''
    def decorator(func):
        def wrapper(self, *args, **kargs):
            self.signin(url)
            return func(self, *args, **kargs)
        return wrapper
    return decorator


class AuthError(Exception):
    '''
    认证错误类
    '''

    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        print(f"认证失败,失败原因:{self.reason}")


class dgutUser(object):
    '''
    莞工用户类

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

    def signin(self, login_url: str):
        '''
        登录函数

        signin(self, login_url)
        login_url : 系统登录url
        '''
        # 检查url
        if not isinstance(login_url, str):
            raise TypeError("login_url参数应为str类型")
        if not re.match(r"^https?://(.*?\.){1,}.*", str(login_url)):
            raise ValueError(f"url<{login_url}>的格式错误")
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
                auth_response = self.session.get(
                    auth_url, timeout=self.timeout)
                if auth_response.status_code == 200:
                    # 认证成功
                    return auth_response
                else:
                    raise AuthError(f'认证{auth_url}失败')
            else:
                if result['code'] == 8:
                    raise AuthError("密码错误")
                if result['code'] == 15:
                    raise AuthError('不存在该用户')

        else:
            return response


class dgutXgxt(dgutUser):
    '''
    莞工学工系统类

    username : 中央认证账号用户名

    password : 中央认证账号密码
    '''

    def __init__(self, username: str, password: str):
        dgutUser.__init__(self, username, password)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Host': 'stu.dgut.edu.cn',
        }

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
        attendance_time = datetime.now()
        return {
            'message': f'{s}成功',
            'code': 1,
            'info': {
                'data': data,
                'time': attendance_time,
            }
        }


class dgutIllness(dgutUser):
    '''
    莞工疫情防控系统类

    username : 中央认证账号用户名

    password : 中央认证账号密码
    '''

    def __init__(self, username: str, password: str):
        dgutUser.__init__(self, username, password)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Host': 'yqfk.dgut.edu.cn',
        }

    @decorator_signin(illness_login)
    def report(self):
        # 1、获取access_token
        response = self.signin(illness_login)
        access_token = re.search(
            r'access_token=(.*)', response.url, re.S)
        if not access_token:
            raise AuthError("获取access_token失败")
        access_token = access_token.group(1)
        self.session.headers['authorization'] = 'Bearer ' + access_token

        # 2、获取并修改数据
        response = self.session.get(
            'https://yqfk.dgut.edu.cn/home/base_info/getBaseInfo')
        if json.loads(response.text)['code'] != 200:
            raise AuthError("获取个人基本信息失败")
        data = json.loads(response.text)['info']
        pop_list = [
            'can_submit',
            'class_id',
            'class_name',
            'continue_days',
            'create_time',
            'current_area',
            'current_city',
            'current_country',
            'current_district',
            'current_province',
            'faculty_id',
            'faculty_name',
            'id',
            'msg',
            'name',
            'username',
            'whitelist',
            'importantAreaMsg',
        ]
        for key in pop_list:
            if data.get(key):
                data.pop(key)

        # 3、提交数据
        response = self.session.post(
            "https://yqfk.dgut.edu.cn/home/base_info/addBaseInfo", json=data)
        return json.loads(response.text)


class dgutJwxt(dgutUser):
    def __init__(self, username: str, password: str):
        dgutUser.__init__(self, username, password)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Host': 'jwyd.dgut.edu.cn',
        }

    @decorator_signin(jwxt_login)
    def get_score(self, score_type: int = 1, course_type: int = 3, time_range: int = 3, **kwargs):
        '''
        获取成绩信息

        score_type: 成绩类型: 1=>原始成绩（默认） | 2=>有效成绩

        course_type: 课程类型: 1=>主修 | 2=>辅修 | 3=>主修和辅修（默认）

        time_range: 时间范围选择: 1=>入学以来 | 2=>学年 | 3=>学期（默认）
        '''
        # 字段合法检测
        if not score_type in [1, 2]:
            raise ValueError(f"score_type取值只能是1|2，而你的取值为{score_type}")
        if not course_type in [1, 2, 3]:
            raise ValueError(f"course_type取值只能是1|2|3，而你的取值为{course_type}")
        if not time_range in [1, 2, 3]:
            raise ValueError(f"time_range取值只能是1|2|3，而你的取值为{time_range}")
        data = {
            "sjxz": "sjxz" + str(time_range),  # 时间选择，1-入学以来，2-学年，3-学期
            # 原始有效，指原始成绩或有效成绩，yscj-原始成绩，yxcj-有效成绩
            "ysyx": "yscj" if score_type == 1 else "yxcj",
            "zx": 1 if not course_type == 2 else 0,  # 主修，1-选择，0-不选择
            "fx": 1 if not course_type == 3 else 0,  # 辅修，1-选择，0-不选择
            # xn-xn1学年第(xq+1)学期
            "xn": "",
            "xn1": "",
            "xq": "",
            "ysyxS": "on",
            "sjxzS": "on",
            "zxC": "on",
            "fxC": "on",
            "menucode_current": "",
        }
        if time_range > 1:
            if kwargs.get('xn'):
                xn = kwargs.get('xn')
            else:
                now = datetime.utcnow()+timedelta(hours=8)
                xn = now.year if now.month >= 9 else now.year-1

            if not isinstance(xn, int) and 1970 <= xn <= 9999:
                raise ValueError(
                    f"xn的类型应是int且取值范围为[1970, 9999]，而不应该是{xn}: {type(xn)}")
            data['xn'] = xn
            data['xn1'] = xn+1

            if time_range > 2:
                if kwargs.get('xq'):
                    xq = kwargs.get('xq')
                else:
                    xq = 1 if now.month >= 9 else 2
                if not isinstance(xq, int) and xq in [1, 2]:
                    raise ValueError(
                        f"xq的类型应是int且只能是1|2，而不应该是{xq}: {type(xq)}")
                xq -= 1
                data['xq'] = xq

        # 发送请求
        responsse = self.session.post(
            "http://jwyd.dgut.edu.cn/student/xscj.stuckcj_data.jsp", data=data)

        # 解析
        html = etree.HTML(responsse.text)
        tr = html.xpath('//table[position() mod 2 = 0]/tbody/tr')
        score_list = [item.xpath('./td/text()') for item in tr]
        return score_list
