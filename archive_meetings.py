import csv
import urllib2
import lxml

from bs4 import BeautifulSoup

file = open('anc_meet_times.csv','r+b')
reader = csv.reader(file)
old_dict = dict(x for x in reader)

# old_dict values are read in as strings. This makes them lists.
new_old_dict = dict()
for k,v in old_dict.items():
	v = v[1:len(v)-1].replace("'",'').split(', ')
	new_old_dict[k] = v

# Get the most recent set of dates
presoup = BeautifulSoup(urllib2.urlopen('http://anc.dc.gov/events'))

lastpage = presoup.find_all('a',{'title':'Go to last page'})
lastnum = lastpage[0]['href']
lastnum = int(lastnum[len(lastnum)-1])

pagenums = ['']; i = 1
while i <= lastnum:
	pagenums.append('&page='+(str(i)))
	i+=1
		
# Now loop through the url's for each page
meettimes = []
anc = []
for page in pagenums:
	soup = BeautifulSoup(urllib2.urlopen('http://anc.dc.gov/events?field_date_time_rep_value[value]=2013-12-25&field_date_time_rep_value2[value]&keys=&type=All&field_topic_tid=All&field_audience_tid=All&field_ward_tid=All&field_police_service_area_tid=All&sort_by=field_date_time_rep_value&sort_order=ASC'+page))

	dates = soup.find_all("span",{'class':'date-display-single'})
	names = soup.find_all("span",{'class':'field-content'})
	
	# Get the individual meeting dates
	for date in dates:
		meettimes.append(date.text.encode('ascii','ignore'))
		
	# Get the corresponding ANC
	for name in names:
		anc.append(name.string[4:6])
	anc.pop()   # For some reason there is an empty entry at the bottom

# Put the meeting times under their corresponding ANC in a dictionary
i = 0
master_dict = {}
while i<len(meettimes):
	master_dict.setdefault(anc[i], []).append(meettimes[i])
	i+=1
	
# Now compare the old dict with the new
for key,value in sorted(master_dict.items()):
	for newbie in value:
		if newbie not in new_old_dict[key]:
			new_old_dict[key].append(newbie)
			break

# Write updated archive to csv
file.seek(0)				
writer = csv.writer(file)
writer.writerow(['ANC','Meeting Times'])

for k,v in sorted(new_old_dict.items()):
	if k == 'ANC':
		continue
	else:
		writer.writerow([k,v])
	
file.truncate()
file.close()