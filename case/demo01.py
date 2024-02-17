from page.wf import Reo


def test_login_by_uid_case():
    sus, error = Reo.attempt_login_by_device_uid(
        uid='952700Y005FT13UE',
        name='APPLE',
        unames=['admin'],
        passwds=['111111..'],
        rm_device=True
    )
    if not sus:
        # logger.error(error)
        assert False
    assert True


def test_clear_all_devices():
    success, error = Reo.clear_all_devices()
