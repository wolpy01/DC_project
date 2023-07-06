from django.core.cache import cache
from django.core.management import BaseCommand

from AskHeroes.models import Profile, Tag
import random


class Command(BaseCommand):
    def handle(self, *args, **options):
        cache.set('top_users', [profile.nickname for profile in Profile.objects.get_top_users(count=5)], 86400 + 500)
        cache.set('popular_tags', [tag.tag_name for tag in Tag.objects.get_top_tags(count=7)], 86400 + 500)
        print('Cache was successfully updated!')
