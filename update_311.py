import json, urllib2, os, errno, requests

# Open/create file, deleting info already in it so that we can make fresh info
file_name = open('data/311.json', 'w')
issues = []
working = {'issues':issues}
data = {}

# Request info from SeeClickFix API
url = 'https://seeclickfix.com/api/v2/issues?place_url=district-of-columbia&&after=2013-08-21T00:00:0000&page=1&per_page=100'
response = urllib2.urlopen(url)
info = json.load(response)
endpoint = info['metadata']['pagination']['pages']

page = 1
while page < endpoint:
    url = 'https://seeclickfix.com/api/v2/issues?place_url=district-of-columbia&&after=2013-08-21T00:00:0000&page='+str(page)+'&per_page=100'
    response = urllib2.urlopen(url)
    info = json.load(response)
    working['issues'] += info['issues']
    page +=1

#Locate in ANC using lat/long coordinates, then calculate the totals

for issue in working['issues']:
    url = 'http://gis.govtrack.us/boundaries/dc-smd-2013/?contains='+str(issue['lat'])+','+str(issue['lng'])
    request = requests.get(url)
    info = json.loads(request.text)
    print issue
    try:
        smd = info['objects'][0]['external_id']
        anc = info['objects'][0]['external_id'][:2]
        variety = issue['summary']
        print smd, issue['lng'], issue['lat'], variety
        if anc in data:
            if smd in data[anc]['smds']:
                data[anc]['smds'][smd]['total'] += 1
            else:
                data[anc]['smds'][smd] = {}
                data[anc]['smds'][smd]['total'] = 1
                data[anc]['smds'][smd]['types'] = {}
            data[anc]['total'] += 1
        else:
            data[anc] = {}
            data[anc]['total'] = 1
            data[anc]['types'] = {}
            data[anc]['smds'] = {}
            data[anc]['smds'][smd] = {}
            data[anc]['smds'][smd]['total'] = 1
            data[anc]['smds'][smd]['types'] = {}
        if variety in data[anc]['types']:
            data[anc]['types'][variety] += 1
            if variety in data[anc]['smds'][smd]['types']:
                data[anc]['smds'][smd]['types'][variety] += 1
            else:
                data[anc]['smds'][smd]['types'][variety] = 1
        else:
            data[anc]['types'][variety] = 1
            data[anc]['smds'][smd]['types'][variety] = 1
    except IndexError:
        continue
    
#    data[anc]['smds'][smd]['locations'].append(location)
#    data[anc]['locations'].append(location)

# Save the JSON file

with open('data/311.json', 'w') as output:
	json.dump(data, output, sort_keys=True, indent=4)

