# coding=utf-8
from typing import Generator
import requests
import re
from lxml import etree
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlparse
from requests.exceptions import HTTPError

xgxt_login = 学工系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html"
illness_login = 疫情防控系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/yqfkdaka/state/%2Fhome.html"
jwxt_login = 教务系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/jwyd.html"


def decorator_signin(url: str):
    '''
    定义一个登录装饰器，url是系统的登录url
    :param url: str
    :return: function
    '''
    def decorator(func):
        wraps(func)

        def wrapper(self, *args, **kargs):
            self.signin(url)
            return func(self, *args, **kargs)
        return wrapper
    return decorator


def detect_type(detection_name, detection, type_: type):
    '''
    类型检测函数，如果符合类型返回该变量，如果不符合类型，则抛出TypeError
    :param detection: type
    '''
    if not isinstance(detection, type_):
        raise TypeError(
            f"[变量类型错误] 变量「{detection_name} = {detection}」不能是{type(detection)}类型，请修改为{type_}类型")
    return detection


class AuthError(Exception):
    '''
    认证错误类
    '''

    def __init__(self, reason) -> None:
        self.reason = reason

    def __str__(self) -> None:
        print(f"[认证失败] 失败原因：{self.reason}")


class dgutUser(object):
    '''
    莞工用户类
    '''

    def __init__(self, username: str, password: str) -> None:
        '''
        :param username(中央认证账号): str
        :param password(中央认证密码): str
        :return: None
        '''
        self.username = detect_type("username", username, str)
        self.__password = detect_type("password", password, str)

        # 创建一个会话
        self.session = requests.Session()
        # 设置请求超时时间
        self.timeout = 30

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }

    def signin(self, login_url: str) -> requests.Response:
        '''
        登录函数
        :param login_url(系统登录url): str
        :return: requests.Response
        '''
        # 检查url
        detect_type("login_url", login_url, str)
        if not re.match(r"^https?://[^\.]{1,}(\.[^\.]{1,})*", str(login_url)):
            raise ValueError(f"[格式错误] 变量「url = {login_url}」的格式错误")
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
            if not response.status_code == 200:
                raise HTTPError(f"[HTTP响应错误] HTTP code {response.status_code}")
            result = response.json()
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
    '''

    def __init__(self, username: str, password: str) -> None:
        dgutUser.__init__(self, username, password)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Host': 'stu.dgut.edu.cn',
        }

    @decorator_signin(xgxt_login)
    def get_workAssignment(self) -> list:
        '''
        获取考勤职位信息
        :return: list
        '''
        # 请求考勤页职位信息
        response = self.session.get(
            "http://stu.dgut.edu.cn/student/partwork/attendance.jsp", timeout=self.timeout)
        if not response.status_code == 200:
            raise HTTPError(f"[HTTP响应错误] HTTP code {response.status_code}")
        works = etree.HTML(response.text).xpath(
            '//div[@class="searchTitle"]/select/option')
        return [(item.xpath('./@value'), item.xpath('./text()')) for item in works[1:]]

    @decorator_signin(xgxt_login)
    def attendance(self, flag: int, workAssignmentId: str = None) -> dict:
        '''
        学工系统考勤
        :param flag: int: 1->签到 | 2->签退
        :param workAssignmentId(职位id，为None时自动获取当前的首个职位): str
        :return: dict
        '''
        if not flag in [1, 2]:
            raise ValueError("[参数错误] 参数flag只能是1或2")
        action_name, s = ('beginWork', '签到') if flag == 1 else (
            'endWork', '签退')

        # 如果没有传递workAssignmentId，自动获取可考勤的第一个职位作为考勤职位
        if not workAssignmentId:
            workAssignment = self.get_workAssignment()
            if len(workAssignment) < 1:
                raise ValueError("[参数错误] 没有可考勤的职位")
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
    '''

    def __init__(self, username: str, password: str) -> None:
        dgutUser.__init__(self, username, password)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            "Origin": "https://yqfk-daka.dgut.edu.cn",
            "Referer": "https://yqfk-daka.dgut.edu.cn/",
            # "Host": "yqfk-daka-api.dgut.edu.cn"
        }

    @decorator_signin(illness_login)
    def report(self) -> dict:
        '''
        疫情打卡
        :return: dict
        '''
        # 1、获取access_token
        res = self.signin(illness_login)
        result = urlparse(res.url)
        data = {}
        for item in result.query.split("&"):
            data[item.split("=")[0]] = item.split("=", maxsplit=2)[-1]
        res = self.session.post("https://yqfk-daka-api.dgut.edu.cn/auth", json=data)
        access_token = res.json().get('access_token')
        if not access_token:
            raise ValueError("[参数错误] 获取access_token失败")
        self.session.headers['authorization'] = 'Bearer ' + access_token
        self.session.headers["Host"] = "yqfk-daka-api.dgut.edu.cn"

        # 2、获取并修改数据
        response = self.session.get(
            'https://yqfk-daka.dgut.edu.cn/record')
        if not response.status_code == 200:
            raise AuthError("获取个人基本信息失败")
        data = response.json()
        if "已打卡" in data.get("message"):
            return {"message": "今日已打卡"}
        pop_list = [
            'is_en',
            'is_important_area_people',
            'created_time',
            'faculty_id',
            'class_id',
            'last_submit_time',
            'off_campus_person_type',
            'jiguan_district',
            'huji_district',
            'remark',
            'holiday_go_out',
            'school_connect_person',
            'school_connect_tel',
            'have_diagnosis',
            'diagnosis_result',
            'processing_method',
            'important_area',
            'leave_important_area_time',
            'last_time_contact_hubei_people',
            'last_time_contact_illness_people',
            'end_isolation_time',
            'plan_back_dg_time',
            'back_dg_transportation',
            'plan_details',
            'finally_plan_details',
            'recent_travel_situation',
            'acid_test_results',
            'two_week_itinerary',
            'first_vaccination_date',
            'plan_vaccination_date',
            'holiday_travel_situation',
            'current_district',
            'gps_district',
            'change_comment',
            'is_change',
        ]
        data = data["user_data"]
        for key in pop_list:
            if key in data:
                data.pop(key)

        # 3、提交数据
        response = self.session.post(
            "https://yqfk-daka.dgut.edu.cn/record", json={"data": data})
        response.encoding = 'utf-8'
        return response.json()


