from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from posts.models import Group, Post


class Command(BaseCommand):
    help = 'Create local demo data without resetting existing users or posts.'

    def add_arguments(self, parser):
        parser.add_argument('--password', default='Demo-Learning-42!')

    @transaction.atomic
    def handle(self, *args, **options):
        users = []
        for username in ['alice', 'bob']:
            user, created = get_user_model().objects.get_or_create(username=username)
            if created:
                user.set_password(options['password'])
                user.save(update_fields=['password'])
            users.append(user)
        group, _ = Group.objects.get_or_create(slug='cats', defaults={'title': 'Котики', 'description': 'Истории о котах'})
        for user in users:
            Post.objects.get_or_create(author=user, text=f'Первый пост {user.username}', defaults={'group': group})
        self.stdout.write(self.style.SUCCESS('Demo ready: alice, bob; group cats. Existing passwords unchanged.'))
