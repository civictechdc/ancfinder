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
  if not os.path.exists("get_googledoc_creds.py"):
    print("This program downloads our public Google Doc with Ward/ANC/SMD information.")
    print("But we need your Google login info to get it...")
    email = input("google account email> ")
    password = getpass.getpass("google account password> ")
  else:
    # Store your personal credentials in this file if you don't want
    # to type it in.
    exec(compile(open("get_googledoc_creds.py").read(), "get_googledoc_creds.py", 'exec'))
    
  # Create Google Documents client and download the spreadsheet as a CSV for each worksheet.
  spreadsheet_id = "0AsuPWK1wtxNfdGdyVWU4Z3J3X3g3RzVyVWJ1Rkd4dXc" # our spreadsheet
  gs = GoogleDocsClient(email, password)
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

def add_geographic_data(output):
  # Add ANC/SMD geographic extents (bounding box) from the GIS server.
  for ward in list(output.values()):
    for anc in list(ward["ancs"].values()):
      anc["bounds"] = json.load(urlopen("http://gis.govtrack.us/boundaries/dc-anc-2013/" + anc["anc"].lower()))["extent"]
      for smd in list(anc["smds"].values()):
        smd["bounds"] = json.load(urlopen("http://gis.govtrack.us/boundaries/dc-smd-2013/" + smd["smd"].lower()))["extent"]

def add_neighborhood_data(output):
  # Add intersections between ANCs/SMDs and neighborhoods and Census block groups.
  for division in ("neighborhood", "blockgroup"):
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
        feature["map"][division].append({
          "name": ix[division]["name"],
          "part-of-" + anc_smd: ix[anc_smd]["ratio"],
          "part-of-" + division: ix[division]["ratio"],
        })

if __name__ == "__main__":
  output = get_base_data()
  add_scraperwiki_data(output)
  add_geographic_data(output)
  add_neighborhood_data(output)
  
  #output = json.load(open("ancbrigadesite/static/ancs.json"))
  #add_neighborhood_data(output)

  # Output.
  output = json.dumps(output, indent=True, ensure_ascii=False, sort_keys=True)
  
  ## for old static file site
  #with open("www/ancs.jsonp", "w") as f:
  #	  f.write("anc_data = ")
  #	  f.write(output)

  # for new Django-backed site
  with open("ancbrigadesite/static/ancs.json", "w") as f:
  	  f.write(output)
  	  
