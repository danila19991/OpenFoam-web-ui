import pytest

from django.urls import reverse

from .utils import TestConstants, first_user_in_bd_logged_in, UserParams


@pytest.mark.django_db
def test_task_not_logged_in(client):
    resp = client.get(reverse('auth_and_static:index'))
    assert resp.status_code == TestConstants.redirect_status_code
    assert resp['Location'] == TestConstants.login_url + '?next=' + \
        TestConstants.task_url


@pytest.mark.django_db
def test_task_url_location(client, first_user_in_bd_logged_in):
    resp = client.get(reverse('auth_and_static:index'))
    assert resp.status_code == TestConstants.ok_status_code
    assert f'{UserParams.first_user_name} previous tasks' in \
           resp.content.decode()
    assert TestConstants.task_template in (t.name for t in resp.templates)


@pytest.mark.django_db
def test_task_log_out(client, first_user_in_bd_logged_in):
    content = {'exit': 'exit'}
    resp = client.post(reverse('auth_and_static:index'), content)
    assert resp.status_code == TestConstants.redirect_status_code
    assert resp['Location'] == TestConstants.login_url

    resp = client.get(reverse('auth_and_static:index'))
    assert resp.status_code == TestConstants.redirect_status_code
    assert resp['Location'] == TestConstants.login_url + '?next=' + \
        TestConstants.task_url



