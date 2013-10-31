import requests, zipfile, subprocess, csv, json

update_data_file = 'http://data.octo.dc.gov/feeds/dcra_building_permits/dcra_building_permits_current_csv.zip'
zip_filename = 'dcra_building_permits_current_csv.zip'

# Gather the file
zip_request = requests.get('http://data.octo.dc.gov/feeds/dcra_building_permits/dcra_building_permits_current_csv.zip', stream=True)

# Download the file and save locally
with open(zip_filename, 'wb') as zip_file:
    for chunk in zip_request.iter_content(chunk_size=1024):
        if chunk:
            zip_file.write(chunk)
            zip_file.flush()    

# Unzip the locally saved file
zipfile.main(['-e', zip_filename, 'data'])

# Clean up downloaded file
subprocess.call('rm dcra_building_permits_current_csv.zip', shell=True)

# Calculate permits in each ANC

permits_read = csv.reader(open('data/dcra_building_permits_current_csv.csv'), delimiter=',')
anc_permits_write = csv.writer(open('data/anc-building-permits.csv', 'w'), delimiter=',')
smd_permits_write = csv.writer(open('data/smd-building-permits.csv', 'w'), delimiter=',')

anc_permits = {}
smd_permits = {}

# The DC CSV does have ANC and SMD data, but it includes SMDs that don't exist, so we need to do it ourselves

for rec in permits_read:
	if rec[26] in ['NONE', 'SMD']:
		continue
	url = "http://gis.govtrack.us/boundaries/dc-smd-2013/?contains=" + rec[18] + "," + rec[19]
	request = requests.get(url)
	data = json.loads(request.text)
	smd = data['objects'][0]['external_id']
	anc = data['objects'][0]['external_id'][:2]
	print smd, rec[20], rec[19]
	if smd in smd_permits:
		smd_permits[smd] += 1
	else:
		smd_permits[smd] = 1
	if anc in anc_permits:
		anc_permits[anc] += 1
	else:
		anc_permits[anc] = 1

for rec in sorted(smd_permits):
	output = [rec] + [smd_permits[rec]]
	smd_permits_write.writerow(output)

for rec in sorted(anc_permits):
	output = [rec] + [anc_permits[rec]]
	anc_permits_write.writerow(output)


