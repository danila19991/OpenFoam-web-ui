from auth_and_static.tests.utils import TestConstants, first_user_in_bd_logged_in, UserParams
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_get_params_url_location(client, first_user_in_bd_logged_in):
    resp = client.get(reverse('task_controller:params'))
    assert resp.status_code == TestConstants.ok_status_code


@pytest.mark.django_db
def test_get_task_url_location(client, first_user_in_bd_logged_in):
    resp = client.get(reverse('task_controller:task'))
    assert resp.status_code == TestConstants.ok_status_code

