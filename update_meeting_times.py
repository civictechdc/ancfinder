from bs4 import BeautifulSoup
import urllib2, lxml, csv, json, datetime, os, errno, re, os.path

# URLs for different pages look like this:
# http://anc.dc.gov/events?field_date_time_rep_value[value]=2013-12-25&field_date_time_rep_value2[value]&keys=& ... 
# type=All&field_topic_tid=All&field_audience_tid=All&field_ward_tid=All&field_police_service_area_tid=All&sort_ ... 
# by=field_date_time_rep_value&sort_order=ASC&page=1
#-----------------------------------------------------------------------------
# Notice the "page=1" at the end. That's page 2. The real page one has no "page" attribute in the URL, but has everything else 
# Link giving the last page number:
#				<a title="Go to last page">
#-----------------------------------------------------------------------------
# A row in the table looks like this:
#
# <div class="views-row views-row-1 views-row-odd views-row-first calendar-event-row">
#				<div class="views-field views-field-field-date-time-rep">
#				<div class="field-content">
#								<span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content="2013-12-25T18:30:00-05:00">
#								12/25/2013 - 6:30pm
#						</span>
#			 </div>
#		</div>	
#		<div class="views-field views-field-title">
#				<span class="field-content">
#								<a href="http://calendar.dc.gov/event/anc-5b-monthly-meeting">
#								ANC 5B Monthly Meeting
#						</a>
#				</span>
#		</div>
# </div>
#------------------------------------------------------------------------------
# To break it down into individual dates and their corresponding ANC:
#
# <span class="date-display-single" property="dc:date" datatype="xsd:dateTime" content="2013-12-25T18:30:00-05:00">
#									-->  date/time in 12/25/2013 - 6:30pm format
# <span class="field-content">	-->  name of council: 'ANC 5B Monthly Meeting'
#------------------------------------------------------------------------------

file_name = 'data/meetings.json'

# Ensure JSON file output directory exists and then open.
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST:
			pass
		else:
			raise
mkdir_p(os.path.basename(file_name))

try:
	archive = json.loads(open(file_name).read())
except IOError:
	archive = {}

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
for page in pagenums:
	soup = BeautifulSoup(urllib2.urlopen('http://anc.dc.gov/events?field_date_time_rep_value[value]=2013-12-25&field_date_time_rep_value2[value]&keys=&type=All&field_topic_tid=All&field_audience_tid=All&field_ward_tid=All&field_police_service_area_tid=All&sort_by=field_date_time_rep_value&sort_order=ASC'+page))
  
	meetings = soup.find_all('div','views-row')
	for meeting in meetings:
		meet = BeautifulSoup(str(meeting))
		date = datetime.datetime.strptime(meet.find('span','date-display-single').text, '%m/%d/%Y - %I:%M%p').isoformat()
		anc = meet.find('span','field-content').text[4:6]
		link = meet.find('a').get('href')
		if link[0] == '/':
			link = 'http://anc.dc.gov' + link
		link_text = BeautifulSoup(urllib2.urlopen(link))
		address = link_text.find('div','field-name-field-location')
		address = address.find('div','field-item').text
		try:
			building = link_text.find('div','field-name-field-building-name')
			building = building.find('div','field-item').text
		except AttributeError:
			building = None
		try:
			room = link_text.find('div','field-name-field-suite-number')
			room = room.find('div','field-item').text
		except AttributeError:
			room = None
                #print link # any output gets emailed to Josh whenever this script is run by cron, so let's not have output
                details = {'address':address,'building':building,'room':room,'link':link}
		try:
			archive[anc]['meetings'][date] = details
		except KeyError:
			meetings = {'meetings': {}}
			archive[anc] = meetings

# Save the JSON file
with open(file_name, 'w') as output:
	json.dump(archive, output, sort_keys=True, indent=4)

