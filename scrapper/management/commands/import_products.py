from django.core.management.base import BaseCommand
from scrapper.models import Product  # Adjust to match your app name
import csv

class Command(BaseCommand):
    help = 'Import products from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        try:
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    asin = row.get('ASIN')
                    title = row.get('TITLE')
                    rsp = row.get('RSP')
                    rsp_vat = row.get('RSP_VAT')
                    amazon_link = row.get('Amazon_Link')
                    dawa_link = row.get('Dawa_Link')
                    nahdi_link = row.get('Nahdi_Link')

                    if asin:
                        Product.objects.update_or_create(
                            ASIN=asin,
                            defaults={
                                'TITLE': title,
                                'RSP': float(rsp) if rsp else None,
                                'RSP_VAT': float(rsp_vat) if rsp_vat else None,
                                'Amazon_Link': amazon_link,
                                'Dawa_Link': dawa_link,
                                'Nahdi_Link': nahdi_link
                            }
                        )
            self.stdout.write(self.style.SUCCESS('Successfully imported products'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
