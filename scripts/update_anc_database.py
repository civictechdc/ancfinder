#!/usr/bin/python3

import sys, os.path, csv, json, re, subprocess
import urllib.request, urllib.parse, urllib.error, io
import getpass
from collections import OrderedDict

anc_json_filename = os.environ.get('STATIC_ROOT', 'static') + '/ancs.json'

# from cspickert, https://gist.github.com/cspickert/1650271
class GoogleDocsClient(object):
    def __init__(self, email, password):
        super(GoogleDocsClient, self).__init__()
        self.email = email
        self.password = password
    
    def _get_auth_token(self, email, password, source, service):
        url = "https://www.google.com/accounts/ClientLogin"
        params = {
            "Email": email, "Passwd": password,
            "service": service,
            "accountType": "HOSTED_OR_GOOGLE",
            "source": source
        }
        req = urllib.request.Request(url, urllib.parse.urlencode(params).encode("utf8"))
        return re.findall(br"Auth=(.*)", urllib.request.urlopen(req).read())[0]
    
    def get_auth_token(self):
        source = type(self).__name__
        return self._get_auth_token(self.email, self.password, source, service="wise")
    
    def download(self, spreadsheet, gid, format="csv"):
        url_format = "https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&exportFormat=%s&gid=%i"
        headers = {
            b"Authorization": b"GoogleLogin auth=" + self.get_auth_token(),
            b"GData-Version": b"3.0"
        }
        req = urllib.request.Request(url_format % (spreadsheet, format, gid), headers=headers)
        return io.TextIOWrapper(urllib.request.urlopen(req), encoding="utf8")

def urlopen(url):
    # Opens a URL and decodes its content assuming UTF-8; returns a stream.
    data = urllib.request.urlopen(url)
    return io.TextIOWrapper(data, encoding="utf8")

def csv_file_to_dict(csv_file):
    return list(csv.DictReader(csv_file))

def get_base_data():
    # This function initializes an empty JSON file with base data.
    # We don't normally use this function since we try to update
    # data in place selectively, because it's a lot faster than
    # collecting everything from scratch.

    print("fetching Google spreadsheet to create base data")

    # Create Google Documents client and download the spreadsheet as a CSV for each worksheet.
    spreadsheet_id = "0AsuPWK1wtxNfdGdyVWU4Z3J3X3g3RzVyVWJ1Rkd4dXc" # our spreadsheet
    gs = GoogleDocsClient(google_email, google_password)
    wards = csv_file_to_dict(gs.download(spreadsheet_id, 1)) # second argument is the worksheet ID
    ancs = csv_file_to_dict(gs.download(spreadsheet_id, 2))
    smds = csv_file_to_dict(gs.download(spreadsheet_id, 0))
            
    output = OrderedDict()
    for ward in wards:
        w = OrderedDict()
        output[ward["Ward"]] = w
        w["ward"] = int(ward["Ward"])
        w["ancs"] = OrderedDict()
    
    for anc in ancs:
        a = OrderedDict()
        output[ anc["ANC"][0] ]["ancs"][ anc["ANC"][1] ] = a
        a["anc"] = anc["ANC"][0:2]
        a["anc_letter"] = anc["ANC"][1]
        a["smds"] = OrderedDict()
        a["committees"] = OrderedDict()

    for smd in smds:
        s = OrderedDict()
        output[ smd["smd"][0] ]["ancs"][ smd["smd"][1] ]["smds"][ smd["smd"][2:] ] = s
        s["anc"] = smd["smd"][0:2]
        s["smd"] = smd["smd"]
        s["smd_number"] = smd["smd"][2:]
        s["ward"] = smd["smd"][0]

    return output
    
def add_scraper_data(output):
    print("adding scraped commissioner data")
    # additional information about ANC commissioners
    scraped = json.loads(open('data/scraped-anc.json').read())
    for rec in scraped:
        smd = rec
        for entry in scraped[rec]:
            output[smd[0]]["ancs"][smd[1]]["smds"][smd[2:]][entry] = scraped[rec][entry]

