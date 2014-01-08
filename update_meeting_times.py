from bs4 import BeautifulSoup
import urllib2, lxml, csv

# URLs for different pages look like this:
# http://anc.dc.gov/events?field_date_time_rep_value[value]=2013-12-25&field_date_time_rep_value2[value]&keys=& ... 
# type=All&field_topic_tid=All&field_audience_tid=All&field_ward_tid=All&field_police_service_area_tid=All&sort_ ... 
# by=field_date_time_rep_value&sort_order=ASC&page=1
#-----------------------------------------------------------------------------
# Notice the "page=1" at the end. That's page 2. The real page one has no "page" attribute in the URL, but has everything else 
# Link giving the last page number:
# 	<a title="Go to last page">
#-----------------------------------------------------------------------------
# A row in the table looks like this:
#
# <div class="views-row views-row-1 views-row-odd views-row-first calendar-event-row">
# 	<div class="views-field views-field-field-date-time-rep">
#   	<div class="field-content">
#       	<span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content="2013-12-25T18:30:00-05:00">
#           	12/25/2013 - 6:30pm
#           </span>
#      </div>
#   </div>  
#   <div class="views-field views-field-title">
#   	<span class="field-content">
#       	<a href="http://calendar.dc.gov/event/anc-5b-monthly-meeting">
#           	ANC 5B Monthly Meeting
#           </a>
#       </span>
#   </div>
# </div>
#------------------------------------------------------------------------------
# To break it down into individual dates and their corresponding ANC:
#
# <span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content="2013-12-25T18:30:00-05:00">
#		  -->  date/time in 12/25/2013 - 6:30pm format
# <span class="field-content">  -->  name of council: 'ANC 5B Monthly Meeting'
#------------------------------------------------------------------------------

# Open up main page and figure out how many pages there are so we can loop through them all

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
		meettimes.append(date.text)
		
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

		
# Write info to .csv as a dictionary. This will have to be read in accordingly
ofile = open('anc_meet_times.csv','wb')
writer = csv.writer(ofile)
writer.writerow(['ANC','Meeting Times'])

for key,value in sorted(master_dict.items()):
	writer.writerow([key,value])
	
ofile.close()

# To read it in in the future:
# reader = csv.reader(open('master_dict.csv', 'rb'))
# mydict = dict(x for x in reader)