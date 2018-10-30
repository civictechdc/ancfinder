from django.core.management.base import BaseCommand
from ancfinder_site.models import *
from collections import OrderedDict
import sys, os.path, json
import requests
import logging


class Command(BaseCommand):
    help = "This command will populate the database with data from outside sources such as opendata.gov and census."

    def add_arguments(self, parser):
        parser.add_argument(
            '--refresh',
            action='store_true',
            dest='refresh',
            help='Use to fully refresh the data in the database.',
        )

    def _updateWards(self, logger):
        #Update the wards model based on info on opendata.gov
        logger.info("~~~Setting up ward models~~~")

        ward_gis_query = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Administrative_Other_Boundaries_WebMercator/MapServer/31/query?where=1%3D1&outFields=WARD,NAME,REP_NAME,WEB_URL,REP_PHONE,REP_EMAIL,REP_OFFICE,WARD_ID&returnGeometry=false&returnDistinctValues=true&outSR=4326&f=json"
        logger.info("Requesting: " + ward_gis_query)

        json_request = requests.get(ward_gis_query, stream=True).json()
        wards = json_request["features"]

        ##add each ward to database
        for ward in wards:
            current_ward = str(ward["attributes"]["WARD"])
            logger.info("Setting up ward " + current_ward)
            ward_model = Ward(id=current_ward)
            ward_model.save();

        logger.info(Ward.objects.all())

    def _updateAncs(self, logger):
        #Update the ancs model based on data on opendata.gov
        logger.info("~~~Setting up anc models~~")
        anc_by_ward_gis_query = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Administrative_Other_Boundaries_WebMercator/MapServer/1/query?where=&text=%25{0}%25&outFields=ANC_ID,WEB_URL,NAME&returnGeometry=true&outSR=4326&f=json"

        if(Ward.objects.all().count() == 0):
            _updateWards()
        else:
            wards = Ward.objects.all()
            for current_ward in wards:
                request_url = anc_by_ward_gis_query.format(current_ward.id)
                print("Requesting: " + request_url)
                json_request = requests.get(request_url, stream=True).json()
                ancs = json_request["features"]

                ## add each ANC for this ward
                for anc in ancs:
                    current_anc = str(anc["attributes"]["ANC_ID"])
                    current_bound = anc["geometry"]["rings"]
                    print("Adding " + current_anc + " to ward " + current_ward.id)
                    anc_model = Anc(id=current_anc, ward=current_ward, boundries=str(current_bound))
                    anc_model.save()
                    logger.info("attributes: " + str(anc["attributes"]))
                    logger.info("geometry: " + str(anc["geometry"]))
        logger.info(Anc.objects.all())

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        if(options['refresh']):
            logger.info("Removing all wards - Due to cascade, all ANC and SMD deleted as well.")
            Ward.objects.all().delete()
        self._updateWards(logger)
        self._updateAncs(logger)
