from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from .models import User, Article, Publisher


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create groups
        self.reader_group = Group.objects.create(name='Reader')
        self.journalist_group = Group.objects.create(name='Journalist')
        self.editor_group = Group.objects.create(name='Editor')

        # Create users
        self.reader = User.objects.create_user(
            'reader', 'reader@test.com', 'pass')
        self.reader.groups.add(self.reader_group)

        self.journalist = User.objects.create_user(
            'journo', 'journo@test.com', 'pass')
        self.journalist.groups.add(self.journalist_group)

    @patch('news.signals.send_mail')
    @patch('news.signals.requests.post')
    def test_approval_signal(self, mock_post, mock_email):
        article = Article.objects.create(
            title="Test", content="Test", author=self.journalist, approved=False
        )
        article.approved = True
        article.save()

        mock_email.assert_called()
        mock_post.assert_called()
