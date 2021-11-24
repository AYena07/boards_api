import pytest
import requests
import json
import logging
import subprocess

LOGGER = logging.getLogger(__name__)
URL = 'http://127.0.0.1:8000/'


def natural_numbers_generator():
    n = 0
    while True:
        n += 1
        yield n


natural_numbers = natural_numbers_generator()


@pytest.fixture
def token():
    url = URL + "api/login/"
    data = {'username': 'test@mail.com', 'password': 'Password1'}
    resp = requests.post(url, data=data)
    resp_json = json.loads(resp.text)
    return resp_json.get('token')


def clear_users():
    url = URL + "api/login/"
    data = {'username': 'test@mail.com', 'password': 'Password1'}
    resp = requests.post(url, data=data)
    j = json.loads(resp.text)
    token = j.get('token')
    if token:
        url = URL + "api/users/delete_me"
        data = {}
        headers = {'Authorization': f'Token {token}'}
        requests.delete(url, data=data, headers=headers)

    url = URL + "api/login/"
    data = {'username': 'test1@mail.com', 'password': 'Password1'}
    resp = requests.post(url, data=data)
    j = json.loads(resp.text)
    token = j.get('token')
    if token:
        url = URL + "api/users/delete_me"
        data = {}
        headers = {'Authorization': f'Token {token}'}
        requests.delete(url, data=data, headers=headers)


def setup_module(_):
    # subprocess.run(args=["mv", "db.sqlite3", "db_backup.sqlite3"])
    # subprocess.run(args=["touch", "db.sqlite3"])
    # subprocess.run(args=["python3", "manage.py", "migrate"])
    # subprocess.run(args=["python3", "manage.py", "runserver"])
    clear_users()


def teardown_module(_):
    clear_users()
    subprocess.run(args=["rm", "db.sqlite3"])
    subprocess.run(args=["mv", "db_backup.sqlite3", "db.sqlite3"])


@pytest.mark.run(order=next(natural_numbers))
def test_registration():
    url = URL + "api/registration/"
    data = {'username': 'test@mail.com', 'password': 'Password1'}
    resp = requests.post(url, data=data)
    resp_json = json.loads(resp.text)
    assert 'id' in resp_json
    assert resp.status_code == 201
    assert resp_json.get('username') == 'test@mail.com'

    url = URL + "api/registration/"
    data = {'username': 'test1@mail.com', 'password': 'Password1'}
    resp = requests.post(url, data=data)
    resp_json = json.loads(resp.text)
    assert 'id' in resp_json
    assert resp.status_code == 201
    assert resp_json.get('username') == 'test1@mail.com'


@pytest.mark.run(order=next(natural_numbers))
def test_failing_registration():
    url = URL + "api/registration/"
    data = {'username': 'a123', 'password': 'pww'}
    resp = requests.post(url, data=data)
    resp_json = json.loads(resp.text)
    assert resp.status_code == 400
    assert resp_json.get('password') == [
        "Password must be at least 8 characters long, contain at least one digit"
    ]


@pytest.mark.run(order=next(natural_numbers))
def test_login(token):
    assert token


@pytest.mark.run(order=next(natural_numbers))
def test_failing_login():
    url = URL + "api/login/"
    data = {'username': 'a123', 'password': 'pww'}
    resp = requests.post(url, data=data)
    resp_json = json.loads(resp.text)
    assert resp.status_code == 400
    assert resp_json.get('non_field_errors') == ["Unable to log in with provided credentials."]


@pytest.mark.run(order=next(natural_numbers))
def test_board_section_creation(token):
    url = URL + "api/boards/"
    data = {'title': 'test board 1', 'description': 'test description 1'}
    headers = {'Authorization': f'Token {token}'}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    board_id = resp_json.get('id')
    assert board_id
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test board 1'
    assert resp_json.get('description') == 'test description 1'

    url = URL + "api/sections/"
    data = {'title': 'test section 1', 'board': board_id}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    section_id = resp_json.get('id')
    assert section_id
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test section 1'
    assert resp_json.get('board') == board_id

    url = URL + f"api/boards/{board_id}/sections"
    resp = requests.get(url, headers=headers)
    sections_array = json.loads(resp.text)
    assert len(sections_array) > 0
    assert resp.status_code == 200
    assert sections_array[0].get('title') == 'test section 1'
    assert sections_array[0].get('board') == board_id


@pytest.mark.run(order=next(natural_numbers))
def test_failing_board_section_creation(token):
    url = URL + "api/sections/"
    data = {'title': 'test section 1', 'board': '9999999'}
    headers = {'Authorization': f'Token {token}'}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    assert resp.status_code == 403
    assert resp_json.get('detail') == 'such board does not exist'


