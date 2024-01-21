from page_object.wf import Reo


def test_login_by_uid_case():
    sus, error = Reo.attempt_login_by_device_uid(
        uid='952700Y0022IMJ2G',
        name='My Device',
        unames=['admin'],
        passwds=['111111'],
        rm_device=False
    )
    if not sus:
        # logger.error(error)
        assert False
    assert True
