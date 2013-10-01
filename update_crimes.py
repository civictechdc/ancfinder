import csv, urllib2, zipfile, StringIO

zipstream = urllib2.urlopen("http://data.octo.dc.gov/feeds/crime_incidents/archive/crime_incidents_2013_CSV.zip")
buf = StringIO.StringIO()
buf.write(zipstream.read())
buf.seek(0)

zip = zipfile.ZipFile(buf)
csvfile = csv.reader(zip.open("the_csv.csv"))
