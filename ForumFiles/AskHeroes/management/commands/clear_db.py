from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'This script is clear the database.'

    def handle(self, *args, **kwargs):
        with open('db.sqlite3', 'w') as file:
            file.write('')