from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from boards.models import Board


class UserTests(APITestCase):
    def setUp(self):
        d = User.objects.create(username="default")
        d.set_password('11111111')
        d.save()
        a = User.objects.create_superuser(username="admin")
        a.set_password('22222222')
        a.save()

    def test_create_user_as_anonymous(self):
        """
        Ensure we can create a new account object.
        """
        url = r'http://127.0.0.1:8000/users/'
        data = {'username': 'DabApps', 'password': '12345678', 'first_name': 'a', 'last_name': 'b'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_as_default(self):
        """
        Ensure we can create a new account object.
        """
        url = r'http://127.0.0.1:8000/users/'
        self.client.login(username='default', password='11111111')
        data = {'username': 'DabApps', 'password': '12345678', 'first_name': 'a', 'last_name': 'b'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 2)

    def test_create_user_as_admin(self):
        """
        Ensure we can create a new account object.
        """
        url = r'http://127.0.0.1:8000/users/'
        self.client.login(username='admin', password='22222222')
        data = {'username': 'DabApps', 'password': '12345678', 'first_name': 'a', 'last_name': 'b'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)


class InviteTests(APITestCase):
    def setUp(self):
        d = User.objects.create(username="default")
        d.set_password('11111111')
        d.save()
        a = User.objects.create(username="admin")
        a.set_password('22222222')
        a.save()
        Board.objects.create(title="test", owner=d)

    def test_invite_not_member(self):
        board = Board.objects.filter(title="test")[0]
        self.assertEqual(board.users.count(), 0)
        key = board.invite_link
        url = r'http://127.0.0.1:8000/invite/' + key + r'/'
        user = User.objects.filter(username='admin')[0]
        self.client.login(username='admin', password='22222222')
        response = self.client.post(url, {}, format='json')
        board = Board.objects.filter(title="test")[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn(board, user.guest_boards.all())
        self.assertEqual(response.data['id'], board.id)
        self.assertEqual(board.users.count(), 1)
        self.assertNotEqual(board.invite_link, key)

    def test_invite_member(self):
        board = Board.objects.filter(title="test")[0]
        user = User.objects.filter(username='admin')[0]
        board.users.add(user)
        self.assertIn(board, user.guest_boards.all())
        key = board.invite_link
        url = r'http://127.0.0.1:8000/invite/' + key + r'/'
        self.client.login(username='admin', password='22222222')
        response = self.client.post(url, {}, format='json')
        board = Board.objects.filter(title="test")[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], board.id)
        self.assertEqual(board.users.count(), 1)
        self.assertEqual(board.invite_link, key)

    def test_invite_owner(self):
        board = Board.objects.filter(title="test")[0]
        self.assertEqual(board.users.count(), 0)
        key = board.invite_link
        url = r'http://127.0.0.1:8000/invite/' + key + r'/'
        self.client.login(username='default', password='11111111')
        response = self.client.post(url, {}, format='json')
        board = Board.objects.filter(title="test")[0]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['id'], board.id)
        self.assertEqual(board.users.count(), 0)
        self.assertEqual(board.invite_link, key)

    def test_invite_anonymus(self):
        board = Board.objects.filter(title="test")[0]
        self.assertEqual(board.users.count(), 0)
        key = board.invite_link
        url = r'http://127.0.0.1:8000/invite/' + key + r'/'
        response = self.client.post(url, {}, format='json')
        board = Board.objects.filter(title="test")[0]
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('id', response.data)
        self.assertEqual(board.users.count(), 0)
        self.assertEqual(board.invite_link, key)