class dgutJwxt(dgutUser):
    '''
    莞工教务系统类
    '''

    def __init__(self, username: str, password: str) -> None:
        dgutUser.__init__(self, username, password)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Host': 'jwyd.dgut.edu.cn',
        }

    @decorator_signin(jwxt_login)
    def get_score(self, score_type: int = 1, course_type: int = 3, time_range: int = 3, **kwargs) -> Generator:
        '''
        获取成绩信息
        :param score_type(成绩类型): int: 1=>原始成绩（默认） | 2=>有效成绩
        :param course_type(课程类型): int: 1=>主修 | 2=>辅修 | 3=>主修和辅修（默认）
        :param time_range(时间范围选择): int: 1=>入学以来 | 2=>学年 | 3=>学期（默认）
        :param kwargs: dict: xn(学年):int & xq(学期):int:1|2
        :return: list
        '''
        # 字段合法检测
        if not score_type in [1, 2]:
            raise ValueError(f"[参数错误] score_type取值只能是1|2，而你的取值为{score_type}")
        if not course_type in [1, 2, 3]:
            raise ValueError(
                f"[参数错误] course_type取值只能是1|2|3，而你的取值为{course_type}")
        if not time_range in [1, 2, 3]:
            raise ValueError(f"[参数错误] time_range取值只能是1|2|3，而你的取值为{time_range}")
        data = {
            "sjxz": "sjxz" + str(time_range),  # 时间选择，1-入学以来，2-学年，3-学期
            # 原始有效，指原始成绩或有效成绩，yscj-原始成绩，yxcj-有效成绩
            "ysyx": "yscj" if score_type == 1 else "yxcj",
            "zx": 1 if not course_type == 2 else 0,  # 主修，1-选择，0-不选择
            "fx": 1 if not course_type == 1 else 0,  # 辅修，1-选择，0-不选择
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
                    f"[参数错误] xn的类型应是int且取值范围为[1970, 9999]，而不应该是「{xn}: {type(xn)}」")
            data['xn'] = xn
            data['xn1'] = xn+1

            if time_range > 2:
                if kwargs.get('xq'):
                    xq = kwargs.get('xq')
                else:
                    xq = 1 if now.month >= 9 else 2
                if not isinstance(xq, int) and xq in [1, 2]:
                    raise ValueError(
                        f"[参数错误] xq的类型应是int且只能是1|2，而不应该是「{xq}: {type(xq)}」")
                xq -= 1
                data['xq'] = xq

        # 发送请求
        response = self.session.post(
            "http://jwyd.dgut.edu.cn/student/xscj.stuckcj_data.jsp", data=data)

        # 解析
        if not response.status_code == 200:
            raise HTTPError(f"[HTTP响应错误] HTTP code {response.status_code}")
        for td in etree.HTML(response.text).xpath('//table[position() mod 2 = 0]/tbody/tr'):
            yield td.xpath('./td[position()>1]/text()')


