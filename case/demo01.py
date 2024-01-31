from selenium.webdriver.common.by import By

from page_object.wf import Reo


def test_login_by_uid_case():
    sus, error = Reo.attempt_login_by_device_uid(
        uid='952700Y0058Y1MGY',
        name='3-4 db',
        unames=['admin'],
        passwds=['reolink123'],
        rm_device=True
    )
    if not sus:
        # logger.error(error)
        assert False
    assert True


