import requests, zipfile, subprocess

update_data_file = 'http://data.octo.dc.gov/feeds/crime_incidents/archive/crime_incidents_2013_CSV.zip'
zip_filename = 'crime_incidents_2013_CSV.zip'

# Gather the file
zip_request = requests.get('http://data.octo.dc.gov/feeds/crime_incidents/archive/crime_incidents_2013_CSV.zip', stream=True)

# Download the file and save locally
with open(zip_filename, 'wb') as zip_file:
    for chunk in zip_request.iter_content(chunk_size=1024):
        if chunk:
            zip_file.write(chunk)
            zip_file.flush()    

# Unzip the locally saved file
zipfile.main(['-e', zip_filename, 'data'])

# Clean up downloaded file
subprocess.call('rm crime_incidents_2013_CSV.zip', shell=True)
