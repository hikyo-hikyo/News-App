from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
    verbose_name = 'News App'

    def ready(self):
        # Import inside ready() to avoid AppRegistryNotReady error
        from django.db.models.signals import post_migrate

        post_migrate.connect(create_default_groups, sender=self)


def create_default_groups(sender, **kwargs):
    """Automatically create user groups after migrations"""
    from django.contrib.auth.models import Group
    for group_name in ['Reader', 'Journalist', 'Editor']:
        Group.objects.get_or_create(name=group_name)
