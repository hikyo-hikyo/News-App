
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
import requests
from .models import Article


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    reader, _ = Group.objects.get_or_create(name='Reader')
    editor, _ = Group.objects.get_or_create(name='Editor')
    journalist, _ = Group.objects.get_or_create(name='Journalist')

    # Assign permissions
    editor.permissions.add(*Permission.objects.filter(codename__in=[
                           'change_article', 'delete_article', 'approve_article', 'change_newsletter', 'delete_newsletter']))
    journalist.permissions.add(*Permission.objects.filter(codename__in=[
                               'add_article', 'change_article', 'delete_article', 'add_newsletter', 'change_newsletter', 'delete_newsletter']))
    # Reader has only view (default via views)


@receiver(post_save, sender=Article)
def handle_approval(sender, instance, **kwargs):
    if instance.approved and kwargs.get('update_fields') and 'approved' in kwargs['update_fields']:
        # Email subscribers
        if instance.publisher:
            subscribers = instance.publisher.subscribers.all()
        else:
            subscribers = instance.author.journalist_subscribers.all()

        for sub in subscribers:
            send_mail(
                subject=f"New Article: {instance.title}",
                message=instance.content[:500],
                from_email='no-reply@newsapp.com',
                recipient_list=[sub.email],
            )

        # Simulate external POST
        requests.post('http://127.0.0.1:8000/api/approved/', json={
            'article_id': instance.id,
            'title': instance.title
        })
