import pytest


from django.contrib.auth.models import User


class UserParams:
    first_user_name = 'john'
    second_user_name = 'maria'
    first_user_email = 'john@host.net'
    second_user_email = 'maria@host.net'
    first_user_pass = 'qwert'
    second_user_pass = 'trewq'
    incorrect_pass = 'pass'


class TestConstants:
    ok_status_code = 200
    redirect_status_code = 302
    register_url = '/register/'
    register_template = 'register.html'
    login_url = '/login/'
    login_template = 'login.html'
    task_url = '/'
    task_template = 'index.html'


@pytest.yield_fixture()
def first_user_in_bd_logged_in(request, db, client):
    user = User.objects.create_user(UserParams.first_user_name,
                                    UserParams.first_user_email,
                                    UserParams.first_user_pass)
    user.save()
    client.force_login(user=user)
    yield user
    client.logout()
    users = User.objects.all()
    for user in users:
        user.delete()
