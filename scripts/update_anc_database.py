#!/usr/bin/python3

import sys, os.path, csv, json, re, subprocess
import urllib.request, urllib.parse, urllib.error, io
import requests
import getpass
from collections import OrderedDict

data_dir = '../data/'

# Opendata.dc.gov queries
ward_gis_query = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Administrative_Other_Boundaries_WebMercator/MapServer/31/query?where=1%3D1&outFields=WARD,NAME,REP_NAME,WEB_URL,REP_PHONE,REP_EMAIL,REP_OFFICE,WARD_ID&returnGeometry=false&returnDistinctValues=true&outSR=4326&f=json"
anc_by_ward_gis_query = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Administrative_Other_Boundaries_WebMercator/MapServer/1/query?where=&text=%25{0}%25&outFields=ANC_ID,WEB_URL,NAME&returnGeometry=false&outSR=4326&f=json"
smd_by_anc_gis_query = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Administrative_Other_Boundaries_WebMercator/MapServer/21/query?where=ANC_ID%3D%27{0}%27&outFields=SMD_ID,ANC_ID,NAME,CHAIR,REP_NAME,LAST_NAME,FIRST_NAME,ADDRESS,ZIP,EMAIL,WEB_URL,PHONE&returnGeometry=false&outSR=4326&f=json"
abra_by_smd_query = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Business_and_Economic_Development_WebMercator/MapServer/5/query?where=UPPER(SMD)%20like%20%27%25{0}%25%27&outFields=LICENSE,APPLICANT,ADDRESS,STATUS,WARD,ZIPCODE,SMD,ANC,TRADE_NAME,CLASS,ADDRID,X,Y,TYPE&outSR=4326&f=json"
building_permits_by_smd_query = "https://maps2.dcgis.dc.gov/dcgis/rest/services/FEEDS/DCRA/MapServer/9/query?where=UPPER(SMD)%20like%20'%25{0}%25'&outFields=PERMIT_ID,PERMIT_TYPE_NAME,PERMIT_SUBTYPE_NAME,PERMIT_CATEGORY_NAME,APPLICATION_STATUS_NAME,FULL_ADDRESS,ZONING,PERMIT_APPLICANT,OWNER_NAME,LATITUDE,LONGITUDE,XCOORD,YCOORD,ZIPCODE,WARD,ANC,SMD&outSR=4326&f=json"

def urlopen(url):
    # Opens a URL and decodes its content assuming UTF-8; returns a stream.
    print('Making a request to: ' + url)
    data = urllib.request.urlopen(url)
    return io.TextIOWrapper(data, encoding="utf8")

def csv_file_to_dict(csv_file):
    return list(csv.DictReader(csv_file))

def load_json(name):
    return json.loads(open(data_dir + name).read())

def add_base_data(anc_json):
    #Start things anew

    #retrieve data from the GIS opendata website
    print("Requesting: " + ward_gis_query)
    json_request = requests.get(ward_gis_query, stream=True).json()
    wards = json_request["features"]

    ##add each ward to json file
    for ward in wards:
        current_ward = str(ward["attributes"]["WARD"])
        print("Setting up ward "+ current_ward)
        anc_json[current_ward] = OrderedDict()
        anc_json[current_ward]["attributes"] = ward["attributes"]

        #each ward has a number of ANCs. Lets query for them.
        request_url = anc_by_ward_gis_query.format(current_ward)
        print("Requesting: " + request_url)
        json_request = requests.get(request_url, stream=True).json()
        ancs = json_request["features"]

        ##add each anc for this ward to json file
        for anc in ancs:
            current_anc = str(anc["attributes"]["ANC_ID"])
            print("Adding " + current_anc + " to ward " + current_ward)
            anc_json[current_ward][current_anc] = OrderedDict()
            anc_json[current_ward][current_anc]["attributes"] = anc["attributes"]

            #each anc has a number of SMDs. Lets query for them.
            request_url = smd_by_anc_gis_query.format(current_anc)
            print("Requesting: " + request_url)
            json_request = requests.get(request_url, stream=True).json()
            smds = json_request["features"]

            ##add each smd for this anc to json file
            for smd in smds:
                current_smd = str(smd["attributes"]["SMD_ID"])
                print("Adding " + current_smd + " to ANC " + current_anc + ", in ward " + current_ward)
                anc_json[current_ward][current_anc][current_smd] = OrderedDict()
                anc_json[current_ward][current_anc][current_smd]["attributes"] = smd["attributes"]

def add_abra_data(output):
    print("adding liquor license information")

    #Iterate through the data for SMDs
    for ward in anc_json:
        if ward == "attributes":
            continue
        for anc in anc_json[ward]:
            if anc == "attributes":
                continue
            for smd in anc_json[ward][anc]:
                if smd == "attributes":
                    continue
                else:
                    #query for the licenses for this SMD
                    request_url = abra_by_smd_query.format(str(smd))
                    print("Requesting: " + request_url)
                    json_request = requests.get(request_url, stream=True).json()
                    liquor_licenses = json_request["features"]
                    anc_json[ward][anc][smd]["licenses"] = liquor_licenses

