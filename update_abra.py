import requests, zipfile, subprocess

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

# Remove existing ABRA file (OGR fails otherwise)
subprocess.call('rm data/abra.geojson', shell=True)

# Run OGR on the downloaded ESRI file
subprocess.call('ogr2ogr -f "GeoJSON" data/abra.geojson abra', shell=True)

# Clean up files
subprocess.call('rm abra.zip', shell=True)
subprocess.call('rm -rf abra', shell=True)


