import pytest

from django.urls import reverse
from django.contrib.auth.models import User

from .utils import TestConstants, UserParams


@pytest.yield_fixture()
def first_user_in_bd(request, db, client):
    user = User.objects.create_user(UserParams.first_user_name,
                                    UserParams.first_user_email,
                                    UserParams.first_user_pass)
    user.save()
    yield user
    users = User.objects.all().delete()


@pytest.mark.django_db
def test_register_url_location(client):
    resp = client.get(TestConstants.register_url)
    assert TestConstants.ok_status_code == resp.status_code
    assert TestConstants.register_template in (t.name for t in resp.templates)


@pytest.mark.django_db
def test_login_url_location(client):
    resp = client.get(TestConstants.login_url)
    assert TestConstants.ok_status_code == resp.status_code
    assert TestConstants.login_template in (t.name for t in resp.templates)


@pytest.mark.django_db
def test_check_registration(client, first_user_in_bd):
    context = {
        'user_name': UserParams.second_user_name,
        'password': UserParams.second_user_pass,
    }
    resp = client.post(reverse('taskshower:register'), context)
    assert resp.status_code == TestConstants.redirect_status_code
    assert resp['Location'] == TestConstants.task_url

    user_req = User.objects.filter(username=UserParams.second_user_name)
    assert len(user_req) == 1
    user = user_req[0]
    assert user.check_password(UserParams.second_user_pass)


@pytest.mark.django_db(transaction=True)
def test_check_registration_used_username(client, first_user_in_bd):
    context = {
        'user_name': UserParams.first_user_name,
        'password': UserParams.first_user_pass,
    }
    resp = client.post(reverse('taskshower:register'), context)
    assert resp.status_code == TestConstants.ok_status_code
    assert f'user name {UserParams.first_user_name} has already used' in \
        resp.content.decode()

    user_req = User.objects.filter(username=UserParams.first_user_name)
    print(len(user_req))
    assert len(user_req) == 1
    user = user_req[0]
    assert user.check_password(UserParams.first_user_pass)


@pytest.mark.django_db
def test_check_login(client, first_user_in_bd):
    context = {
        'user_name': UserParams.first_user_name,
        'password': UserParams.first_user_pass,
    }
    resp = client.post(reverse('taskshower:login'), context)
    assert resp.status_code == TestConstants.redirect_status_code
    assert resp['Location'] == TestConstants.task_url


@pytest.mark.django_db(transaction=True)
def test_check_login_incorrect_pass(client, first_user_in_bd):
    context = {
        'user_name': UserParams.first_user_name,
        'password': UserParams.incorrect_pass,
    }
    resp = client.post(reverse('taskshower:login'), context)
    assert resp.status_code == TestConstants.ok_status_code
    assert 'incorrect data' in resp.content.decode()
