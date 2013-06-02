#!/usr/bin/python

import csv
import json
import re, urllib, urllib2, os.path
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
    req = urllib2.Request(url, urllib.urlencode(params))
    return re.findall(r"Auth=(.*)", urllib2.urlopen(req).read())[0]
  
  def get_auth_token(self):
    source = type(self).__name__
    return self._get_auth_token(self.email, self.password, source, service="wise")
  
  def download(self, spreadsheet, gid, format="csv"):
    url_format = "https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=%s&exportFormat=%s&gid=%i"
    headers = {
      "Authorization": "GoogleLogin auth=" + self.get_auth_token(),
      "GData-Version": "3.0"
    }
    req = urllib2.Request(url_format % (spreadsheet, format, gid), headers=headers)
    return urllib2.urlopen(req)

def csv_file_to_dict(csv_file):
  return list(csv.DictReader(csv_file))

if __name__ == "__main__":
  if not os.path.exists("get_googledoc_creds.py"):
    print "This program downloads our public Google Doc with Ward/ANC/SMD information."
    print "But we need your Google login info to get it..."
    email = raw_input("google account email> ")
    password = getpass.getpass("google account password> ")
  else:
    # Store your personal credentials in this file if you don't want
    # to type it in.
    execfile("get_googledoc_creds.py")
    
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
    s = OrderedDict()
    output[ smd["SMD"][0] ]["ancs"][ smd["SMD"][1] ]["smds"][ smd["SMD"][2:] ] = s
    s["smd"] = smd["SMD"]
    s["smd_number"] = smd["SMD"][2:]
    del smd["SMD"]
    s.update(smd)
    
  # Now add scraped info from scraperwiki.
  
  for rec in json.load(urllib.urlopen("https://api.scraperwiki.com/api/1.0/datastore/sqlite?format=json&name=dc_anc_commissioners&query=select+*+from+`swdata`&apikey=")):
    smd = rec["SMD"].strip()
    for k, v in rec.items():
      if v == None: continue
      output[smd[0]]["ancs"][smd[1]]["smds"][smd[2:]][k] = v.strip()

  # Add quarterly financial report URLs from Luke's CSV file.
  # Warning: Historical information may not correspond to current ANCs if they
  # were renamed after 2012 redistricting.
  for rec in csv.DictReader(urllib.urlopen("https://s3.amazonaws.com/dcanc/index.csv")):
    try:
      anc = output[rec["ANC"][0]]["ancs"][rec["ANC"][1]]
    except KeyError:
      # ANC no longer exists after redistricting.
      continue
    anc.setdefault("quarterly_financial_report_pdf_url", []).append(
      {
        "fiscal_year": rec["FY"],
        "quarter": rec["quarter"],
        "url": "https://s3.amazonaws.com/dcanc/" + rec["filename"],
        "size": rec["size"],
        "pages": rec["pages,"],
      })
    
  # Add ANC/SMD geographic extents (bounding box) from the GIS server.
  for ward in output.values():
    for anc in ward["ancs"].values():
      anc["bounds"] = json.load(urllib.urlopen("http://gis.govtrack.us/boundaries/dc-anc-2013/" + anc["anc"].lower()))["extent"]
      for smd in anc["smds"].values():
      	  smd["bounds"] = json.load(urllib.urlopen("http://gis.govtrack.us/boundaries/dc-smd-2013/" + smd["smd"].lower()))["extent"]

  # Output.
  print json.dumps(output, indent=True, ensure_ascii=False).encode("utf8")
  
