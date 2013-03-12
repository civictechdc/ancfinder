#!/usr/bin/python

import csv
import json

# Read in from Google Docs.  See: http://gdata-python-client.googlecode.com/hg/pydocs/gdata.docs.service.html

# Open the CSV  
csvFile = open( 'ANCList.csv', 'rU' )  
reader = csv.DictReader( csvFile, fieldnames = ( "anc","name","emailAddress","mailingAddress","website","screenshotURL","meetingLocation","meetingDate" ))
# Skip the header
reader.next()

# Parse the CSV into JSON  
out = json.dumps( [ row for row in reader ] )  

# Save the JSON  
jsonFile = open( 'ANCList.json', 'w')  
jsonFile.write(out)