def add_building_permit_data(output):
    print("adding building permit information")
    # Number of building permits in each ANC and SMD

    #Iterate through the data for SMDs
    for ward in anc_json:
        if ward == "attributes":
            continue
        for anc in anc_json[ward]:
            if anc == "attributes":
                continue
            for smd in anc_json[ward][anc]:
                if smd == "attributes":
                    continue
                else:
                    #query for the licenses for this SMD
                    request_url = building_permits_by_smd_query.format(str(smd))
                    print("Requesting: " + request_url)
                    json_request = requests.get(request_url, stream=True).json()
                    building_permits = json_request["features"]
                    anc_json[ward][anc][smd]["buildingPermits"] = building_permits

def add_311_data(output):
    print("adding 311 information")
    # Number of 311 requests in each ANC 
    data = json.loads(open('data/311.json').read())
    for anc in data:
        output[anc[0]]['ancs'][anc[1]]['census']['311_requests'] = { "value": int(data[anc]['total']) }

def add_geographic_data(output):
    print("adding geographic data")

    def get_gis_data(name, layer):
            gisdata = json.load(urlopen("http://gis.govtrack.us/boundaries/dc-%s-2013/%s" % (layer, name.lower())))
            ret = OrderedDict()
            ret["bounds"] = gisdata["extent"]
            ret["area"] = gisdata["metadata"]["area_sq_m"] # square meters
            return ret

    # Add ANC/SMD geographic extents (bounding box) from the GIS server.
    for ward in list(output.values()):
        for anc in list(ward["ancs"].values()):
            anc.update(get_gis_data(anc["anc"], "anc"))
            for smd in list(anc["smds"].values()):
                smd.update(get_gis_data(smd["smd"], "smd"))

def add_neighborhood_data(output):
    print("adding neighborhood data")

    # Add intersections between ANCs/SMDs and neighborhoods, and estimate the
    # population in every intersection because it looks weird to say ANC 2A
    # contains the "Tidal Basin". We'll handle small-population intersections
    # in the front-end.

    # Query the Census API for the population of every block group that intersects
    # with a neighborhood.
    bg_population = { }
    for intsect in json.load(open("data/neighborhoods-blockgroups.json")):
        bg = intsect["2012-blockgroups"]["id"]
        if bg in bg_population: continue
        state_fips, county_fips, tract, bg_num = bg[0:2], bg[2:5], bg[5:11], bg[11:12]
        if state_fips != "11":
            # not in DC! this should be a denegerate intersection of some sort
            bg_population[bg] = 0
            continue
        url = "http://api.census.gov/data/%s?key=%s&get=%s&in=state:%s+county:%s+tract:%s&for=block+group:%s" \
                % ("2010/sf1", census_api_key, "P0010001", state_fips, county_fips, tract, bg_num)
        census_data = json.load(urlopen(url))
        bg_population[bg] = int(census_data[1][0])

    # For each neighborhood, sum the populations of the block groups it intersects with
    # weighted by the proportion of the block group that intersects with the neighborhood.
    hood_population = { }
    for intsect in json.load(open("data/neighborhoods-blockgroups.json")):
        h = intsect["dc-neighborhoods"]["id"]
        bg = intsect["2012-blockgroups"]["id"]
        intsect_pop = bg_population[bg] * intsect["2012-blockgroups"]["ratio"]
        hood_population[h] = hood_population.get(h, 0) + intsect_pop
        
    # Clear out existing data.
    for ward in output.values():
        for anc in ward["ancs"].values():
            anc["neighborhoods"] = []
            for smd in anc["smds"].values():
                smd["neighborhoods"] = []
    
    # Now store the neighborhood data in the output, once for ANCs as a whole
    # and once for the SMDs.

    for anc_smd in ("anc", "smd"):
        dat = json.load(open("data/%s-neighborhood.json" % anc_smd))
        for ix in dat:
            ward = ix[anc_smd]["id"][0]
            anc = ix[anc_smd]["id"][1]

            if anc_smd == "anc":
                feature = output[ward]["ancs"][anc]
            else:
                smd = ix[anc_smd]["id"][2:]
                feature = output[ward]["ancs"][anc]["smds"][smd]
                
            feature["neighborhoods"].append({
                "name": ix["neighborhood"]["name"],
                "part-of-" + anc_smd: ix[anc_smd]["ratio"],
                "part-of-neighborhood": ix["neighborhood"]["ratio"],
                "population": int(round(hood_population[ix["neighborhood"]["id"]] * ix["neighborhood"]["ratio"])),
            })

    # Sort so that JSON output is consistent from run to run.
    for ward in output.values():
        for anc in ward["ancs"].values():
            anc["neighborhoods"].sort(key = lambda h : -h["part-of-anc"])
            for smd in anc["smds"].values():
                smd["neighborhoods"].sort(key = lambda h : -h["part-of-smd"])

