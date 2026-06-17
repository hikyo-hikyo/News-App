from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import requests
from .models import Article


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, **kwargs):
    if instance.approved and not created:  # Only on update
        # Email subscribers
        if instance.publisher:
            subscribers = instance.publisher.subscribers.all()
        else:
            subscribers = instance.author.journalist_subscribers.all()

        for subscriber in subscribers:
            send_mail(
                subject=f"New Article Approved: {instance.title}",
                message=instance.content[:500] +
                "\n\nRead full article on NewsApp.",
                from_email='no-reply@newsapp.com',
                recipient_list=[subscriber.email],
                fail_silently=True,
            )

        # Simulate external API call
        try:
            requests.post('http://127.0.0.1:8000/api/approved/',
                          json={'article_id': instance.id,
                                'title': instance.title},
                          timeout=5)
        except:
            pass  # Don't break if localhost fails in production
