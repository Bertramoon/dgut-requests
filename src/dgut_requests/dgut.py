# coding=utf-8
from typing import Generator
import requests
import re
from lxml import etree
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlparse
from requests.exceptions import HTTPError



class AuthError(Exception):
    '''
    认证错误类
    '''

    def __init__(self, reason) -> None:
        self.reason = reason

    def __str__(self) -> None:
        return f"认证失败，失败原因：{self.reason}"


class DgutUser(object):
    '''
    莞工用户类
    '''

    def __init__(self, username: str, password: str, timeout: int=30) -> None:
        '''
        :param username(str): 中央认证账号
        :param password(str): 中央认证密码
        :return: None
        '''
        assert isinstance(username, str), '用户名应为字符串类型'
        assert isinstance(password, str), '密码应为字符串类型'
        assert isinstance(timeout, int), 'HTTP请求超时时间应为整型类型'
        self.username = username
        self.__password = password
        self.is_authenticated = False

        # 创建一个会话
        self.session = requests.Session()
        # 设置请求超时时间
        self.timeout = timeout

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }

    
    def signin(self, login_url: str) -> requests.Response:
        '''
        登录函数
        :param login_url(str): 系统登录url
        :return: requests.Response
        '''
        # 检查url
        assert isinstance(login_url, str), '登录URL应为字符串类型'
        assert re.match(r"^https?://[^\.]{1,}(\.[^\.]{1,})*", str(login_url)), '登录URL应符合HTTP URL的格式规范'

        # 获取登录token
        response = self.session.get(login_url, timeout=self.timeout)
        if re.search('token = \".*?\"', response.text):
            # 如果获取到登录token，说明还未登录
            __token__ = re.search('token = \"(.*?)\"', response.text).group(1)
            # 发送登录请求
            data = {
                'username': self.username,
                'password': self.__password,
                '__token__': __token__
            }
            response = self.session.post(login_url, data=data, timeout=self.timeout)
            if not response.status_code == 200:
                raise HTTPError(f"HTTP {response.status_code}错误")
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
    
    @staticmethod
    def decorator_signin(url: str):
        '''
        定义一个登录装饰器，url是系统的登录url
        :param url: str
        :return: function
        '''
        def decorator(func):
            wraps(func)
            def wrapper(self, *args, **kargs):
                if self.is_authenticated is False:
                    self.signin(url)
                    self.is_authenticated = True
                return func(self, *args, **kargs)
            return wrapper
        return decorator



class DgutXgxt(DgutUser):
    '''
    莞工学工系统类
    '''
    xgxt_login = 学工系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/xgxtt.html"
    def __init__(self, username: str, password: str, timeout: int=30) -> None:
        super().__init__(username, password, timeout)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Host': 'stu.dgut.edu.cn',
        }

        # 添加登录装饰器
        DgutXgxt.get_workAssignment = DgutUser.decorator_signin(self.xgxt_login)(DgutXgxt.get_workAssignment)
        DgutXgxt.attendance = DgutUser.decorator_signin(self.xgxt_login)(DgutXgxt.attendance)


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


    def attendance(self, flag: int, workAssignmentId: str = None) -> dict:
        '''
        学工系统考勤
        :param flag(int): 1->签到 | 2->签退
        :param workAssignmentId(str): 职位id，为None时自动获取当前的首个职位
        :return: dict
        '''
        assert flag in [1, 2], 'flag只能是1(签到)或2(签退)'

        action_name, action_description = ('beginWork', '签到') if flag == 1 else ('endWork', '签退')

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
        attendance_time = datetime.utcnow() + timedelta(hours=8)
        return {
            'message': f'{action_description}成功',
            'code': 1,
            'info': {
                'data': data,
                'time': attendance_time,
            }
        }


