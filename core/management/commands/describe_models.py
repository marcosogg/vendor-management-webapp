from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Describes the structure of all models in the project'

    def handle(self, *args, **options):
        for model in apps.get_models():
            self.stdout.write(self.style.SUCCESS(f'\nModel: {model.__name__}'))
            self.stdout.write('Fields:')
            for field in model._meta.fields:
                self.stdout.write(f'  - {field.name}: {field.get_internal_type()}')
            self.stdout.write('Relationships:')
            for field in model._meta.many_to_many:
                self.stdout.write(f'  - {field.name}: ManyToManyField to {field.related_model.__name__}')
            for related_object in model._meta.related_objects:
                self.stdout.write(f'  - {related_object.name}: {related_object.get_internal_type()} from {related_object.related_model.__name__}')
