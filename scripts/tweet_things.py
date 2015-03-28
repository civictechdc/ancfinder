# django setup...

import  sys, os
sys.path.insert(0, '.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ancfindersite.settings'

import django
django.setup()

# ok...

import os.path, json, re, random
from datetime import datetime, timedelta
import dateutil.parser

from ancfindersite import settings
from ancfindersite.models import Document

def main():
	# What have we tweeted about before?
	tweets_storage_fn = os.environ.get('STATIC_ROOT', 'static') + '/tweets.json'
	if not os.path.exists(tweets_storage_fn):
		previous_tweets = {}
	else:
		previous_tweets = json.loads(open(tweets_storage_fn).read())

	# Post to Twitter. Mix it up a bit.
	if (random.random() > .5) or not post_meeting_tweet(previous_tweets):
		post_document_tweet(previous_tweets)

	# Save the JSON file so we can record the things we've already
	# tweeted about.
	with open(tweets_storage_fn, 'w') as output:
		json.dump(previous_tweets, output, sort_keys=True, indent=4)


def post_meeting_tweet(previous_tweets):
	# Load the meetings database.
	file_name = os.environ.get('STATIC_ROOT', 'static') + '/meetings.json'
	meetings = json.loads(open(file_name).read())
	now = datetime.now()

	def all_meetings_sorted(tweet_type):
		# Sort all of the known, future meetings by their meeting date.
		def meeting_iterator():
			for anc in meetings:
				for meeting_date, meeting_info in meetings[anc]['meetings'].items():
					if meeting_info.get("status") == "invalid": continue # don't tweet these
					meeting_date = dateutil.parser.parse(meeting_date)
					if meeting_date <= now: continue
					tweet_key = 'meeting:' + meeting_date.isoformat() + ':' + tweet_type
					yield { 'anc': anc, 'date': meeting_date, 'info': meeting_info, 'key': tweet_key }
		return sorted(meeting_iterator(), key = lambda m : m['date'])
	
	def first_meeting_for_each_anc(tweet_type):
		seen = set()
		for mtg in all_meetings_sorted(tweet_type):
			if mtg['anc'] in seen: continue
			yield mtg
			seen.add(mtg['anc'])

	def get_next_day_of_meeting():
		day_of = [m for m in all_meetings_sorted('day-of')
				   if m['date'].date() == now.date() and m['date'] > now + timedelta(hours=1) and m['date'].hour >= 17
				      and m['key'] not in previous_tweets]
		if len(day_of) == 0:
			return None
		return day_of[0]

	def get_next_meeting_posted():
		to_announce = [m for m in first_meeting_for_each_anc('posted')
				   if m['date'] > now + timedelta(days=1)
				      and m['date'] < now + timedelta(days=31)
				      and m['key'] not in previous_tweets]
		if len(to_announce) == 0:
			return None
		return to_announce[0]

	# Post something to our Twitter account.

	day_of = get_next_day_of_meeting()
	next_posted = get_next_meeting_posted()

	if day_of:
		# Post a tweet for the next meeting that is tonight.
		post_tweet(
			day_of['key'],
			"ANC %s meeting tonight at %s. More at http://www.ancfinder.org/%s. #ANC%s"
			% (day_of['anc'], re.sub("^0", "", day_of['date'].strftime("%I:%M %p")), day_of['anc'], day_of['anc']),
			previous_tweets)
		return True

	elif next_posted:
		# If there is no day-of tweet, then post a tweet for the next upcoming ANC meeting
		# that we haven't tweeted about.
		post_tweet(
			next_posted['key'],
			"ANC %s's next meeting is on %s. More at http://www.ancfinder.org/%s. #ANC%s"
			% (next_posted['anc'], next_posted['date'].strftime("%A, %B %d at %I:%M %p").replace(" 0", " "), next_posted['anc'], next_posted['anc']),
			previous_tweets)
		return True

	else:
		# No meeting to tweet.
		return False

def post_document_tweet(previous_tweets):
	from django.utils.timezone import now

	for doc in Document.objects.filter(created__gt=now() - timedelta(days=5)).order_by('created'):
		key = "document:%d" % doc.id
		if key in previous_tweets: continue

		post_tweet(
			key,
			"New: %s at %s. #ANC%s"
			% ( doc.get_display_title()[0:100], settings.SITE_ROOT_URL + doc.get_absolute_url(), doc.anc ),
			previous_tweets)

		# Just do one, of course.
		break

def post_tweet(key, text, previous_tweets):
	from twitter import Twitter, OAuth

	exec(compile(open("credentials.py").read(), "credentials.py", 'exec'))

	t = Twitter(auth=OAuth(twitter_access_token, twitter_access_token_secret, twitter_app_key, twitter_app_secret))	
	ret = t.statuses.update(status=text)
	previous_tweets[key] = ret

	#print(text)
	#print(json.dumps(ret, sort_keys=True, indent=4))

main()
