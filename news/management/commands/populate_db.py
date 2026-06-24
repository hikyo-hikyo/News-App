from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.utils import timezone
from news.models import User, Publisher, Article, Newsletter


class Command(BaseCommand):
    help = 'Populate MariaDB with realistic test data (some articles unpublished)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            'Starting database population...'))

        # Create Groups
        Group.objects.get_or_create(name='Reader')
        Group.objects.get_or_create(name='Journalist')
        Group.objects.get_or_create(name='Editor')

        # Create Users
        users_data = [
            ('reader1', 'reader1@test.com', 'Reader'),
            ('reader2', 'reader2@test.com', 'Reader'),
            ('journo1', 'journo1@test.com', 'Journalist'),
            ('journo2', 'journo2@test.com', 'Journalist'),
            ('editor1', 'editor1@test.com', 'Editor'),
        ]

        users = {}
        for username, email, role in users_data:
            user, created = User.objects.get_or_create(
                username=username, defaults={'email': email})
            if created:
                user.set_password('password123')
                user.save()
            user.groups.add(Group.objects.get(name=role))
            users[username] = user

        # Create Publishers
        publishers = [
            Publisher.objects.get_or_create(
                name="BBC News", description="Global Breaking News")[0],
            Publisher.objects.get_or_create(
                name="TechCrunch", description="Technology and Startups")[0],
            Publisher.objects.get_or_create(
                name="The Guardian", description="Independent Journalism")[0],
            Publisher.objects.get_or_create(
                name="Reuters", description="World News Agency")[0],
        ]

        # Create Articles (Some approved=False)
        articles = [
            {"title": "AI Breakthrough in 2026", "content": "Scientists have achieved a major breakthrough...",
                "author": users['journo1'], "publisher": publishers[0], "approved": True},
            {"title": "Climate Summit Ends with Bold Targets", "content": "World leaders reached historic agreement...",
                "author": users['journo2'], "publisher": publishers[1], "approved": True},
            {"title": "Quantum Computing Just Got Much Faster", "content": "A new chip promises 100x performance...",
                "author": users['journo1'], "publisher": publishers[0], "approved": True},
            {"title": "Unpublished Draft: Future of Remote Work", "content": "This is a draft article about remote work trends...",
                "author": users['journo2'], "publisher": publishers[2], "approved": False},
            {"title": "Independent Investigation: Social Media Addiction", "content": "Our long-term study reveals shocking effects...",
                "author": users['journo1'], "publisher": None, "approved": True},
            {"title": "Draft: New Electric Car Battery Technology", "content": "This revolutionary battery could change everything...",
                "author": users['journo2'], "publisher": publishers[1], "approved": False},
        ]

        for data in articles:
            Article.objects.get_or_create(
                title=data["title"],
                defaults={
                    "content": data["content"],
                    "author": data["author"],
                    "publisher": data["publisher"],
                    "approved": data["approved"],
                    "created_at": timezone.now()
                }
            )

        # Create Newsletters
        Newsletter.objects.get_or_create(
            title="Weekly Technology Digest",
            defaults={
                "description": "Curated tech news from this week",
                "author": users['journo1'],
            }
        )

        Newsletter.objects.get_or_create(
            title="Global Affairs Weekly",
            defaults={
                "description": "Important international stories",
                "author": users['journo2'],
            }
        )

        # Add Subscriptions
        reader1 = users['reader1']
        reader1.subscriptions_publishers.add(publishers[0], publishers[1])
        reader1.subscriptions_journalists.add(users['journo1'])

        self.stdout.write(self.style.SUCCESS(
            'Database populated successfully!'))
        self.stdout.write(self.style.SUCCESS(
            'Users created with password: password123'))
        self.stdout.write(self.style.SUCCESS(
            'Some articles are intentionally unpublished (approved=False)'))
