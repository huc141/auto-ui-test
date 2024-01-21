from enum import Enum
from read_config import config
import os


class EMode(Enum):
    DEBUG = 'debug'
    TEST = 'test'
    RELEASE = 'release'


class EDeviceType(Enum):
    WIRED = 0
    WIRELESS_NOVC = 1
    WIRELESS_VC = 2


class EDeviceWifiType(Enum):
    OTHER = 0       # 未知类型
    WIRED_ONLY = 1  # 仅支持有线
    WIFI_ONLY = 2   # 支持WiFi 2.4g
    WIFI_ALL = 3    # 支持WiFi 2.4/5g


class ESwitch(Enum):
    ON = 'on'
    OFF = 'off'


class EWindow(Enum):
    MAIN = 0
    DEVICE = 1
    POPUP = 2


class Common:
    """
        存放公共参数
    """

    __i18n = {
        'zh_CN': {
            '_default': '默认',
            '_setting': '设置',
            '_retry': '重试',
            '_ftp': 'FTP',
            '_flip': '翻转',
            '_status_light': '状态灯',
            '_infrared_light': '红外灯',
            '_floodlight_lightness': '照明灯亮度',
            '_floodlight_nightsight': '照明灯夜视模式',
            '_mirror': '镜像',
            '_ftps': '仅用FTPS',
            '_anonymous': '匿名',
            '_ftp_server': 'FTP 服务器',
            '_ftp_port': '端口 (1~65535)',
            '_username': '用户名',
            '_transfer_mode': '传输模式',
            '_enable_mailbox_alert': '启用邮箱报警',
            '_record_sound': '录制声音',
            '_device_name': '设备名称',
            '_smtp_server': 'SMTP服务器',
            '_ssl_tls': '使用SSL或TLS',
            '_smtp_port': 'SMTP端口号 (1~65535)',
            '_sender_name': '发件人名称',
            '_sender_email': '发件邮箱',
            '_password': '密码',
            '_alarm_setting': '报警设置',
            '_received_email_one': '收件邮箱1',
            '_received_email_two': '收件邮箱2',
            '_received_email_three': '收件邮箱3',
            '_email_context': '邮件内容',
            '_interval': '间隔',
            '_video': '录像',
            '_cover': '覆盖',
            '_video_size': '视频最大大小(MB)',
            '_video_cover': '录像覆盖',
            '_video_delay': '录像延时',
            '_video_start': '开启录像',
            '_video_prerecord': '预录像',
            '_datetime': '日期和时间',
            '_time_format': '时间格式',
            '_date_format': '日期格式',
            '_time_zone': '时区',
            '_dst': 'DST',
            '_deviation': '偏移',
            '_start': '开始',
            '_end': '结束',
            '_watermark': '水印',
            '_anti_blink': '抗闪烁',
            '_day_night': '白天和黑夜',
            '_cover_area': '遮盖区域',
            '_advanced_setting': '高级设置',
            '_display_advanced_setting': {
                '_brightness': '亮度',
                '_contrast': '对比度',
                '_saturability': '饱和度',
                '_hue': '色调',
                '_acutance': '锐度',
                'other': {
                    '_exposure': '曝光',
                    '_blc': '背光补偿',
                    '_3d_denoise': '3D降噪',
                    '_day_color': '白天彩色',
                    '_night_color': '夜视彩色'
                }
            },
            '_all_default': '全部默认',
            '_update_processing': '正在升级...\n升级完成前请勿断开电源',
            '_cam': '摄像机',
            '_email_config': '邮件设置',
            '_deploy': '布防',
            '_remote_directory': '远程目录',
            '_generate_subdirectory': '生成子目录',
            '_upload': '上传',
            '_mailbox': '邮箱',
            '_user_manage': '用户管理',
            '_light': '灯',
            '_upnp': '开启UPnP',
            '_uid': '开启UID',
            '_ddns': '开启DDNS',
            '_server_type': '服务器类型',
            '_info': '信息',
            '_stream': '码流',
            '_audio': '音频',
            '_resolution': '分辨率:',
            '_resolve': '分辨率',
            '_video_extension': 'FTP录像延长',
            '_max_stream': '最大码率(Kbps)',
            '_fps': '帧率(FPS)',
            '_preview': '预览',
            '_playback': '回放',
            '_sys': '系统',
            '_network': '网络',
            '_server': '服务器',
            '_ntp_port': '端口号 (1~65535)',
            '_syn_time': '同步间隔时间 (60~65535)',
            '_auto_syn': '自动同步',
            '_maintain': '维护管理',
            '_push': '推送',
            '_whitle': '鸣笛',
            '_confirm': '确定',
            '_media_port': '媒体端口',
            '_rtmp': 'RTMP',
            '_http': 'HTTP',
            '_https': 'HTTPS',
            '_rtsp': 'RTSP',
            '_onvif': 'ONVIF',
            '_rtmp_port': 'RTMP端口',
            '_http_port': 'HTTP端口',
            '_https_port': 'HTTPS端口',
            '_rtsp_port': 'RTSP端口',
            '_onvif_port': 'ONVIF端口',
            '_link_type': '连接类型',
            '_static_ip': '静态',
            '_dns_type': 'DNS',
            '_static_dns': '静态DNS',
            '_ip_addr': 'IP 地址',
            '_mac_addr': 'Mac 地址',
            '_subnet_mask': '子网掩码',
            '_gateway': '网关',
            '_primary_dns': '首选DNS',
            '_alternative_dns': '备用DNS',
            '_remove': '删除',
            '_disconnect': '断开连接',
            '_verify_success': '校验成功',
            '_connect_fail': '连接失败',
            '_storage': '存储',
            '_week': {
                '0': '每天',
                '1': '每周一',
                '2': '每周二',
                '3': '每周三',
                '4': '每周四',
                '5': '每周五',
                '6': '每周六',
                '7': '每周日'
            },
            '_stream_mode': {
                'high': '清晰',
                'standard': '标准',
                'low': '流畅'
            },
            '_error_msg': {
                '_manual_reboot_fail': '手动重启错误',
                '_video_not_fount': '视频未找到, 请确认上传是否选择了视频',
                '_picture_not_fount': '图片未找到, 请确认上传是否选择了图片',
                '_grab_pic_fail': '抓拍失败',
                '_record_fail': '录像失败',
                '_wrong_params': '参数错误',
                '_invalid_time_format': '时间必须为整型',
                '_invalid_day': '星期天数取值范围1~7',
                '_invalid_time': '不合法的时间',
                '_date_not_allowed': '不允许设置大于当天的时间',
                '_device_already_active': '设备已连接',
                '_device_not_found': '设备未找到',
                '_get_lan_devices_fail': '获取局域网设备列表失败',
                '_device_rename_fail': '设备重命名失败',
                '_not_active_device': '非已连接设备',
                '_setting_item_not_found': '设置项未找到',
                '_invalid_action': '非法操作项',
                '_load_app_setting_fail': '载入应用全局配置失败',
                '_get_last_pic_info_fail': '获取抓拍图像信息失败',
                '_element_not_found': '元素未找到',
                '_element_not_interactable': '元素不可交互',
                '_unsupported_num': 'num只能是0~12的整数',
                '_wifi_not_fount': '找不到已连接的wifi',
                '_wifi_connect_fail': 'wifi连接失败',
                '_clip_no_match': '下载的录像与板端不匹配',
                '_clip_partial_no_match': '下载的录像与板端部分不匹配',
                '_open_setting_fail': '跳转到设备设置错误',
                '_open_dl_window_fail': '跳转到录像下载窗口错误',
                '_open_base_net_info_fail': '打开基础网络配置错误',
                '_open_net_setting_fail': '打开网络配置错误',
                '_set_net_type_fail': '设置网络连接类型错误',
                '_set_static_ip_fail': '设置静态ip错误',
                '_set_subnet_mask_fail': '设置子网掩码错误',
                '_set_gateway_fail': '设置网关错误',
                '_set_stream_config_fail': '设置设备支持的码流信息失败',
                '_set_dns_type_fail': '设置DNS类型错误',
                '_set_primary_dns_fail': '设置首选DNS错误',
                '_set_alternative_dns_fail': '设置备用DNS错误',
                '_save_base_net_info_fail': '保存基础网络信息失败',
                '_close_base_net_info_window_fail': '关闭基础网络信息窗口失败',
                '_close_setting_window_fail': '关闭设备设置窗口失败',
                '_remove_device_fail': '移除设备失败',
                '_disconnect_device_fail': '断开设备连接失败',
                '_connect_by_ip_host_fail': '通过ip/host连接设备失败',
                '_connect_by_uid_fail': '通过uid连接设备失败',
                '_login_device_fail': '登陆设备失败',
                '_get_device_net_info_fail': '获取设备网络信息失败',
                '_get_stream_config_fail': '获取设备支持的码流信息失败',
                '_get_device_info_fail': '获取设备基础信息失败',
                '_dict_not_match_key': '未找到匹配的key',
                '_net_info_not_match': '网络信息不匹配',
                '_grab_pic_rs_not_match': '抓拍图像分辨率不匹配',
                '_grab_pic_rs_partial_not_match': '抓拍图像分辨率部分不匹配',
                '_device_reset_not_match': '设备重置校验不通过',
                '_open_wifi_setting_fail': '打开WiFi设置失败',
                '_search_wifi_fail': '查找WiFi失败',
                '_handle_wifi_fail': '配置WiFi窗口失败',
                '_sd_card_not_available': '未检测到SD卡。',
                '_no_available_dl_item': '没有可供下载的项目',
                '_no_available_pb_item': '没有可供预览的项目',
                '_open_stream_window_fail': '打开码流设置窗口失败',
                '_open_maintain_fail': '打开维护管理窗口失败',
                '_open_add_device_window_fail': '打开添加设备窗口失败',
                '_select_device_fail': '选中设备失败',
                '_set_auto_reboot_fail': '设置自动维护重启失败',
                '_set_max_stream_fail': '设置最大码率失败',
                '_set_rs_fail': '设置分辨率失败',
                '_set_fps_fail': '设置帧率失败',
                '_set_stream_fail': '码流相关配置失败',
                '_preview_fail': '预览失败',
                '_login_fail': '登录失败',
                '_init_uname_passwd_fail': '初始化用户名/密码失败',
                '_attempt_awake_device_fail': '尝试唤醒设备失败',
                '_playback_fail': '回放失败',
                '_sd_card_info_verify_fail': 'sd卡信息验证失败',
                '_open_storage_fail': '打开存储信息失败',
                '_get_storage_info_fail': '获取存储信息失败',
                '_get_display_info_fail': '获取显示信息失败',
                '_write_log_fail': '日志写入失败',
                '_format_sd_card_fail': '格式化sd卡失败',
                '_retry_exceed_limit': '重试次数超限',
                '_element_timeout': '获取元素超时',
                '_no_maximum': '获取不到滑动条最大值',
                '_no_minimum': '获取不到滑动条最小值',
                '_get_click_loc_fail': '获取点击位置失败',
                '_get_sniff_time_fail': '获取设备嗅探升级时间失败',
                '_check_release_fail': '检查最新版本失败'
            },
            '_e_device_status': {
                'ACTIVE': '已连接',
                'INACTIVE': '未连接',
                'CONNECTING': '连接中',
                'WRONG_PASS': '密码错误',
                'UNINITIALIZED': '未初始化',
                'FAIL': '失败',
                'OTHER': '其他'
            }
        }
    }

    def __init__(self) -> None:
        self.ENV = config.get_page_data(tier='')
        # self.Device = config.get_page_data(tier='', source='device')
        lang = self.ENV['lang'] if 'lang' in self.ENV else 'zh_CN'
        self.EDeviceType = EDeviceType
        self.EDeviceWifiType = EDeviceWifiType
        self.EMode = EMode
        self.ESwitch = ESwitch
        self.EWindow = EWindow
        self.I18n = self.__i18n[lang]
        self.ProjectRoot = os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))
        )


common = Common()
