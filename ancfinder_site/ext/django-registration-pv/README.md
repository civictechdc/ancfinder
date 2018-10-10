Django Registration App (originally by POPVOX)
==============================================

This app provides infrastructure for new user registration including support
for social logins (built-in support for Google, Twitter, LinkedIn, and Facebook).
For new user accounts using an email address and password, the user is sent a
confirmation (verification) email *before* the account is created.

The email verification routine can be used as an independent app that provides
an infrastructure for executing callback routines when a user follows a custom
link sent to them in an email. See emailverification/README.txt for details.

Utilities are also provided to manage bounced mail.

Configuration
-------------

After cloning this repository, make the `registration` and `emailverification` directories
available on your Python path. Then install the dependencies:

    pip install -r requirements.txt

In settings.py, add to your INSTALLED_APPS:

	django.contrib.staticfiles
	emailverification
	registration

Then set:

    APP_NICE_SHORT_NAME = "MySite" # a short name for your site
    SERVER_EMAIL = "MySite <noreply@example.org>" # From: address on verification emails
    REGISTRATION_ASK_USERNAME = True
    
If `REGISTRATION_ASK_USERNAME` is True, then the user is always asked for
a username. If False, a username is guessed when enough information is
provided by the login provider.
		
Optionally set:

    SITE_ROOT_URL = "http://www.example.org" # canonical base URL of the site, no trailing slash
                                             # The default will be "http://%s" % Site.objects.get_current().domain
		
Add records to your URLConf like this (you can use any base path):

    url(r'^emailverif/', include('emailverification.urls')),
    url(r'^registration/', include('registration.urls')),
    
The registration app provides a new user registration page at /registration/signup.

You will probably also want to use:

    url(r'^accounts/login/?$', 'registration.views.loginform'),
    url(r'^accounts/logout/?$', 'registration.views.logoutview'),
    url(r'^accounts/profile/?$', 'registration.views.profile'),

You will probably want to override the templates in

    emailverification/templates/emailverification
        badcode.html: invalid verification code or an error occurred processing it
        expired.htm: expired verification code

by either editing them in place or copying the directories to your site's
root templates directory and editing the copies there. 

Run `python manage.py syncdb` to create the necessary database tables.

Beyond this, many of the components of this app are optional. The dependencies
and configuration for the optional parts are given next.

Configuring Login Providers
---------------------------

reCAPTCHA on new account creations:

	dependencies: python-recaptcha <http://pypi.python.org/pypi/recaptcha-client>

	settings.py:

	RECAPTCHA_PUBLIC_KEY = "..."
	RECAPTCHA_PRIVATE_KEY = "..."

Google login with OpenID:

	dependencies: python-openid <https://github.com/openid/python-openid>

	No configuration necessary.

Google login with OAuth 1 (not recommended unless you are accessing
the user's Google resources):

	dependencies: python-oauth2 <http://github.com/simplegeo/python-oauth2>

	settings.py:

	GOOGLE_OAUTH_TOKEN = "..."
	GOOGLE_OAUTH_TOKEN_SECRET = "..."
	GOOGLE_OAUTH_SCOPE = "http://www.google.com/m8/feeds/contacts/default/full" # can be an empty string

Twitter login with OAuth 1:

	dependencies: python-oauth2 <http://github.com/simplegeo/python-oauth2>

	settings.py:

	TWITTER_OAUTH_TOKEN = "..."
	TWITTER_OAUTH_TOKEN_SECRET = "..."

LinkedIn login with OAuth 1:

	dependencies: python-oauth2 <http://github.com/simplegeo/python-oauth2>

	settings.py:

	LINKEDIN_API_KEY = "..."
	LINKEDIN_SECRET_KEY = "..."

Facebook login with OAuth 2:

	no dependencies

	settings.py:

	FACEBOOK_APP_ID = "..."
	FACEBOOK_APP_SECRET = "..."
	FACEBOOK_AUTH_SCOPE = "email" # can be an empty string

Management
----------

When users register with an email address, they are sent an email to
confirm their address. The table that stores state for that should
be cleared periodically (e.g. daily) with:

    python manage.py clear_expired_email_verifications
  

	
Bounced Mail Utility
====================

The emailverification app also contains a utility to check an IMAP mailbox for bounced
mail from your site's outgoing mail to registered users.

Send your outbound email with a return path to a special mailbox address that encodes
the user ID the message was sent to. For instance, use:

	from django.core.mail import EmailMessage
	email = EmailMessage(emailsubject, body, "bounces+uid=USER_ID@example.com",
		"user1234@gmail.com", headers = { 'From': "Example Website <feedback@example.com>" })

to specify a return path encoding the recipiens user's id separate from the From: field
on the message. Most mail servers ignore the part of an address starting with a plus
sign, so you can create an infinite number of virtual addresses. If you use a different
address for each user, you can reliably tell who you emailed in message delivery failure
emails.

Create an account to receive the mail (e.g. bounces@example.com) that you can access
with IMAP. In settings.py, configure access to that inbox:

	BOUNCES_IMAP_SSL = True
	BOUNCES_IMAP_HOST = 'localhost'
	BOUNCES_IMAP_USER = 'bounces'
	BOUNCES_IMAP_PASSWORD = '...'

And also configure a regular expression that picks out the user ID from the email address:
	
	BOUNCES_UID_REGEX = re.compile(r"bounces\+uid=(\d+)@example\.com")
	
Then run:

	./manage.py catch_bounces
	
Which will create an emailverification.BouncedEmail record for each user that a bounced mail
was received from, and it will increment a counter for each bounced message. And, it will
delete the message from the IMAP server so that you don't count it again the next time you
run the management command.

It is up to you to do something with the BouncedEmail records.


Copyright
=========

Copyright (C) 2011 POPVOX.com, 2012-2013 Civic Impulse LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
