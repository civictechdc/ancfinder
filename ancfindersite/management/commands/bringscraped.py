import json
from django.core.management.base import BaseCommand
from ancfindersite.models import CommissionerInfo

class Command(BaseCommand):

    def handle(self, path_to_json, *args, **options):
        if CommissionerInfo.objects.count() > 0:
            print "This script is intended to initialize our database after an election. There are already objects in the database, so not continuing."
            return

        with open(path_to_json) as source_file:
            scraped_data = json.load(source_file)

        for ID, fields in scraped_data.items():
            anc, smd = ID[:2], ID[2:]

            for field_name, field_value in fields.items():
                # If the scraped data matches what is in the database,
                # then don't write a new object.
                try:
                    if field_value == CommissionerInfo.get(anc, smd, field_name):
                        continue
                except CommissionerInfo.DoesNotExist:
                    pass

                # Write a new object.
                CommissionerInfo.put(None, anc, smd, field_name, field_value)
