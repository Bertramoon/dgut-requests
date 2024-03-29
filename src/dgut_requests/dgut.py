# coding=utf-8
from typing import Any, NoReturn, Callable
import re
from datetime import datetime, timedelta
from functools import wraps
import base64
from random import choices
from lxml import etree
import requests
from requests.exceptions import HTTPError
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES

__all__ = [
    "validate_type",
    "LoginError", "AuthError", "ObjectTypeError", "GetAesKeyError", "AESEncryptError",
    "DgutUser", "DgutXgxt", "DgutJwxt",
    "dgutUser", "dgutXgxt", "dgutJwxt"
]


def validate_type(obj: Any, type_: type) -> NoReturn:
    """
    类型校验器

    :param obj: 被检查的对象
    :param type_: 被检查对象应属于的类型
    :return: None or except
    """
    if not isinstance(type_, type):
        raise TypeError(f"参数type_必须是type类型，而不能是{type(type_)}类型")
    if not isinstance(obj, type_):
        raise ObjectTypeError(f"校验失败，输入数据应该是{type_}类型，而不是{type(obj)}类型")


class DgutUser(object):
    """莞工用户类"""

    LOGIN_URL = "https://auth.dgut.edu.cn/authserver/login"  # 登录URL
    AUTH_URL = ""  # 认证URL

    def __init__(self, username: str, password: str, timeout: int = 30) -> None:
        """
        :param username: 中央认证账号
        :param password: 中央认证密码
        :return: None
        """
        validate_type(username, str)
        validate_type(password, str)
        validate_type(timeout, int)

        self.username = username
        self.__password = password
        self._aes_key = None  # aes key of bytes
        self._aes_password = None  # aes password by aes key encrypt
        self.is_authenticated = False

        # 创建一个会话
        self.session = requests.Session()
        # 设置请求超时时间
        self.timeout = timeout

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.141 Safari/537.36',
        }

    def login(self) -> requests.Response:
        """
        登录

        :return: requests.Response
        """
        headers = {
            "Host": "auth.dgut.edu.cn",
            "Origin": "https://auth.dgut.edu.cn",
            "Referer": "https://auth.dgut.edu.cn/authserver/login",
        }
        # 1. 获取pwdEncryptSalt(AES key)和execution
        resp = self.session.get(self.LOGIN_URL, headers=headers, timeout=self.timeout)
        try:
            regex = r'id="_eventId".*?value="(.*?)".*?' \
                    r'id="cllt".*?value="(.*?)".*?' \
                    r'id="dllt".*?value="(.*?)".*?' \
                    r'id="lt".*?value="(.*?)".*?' \
                    r'id="pwdEncryptSalt".*?value="(.*?)".*?' \
                    r'id="execution".*?value="(.*?)"'
            _eventId, cllt, dllt, lt, pwd_encrypt_salt, execution = re.search(regex, resp.text).groups()
        except AttributeError as e:
            raise GetAesKeyError() from e
        self._aes_key = pwd_encrypt_salt.encode("utf-8")

        # 2. 生成加密密码
        try:
            self._aes_password = self._encrypt(self.__password, self._aes_key)
        except (TypeError, ObjectTypeError, TypeError, ValueError) as e:
            raise AESEncryptError() from e

        # 3. 发送登录请求
        data = {
            "username": self.username,
            "password": base64.b64encode(self._aes_password).decode(),  # base64密码
            "execution": execution,
            "captcha": "",
            "_eventId": _eventId,
            "cllt": cllt,
            "dllt": dllt,
            "lt": lt,
        }
        resp = self.session.post(self.LOGIN_URL, data=data, headers=headers, timeout=self.timeout)
        if resp.status_code == 401:
            raise LoginError("账号或密码错误")
        if not (resp.ok and resp.history):
            raise LoginError("非预期的错误，登录失败")
        return resp

    @staticmethod
    def _encrypt(text: str, key: bytes) -> bytes:
        """
        AES 128位CBC模式加密，使用pkcs7填充。iv随机生成

        :param text: 明文
        :param key: 密钥
        :return: bytes密文
        """
        validate_type(text, str)
        validate_type(key, bytes)

        chars = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
        password = pad(
            "".join(choices(chars, k=64)).encode("utf-8") + text.encode("utf-8"),
            AES.block_size,
            'pkcs7'
        )
        iv = "".join(choices(chars, k=16)).encode("utf-8")
        aes = AES.new(key, AES.MODE_CBC, iv)
        return aes.encrypt(password)

    def _auth(self):
        """认证"""
        if not self.AUTH_URL:
            return
        resp = self.session.get(self.AUTH_URL, timeout=self.timeout)
        if not resp.ok:
            raise AuthError("认证失败")
        return resp

    @staticmethod
    def login_decorator(func: Callable) -> Callable:
        """
        登录装饰器

        :param func: Callable
        :return: Callable
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.is_authenticated is False:
                self.login()
                self.is_authenticated = True
            self._auth()  # 认证
            return func(self, *args, **kwargs)

        return wrapper


class DgutXgxt(DgutUser):
    """莞工学工系统类"""

    AUTH_URL = "https://stu.dgut.edu.cn/homepage.jsp"

    def __init__(self, username: str, password: str, timeout: int = 30):
        super().__init__(username, password, timeout)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/87.0.4280.141 Safari/537.36',
        }

    @DgutUser.login_decorator
    def get_work_assignment(self) -> list:
        """
        获取考勤职位信息

        :return: list
        """
        # 请求考勤页职位信息
        headers = {
            "Referer": "https://stu.dgut.edu.cn/student/partwork/attendance_main.jsp"
        }
        resp = self.session.get("https://stu.dgut.edu.cn/student/partwork/attendance.jsp",
                                timeout=self.timeout,
                                headers=headers)
        if not resp.status_code == 200:
            raise HTTPError(f"HTTP {resp.status_code} 响应错误，{resp.reason}")
        works = etree.HTML(resp.text).xpath('//div[@class="searchTitle"]/select/option')
        return [(item.xpath('./@value'), item.xpath('./text()')) for item in works[1:]]

    @DgutUser.login_decorator
    def attendance(self, flag: int, work_assignment_id: int = None) -> dict:
        """
        学工系统考勤

        :param flag: 1->签到 | 2->签退
        :param work_assignment_id: 职位id，为None时自动获取当前的首个职位
        :return: dict
        """
        validate_type(flag, int)
        if flag not in (1, 2):
            raise ValueError("flag只能是1(签到)或2(签退)")
        work_assignment_id = str(work_assignment_id)
        if not work_assignment_id.isdigit():
            raise ValueError("work_assignment_id必须是数字")

        action_name, action_description = ('beginWork', '签到') \
            if flag == 1 else ('endWork', '签退')

        # 如果没有传递work_assignment_id，自动获取可考勤的第一个职位作为考勤职位
        if not work_assignment_id:
            work_assignment = self.get_work_assignment()
            if len(work_assignment) < 1:
                raise ValueError("没有可考勤的职位")
            work_assignment_id = work_assignment[0][0]

        # 请求考勤界面
        resp = self.session.get(
            "https://stu.dgut.edu.cn/student/partwork/attendance.jsp", timeout=self.timeout)

        # 获取session_token
        session_token = re.search(
            r'session_token.*?value="(.*?)"/>', resp.text, re.S).group(1)

        # 提交表单数据
        data = {
            'action_name': action_name,
            'modifying': 'true',
            'salaryInfoId': '',
            'session_token': session_token,
            'backUrl': '',
            'workAssignmentId': work_assignment_id
        }

        # 发送请求
        resp = self.session.post(
            "https://stu.dgut.edu.cn/student/partwork/attendance.jsp", data=data, timeout=self.timeout)

        attendance_time = datetime.utcnow() + timedelta(hours=8)
        return {
            'message': f'{action_description}成功',
            'code': 1,
            'info': {
                'data': data,
                'time': attendance_time,
            }
        }


class DgutJwxt(DgutUser):
    """莞工教务系统类"""

    AUTH_URL = "https://jw.dgut.edu.cn/caslogin"

    def __init__(self, username: str, password: str, timeout: int = 30):
        super().__init__(username, password, timeout)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }

    @DgutUser.login_decorator
    def get_lesson(self, xn: int = 2022, xq: int = 0):
        validate_type(xn, int)
        validate_type(xq, int)
        if xq not in (0, 1):
            raise ValueError('xq取值只能是0|1')

        # 获取教务系统xh
        temp = self.session.get('https://jw.dgut.edu.cn/custom/js/SetRootPath.jsp')
        xh = re.search(r"G_USER_CODE = '(.*?)'.*", temp.text).group(1)

        # base64加密字符串
        params = base64.b64encode(('xn=' + str(xn) + '&xq=' + str(xq) + '&xh=' + str(xh)).encode('utf-8')).decode(
            'utf-8')
        result = self.session.get('https://jw.dgut.edu.cn/student/wsxk.xskcb10319.jsp?params=' + params,
                                  headers={
                                      'Referer': 'https://jw.dgut.edu.cn/student/xkjg.wdkb.jsp?menucode=S40303'},
                                  )
        # 数据未处理
        return result.text

    @DgutUser.login_decorator
    def get_score(self, score_type: int = 1, course_type: int = 3,
                  time_range: int = 1, **kwargs) -> list:
        """
        获取成绩信息

        :param score_type: 成绩类型,，1=>原始成绩（默认） | 2=>有效成绩
        :param course_type: 课程类型,，1=>主修 | 2=>辅修 | 3=>主修和辅修（默认）
        :param time_range: 时间范围选择，1=>入学以来 | 2=>学年 | 3=>学期（默认）
        :param kwargs: xn: 学年 & xq: 学期，0|1
        :return: Generator
        """
        # 字段合法检测
        validate_type(score_type, int)
        validate_type(course_type, int)
        validate_type(time_range, int)
        if score_type not in (1, 2):
            raise ValueError('core_type取值只能是1|2')
        if course_type not in (1, 2, 3):
            raise ValueError('course_type取值只能是1|2|3')
        if time_range not in (1, 2, 3):
            raise ValueError('time_range取值只能是1|2|3')

        data = {
            "sjxz": "sjxz" + str(time_range),  # 时间选择，1-入学以来（默认），2-学年，3-学期
            # 原始有效，指原始成绩或有效成绩，yscj-原始成绩，yxcj-有效成绩
            "ysyx": "yscj" if score_type == 1 else "yxcj",
            # course_type -> 1: 主修 2: 辅修 3: 主修和辅修（默认）
            "zx": 1 if not course_type == 2 else 0,  # 主修，1-选择，0-不选择
            "fx": 1 if not course_type == 1 else 0,  # 辅修，1-选择，0-不选择
            "btnExport": r"%B5%BC%B3%F6",
            # xn-xn1学年第(xq+1)学期
            "xn": "",
            "xn1": "",
            "xq": "",
            "ysyxS": "on",
            "sjxzS": "on",
            "zxC": "on",
            "fxC": "on",
            "menucode_current": "S40303",
        }
        if time_range > 1:
            xn = kwargs.get("xn")
            now = datetime.utcnow() + timedelta(hours=8)
            if xn is None:
                xn = now.year if now.month >= 9 else now.year - 1
            validate_type(xn, int)
            if not (1970 <= xn <= now.year):
                raise ValueError(f"xn={xn}，不在范围[1970, {now.year}]中")
            data['xn'] = xn
            data['xn1'] = xn + 1

            if time_range > 2:
                xq = kwargs.get('xq')
                if xq is None:
                    xq = 0 if now.month >= 9 else 1
                validate_type(xq, int)
                if xq not in (0, 1):
                    raise ValueError(f"xq的类型应是int且只能是0|1，而不应该是{xq}")
                data['xq'] = xq

        # 发送请求
        resp = self.session.post(url="https://jw.dgut.edu.cn/student/xscj.stuckcj_data.jsp",
                                 headers={"Content-Type": "application/x-www-form-urlencoded",
                                          'Referer': 'https://jw.dgut.edu.cn/student/xscj.stuckcj.jsp?menucode=S40303'},
                                 data=data)

        # 解析
        if not resp.status_code == 200:
            raise HTTPError(f"HTTP {resp.status_code}错误")
        result = []
        for td in etree.HTML(resp.text).xpath('//table[position() mod 2 = 0]/tbody/tr'):
            result.append(td.xpath('./td[position()>1]/text()'))
        return result


class DgutDs(DgutUser):
    """订水系统类 未完成"""

    AUTH_URL = "https://ds.dgut.edu.cn/admin/oauth/login?state=h5"

    def __init__(self, username: str, password: str, timeout: int = 30):
        super().__init__(username, password, timeout)
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        }

    def get_barrel_list(self):
        resp = self.session.get(url="https://ds.dgut.edu.cn/home/Distribution/getBarrelListByUser?",
                                headers={"referer": "https://ds.dgut.edu.cn/selectBrand"}
                                ).json()
        if not resp.get('code') == 1000:
            raise AuthError
        result = resp['info']
        return result

    def get_distribution_pre(self, area_id: int, building_id: int, campus_id: int, room_number: int):
        data = {'area_id': area_id,
                'building_id': building_id,
                'campus_id': campus_id,
                'room_number': room_number}
        resp = self.session.post(url="https://ds.dgut.edu.cn/home/Distribution/getDistributionPre",
                                 data=data)

    def check_pay(self, price: int):
        """
        检查余额是否足够用于支付
        Args:
            price: 价格

        Returns:
            bool
        """
        data = {'total_price': price}
        resp = self.session.post(url="https://ds.dgut.edu.cn/home/Pay/checkPay",
                                 data=data)
        if not resp.json().get('message') == "可以支付":
            return False
        return True

    def add_distribution(self, area_id: int, building_id: int, campus_id: int, room_number: int, barrel_id: int,
                         phone: int):
        data = {"campus_id": campus_id,
                "area_id": area_id,
                "building_id": building_id,
                "room_number": room_number,
                "barrel_id": barrel_id,
                "send_num": 1,
                "phone": phone,
                "password": ""}


class LoginError(Exception):
    """登录错误类"""

    def __init__(self, reason: str = None):
        super().__init__()
        self.reason = reason \
            if reason is not None \
            else "登录错误"

    def __str__(self):
        return self.reason


class AuthError(Exception):
    """认证错误类"""

    def __init__(self, reason: str = None):
        super().__init__()
        self.reason = reason \
            if reason is not None \
            else "认证失败"

    def __str__(self):
        return self.reason


class ObjectTypeError(TypeError):
    """对象类型错误"""

    def __init__(self, reason: str = None):
        super().__init__()
        self.reason = reason \
            if reason is not None \
            else "类型错误"

    def __str__(self):
        return self.reason


class GetAesKeyError(Exception):
    """获取AES密钥错误"""

    def __str__(self):
        return "获取AES加密密钥失败"


class AESEncryptError(Exception):
    """AES加密错误"""

    def __str__(self):
        return "AES加密错误"


dgutUser = DgutUser
dgutXgxt = DgutXgxt
dgutJwxt = DgutJwxt
