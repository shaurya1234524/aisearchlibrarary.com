from django.core.management.base import BaseCommand
from django.db import connection
from tools.models import Tool


class Command(BaseCommand):
    help = 'Fix the sequence for Tool model primary key'

    def handle(self, *args, **options):
        try:
            # Get max ID from existing records
            max_id = Tool.objects.values_list('id', flat=True).order_by('-id').first() or 0
            
            self.stdout.write(f"Max existing ID: {max_id}")
            
            # Reset the sequence for PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('tools_tool', 'id'), {max_id} + 1);")
                self.stdout.write(self.style.SUCCESS(f"Sequence reset to {max_id + 1}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            self.stdout.write(self.style.WARNING("This command works for PostgreSQL. If using SQLite, delete and recreate the database."))
