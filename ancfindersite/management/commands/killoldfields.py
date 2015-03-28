import json
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, path_to_json, *args, **options):
        with open(path_to_json) as source_file:
            data = json.load(source_file)

        for wardinfo in data.values():
            for ancinfo in wardinfo['ancs'].values():
                for smdinfo in ancinfo['smds'].values():
                    for key in ['Committee(s)', 'last_name', 'suffix', 'official_name', 'Position', 'Website', 'first_name', 'Listserv', u'LinkedIn/Misc', u'middle_name', u'Facebook', u'email', u'contestation', u'terms', u'phone', u'address', u'Short Bio', u'Key Initiatives', u'nickname', u'Twitter']:
                        if key in smdinfo:
                            del smdinfo[key]

        with open(path_to_json, 'w') as source_file:
            json.dump(data, source_file, indent=2)