def add_census_data(output):
    # Estimate ANC/SMD Census population data by averaging across the tracts that
    # each ANC and SMD intersects with. Tracts appear to be the lowest level that
    # interesting data is uniformly available from the 2011 American Community Survey.
    # We can get more precise information on population from block groups though.

    # Pre-load the relevant data points from the Census API.

    census_fields = {
            "2010/sf1": [
                    ("P0010001", int, "count"), # Total Population
                    ("P0180001", int, "count"), # Households
                    ("P0180002", int, "count"), # Family Households
                    ("H0040001", int, "count"), # Occupied Housing Units
                    ("H0050001", int, "count"), # Vacant Housing Units
            ],

            # http://www.census.gov/developers/data/acs_5yr_2011_var.xml
            "2011/acs5": [
                    ("B01003_001E", int, "count"), # Total Population
                    ("B01002_001E", float, "median"), # Median Age
                    ("B07001_001E", int, "count"), # Geographic Mobility in the Past Year Total Population
                    ("B07001_017E", int, "count"), # .... Same House One Year Ago
                    ("B07001_033E", int, "count"), # .... Moved Within Same County
                    ("B07001_065E", int, "count"), # .... Moved From Different State
                    ("B07001_081E", int, "count"), # .... Moved From Abroad
                    ("B19019_001E", float, "median"), # Median Household Income
                    ("B16002_001E", int, "count"), # No One Age 14+ in Household Speaks English
            ],
    }

    census_data = { }
    for division in ("tract", "blockgroup"):
        dat = json.load(open("data/smd-%s.json" % division))
        for intsect in dat:
            #if intsect["smd"]["id"] != "1A02": continue

            # get the ID of this tract or blockgroup
            id = intsect[division]["id"]
            if id in census_data: continue
            census_data[id] = { }

            # query Census API
            state_fips, county_fips, tract, bg_num = id[0:2], id[2:5], id[5:11], (id+"?")[11:12]
            for census_table in census_fields:
                field_list = ",".join(f[0] for f in census_fields[census_table])
                if division == "tract":
                    url = "http://api.census.gov/data/%s?key=%s&get=%s&in=state:%s+county:%s&for=tract:%s" \
                        % (census_table, census_api_key, field_list, state_fips, county_fips, tract)
                else:
                    url = "http://api.census.gov/data/%s?key=%s&get=%s&in=state:%s+county:%s+tract:%s&for=blockgroup:%s" \
                        % (census_table, census_api_key, field_list, state_fips, county_fips, tract, bg_num)
                data_from_api = json.load(urlopen(url))
                for i, (fieldname, datatype, sum_mode) in enumerate(census_fields[census_table]):
                    v = data_from_api[1][i]
                    if v is not None: v = datatype(v)
                    census_data[id][fieldname] = v

    # Clear out existing data.
    for ward in output.values():
        for anc in ward["ancs"].values():
            anc["census"] = { "by-blockgroup": { }, "by-tract": { } }
            for smd in anc["smds"].values():
                smd["census"] = { "by-blockgroup": { }, "by-tract": { } }

    # Estimate values for the ANCs and SMDs as a whole.
    for division1 in ("smd", "anc"):
        for division2 in ("tract", "blockgroup"):
            dat = json.load(open("data/%s-%s.json" % (division1, division2)))
            for ix in dat:
                # Here's an intersection between an ANC/SMD and a blockgroup/tract.

                # Get the dict that represents the ANC or SMD's census info.
                ward = ix[division1]["id"][0]
                anc = ix[division1]["id"][1]
                if division1 == "anc":
                    feature = output[ward]["ancs"][anc]
                else:
                    smd = ix[division1]["id"][2:]
                    feature = output[ward]["ancs"][anc]["smds"][smd]
                feature = feature["census"]["by-" + division2]

                # Get the id of the blockgroup or tract.
                census_id = ix[division2]["id"]
                #if census_id not in census_data: continue # only for testing

                # Estimate each field for the ANC/SND as a whole.
                for census_table in census_fields:
                    for fieldname, datatype, summode in census_fields[census_table]:
                        if summode == "count":
                            # This value may not available from the Census (some blockgroup ACS data) so
                            # mark the feature as not-computable.
                            if census_data[census_id][fieldname] is None:
                                feature[fieldname] = "missing-data"
                                continue
                            if feature.get(fieldname) == "missing-data":
                                # Already marked this field is non-computable because data is missing?
                                continue

                            # This field is a count, so we estimate the whole by adding the
                            # field values weighted by the ratio of the intersection area to
                            # the area of the blockgroup or tract.
                            feature.setdefault(fieldname, { "value": 0, "type": summode })
                            feature[fieldname]["value"] += census_data[census_id][fieldname] * ix[division2]["ratio"]
                        elif summode == "median":
                            # For medians, we take the average across all of the intersections
                            # weighted by the population in each intersction.
                            feature.setdefault(fieldname, { "value": 0.0, "type": summode, "weight": 0.0, "missing_weight": 0.0 })
                            w = census_data[census_id]["B01003_001E"] * ix[division2]["ratio"]

                            # This value may not available from the Census (some blockgroup ACS data). It seems
                            # like even tracts are missing some of these values, but we want to estimate as
                            # best as possible so we'll estimate from those tracts where values exist, and we'll
                            # record the proportion of the population in this ANC/SMD that did not contribute
                            # to the estimate.
                            if census_data[census_id][fieldname] is None:
                                feature[fieldname]["missing_weight"] += w
                                continue

                            feature[fieldname]["value"] += census_data[census_id][fieldname] * w
                            feature[fieldname]["weight"] += w

    # Finish up.
    def clean_up(f):
        # Prefer blockgroup statistics if available.
        # Round some values.
        # For medians, divide by the total weight.
        for division in ("tract", "blockgroup"):
            for k, v in list(f["by-" + division].items()):
                if v == "missing-data": continue

                if v["type"] == "count":
                    f[k] = v
                    f[k]["source"] = division
                    v["value"] = int(round(v["value"]))
                elif v["type"] == "median" and v["weight"] > 0:
                    # Skip this if we're missing more data as a blockgroup than as a tract,
                    # or if we're just missing a lot of data (more than 33%).
                    v["missing_pct"] = v["missing_weight"] / (v["weight"] + v["missing_weight"])
                    if v["missing_pct"] > .33 or (k in f and f[k]["missing_pct"] < v["missing_pct"]): continue

                    f[k] = v
                    f[k]["source"] = division
                    v["value"] = round(v["value"] / v["weight"])
                    del v["weight"]
                    del v["missing_weight"]
                del v["type"]
            del f["by-" + division]

    for ward in output.values():
        for anc in ward["ancs"].values():
            clean_up(anc["census"])
            for smd in anc["smds"].values():
                clean_up(smd["census"])

