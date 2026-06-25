from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        post_migrate.connect(create_default_groups, sender=self)


def create_default_groups(sender, **kwargs):
    """Create default groups automatically after migrations"""
    for group_name in ['Reader', 'Journalist', 'Editor']:
        Group.objects.get_or_create(name=group_name)
