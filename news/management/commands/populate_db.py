from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.utils import timezone
from news.models import User, Publisher, Article, Newsletter


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            'Starting database population...'))

        # 1. Create Groups
        reader, _ = Group.objects.get_or_create(name='Reader')
        journalist, _ = Group.objects.get_or_create(name='Journalist')
        editor, _ = Group.objects.get_or_create(name='Editor')

        # 2. Create Users
        users = [
            ('reader1', 'reader1@test.com', 'Reader'),
            ('reader2', 'reader2@test.com', 'Reader'),
            ('journo1', 'journo1@test.com', 'Journalist'),
            ('journo2', 'journo2@test.com', 'Journalist'),
            ('editor1', 'editor1@test.com', 'Editor'),
        ]

        created_users = {}
        for username, email, role in users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                user.set_password('password123')
                user.save()
            user.groups.add(Group.objects.get(name=role))
            created_users[username] = user

        # 3. Create Publishers
        pub1 = Publisher.objects.get_or_create(
            name="BBC News", description="Global News")[0]
        pub2 = Publisher.objects.get_or_create(
            name="TechCrunch", description="Technology News")[0]
        pub3 = Publisher.objects.get_or_create(
            name="The Guardian", description="Independent Journalism")[0]

        # 4. Create Articles
        articles_data = [
            {
                "title": "AI Breakthrough in 2026",
                "content": "Scientists have achieved a major breakthrough in artificial general intelligence...",
                "author": created_users['journo1'],
                "publisher": pub1,
            },
            {
                "title": "Climate Change Summit Results",
                "content": "World leaders reached a historic agreement at COP31...",
                "author": created_users['journo2'],
                "publisher": pub2,
            },
            {
                "title": "Independent Investigation: Tech Monopolies",
                "content": "Our in-depth report reveals how big tech controls the information flow...",
                "author": created_users['journo1'],
                "publisher": None,
            },
            {
                "title": "Quantum Computing Milestone Reached",
                "content": "A new quantum processor has achieved 1000 logical qubits...",
                "author": created_users['journo2'],
                "publisher": pub1,
            },
        ]

        for data in articles_data:
            article, created = Article.objects.get_or_create(
                title=data["title"],
                defaults={
                    "content": data["content"],
                    "author": data["author"],
                    "publisher": data["publisher"],
                    "approved": True,   # Most are approved for testing
                    "created_at": timezone.now()
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created article: {article.title}'))

        # 5. Create one Newsletter
        Newsletter.objects.get_or_create(
            title="Weekly Tech Digest",
            defaults={
                "description": "Curated technology news from this week",
                "author": created_users['journo1'],
            }
        )

        # 6. Add Subscriptions
        reader1 = created_users['reader1']
        reader1.subscriptions_publishers.add(pub1, pub2)
        reader1.subscriptions_journalists.add(created_users['journo1'])

        self.stdout.write(self.style.SUCCESS(
            'Database populated successfully!'))
        self.stdout.write(self.style.SUCCESS(
            'Users created with password: password123'))