@pytest.mark.run(order=next(natural_numbers))
def test_sticker_movement(token):
    url = URL + "api/boards/"
    data = {'title': 'test board 2', 'description': 'test description 2'}
    headers = {'Authorization': f'Token {token}'}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    board_id = resp_json.get('id')
    assert board_id
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test board 2'
    assert resp_json.get('description') == 'test description 2'

    url = URL + "api/sections/"
    data = {'title': 'test section 21', 'board': board_id}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    section_id_1 = resp_json.get('id')
    assert section_id_1
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test section 21'
    assert resp_json.get('board') == board_id

    url = URL + "api/sections/"
    data = {'title': 'test section 22', 'board': board_id}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    section_id_2 = resp_json.get('id')
    assert section_id_2
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test section 22'
    assert resp_json.get('board') == board_id

    url = URL + "api/stickers/"
    data = {'title': 'test sticker 1', 'text': 'Sample text', 'section': section_id_1}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    sticker_id = resp_json.get('id')
    assert sticker_id
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test sticker 1'
    assert resp_json.get('text') == 'Sample text'
    assert resp_json.get('section') == section_id_1

    url = URL + f"api/stickers/{sticker_id}/"
    data = {'title': 'test sticker 1', 'text': 'Sample text', 'section': section_id_2}
    resp = requests.put(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    sticker_id = resp_json.get('id')
    assert sticker_id
    assert resp.status_code == 200
    assert resp_json.get('title') == 'test sticker 1'
    assert resp_json.get('text') == 'Sample text'
    assert resp_json.get('section') == section_id_2

    url = URL + f"api/sections/{section_id_2}/stickers"
    resp = requests.get(url, headers=headers)
    sticker_array = json.loads(resp.text)
    assert len(sticker_array) > 0
    assert resp.status_code == 200
    assert sticker_array[0].get('title') == 'test sticker 1'
    assert sticker_array[0].get('text') == 'Sample text'
    assert sticker_array[0].get('section') == section_id_2


@pytest.mark.run(order=next(natural_numbers))
def test_failing_sticker_movement(token):
    url = URL + "api/boards/"
    data = {'title': 'test board 3', 'description': 'test description 3'}
    headers = {'Authorization': f'Token {token}'}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    board_id = resp_json.get('id')
    assert board_id
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test board 3'
    assert resp_json.get('description') == 'test description 3'

    url = URL + "api/sections/"
    data = {'title': 'test section 31', 'board': board_id}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    section_id_1 = resp_json.get('id')
    assert section_id_1
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test section 31'
    assert resp_json.get('board') == board_id

    url = URL + "api/sections/"
    data = {'title': 'test section 32', 'board': board_id}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    section_id_2 = resp_json.get('id')
    assert section_id_2
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test section 32'
    assert resp_json.get('board') == board_id

    url = URL + "api/stickers/"
    data = {'title': 'test sticker 2', 'text': 'Sample text', 'section': section_id_1}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    sticker_id = resp_json.get('id')
    assert sticker_id
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test sticker 2'
    assert resp_json.get('text') == 'Sample text'
    assert resp_json.get('section') == section_id_1

    url = URL + f"api/stickers/{sticker_id}/"
    data = {'title': 'test sticker 2', 'text': 'Sample text', 'section': section_id_2 + section_id_1}
    resp = requests.put(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    assert sticker_id
    assert resp.status_code == 403
    assert resp_json.get('section') == ['Such section does not exist']


@pytest.mark.run(order=next(natural_numbers))
def test_invite_link(token):
    url = URL + "api/boards/"
    data = {'title': 'test board 4', 'description': 'test description 4'}
    headers = {'Authorization': f'Token {token}'}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    board_id = resp_json.get('id')
    invite_link = resp_json.get('invite_link')
    assert invite_link
    assert board_id
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test board 4'
    assert resp_json.get('description') == 'test description 4'

    url = URL + "api/login/"
    data = {'username': 'test1@mail.com', 'password': 'Password1'}
    resp = requests.post(url, data=data)
    resp_json = json.loads(resp.text)
    new_token = resp_json.get('token')
    assert new_token

    url = URL + f"api/boards/{board_id}/"
    headers = {'Authorization': f'Token {new_token}'}
    resp = requests.get(url, headers=headers)
    resp_json = json.loads(resp.text)
    assert resp.status_code == 404
    assert resp_json.get('detail') == "Not found."

    url = URL + f"api/invite/{invite_link}/"
    data = {}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    received_board_id = resp_json.get('id')
    assert received_board_id == board_id
    assert resp.status_code == 200

    url = URL + f"api/boards/{received_board_id}/"
    resp = requests.get(url, headers=headers)
    resp_json = json.loads(resp.text)
    board_id = resp_json.get('id')
    new_invite_link = resp_json.get('invite_link')
    assert new_invite_link != invite_link
    assert board_id == received_board_id
    assert resp.status_code == 200
    assert resp_json.get('title') == 'test board 4'
    assert resp_json.get('description') == 'test description 4'


@pytest.mark.run(order=next(natural_numbers))
def test_failing_invite_link(token):
    url = URL + "api/boards/"
    data = {'title': 'test board 5', 'description': 'test description 5'}
    headers = {'Authorization': f'Token {token}'}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    board_id = resp_json.get('id')
    invite_link = resp_json.get('invite_link')
    assert invite_link
    assert board_id
    assert resp.status_code == 201
    assert resp_json.get('title') == 'test board 5'
    assert resp_json.get('description') == 'test description 5'

    url = URL + "api/login/"
    data = {'username': 'test1@mail.com', 'password': 'Password1'}
    resp = requests.post(url, data=data)
    resp_json = json.loads(resp.text)
    new_token = resp_json.get('token')
    assert new_token

    invalid_link = 'aaaa'
    url = URL + f"api/invite/{invalid_link}/"
    data = {}
    headers = {'Authorization': f'Token {new_token}'}
    resp = requests.post(url, data=data, headers=headers)
    resp_json = json.loads(resp.text)
    assert resp.status_code == 404
    assert resp_json.get('detail') == 'Such invite token does not exist'

    url = URL + f"api/boards/{board_id}/"
    resp = requests.get(url, headers=headers)
    resp_json = json.loads(resp.text)
    assert resp.status_code == 404
    assert resp_json.get('detail') == "Not found."
