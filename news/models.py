from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils import timezone


class User(AbstractUser):

    email = models.EmailField(unique=True)  # Unique email

    subscriptions_publishers = models.ManyToManyField(
        'Publisher', blank=True, related_name='subscribers')

    subscriptions_journalists = models.ManyToManyField('User', blank=True,
                                                       related_name='journalist_subscribers',
                                                       limit_choices_to={'groups__name': 'Journalist'})

    def __str__(self):
        return self.username


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_articles',
                               limit_choices_to={'groups__name': 'Journalist'})
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("approve_article", "Can approve articles"),
        ]

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               limit_choices_to={'groups__name': 'Journalist'})
    articles = models.ManyToManyField(Article, related_name='newsletters')

    def __str__(self):
        return self.title
