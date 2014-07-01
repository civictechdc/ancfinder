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
        data[smd]['official_name'] = td[1].text.strip()
        name = td[1].text.strip().split()
        data[smd]['first_name'] = name[0]
        data[smd]['middle_name'] = ''
        data[smd]['nickname'] = ''
        if name[len(name) - 1] in ['Jr', 'Jr.', 'Sr.', 'Sr', 'I', 'II', 'III']:
            data[smd]['suffix'] = name[len(name) - 1]
            data[smd]['last_name'] = name[len(name) - 2]
        else:
            data[smd]['suffix'] = ''
            data[smd]['last_name'] = name[len(name) - 1]
        if data[smd]['last_name'] in ['Vacant', 'vacant']:
            data[smd]['last_name'] = ''
        for word in name[1:len(name) - 1]:    #nickname or Middle Name?
            if word[0] == '"' or word[0] == '(':
                data[smd]['nickname'] = word
            else: 
                if word != data[smd]['last_name']:
                    data[smd]['middle_name'] = word
            if data[smd]['suffix'] in ['Jr', 'Sr']:
                data[smd]['suffix'] += '.'
            if (data[smd]['suffix'] in ['Jr.', 'Sr.', 'I', 'II', 'III']) & (data[smd]['last_name'][len(data[smd]['last_name']) - 1] != ','):
                data[smd]['last_name'] += ','
        data[smd]['address'] = re.sub("\xa0", " ", re.sub("\s*\n\s*", "; ", td[2].text.strip()))
        phone = td[3].text.strip()
        phone = phone.replace("(202) ", "202-")
        if len(phone) == 8:
            phone = '202-' + phone
        elif len(phone) < 8:
            phone = ''
        data[smd]['phone'] = phone
        data[smd]['email'] = td[4].a.text
        print data[smd]

with open('data/scraped-anc.json', 'w') as output:
    json.dump(data, output, sort_keys=True, indent=4)