def add_googledoc_data(output):
    print("adding Google spreadsheet data")
    scraped = json.loads(open('data/scraped-anc.json').read())

    # Don't ever run this without also running the scraperwiki
    # data because scraperwiki overrides google doc data.
    
    # Create Google Documents client and download the spreadsheet as a CSV for each worksheet.
    spreadsheet_id = "0AsuPWK1wtxNfdGdyVWU4Z3J3X3g3RzVyVWJ1Rkd4dXc" # our spreadsheet
    gs = GoogleDocsClient(google_email, google_password)
    wards = csv_file_to_dict(gs.download(spreadsheet_id, 1)) # second argument is the worksheet ID
    ancs = csv_file_to_dict(gs.download(spreadsheet_id, 2))
    smds = csv_file_to_dict(gs.download(spreadsheet_id, 0))
    committees = csv_file_to_dict(gs.download(spreadsheet_id, 10))
            
    for ward in wards:
        w = output[ward["Ward"]]
        w["description"] = ward["Description"]
    
    for anc in ancs:
        try:
            a = output[ anc["ANC"][0] ]["ancs"][ anc["ANC"][1] ]
        except KeyError:
            raise ValueError(anc["ANC"][0] + " is not an ANC.")
        a["website"] = anc["Website"]
        a["committees"] = OrderedDict() # clear
    
    # Use name from anc.dc.gov to check that we have the right commissioner
    # before overwriting with spreadsheet information
    for smd in smds:
        s = output[ smd["smd"][0] ]["ancs"][ smd["smd"][1] ]["smds"][ smd["smd"][2:] ]
        if scraped[smd["smd"]]["official_name"] == smd["official_name"]:
            s.update(smd)
        if isinstance(s.get("Position"), str):
            # migrate this field to a list; once we're all migrated we should
            # move this conversion out of this if block and up to where we
            # update s.
            # We encode multiple positions using double asterisks in the spreadsheet.
            if s["Position"].strip() == "":
                s["Position"] = [] # empty list
            else:
                s["Position"] = s["Position"].split("**")

    for cmte in committees:
        c = OrderedDict()
        output[ cmte["ANC"][0] ]["ancs"][ cmte["ANC"][1] ]["committees"][ cmte["committee"]] = c
        c["committee"] = cmte["committee"]
        c["meetings"] = cmte["meetings"]
        c["chair"] = cmte["chair"]
        c["chair_email"] = cmte["chair email"]
        c["purpose"] = cmte["purpose"]
                    
def add_term_data(output):
    print("adding commissioner term information")
    # Number of terms served by current ANC commissioner
    term_data = csv.reader(open('data/anc-terms.csv'), delimiter=',')
    con_data = csv.reader(open('data/anc-contestation.csv'), delimiter=',')
    for rec in term_data:
        smd = rec[1]
        output[smd[0]]["ancs"][smd[1]]["smds"][smd[2:]]["terms"] = rec[5]
    for rec in con_data:
        smd = rec[0]
        output[smd[0]]["ancs"][smd[1]]["smds"][smd[2:]]["contestation"] = rec[1]
        
def add_abra_data(output):
    print("adding liquor license information")
    # Number of liquor licenses in each ANC and SMD
    abra_data = json.loads(open('data/abra-licenses.json').read())
    for rec in abra_data:
        anc = rec
        output[anc[0]]["ancs"][anc[1]]["census"]["liquor_licenses"] = { "value": abra_data[rec]['number'] }
        for rec in abra_data[rec]['smds']:
                smd = rec
                output[smd[0]]["ancs"][smd[1]]["smds"][smd[2:]]["census"]["liquor_licenses"] = { "value": abra_data[rec[:2]]['smds'][rec]['number'] }

def add_building_permit_data(output):
    print("adding building permit information")
    # Number of building permits in each ANC and SMD
    smd_building_permits = csv.reader(open('data/smd-building-permits.csv'), delimiter=',')
    anc_building_permits = csv.reader(open('data/anc-building-permits.csv'), delimiter=',')
    for rec in smd_building_permits:
        smd = rec[0]
        output[smd[0]]["ancs"][smd[1]]["smds"][smd[2:]]["census"]["building_permits"] = { "value": int(rec[1]) }
    for rec in anc_building_permits:
        anc = rec[0]
        output[anc[0]]["ancs"][anc[1]]["census"]["building_permits"] = { "value": int(rec[1]) }

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
    if not os.path.exists("credentials.py"):
        print("This program downloads our public Google Doc with Ward/ANC/SMD information.")
        print("But we need your Google login and Census API key info to get it...")
        google_email = input("google account email> ")
        google_password = getpass.getpass("google account password> ")
        census_api_key = getpass.getpass("census api key> ")
    else:
        # Or create a file named "credentials.py" and put in
        # it your Google credentials and Census API key (see the README).
        exec(compile(open("credentials.py").read(), "credentials.py", 'exec'))
        
    
    if "--reset" in sys.argv:
        # Re-create file from scratch.
        output = get_base_data()
    else:
        # Update file in place.
        output = json.load(open(anc_json_filename), object_pairs_hook=OrderedDict)

    if "--update" in sys.argv:
        subprocess.call(['python', 'update_abra.py', '&&', 'python', 'update_311.py'])

    def should(argname):
        # Should we process this selective update? Yes if:
        #       * no command line arguments were given (i.e. process all)
        #       * --reset was specified (must process all)
        #       * --argname was specified
        return len(sys.argv) == 1 or "--reset" in sys.argv or ("--"+argname) in sys.argv

    if should("base"):
        # always do this together
        add_scraper_data(output)
        add_googledoc_data(output)
    if should("terms"): add_term_data(output)
    if should("gis"): add_geographic_data(output)
    if should("neighborhoods"): add_neighborhood_data(output)
    if should("census"): add_census_data(output)
    if should("census") or should("census-analysis"): add_census_data_analysis(output)
    if should("abra"): add_abra_data(output)
    if should("building"): add_building_permit_data(output)
    if should("311"): add_311_data(output)
    
    # Output.
    output = json.dumps(output, indent=True, ensure_ascii=False, sort_keys=("--reset" in sys.argv))
    
    # for new Django-backed site
    with open(anc_json_filename, "w") as f:
                f.write(output)
                
