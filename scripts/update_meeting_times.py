from bs4 import BeautifulSoup
import dateutil.parser
import sys, urllib2, lxml, csv, json, datetime, os, errno, re, os.path, urlparse

# Get ANC upcoming meetings from http://anc.dc.gov/events by reading the page
# for meeting details URLs, and following the "next >" link to page through
# the paginated results.
#
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

file_name = os.environ.get('STATIC_ROOT', 'static') + '/meetings.json'

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

# Loop through the paginated list of upcoming ANC events.

url = 'http://anc.dc.gov/events'
cached_meeting_data = { }
meeting_links = []
seen_meetings = set()
while True:
	if sys.stdout.isatty(): print url, "..." # don't print when running from a cron job

	soup = BeautifulSoup(urllib2.urlopen(url))
	meetings = soup.find_all('div','views-row')
	last_meeting_date = None
	for meet in meetings:
		# get the date, ANC, and link to more information
		date = datetime.datetime.strptime(meet.find('span','date-display-single').text, '%m/%d/%Y - %I:%M%p')
		anc = meet.find('span','field-content').text[4:6]
		link = urlparse.urljoin(url, meet.find('a').get('href'))

		# scrape the individual meeting page for more details. the same
		# target page is used for each meeting time, so we can cache it
		# to be a little faster.
		if link not in cached_meeting_data:
			if sys.stdout.isatty(): print "\t", link, "..."
			meeting_info = urllib2.urlopen(link).read()
			cached_meeting_data[link] = meeting_info
		else:
			meeting_info = cached_meeting_data[link]
		meeting_info = BeautifulSoup(meeting_info)

		try:
			address = meeting_info.find('div', 'field-name-field-location').find('div','field-item').text
		except AttributeError:
			address = None

		try:
			building = meeting_info.find('div','field-name-field-building-name').find('div','field-item').text
		except AttributeError:
			building = None

		try:
			room = meeting_info.find('div','field-name-field-suite-number').find('div','field-item').text
		except AttributeError:
			room = None

		if anc not in archive: archive[anc] = { "meetings": { } }

		date_key = date.isoformat()

		# Record the date we first saw this meeting. In our RSS feed, we'll use
		# this date as the <pubdate>.
		prev_mtg_record = archive[anc]['meetings'].get(date_key)
		record_created = datetime.datetime.now().isoformat()
		if prev_mtg_record is not None:
			record_created = prev_mtg_record.get("created")

		archive[anc]['meetings'][date_key] = {
			'created': record_created,
			'address': address,
			'building': building,
			'room': room,
			'link': link
		}

		last_meeting_date = date
		seen_meetings.add((anc, date_key))

	# Stop if we are waaaay in the future, since the events page goes years ahead, which
	# is not actually very helpful. Cut off after 3 months.
	if last_meeting_date and last_meeting_date > datetime.datetime.now()+datetime.timedelta(days=3*30.5):
		break

	# Go onto the next page, if there is a next page.
	nextpage = soup.find_all('a',{'title':'Go to next page'})
	if not nextpage:
		break

	# turn a relative URL into an absolute URL for the next iteration
	url = urlparse.urljoin(url, nextpage[0]['href'])

# Remove future meetings that no longer are posted by DC.
# Don't delete meetings with status == "manual" which are
# meetings we're entering by hand when the DC data is wrong.
for anc, ancmtgs1 in archive.items():
	for mtgdate, mtgobj in list(ancmtgs1.get("meetings", {}).items()):
		if mtgobj.get("status") == "manual": continue
		if (anc, mtgdate) not in seen_meetings and dateutil.parser.parse(mtgdate) > datetime.datetime.now():
			del ancmtgs1["meetings"][mtgdate]

# Save the JSON file
with open(file_name, 'w') as output:
	json.dump(archive, output, sort_keys=True, indent=4)

