#!/usr/bin/python

import csv
import json
import re, urllib, urllib2
import getpass
 
# Spreadsheet and Client classes from cspickert, https://gist.github.com/cspickert/1650271
class Spreadsheet(object):
  def __init__(self, key):
    super(Spreadsheet, self).__init__()
    self.key = key
 
class Client(object):
  def __init__(self, email, password):
    super(Client, self).__init__()
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
    req = urllib2.Request(url_format % (spreadsheet.key, format, gid), headers=headers)
    return urllib2.urlopen(req)

def csv_file_to_json(csv_file):
  #csvFile = open( file_path, 'rU' )  
  reader = csv.DictReader( csv_file, fieldnames = ( "anc","name","emailAddress","mailingAddress","website","screenshotURL","meetingLocation","meetingDate" ))
  # Skip the header
  reader.next()

  # Parse the CSV into JSON  
  out = json.dumps( [ row for row in reader ] )  

  # Save the JSON  
  jsonFile = open( 'ANCList.json', 'w')  
  jsonFile.write(out)

if __name__ == "__main__":
  email = "" # (your email here)
  password = getpass.getpass()
  spreadsheet_id = "0AsuPWK1wtxNfdGdyVWU4Z3J3X3g3RzVyVWJ1Rkd4dXc" # DC ANC Unearthing Spreadsheet ID

  # Create client and spreadsheet objects
  gs = Client(email, password)
  ss = Spreadsheet(spreadsheet_id)

  # Request a file-like object containing the spreadsheet's contents
  csv_file = gs.download(ss,2) # 2nd param is the worksheet id, 1=first worksheet, 2=second worksheet, etc.
  csv_file_to_json(csv_file)
