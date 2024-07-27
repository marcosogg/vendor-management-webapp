from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = 'Clears all data from all tables in the database'

    def handle(self, *args, **kwargs):
        # Get all models
        models = apps.get_models()

        with connection.cursor() as cursor:
            # Disable foreign key checks
            if connection.vendor == 'sqlite':
                cursor.execute('PRAGMA foreign_keys = OFF;')
            
            for model in models:
                table_name = model._meta.db_table
                self.stdout.write(f'Clearing data from {table_name}')
                cursor.execute(f'DELETE FROM {table_name};')
                
                # Reset auto-increment counters for SQLite
                if connection.vendor == 'sqlite':
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")

            # Re-enable foreign key checks
            if connection.vendor == 'sqlite':
                cursor.execute('PRAGMA foreign_keys = ON;')

        self.stdout.write(self.style.SUCCESS('Successfully cleared all data from the database'))
