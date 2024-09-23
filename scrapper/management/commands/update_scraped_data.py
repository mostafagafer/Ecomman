from django.core.management.base import BaseCommand
from scrapper.models import ScrapedData

class Command(BaseCommand):
    help = 'Update all ScrapedData records with the new calculation logic'

    def handle(self, *args, **kwargs):
        scraped_data_qs = ScrapedData.objects.all()
        total_records = scraped_data_qs.count()

        for index, data in enumerate(scraped_data_qs, start=1):
            data.save()  # This will trigger all recalculations and save the updated data
            self.stdout.write(f'Updated {index}/{total_records} records')

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {total_records} ScrapedData records'))
