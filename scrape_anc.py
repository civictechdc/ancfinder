import urllib2, lxml, csv, re
from bs4 import BeautifulSoup

scraper_writer = csv.writer(open('data/scraped-anc.csv', 'w'), delimiter=',')
scraper_writer.writerow(['SMD'] + ['First Name'] + ['Middle Name'] + ['Nickname'] + ['Last Name'] + ['Suffix'] + ['Address'] + ['Phone'] + ['Email'])

ANC = ['1A', '1B', '1C', '1D', '2A', '2B', '2C', '2D', '2E', '2F', '3B', '3C', '3D', '3E', '3F', '3G', '4A', '4B', '4C', '4D', '5A', '5B', '5C', '5D', '5E', '6A', '6B', '6C', '6D', '6E', '7B', '7C', '7D', '7E', '7F', '8A', '8B', '8C', '8D'] # + ['8E']

# ANC 8E has a table that is missing elements, so it needs to be done separately. Once DC fixes this, the list should be recombined and the code at the bottom deleted.

def name_parse(name):   #Separates name into proper fields
	records['First Name'] = name[0]
	records['Middle Name'] = ''
	records['Nickname'] = ''
	if name[len(name) - 1] in ['Jr', 'Jr.', 'Sr.', 'Sr', 'I', 'II', 'III']:
		records['Suffix'] = name[len(name) - 1]
		records['Last Name'] = name[len(name) - 2]
	else:
		records['Suffix'] = ''
		records['Last Name'] = name[len(name) - 1]
	for word in name[1:len(name) - 1]:    #Nickname or Middle Name?
		if word[0] == '"' or word[0] == '(':
			records['Nickname'] = word
		else: 
			if word != records['Last Name']:
				records['Middle Name'] = word
		if records['Suffix'] in ['Jr', 'Sr']:
			records['Suffix'] += '.'
		if (records['Suffix'] in ['Jr.', 'Sr.', 'I', 'II', 'III']) & (records['Last Name'][len(records['Last Name']) - 1] != ','):
			records['Last Name'] += ','

def area_coder(phone):    #Adds (202) area code, if necessary
	phone = phone.replace("(202) ", "202-")
	if len(phone) == 8:
		records['Phone'] = '202-' + phone
	elif len(phone) < 8:
		records['Phone'] = ''
	else:
		records['Phone'] = phone

for anc in ANC:
	url = 'http://anc.dc.gov/page/advisory-neighborhood-commission-' + anc
	soup = BeautifulSoup(urllib2.urlopen(url))
	tag_extract = ['br', 'i', 'sub']
	for tag in tag_extract:
	    for d in soup.find_all(tag):
	    	d.extract()
	
	data = soup('tbody', limit=3)[2]
	tr = data.find_all('tr')
	for row in tr:
		td = row.find_all('td')
		records = {}
		records['SMD'] = td[0].text.strip()
		name_parse(td[1].text.encode('utf-8').strip().split())
		records['Address'] = re.sub("\s*\n\s*", "; ", td[2].text.encode('utf-8').strip())
		area_coder(td[3].text.encode('utf-8').strip())
		records['Email'] = td[4].a.text
		print(records)
		scraper_writer.writerow([records['SMD']] + [records['First Name']] + [records['Middle Name']] + [records['Nickname']] + [records['Last Name']] + [records['Suffix']] + [records['Address']] + [records['Phone']] + [records['Email']])

# Add in the final information from broken 8E page

url = 'http://anc.dc.gov/page/advisory-neighborhood-commission-8E'
soup = BeautifulSoup(urllib2.urlopen(url))
for d in soup.find_all('br'):
	d.extract()
for d in soup.find_all('i'):
	d.extract()
data = soup('tbody', limit=3)[2]
tr = data.find_all('tr')
for row in tr:
	td = row.find_all('td')
	records = {}
	records['SMD'] = td[0].text.strip()
	name_parse(td[1].text.encode('utf-8').strip().split())
	records['Address'] = re.sub("\s*\n\s*", "; ", td[2].text.encode('utf-8').strip())
	try:
		area_coder(td[3].text.encode('utf-8').strip())
		records['Email'] = td[4].a.text
		print(records)
		scraper_writer.writerow([records['SMD']] + [records['First Name']] + [records['Middle Name']] + [records['Nickname']] + [records['Last Name']] + [records['Suffix']] + [records['Address']] + [records['Phone']] + [records['Email']])
	except IndexError:
		records['Phone'] = ''
		records['Email'] = td[3].a.text
		print(records)
		scraper_writer.writerow([records['SMD']] + [records['First Name']] + [records['Middle Name']] + [records['Nickname']] + [records['Last Name']] + [records['Suffix']] + [records['Address']] + [records['Phone']] + [records['Email']])
