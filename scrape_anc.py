import urllib2, csv, re, json
from bs4 import BeautifulSoup

# Open/create file, deleting old data if it exists
file_name = open('data/scraped-anc.json', 'w')
data = {}

ANC = ['1A', '1B', '1C', '1D', '2A', '2B', '2C', '2D', '2E', '2F', '3B', '3C', '3D', '3E', '3F', '3G', '4A', '4B', '4C', '4D', '5A', '5B', '5C', '5D', '5E', '6A', '6B', '6C', '6D', '6E', '7B', '7C', '7D', '7E', '7F', '8A', '8B', '8C', '8D', '8E']

for anc in ANC:
    url = 'http://anc.dc.gov/page/advisory-neighborhood-commission-' + anc
    soup = BeautifulSoup(urllib2.urlopen(url))
    tag_extract = ['br', 'i', 'sub']
    for tag in tag_extract:
        for d in soup.find_all(tag):
            d.extract()
    info = soup('tbody', limit=3)[2]
    tr = info.find_all('tr', recursive=False)
    for row in tr:
        td = row.find_all('td', recursive=False)
        smd = td[0].text.strip()
        data[smd] = {}
        name = td[1].text.strip().split()
        data[smd]['First_Name'] = name[0]
        data[smd]['Middle_Name'] = ''
        data[smd]['Nickname'] = ''
        if name[len(name) - 1] in ['Jr', 'Jr.', 'Sr.', 'Sr', 'I', 'II', 'III']:
            data[smd]['Suffix'] = name[len(name) - 1]
            data[smd]['Last_Name'] = name[len(name) - 2]
        else:
            data[smd]['Suffix'] = ''
            data[smd]['Last_Name'] = name[len(name) - 1]
        for word in name[1:len(name) - 1]:    #Nickname or Middle Name?
            if word[0] == '"' or word[0] == '(':
                data[smd]['Nickname'] = word
            else: 
                if word != data[smd]['Last_Name']:
                    data[smd]['Middle_Name'] = word
            if data[smd]['Suffix'] in ['Jr', 'Sr']:
                data[smd]['Suffix'] += '.'
            if (data[smd]['Suffix'] in ['Jr.', 'Sr.', 'I', 'II', 'III']) & (data[smd]['Last_Name'][len(data[smd]['Last_Name']) - 1] != ','):
                data[smd]['Last_Name'] += ','
        data[smd]['Address'] = re.sub("\xa0", " ", re.sub("\s*\n\s*", "; ", td[2].text.strip()))
        phone = td[3].text.strip()
        phone = phone.replace("(202) ", "202-")
        if len(phone) == 8:
            phone = '202-' + phone
        elif len(phone) < 8:
            phone = ''
        data[smd]['Phone'] = phone
        data[smd]['Email'] = td[4].a.text
        print data[smd]

with open('data/scraped-anc.json', 'w') as output:
    json.dump(data, output, sort_keys=True, indent=4)

