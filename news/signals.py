from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import requests
from .models import Article


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, **kwargs):
    """Handle email + webhook only when article is approved (not on create)"""
    if instance.approved and not created:   # Only on update to approved
        # Email subscribers
        if instance.publisher:
            subscribers = instance.publisher.subscribers.all()
        else:
            subscribers = instance.author.journalist_subscribers.all()

        for sub in subscribers:
            send_mail(
                subject=f"New Article: {instance.title}",
                message=instance.content[:500] + "\n\nRead more on NewsApp.",
                from_email='no-reply@newsapp.com',
                recipient_list=[sub.email],
                fail_silently=True,
            )

        # External webhook simulation
        try:
            requests.post('http://127.0.0.1:8000/api/approved/',
                          json={'article_id': instance.id,
                                'title': instance.title,
                                'author': instance.author.username,
                                },
                          timeout=5)
        except:
            pass
