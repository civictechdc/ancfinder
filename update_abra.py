import requests, zipfile, subprocess, csv, json

update_data_file = 'http://dcatlas.dcgis.dc.gov/catalog/download.asp?downloadID=969&downloadTYPE=ESRI'
zip_filename = 'abra.zip'

# Gather the file
zip_request = requests.get('http://dcatlas.dcgis.dc.gov/catalog/download.asp?downloadID=969&downloadTYPE=ESRI', stream=True)

# Download the file and save locally
with open(zip_filename, 'wb') as zip_file:
    for chunk in zip_request.iter_content(chunk_size=1024):
        if chunk:
            zip_file.write(chunk)
            zip_file.flush()    

# Unzip the locally saved file
zipfile.main(['-e', zip_filename, 'abra'])

# Remove existing ABRA download (OGR fails otherwise)
subprocess.call('rm data/abra.csv', shell=True)

# Run OGR on the downloaded ESRI file
subprocess.call('ogr2ogr -f "CSV" data/abra.csv abra', shell=True)

# Cut out coordinates and convert to Lat/Long instead of Maryland State Plane NAD83
abra_read = csv.reader(open('data/abra.csv'), delimiter=',')
abra_write = csv.writer(open('data/abra-nad83.csv', 'w'), delimiter=' ')

for rec in abra_read:
    if rec[7] == 'X':
	continue
    else:
	output = [rec[7]] + [rec[8]]
	abra_write.writerow(output)

subprocess.call('gdaltransform -s_srs EPSG:26985 -t_srs EPSG:4326 < data/abra-nad83.csv > data/abra-latlong.csv', shell=True)

# Check coordinates against Govtrack GIS and sort into CSV
abra_latlong = csv.reader(open('data/abra-latlong.csv'), delimiter=' ')

licenses = {}

for rec in abra_latlong:
    location = rec[1] + ',' + rec[0]
    url = 'http://gis.govtrack.us/boundaries/dc-smd-2013/?contains=' + location
    request = requests.get(url)
    data = json.loads(request.text)
    smd = data['objects'][0]['external_id']
    anc = data['objects'][0]['external_id'][:2]
    print smd, rec[0], rec[1]
    if anc in licenses:
        if smd in licenses[anc]['smds']:
            licenses[anc]['smds'][smd]['number'] += 1
        else:
            licenses[anc]['smds'][smd] = {}
            licenses[anc]['smds'][smd]['locations'] = []
            licenses[anc]['smds'][smd]['number'] = 1
        licenses[anc]['number'] += 1
    else:
        licenses[anc] = {}
        licenses[anc]['locations'] = []
        licenses[anc]['number'] = 1
        licenses[anc]['smds'] = {}
        licenses[anc]['smds'][smd] = {}
        licenses[anc]['smds'][smd]['locations'] = []
        licenses[anc]['smds'][smd]['number'] = 1
    licenses[anc]['smds'][smd]['locations'].append(location)
    licenses[anc]['locations'].append(location)

with open('data/abra-licenses.json', 'w') as output:
    json.dump(licenses, output, sort_keys=True, indent=4)


# Clean up extra files
subprocess.call('rm -rf abra abra.zip data/abra-nad83.csv data/abra-latlong.csv', shell=True)
