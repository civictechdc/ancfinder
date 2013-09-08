#!/usr/bin/python3

import csv
import json
import re, urllib.request, urllib.parse, urllib.error, os.path, io
import getpass
from collections import OrderedDict

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
    w["description"] = ward["Description"]
    w["ancs"] = OrderedDict()
  
  for anc in ancs:
    a = OrderedDict()
    output[ anc["ANC"][0] ]["ancs"][ anc["ANC"][1] ] = a
    a["anc"] = anc["ANC"][0:2]
    a["anc_letter"] = anc["ANC"][1]
    a["website"] = anc["Website"]
    a["smds"] = OrderedDict()

  for smd in smds:
    output[ smd["smd"][0] ]["ancs"][ smd["smd"][1] ]["smds"][ smd["smd"][2:] ] = smd
    smd["smd_number"] = smd["smd"][2:]
    
  return output
  
def add_scraperwiki_data(output):
  # additional information about ANC commissioners
  sw_data = urlopen("https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=json&name=dc_anc_commissioner_info_from_official_anc_website&query=select+*+from+`swdata`&apikey=")
  for rec in json.load(sw_data):
    smd = rec["smd"].strip()
    for k, v in list(rec.items()):
      if v == None: continue
      output[smd[0]]["ancs"][smd[1]]["smds"][smd[2:]][k] = v.strip()
      
def add_term_data(output):
  # Number of terms served by current ANC commissioner
  term_data = csv.reader(open('data/anc-terms.csv'), delimiter=',')
  for rec in term_data:
    smd = rec[1]
    output[smd[0]]["ancs"][smd[1]]["smds"][smd[2:]]["terms"] = rec[5]

def add_geographic_data(output):
  # Add ANC/SMD geographic extents (bounding box) from the GIS server.
  for ward in list(output.values()):
    for anc in list(ward["ancs"].values()):
      anc["bounds"] = json.load(urlopen("http://gis.govtrack.us/boundaries/dc-anc-2013/" + anc["anc"].lower()))["extent"]
      for smd in list(anc["smds"].values()):
        smd["bounds"] = json.load(urlopen("http://gis.govtrack.us/boundaries/dc-smd-2013/" + smd["smd"].lower()))["extent"]

def add_neighborhood_data(output):
  # Add intersections between ANCs/SMDs and neighborhoods and Census block groups.
  
  # First estimate the total population of DC neighborhoods because we'll want
  # to ignore neighborhoods for non-residential areas, because they look really
  # odd when we say ANC 1B contains the Tidal Basin.
  #
  # For each neighborhood, sum the populations of the block groups it intersects with
  # weighted by the proportion of the block group that intersects with the neighborhood.
  hood_population = { }
  for intsect in json.load(open("data/neighborhoods-blockgroups.json")):
    h = intsect["dc-neighborhoods"]["id"]
    tr = intsect["2012-blockgroups"]["id"]
    state_fips, county_fips, tract, bg = tr[0:2], tr[2:5], tr[5:11], tr[11:12]
    if state_fips != "11": continue # not DC
    url = "http://api.census.gov/data/%s?key=%s&get=%s&in=state:%s+county:%s+tract:%s&for=block+group:%s" \
        % ("2010/sf1", census_api_key, "P0010001", state_fips, county_fips, tract, bg)
    census_data = json.load(urlopen(url))
    tract_pop = int(census_data[1][0])
    intsect_pop = tract_pop * intsect["2012-blockgroups"]["ratio"]
    hood_population[h] = hood_population.get(h, 0) + intsect_pop
    
  # Bring in the pre-computed intersection data.
  for division in ("neighborhood", "blockgroup", "tract"):
    # clear out existing data
    for ward in output.values():
      for anc in ward["ancs"].values():
        anc.setdefault("map", {})[division] = []
        for smd in anc["smds"].values():
          smd.setdefault("map", {})[division] = []
    
    # set data
    for anc_smd in ("anc", "smd"):
      dat = json.load(open("data/%s-%s.json" % (anc_smd, division)))
      for ix in dat:
        ward = ix[anc_smd]["id"][0]
        anc = ix[anc_smd]["id"][1]
        smd = ix[anc_smd]["id"][2:]
        if anc_smd == "anc":
          feature = output[ward]["ancs"][anc]
        else:
          feature = output[ward]["ancs"][anc]["smds"][smd]
          
        f = {
          "name": ix[division]["name"],
          "part-of-" + anc_smd: ix[anc_smd]["ratio"],
          "part-of-" + division: ix[division]["ratio"],
        }
        
        if division == "neighborhood":
          # Esimate the population of this neighborhood intersection by multiplying our
          # earlier estimate of the neighborhood's population by the portion of the
          # neighborhood that falls within this ANC/SMD.
          f["population"] = hood_population[ix[division]["id"]] * ix[division]["ratio"] 
        
        if division == "tract":
          # Query the Census API for information about this tract.
          state_fips, county_fips, tract = ix[division]["id"][0:2], ix[division]["id"][2:5], ix[division]["id"][5:11]
          
          # Remove degenerate intersections with Virginia and Maryland block groups.
          if state_fips != "11" or county_fips != "001": continue
              
          # Query the Census API for population information for this tract.
          census_fields = {
              "2010/sf1": [
                  "P0010001", # Total Population
                  "P0180001", # Households
                  "P0180002", # Family Households
                  "H0040001", # Occupied Housing Units
                  "H0050001", # Vacant Housing Units
              ],
              "2011/acs5": [
                  "B01002_001E", # Median Age
                  "B07001_001E", # Geographic Mobility in the Past Year Total Population
                  "B07001_017E", # .... Same House One Year Ago
                  "B07001_033E", # .... Moved Within Same County
                  "B07001_065E", # .... Moved From Different State
                  "B07001_081E", # .... Moved From Abroad
                  "B19019_001E", # Median Household Income
#                  "B16002_001E", # No One Age 14+ in Household Speaks English
#                  "B99151_001E", # Imputation of Educational Attainment for Age 25+
              ],
          }
          for census_table in census_fields:
              url = "http://api.census.gov/data/%s?key=%s&get=%s&in=state:%s+county:%s&for=tract:%s" \
                  % (census_table, census_api_key, ",".join(census_fields[census_table]), state_fips, county_fips, tract)
              census_data = json.load(urlopen(url))
              for i, k in enumerate(census_fields[census_table]):
                  f[k] = census_data[1][i]

        feature["map"][division].append(f)

if __name__ == "__main__":
  if not os.path.exists("update_anc_database_creds.py"):
    print("This program downloads our public Google Doc with Ward/ANC/SMD information.")
    print("But we need your Google login info to get it...")
    google_email = input("google account email> ")
    google_password = getpass.getpass("google account password> ")
    census_api_key = getpass.getpass("census api key> ")
  else:
    # Store your personal credentials in this file if you don't want
    # to type it in.
    exec(compile(open("update_anc_database_creds.py").read(), "update_anc_database_creds.py", 'exec'))
    
    
  output = get_base_data()
  add_scraperwiki_data(output)
  add_term_data(output)
  add_geographic_data(output)
  add_neighborhood_data(output)
  
  #output = json.load(open("ancbrigadesite/static/ancs.json"))
  #add_neighborhood_data(output)

  # Output.
  output = json.dumps(output, indent=True, ensure_ascii=False, sort_keys=True)
  
  ## for old static file site
  #with open("www/ancs.jsonp", "w") as f:
  #      f.write("anc_data = ")
  #      f.write(output)

  # for new Django-backed site
  with open("ancbrigadesite/static/ancs.json", "w") as f:
        f.write(output)
        
