import requests, zipfile, subprocess

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
