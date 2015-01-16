import urllib2, csv, re, json
from bs4 import BeautifulSoup

# Open/create file, deleting old data if it exists
file_name = open('data/scraped-anc.json', 'w')
data = {}

ANC = []

base = BeautifulSoup(urllib2.urlopen('http://anc.dc.gov/'))
links = base('div', id='block-domain-conf-domain-main-links')[0].find_all('a')
for link in links:
    if re.search('commission-', link['href']):
        ANC.append(link['href'])


for anc in ANC:
    url = 'http://anc.dc.gov' + anc
    soup = BeautifulSoup(urllib2.urlopen(url))
    tag_extract = ['br', 'i', 'sub']
    for tag in tag_extract:
        for d in soup.find_all(tag):
            d.extract()
    info = soup('tbody', limit=3)[0]
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
        #print data[smd]

with open('data/scraped-anc.json', 'w') as output:
    json.dump(data, output, sort_keys=True, indent=4)
