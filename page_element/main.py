from typing import List
from page_element.base import BaseWF
from common import common


class MainWF(BaseWF):
    """主工作流"""

    def attempt_login_by_device_uid(
            self,
            uid: str,
            name: str,
            unames: List[str],
            passwds: List[str],
            rm_device: bool = True
    ) -> tuple:
        """
            登录工作流(通过设备uid添加, 主要用于电池机)

            参数:
                - uid: 待登录的设备`uid`
                - name: 待登录设备名称, 用于登录前移除设备
                - unames: 尝试登录的用户名列表
                - passwds: 尝试登录的密码列表
                - rm_device: 可选, 执行工作流前是否先自动删除待测试设备, 默认为`True`

            注: 会循环提供的 `unames` 和 `passwds`, 直到登录成功

            返回值:
                - tuple: 正确执行操作返回`True`, 错误信息为空; 否则, 返回`False`与错误信息
        """
        _logs = ''
        try:
            # 尝试唤醒设备
            # self.awake_device_by_need(name)
            main_window = self._main_window

            if rm_device:
                sus, err = main_window.remove_devices([name])
                if not sus:
                    raise ValueError(
                        f"{common.I18n['_error_msg']['_remove_device_fail']}-{name}: {err}"
                    )

            # 尝试点击添加设备按钮。 sus 表示 "success"，如果操作成功，sus 为 True，否则为 False。
            sus, err = main_window.click_add_device_button()
            if not sus:
                raise ValueError(
                    f"{common.I18n['_error_msg']['_open_add_device_window_fail']}: {err}"
                )

            # 切换到添加设备窗口
            add_device_window = main_window.switch_to_add_device_window()

            # 尝试通过 UID 添加设备
            sus, err = add_device_window.add_device_by_uid(uid)
            if not sus:
                raise ValueError(
                    f"{common.I18n['_error_msg']['_connect_by_uid_fail']}: {err}"
                )

            # 处理设备的 Wi-Fi 连接
            sus, err = add_device_window.handle_wifi(uid)
            if not sus:
                raise ValueError(
                    f"{common.I18n['_error_msg']['_handle_wifi_fail']}: {err}"
                )

            for u in unames:
                for p in passwds:
                    sus, err = add_device_window.login_device(
                        uname=u,
                        password=p
                    )
                    if not sus:
                        _logs += f"{common.I18n['_error_msg']['_login_fail']} uname-{u} | password-{p}: {err} ---> fail\n"
                    else:
                        _logs += f"{common.I18n['_verify_success']} uname-{u} | password-{p} ---> pass\n"

                        return True, ''

            # 记录日志
            # self._logger.info(str(_logs))

            return False, common.I18n['_error_msg']['_login_fail']

        except BaseException as err:
            return False, str(err)
        finally:
            # 最终的清理工作
            try:
                add_device_window.close_add_device_window()
                add_device_window.close_login_window()
                main_window.switch_to_window(common.EWindow.MAIN)
            except:
                pass