def add_census_data_analysis(output):
    # Compute vacant home %, new resident %, population density.
    for ward in output.values():
        for anc in ward["ancs"].values():
            anc["census"]["H0050001_PCT"] = { "value": int(round(100.0 * anc["census"]["H0050001"]["value"] / anc["census"]["H0040001"]["value"])) }
            anc["census"]["B07001_001E_PCT"] = { "value": int(round(100.0 * (anc["census"]["B07001_065E"]["value"] + anc["census"]["B07001_081E"]["value"]) / anc["census"]["B07001_001E"]["value"])) }
            anc["census"]["POP_DENSITY"] = { "value": int(round(anc["census"]["P0010001"]["value"] / anc["area"] * 2589990.0)) } # pop per sq mi

if __name__ == "__main__":

    # Should we process this selective update? Yes if:
    #       * no command line arguments were given (i.e. process all)
    #       * --reset was specified (must process all)
    #       * --argname was specified
    def should(argname):
        return len(sys.argv) == 1 or "--reset" in sys.argv or ("--"+argname) in sys.argv

    if not os.path.exists("credentials.py"):
        print("Please provide your census api key> ")
        census_api_key = getpass.getpass("census api key> ")
    else:
        exec(compile(open("credentials.py").read(), "credentials.py", 'exec'))

    ## if the anc json exists then open it for reader
    ## otherwise grab the base data
    if os.path.exists(data_dir + 'ancs.json'):
        anc_json = json.load(open(data_dir + 'ancs.json'), object_pairs_hook=OrderedDict)
    else:
        if not "base" in sys.argv:
            anc_json = OrderedDict()
            sys.argv.append("base")

    ## Lets pars the passed arguments
    if should("base"): add_base_data(anc_json)

    if should("terms"): add_term_data(output)
    if should("gis"): add_geographic_data(output)
    if should("neighborhoods"): add_neighborhood_data(output)
    if should("census"): add_census_data(output)
    if should("census") or should("census-analysis"): add_census_data_analysis(output)
    if should("abra"): add_abra_data(output)
    if should("building"): add_building_permit_data(output)
    if should("311"): add_311_data(output)
    # Output.
    anc_json = json.dumps(anc_json, indent=True, ensure_ascii=False, sort_keys=("--reset" in sys.argv))

    # for new Django-backed site
    with open(data_dir + 'ancs.json', "w") as f:
                f.write(anc_json)
