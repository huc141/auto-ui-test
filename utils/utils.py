import json
import os
from typing import Iterable, Union, Dict
from utils.common import common
from utils.read_config import config
from PIL import Image
from requests import get
import av
import time
import shutil
from imbox import Imbox


"""
封装了一系列工具函数，如获取全局配置、设备类型等函数，方便开发过程中调用
"""


class Util:

    _app_settings = None

    def __init__(self) -> None:
        self._app_settings = self.get_app_settings()

    def get_app_settings(
        self,
        key: str = None,
        default: str = None,
        ns: str = 'userSettings'
    ):
        """
            获取客户端全局配置

            参数:
                - key: 待获取的key
                - default: 当没有值时返回default
                - ns: 命名空间, 支持多层级, 以 `.` 分割

            返回值:
                - Any: 获取到的值
        """

        if not self._app_settings:
            with open(os.path.join(config.app_data_dir, 'electron-storage.json'), encoding='utf-8') as stream:
                self._app_settings = json.load(stream)

        _data = self._app_settings

        if not ns:
            return _data[key] if key in _data else default

        tiers = ns.split('.')
        _ret = None
        for t in tiers:
            flag = False
            if isinstance(_data, Iterable):
                for k, v in _data.items():
                    if k == t:
                        flag = True
                        _data = v
                        _ret = v
                        break
            else:
                _ret = _data
            if not flag:
                _ret = {}
                break

        return _ret[key] if key in _ret else default

    def __deal_raw_data(
        self,
        raw:
        str
    ) -> dict:
        '''
            @deprecated
            客户端更换了配置格式
        '''
        raw = raw.strip().replace('}', '},')[0:-1]
        raw = '[' + raw + ']'
        data = json.loads(raw)
        res = dict()
        for item in data:
            if 'key' in item:
                res[item['key']] = item['value']
        return res

    def __get_imginfo(
        self,
        fname: str
    ) -> str:
        '''
            获取图片信息（分辨率）

            参数:
                - fname: 图片完整路径

            返回值
                - str: 图片分辨率
        '''

        fname = fname.encode('utf-8')
        with Image.open(fname) as img:
            return (str)(img.size[0]) + '*' + (str)(img.size[1])

    def __get_videoinfo(
        self,
        fname: str
    ) -> dict:
        '''
            获取视频文件信息(时长)

            参数:
                - fname: 视频文件完整路径

            返回值
                - dict: 视频基础参数, 包括
                    - duration: 时长
                    - with: 帧宽度
                    - height: 帧长度
                    - fps: 帧率
        '''
        stream = av.open(fname).streams.video[0]
        return {
            'fps': float(stream.average_rate),
            'duration': stream.duration * 1.0 * stream.time_base,
            'width': stream.width,
            'height': stream.height
        }

    def get_device_battery_type(
        self,
        uid: str,
    ) -> common.EDeviceType:
        '''
            通过 `UID` 判断设备类型

            参数:
                - uid: 设备uid

            返回值:
                - (EDeviceType, str): (设备类型, 错误信息)
        '''

        if not uid:
            raise ValueError(
                f"{common.I18n['_error_msg']['_wrong_params']}: uid 不可为空"
            )
        endpoint = str(config.get_data('device_type_api'))
        endpoint = endpoint.replace('${uid}', uid)
        resp = json.loads(get(url=endpoint).text)
        return common.EDeviceType(resp['batteryType'])

    def get_device_wifi_type(
        self,
        uid: str
    ) -> common.EDeviceWifiType:
        '''
            通过 `UID` 判断设备类型

            参数:
                - uid: 设备uid

            返回值:
                - (EDeviceWifiType, str): (设备类型, 错误信息)
        '''
        if not uid:
            raise ValueError(
                f"{common.I18n['_error_msg']['_wrong_params']}: uid 不可为空"
            )
        endpoint = str(config.get_data('device_type_api'))
        endpoint = endpoint.replace('${uid}', uid)
        resp = json.loads(get(url=endpoint).text)
        return common.EDeviceWifiType(int(resp['wifiType']))

    def is_integer(
        self,
        string: str
    ) -> bool:
        '''
            判断一个字符串是否为整形

            参数
                - string: 给定的字符串
        '''
        return string[1:].isdigit() if string[0] == ('-', '+') else string.isdigit()

    def is_valid_datetime(
        self,
        dt: str,
        ref_fmt: str = '%Y-%m-%d %H:%M:%S'
    ) -> bool:
        '''
            判断是否是否是合法的时间字符串

            参数：
                - dt: 时间字符串, 形如 2022-10-15 17:03:34
                - ref_fmt: 参考时间格式

            返回值:
                - bool: 如果 `dt` 不符合 `ref_fmt` 所指定的格式, 返回 `False`
        '''
        try:
            time.strptime(dt, ref_fmt)
            return True
        except:
            return False

    def get_fileinfo(
        self,
        cat: str,
        num: int = 1,
        sort: str = 'new'
    ) -> tuple:
        '''
            获取文件 `图片/下载/录像` 详细信息

            参数:
                - cat: 待获取的文件类型, 可选值 image|download|record
                    - image: 抓拍图片目录
                    - download: 录像下载目录
                    - record: 录像目录
                - num: 待获取路径的文件数量, 默认为1
                - sort: 返回文件创建时间排序, 可选值 new|old
                    - new: 最近创建排最前
                    - old: 最早创建排最前

            返回值:
                - (List[dict], str): (列表[文件信息], 错误信息)
                - 文件信息包括:
                    - fname(str): 文件名
                    - size(float): 文件大小(KB)
                    - ctime(float): 创建时间
                    - rs(str): 分辨率(图片)  仅cat为 `image` 时, 该参数有值
                    - vinfo(dict): 视频基础信息 仅cat为 `download`|`record` 时, 该参数有值
                    参考 Util.`__get_videoinfo` 的返回值
        '''
        try:
            if cat not in ['image', 'download', 'record']:
                raise ValueError(
                    f"common.I18n['_error_msg']['_wrong_params']: {cat}"
                )

            if sort not in ['new', 'old']:
                raise ValueError(
                    f"common.I18n['_error_msg']['_wrong_params']: {sort}"
                )

            if num <= 0:
                raise ValueError(
                    f"common.I18n['_error_msg']['_wrong_params']: {num}"
                )

            mappings = {
                'image': 'sCaptureFolder',
                'download': 'sDownloadFolder',
                'record': 'sRecordFolder'
            }

            td = os.path.join(common.ProjectRoot, 'outcome', cat)
            first = False
            if not os.path.exists(td):
                first = True
                os.makedirs(td)

            target_dir = self.get_app_settings(key=mappings[cat])

            if cat == 'record':
                target_dir = os.path.join(
                    target_dir,
                    self.get_time_by_fmt('%m%d%Y')
                )

            _ret = []
            for fn in os.listdir(target_dir):

                fname = os.path.join(target_dir, fn)
                if os.path.isdir(fname):
                    continue

                tf = os.path.join(td, fn)

                if not os.path.exists(tf):
                    shutil.copy(fname, tf)

                fi = fname if first else tf
                _ret.append({
                    'fname': fi,
                    'ctime': os.path.getctime(fi),
                    'size': round(os.path.getsize(fi) / 1024, 2),
                    'rs': self.__get_imginfo(fi) if cat == 'image' else '',
                    'vinfo': self.__get_videoinfo(fi) if cat != 'image' else {}
                })

            _ret.sort(
                key=lambda x: x['ctime'],
                reverse=sort == 'new'
            )

            return _ret[:num], ''

        except BaseException as err:
            return None, str(err)

    def get_dict_key_by_value(
        self,
        dic: dict,
        value: Union[str, int]
    ) -> Union[str, int]:
        '''
            通过字段value获取key(字典key必须为可hash的类型, 仅支持 str|int)

            参数:
                - dic: 要获取key的字典
                - value: 要获取key的值

            返回值:
                - Union(str, int)
                    - 成功返回value对应的 `key`
                    - 失败抛出异常
        '''
        for k, v in dic.items():
            if v == value:
                return k

        raise ValueError(
            f"{common.I18n['_error_msg']['_dict_not_match_key']}-{value}"
        )

    def get_time_by_fmt(
        self,
        fmt: str = '%Y-%m-%d',
        dt: str = time.localtime()
    ) -> str:
        return time.strftime(fmt, dt)

    def get_email_details(
        self,
        email: str,
        passwd: str,
        host: str
    ) -> dict:
        '''
            获取邮件内容关于邮件报警的内容

            参数:
                - email: 邮件报警收件邮箱地址
                - passwd: 邮箱客户端授权码
                - host: 邮件服务器地址

            返回值:
                - 邮件详情(dict):
                    - subject(str): 邮件主题
                    - sent_from(List[dict[str, str]]): 发件人
                    - sent_to(List[dict[str, str]]): 收件人
                    - body(str): 邮件正文
                    - attachments(List[dict[str, str|int]]): 附件
                - 错误消息(str): 正确返回时为空, 否则返回错误消息
        '''
        with Imbox(host, username=email, password=passwd, ssl=True) as ibox:
            all_msgs = ibox.messages(
                unread=True,
                date__on=time.strftime('%d-%b-%Y')
            )
            list = []
            for _, msg in all_msgs:
                if msg.subject.find('Scheduled Email for') != -1 or msg.subject.find('Motion Detection for') != -1:
                    list.append(
                        {
                            'subject': msg.subject,
                            'sent_from': msg.sent_from,
                            'sent_to': msg.sent_to,
                            'body': msg.body['html'][0] if msg.body['html'] else msg.body['plain'][0],
                            'attachments': msg.attachments
                        }
                    )

            if not list:
                return None

            ml = list[-1]
            if ml['attachments']:
                fp = os.path.join(common.ProjectRoot, 'outcome', 'mail')
                if not os.path.exists(fp):
                    os.makedirs(fp)
                for i, atch in enumerate(ml['attachments']):
                    fname = os.path.join(
                        fp,
                        atch['filename']
                    )
                    with open(fname, "wb") as of:
                        # Copy the BytesIO stream to the output file
                        of.write(atch['content'].getbuffer())

                    ml['attachments'][i]['filename'] = fname
                    del ml['attachments'][i]['content']
                    del ml['attachments'][i]['content-id']

            return ml

    def get_sniff_time_by_uid(
        self,
        uid: str
    ) -> Dict[str, str]:
        '''
            通过uid计算嗅探升级时间
            1 、 取 UID % 9、10、11三位转化为在线升级探测时间(UID从计算从0位开始)
            2 、 UID 先从ASCII转化为16进制(如下图), 然后转化为二进制, 然后除24或者60取余, 得到时、分、秒

            参数
                uid: 设备uid

            返回:
                嗅探升级时间 Dict[str, str]
                    - date: 升级日期
                    - time: 升级时间
                    - b_date: 升级日期(2分钟前)
                    - time: 升级时间(2分钟前)
        '''
        hour = ord(uid[9]) % 24
        min = ord(uid[10]) % 60
        sec = ord(uid[11]) % 60
        today = time.strftime('%d/%m/%Y')

        b_min = min-2 if min-2 >= 0 else min-2+60
        b_hour = hour if min-2 >= 0 else hour-1
        b_today = today if b_hour >= 0 else time.strftime(
            '%d/%m/%Y',
            time.localtime(time.time()-86400)
        )
        b_hour = b_hour if b_hour >= 0 else b_hour+24
        return {
            'date': today,
            'time': '{hour}:{min}:{sec}'.format(hour=hour if hour > 10 else f'0{hour}', min=min if min > 10 else f'0{min}', sec=sec if sec > 10 else f'0{sec}'),
            'b_date': b_today,
            'b_time': '{hour}:{min}:{sec}'.format(hour=b_hour if b_hour > 10 else f'0{b_hour}', min=b_min if b_min > 10 else f'0{b_min}', sec=sec if sec > 10 else f'0{sec}'),
        }


util = Util()
