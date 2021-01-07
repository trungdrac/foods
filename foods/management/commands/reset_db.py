from django.core.management.base import BaseCommand
from django.db import connection

SCHEMA = 'public'


class Command(BaseCommand):
    help = 'Resets the database'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                cursor.execute('DROP SCHEMA {} CASCADE;'.format(SCHEMA))
            except Exception as e:
                print(e)
            try:
                cursor.execute('CREATE SCHEMA {};'.format(SCHEMA))
            except Exception as e:
                print(e)
