import json
from django.core.management.base import BaseCommand
from django.template import Template, Context
from ancfindersite.models import CommissionerInfo

class Command(BaseCommand):

    def handle(self, path_to_json, *args, **options):
        if CommissionerInfo.objects.filter(field_name='committees').count() > 0:
            print "This script is intended to initialize our database with committee info from ancs.json."
            return

        with open(path_to_json) as source_file:
            anc_data = json.load(source_file)

        for ward in anc_data.values():
            for anc in ward['ancs'].values():
                committees = ""
                for committee in anc['committees'].values():
                    md = Template("""# {{cmte.committee}}

{% if cmte.chair %}Chair: {{ cmte.chair }}{% if cmte.chair_email %} ({{cmte.chair_email}}){% endif %}{% endif %}

{{cmte.purpose}}

{% if cmte.meetings %}
Meetings: {{ cmte.meetings|safe }}
{% endif %}

""")
                    md = md.render(Context({ 'cmte': committee }))
                    committees += md

                if committees.strip() == "":
                    continue

                try:
                    if CommissionerInfo.get(anc['anc'], None, "committees") == committees:
                        continue
                except CommissionerInfo.DoesNotExist:
                    pass

                # Write a new object.
                CommissionerInfo.put(None, anc['anc'], None, "committees", committees)
