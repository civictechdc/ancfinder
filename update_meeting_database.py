# Scrape the DC ANC website's RSS feed for upcoming ANC meetings.
#
# Store them in www/meetings.json, and update existing meetings
# in place according to the RSS feed's guid field.

import json, os.path, urllib
import lxml.etree, lxml.html

output_filename = "www/meetings.json"

if os.path.exists(output_filename):
	meetings = json.load(open(output_filename))
else:
	meetings = []

# Open the RSS feed.	
dom = lxml.etree.parse(urllib.urlopen("http://anc.dc.gov/node/all/events"))

# In the description HTML, divs have nice class names identifying what
# the information is about. Map CSS classes to field names we'll store
# in our file.
class_name_map = {
	"field-name-field-building-name": "location2",
	"field-name-field-contact": "contact",
	#"field-name-field-date-time-rep": "date-time-rep", # duplicates 'field-type-datetime'
	"field-name-field-email": "email",
	"field-name-field-external-link-url": "link",
	"field-name-field-location": "location",
	"field-name-field-phone": "phone",
	"field-name-field-second-location": "alternate-location",
	"field-name-field-suite-number": "suite-number",
	"field-name-field-ward": "ward",
	"field-type-datetime": "when",
	"field-type-text": "text",
	#"field-type-text-long": "text2", # appears to be a broken website link
	"field-type-text-with-summary": "about_anc",
}

# The fields in the HTML have label divs and field value divs. Let's
# skip labels when they match a known value.
hide_field_labels = {
	"field-name-field-building-name": "Building",
	"field-name-field-email": "Email",
	"field-name-field-external-link-url": "Website",
	"field-name-field-location": "Location",
	"field-name-field-phone": "Phone",
	"field-name-field-suite-number": "Room",
	"field-name-field-ward": "Ward",
	"field-type-text": "Building",
	"field-type-text-with-summary": "Details",
}

# Take note of meetings already in our JSON file.
meetings_by_guid = { }
for meeting in meetings:
	meetings_by_guid[meeting["guid"]] = meeting

# Go through the RSS feed.
for meeting in dom.xpath("channel/item"):
	# Assemble meeting information.
	meeting_info = {
		"title": meeting.xpath("string(title)"),
		"calendar_link": meeting.xpath("string(link)"),
		"guid": meeting.xpath("string(guid)"),
	}
	
	# Replace existing meeting info if it's already in our file, or add it
	# if we don't know about it yet.
	if meeting_info["guid"] in meetings_by_guid:
		meetings_by_guid[meeting_info["guid"]].update(meeting_info)
		meeting_info = meetings_by_guid[meeting_info["guid"]]
	else:
		meetings.append(meeting_info)
	
	# The description tag has HTML content. Parse it.
	descr = meeting.xpath("string(description)").replace("&nbsp;", u"\u00A0")
	description = lxml.html.fromstring(descr)
	
	# Loop through the fields we know about and try to extract the values.
	for classname, fieldname in class_name_map.items():
		# Should we include the field's label in the value we store?
		# Get the field value's div elements. There may be more than one.
		labels = description.cssselect("." + classname + " .field-label")
		if classname in hide_field_labels and len(labels) > 0 and labels[0].text_content().strip() == hide_field_labels[classname]+":":
			divs = description.cssselect("." + classname + " .field-items")
		else:
			divs = description.cssselect("." + classname)
		if len(divs) > 0:
			value = "; ".join(d.text_content().strip() for d in divs)
			meeting_info[fieldname] = value

# Write out the JSON file.
with open(output_filename, "w") as outputfile:
	json.dump(meetings, outputfile, sort_keys=True, indent=4)

