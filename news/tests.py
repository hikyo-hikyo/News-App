# news/tests.py
from django.test import TestCase
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Article, Publisher, User


class NewsAppTests(APITestCase):

    def setUp(self):
        self.reader_group = Group.objects.get_or_create(name='Reader')[0]
        self.journalist_group = Group.objects.get_or_create(name='Journalist')[
            0]
        self.editor_group = Group.objects.get_or_create(name='Editor')[0]

        self.reader = User.objects.create_user(
            username='reader', password='pass123')
        self.journalist = User.objects.create_user(
            username='journalist', password='pass123')
        self.editor = User.objects.create_user(
            username='editor', password='pass123')

        self.reader.groups.add(self.reader_group)
        self.journalist.groups.add(self.journalist_group)
        self.editor.groups.add(self.editor_group)

        self.publisher = Publisher.objects.create(name="Tech Daily")
        self.reader.subscriptions_publishers.add(self.publisher)

        self.article = Article.objects.create(
            title="Test Article",
            content="Content here...",
            author=self.journalist,
            publisher=self.publisher,
            approved=True
        )

    def test_reader_can_access_subscribed_articles(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reader_cannot_create_article(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.post('/api/articles/', {
            "title": "Bad", "content": "No"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_journalist_can_create_article(self):
        self.client.force_authenticate(user=self.journalist)
        response = self.client.post('/api/articles/', {
            "title": "New Article by Journalist",
            "content": "This should work",
            "publisher": self.publisher.id
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'],
                         self.journalist.id)
        self.assertFalse(response.data.get('approved', True))

    def test_unauthenticated_cannot_access_api(self):
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_article_triggers_signal(self):
        self.client.force_login(self.editor)
        response = self.client.post(reverse('approve-article', args=[self.article.pk]), {
            'approved': True
        })
        self.assertEqual(response.status_code, 302)
        self.article.refresh_from_db()
        self.assertTrue(self.article.approved)