class DgutIllness(DgutUser):
    '''
    莞工疫情防控系统类
    '''
    illness_login = 疫情防控系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/yqfkdaka/state/%2Fhome.html"
    def __init__(self, username: str, password: str, timeout: int=30) -> None:
        super().__init__(username, password, timeout)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            "Origin": "https://yqfk-daka.dgut.edu.cn",
            "Referer": "https://yqfk-daka.dgut.edu.cn/",
            # "Host": "yqfk-daka-api.dgut.edu.cn"
        }
    

    def set_authorization(self) -> None:
        """
        设置authorization
        """
        res = self.signin(self.illness_login)
        result = urlparse(res.url)
        data = {}
        for item in result.query.split("&"):
            data[item.split("=")[0]] = item.split("=", maxsplit=2)[-1]
        res = self.session.post("https://yqfk-daka-api.dgut.edu.cn/auth", json=data)
        access_token = res.json().get('access_token')
        if not access_token:
            raise ValueError("获取access_token失败")
        self.session.headers['authorization'] = f'Bearer {access_token}'

    def get_authorization(self) -> str:
        """
        获取authorization
        :return: str
        """
        if self.session.haeders.get('authorization') is None:
            self.set_authorization()
        return self.session.headers['authorization']


    def get_record(self) -> dict:
        """
        获取打卡表单记录
        :return: dict
        """
        if hasattr(self, 'record') and self.record and isinstance(self.record, dict):
            return self.record
        headers = {"Host": "yqfk-daka-api.dgut.edu.cn"}
        # 1. 没有登录或http头部没有设置authorization字段
        if self.is_authenticated is False or self.session.headers.get('authorization') is None:
            self.set_authorization()

        # 2、获取数据
        response = self.session.get('https://yqfk-daka.dgut.edu.cn/record', headers=headers)
        if not response.status_code == 200:
            raise AuthError("获取个人基本信息失败")
        self.record = response.json()
        return response.json()


    def report(self, custom_data: dict=None, priority: bool=False) -> dict:
        '''
        疫情打卡
        :param custom_data(dict): 用户自定义数据
        :param priority(bool): 用户自定义数据是否具有优先级。即，是覆盖云端数据，还是被云端数据覆盖
        :return: dict
        '''
        assert isinstance(custom_data, dict) or custom_data is None
        assert isinstance(priority, bool)
        # 获取云端记录
        record = self.get_record()
        
        # 判断是否已打卡
        if "已打卡" in record.get("message"):
            return {"message": "今日已打卡"}
        
        # 删除多余字段
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
        cloud_data = record["user_data"]
        for key in pop_list:
            if key in cloud_data:
                cloud_data.pop(key)
        
        if custom_data is None:
            data = cloud_data
        else:
            if custom_data.get('data') and len(custom_data) == 1:
                custom_data = custom_data['data']
            if priority is True:
                data = {**cloud_data, **custom_data}
            else:
                data = {**custom_data, **cloud_data}
        

        # 提交数据
        headers = {"Host": "yqfk-daka-api.dgut.edu.cn"}
        response = self.session.post(
            "https://yqfk-daka.dgut.edu.cn/record", json={"data": data}, headers=headers)
        response.encoding = 'utf-8'
        return response.json()


class DgutJwxt(DgutUser):
    '''
    莞工教务系统类
    '''
    jwxt_login = 教务系统登录 = "https://cas.dgut.edu.cn/home/Oauth/getToken/appid/jwyd.html"
    def __init__(self, username: str, password: str, timeout: int=30) -> None:
        super().__init__(username, password, timeout)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            'Host': 'jwyd.dgut.edu.cn',
        }
        DgutJwxt.get_score = DgutUser.decorator_signin(self.jwxt_login)(DgutJwxt.get_score)


    def get_score(self, score_type: int = 1, course_type: int = 3, time_range: int = 3, **kwargs) -> Generator:
        '''
        获取成绩信息
        :param score_type(int): 成绩类型,，1=>原始成绩（默认） | 2=>有效成绩
        :param course_type(int): 课程类型,，1=>主修 | 2=>辅修 | 3=>主修和辅修（默认）
        :param time_range(int): 时间范围选择，1=>入学以来 | 2=>学年 | 3=>学期（默认）
        :param kwargs: dict: xn(int): 学年 & xq(int): 学期，0|1
        :return: Generator
        '''
        # 字段合法检测
        assert score_type in [1, 2], f'core_type取值只能是1|2，而你的取值为{score_type}'
        assert course_type in [1, 2, 3], f'course_type取值只能是1|2|3，而你的取值为{course_type}'
        assert time_range in [1, 2, 3], f'time_range取值只能是1|2|3，而你的取值为{time_range}'
        
        data = {
            "sjxz": "sjxz" + str(time_range),  # 时间选择，1-入学以来，2-学年，3-学期
            # 原始有效，指原始成绩或有效成绩，yscj-原始成绩，yxcj-有效成绩
            "ysyx": "yscj" if score_type == 1 else "yxcj",
            # course_type -> 1: 主修 2: 辅修 3: 主修和辅修（默认）
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
            if kwargs.get('xn') is not None:
                xn = kwargs.get('xn')
            else:
                now = datetime.utcnow()+timedelta(hours=8)
                xn = now.year if now.month >= 9 else now.year-1

            if not (isinstance(xn, int) and 1970 <= xn <= 9999):
                raise ValueError(
                    f"xn的类型应是int且取值范围为[1970, 9999]，而不应该是「{xn}: {type(xn)}」")
            data['xn'] = xn
            data['xn1'] = xn+1

            if time_range > 2:
                if kwargs.get('xq') is not None:
                    xq = kwargs.get('xq')
                else:
                    # now = datetime.utcnow()+timedelta(hours=8)
                    xq = 0 if now.month >= 9 else 1
                if not (isinstance(xq, int) and xq in [0, 1]):
                    raise ValueError(
                        f"xq的类型应是int且只能是0|1，而不应该是「{xq}: {type(xq)}」")
                data['xq'] = xq

        # 发送请求
        response = self.session.post(
            "http://jwyd.dgut.edu.cn/student/xscj.stuckcj_data.jsp", data=data)

        # 解析
        if not response.status_code == 200:
            raise HTTPError(f"HTTP {response.status_code}错误")
        for td in etree.HTML(response.text).xpath('//table[position() mod 2 = 0]/tbody/tr'):
            yield td.xpath('./td[position()>1]/text()')



dgutUser = DgutUser
dgutXgxt = DgutXgxt
dgutIllness = DgutIllness
dgutJwxt = DgutJwxt
