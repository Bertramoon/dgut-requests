from .dgutLogin import dgutLogin
import requests
import re
import lxml.etree
import json
import datetime


# 登录装饰器
def xgxtt_decorator_signin(func):
    '''
    定义一个登录学工系统的装饰器
    '''

    def wrapper(self, *args, **kargs):
        response = self.signin('xgxtt')
        # 情况处理
        if response['code'] == 1:
            return func(self, *args, **kargs)
        else:
            return response
    return wrapper


class dgutXgxtt(dgutLogin):
    '''
    学工系统类

    username : 中央认证账号用户名
    password : 中央认证账号密码
    '''

    def __init__(self, username, password):
        dgutLogin.__init__(self, username, password)
        self.xgxtt = {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
                'Host': 'stu.dgut.edu.cn',
            },
            # 系统主页
            'homepage': {
                'url': 'http://stu.dgut.edu.cn/homepage.jsp',
                'response': [],
            },
            # 考勤界面
            'attendance_main': {
                'url': 'http://stu.dgut.edu.cn/student/partwork/attendance_main.jsp',
                'response': [],
            },
            # 考勤请求
            'attendance': {
                'url': 'http://stu.dgut.edu.cn/student/partwork/attendance.jsp',
                'response': [],
            },
        }

    def __str__(self):
        addr = hex(id(self))
        return f"<dgutXgxtt at 0x{addr[2:].upper().zfill(16)} username is {self.username}>"

    @xgxtt_decorator_signin
    def get_workAssignment(self):
        '''
        获取考勤职位信息
        '''
        try:
            # 请求考勤页职位信息
            response = self.session.get(
                self.xgxtt['attendance']['url'], headers=self.xgxtt['headers'], timeout=self.timeout)
            self.xgxtt['attendance']['response'].append([response])

            if response.status_code != 200:
                return {'message': '页面请求失败', 'code': 300}

            html = lxml.etree.HTML(response.text)
            result = html.xpath('//div[@class="searchTitle"]')
            works = result[0].xpath('./select/option[position()>1]')
            workAssignment = []
            if not len(works):
                return {'message': '请求的职位信息为空', 'code': 304}
            for item in works:
                id_ = item.xpath('./@value')
                name = item.xpath('./text()')
                workAssignment.append((id_[0], name[0]))

            return {'message': '获取职位信息成功', 'code': 1, 'workAssignment': workAssignment}

        except requests.exceptions.ConnectTimeout:
            # 请求超时
            return {'message': '请求超时', 'code': 303}

    @xgxtt_decorator_signin
    def attendance(self, flag: int, workAssignmentId: int = None):
        '''
        学工系统考勤

        attendance(self, flag[, workAssignmentId])
        flag : 0->模拟到选择职位那一步，用于测试 / 1->签到 / 2->签退
        workAssignmentId : 职位id，为None时自动获取当前的首个职位
        '''
        try:
            self.xgxtt['attendance']['response'].append(list())

            if not flag in [0, 1, 2]:
                return {'message': '参数错误：flag只能是0、1或2', 'code': 2}
            if flag == 0:
                action_name = ''
                s = '测试'
            if flag == 1:
                action_name = 'beginWork'
                s = '签到'
            if flag == 2:
                action_name = 'endWork'
                s = '签退'

            # 如果没有传递workAssignmentId，自动获取可考勤的第一个职位作为考勤职位
            if not workAssignmentId:
                workAssignment = self.get_workAssignment()
                if workAssignment['code'] != 1:
                    message = workAssignment['message']
                    return {'message': f'请求信息失败：{message}', 'code': 305}
                workAssignmentId = workAssignment['workAssignment'][0][0]

            # 请求考勤界面
            response = self.session.get(
                self.xgxtt['attendance']['url'], headers=self.xgxtt['headers'], timeout=self.timeout)
            self.xgxtt['attendance']['response'][-1].append(response)
            if response.status_code != 200:
                return {'message': '考勤页面请求失败', 'code': 300}

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
                self.xgxtt['attendance']['url'], headers=self.xgxtt['headers'], data=data, timeout=self.timeout)
            self.xgxtt['attendance']['response'][-1].append(response)

            if response.status_code != 200:
                return {'message': f'考勤{s}请求失败', 'code': 300}
            sign_time = datetime.datetime.now()
            return {
                'message': f'{s}成功',
                'code': 1,
                'info': {
                    'data': data,
                    'time': sign_time,
                }
            }

        except AttributeError:
            # 属性错误
            return {'message': '页面session_token请求失败', 'code': 301}
        except requests.exceptions.ConnectTimeout:
            # 请求超时
            return {'message': '请求超时', 'code': 303}
