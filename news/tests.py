from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from .models import User, Article, Publisher


class APITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.reader = User.objects.create_user('reader', password='pass')
        self.reader.groups.add(Group.objects.get(name='Reader'))
        # ... create journalist, editor, articles, subscriptions

    def test_reader_subscribed_content(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, 200)
        # assert only subscribed

    def test_journalist_create(self):
        # similar
        pass

    # Mock signals for email/requests
    @patch('news.signals.send_mail')
    @patch('news.signals.requests.post')
    def test_approval_signal(self, mock_post, mock_email):
        article = Article.objects.create(...)  # set approved=True
        article.approved = True
        article.save()
        mock_email.assert_called()
        mock_post.assert_called()
