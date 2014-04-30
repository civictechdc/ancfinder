from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.conf import settings

import base64, collections

try:
	import json
except ImportError:
	import simplejson as json

anc_data_as_json = open(settings.STATIC_ROOT + "/ancs.json").read()
anc_data = json.loads(anc_data_as_json, object_pairs_hook=collections.OrderedDict)
anc_list = []
for ward in anc_data.values():
	anc_list.extend(list(x['anc'] for x in ward['ancs'].values()))
anc_list.sort()

class Document(models.Model):
	"""An ANC document."""

	doc_type_choices = [
		(0, "Unknown"),
		(1, "Agenda"),
		(2, "Minutes"),
		(3, "Report"),
		(4, "Decision"), # resolutions, etc.
		(5, "Draft"),
		(6, "Application"),
		(7, "Grant"),
		(8, "Official Correspondence"),
		(9, "Financial Statement"),
		(10, "Operating Documents"), # charter, etc.
		(11, "Committee Agenda"),
		(12, "Committee Minutes"),
		(13, "Committee Report"),
		]

	owner = models.ForeignKey(User, related_name="uploaded_documents")

	anc = models.CharField(choices=[(x,x) for x in anc_list], max_length=4, db_index=True, verbose_name="ANC") # e.g. "3B" or later perhaps "3B08"
	title = models.CharField(max_length=64, default="No Title")
	created = models.DateTimeField(auto_now_add=True, db_index=True)

	doc_type = models.IntegerField(choices=doc_type_choices, default=0, verbose_name="Document Type")
	pub_date = models.DateField(blank=True, null=True, verbose_name="Date Published", help_text="The date the document was published by the ANC, if known.")
	meeting_date = models.DateField(blank=True, null=True, verbose_name="Date of Meeting", help_text="The date of an associated meeting, if relevant.")
	
	document_content = models.TextField(editable=False, help_text="The binary document content, stored Base64-encoded.")
	document_content_type = models.CharField(editable=False, max_length=128, help_text="The MIME type of the document_content.")
	document_content_size = models.IntegerField(editable=False, blank=True, null=True)

	source_url = models.CharField(max_length=256, blank=True, null=True, verbose_name="Source URL", help_text="The web address where this document was obtained from.")
	
	annotation_document = models.ForeignKey('annotator.Document', editable=False, blank=True, null=True, on_delete=models.SET_NULL)

	def __str__(self):
		return self.get_display_date().isoformat() + " " + self.anc + " " + self.get_doc_type_display() + ("/" + self.title if self.title else "")

	def get_absolute_url(self):
		title = self.title
		if title is None or title.strip() in ("", "No Title"):
			title = self.get_doc_type_display()
		return "/document/%s/%s/%d/%s" % (self.anc, self.get_display_date().isoformat(), self.id, slugify(title))

	def get_display_title(self):
		if self.doc_type in (1, 2):
			if self.meeting_date:
				return "ANC %s %s for %s" % (self.anc, self.get_doc_type_display(), self.meeting_date.strftime("%B %d, %Y"))
		if self.title is None: return "No Title"
		return self.title

	def get_display_date(self):
		if self.meeting_date:
			return self.meeting_date
		elif self.pub_date:
			return self.pub_date
		else:
			return self.created.date()

	def get_tags(self):
		if not self.annotation_document: return []
		return sum([json.loads(a.data)["tags"] for a in self.annotation_document.annotations.all()], [])

	def set_document_content(self, content, mime_type=None):
		if mime_type:
			self.document_content = content
			self.document_content_type = mime_type
		elif isinstance(content, (str, unicode)):
			if isinstance(content, unicode): content = content.encode("utf8")
			self.document_content = content
			self.document_content_type = "text/html"
		else:
			# content is a Django UploadedFile object.
			self.document_content = content.read()
			self.document_content_type = content.content_type
			if content.charset and content.charset != "utf8":
				self.document_content = self.document_content.decode(content.charset, "replace").encode("utf8")

		self.document_content_size = len(self.document_content)
		self.document_content = base64.b64encode(self.document_content)

		self.save()
		
	def populate_annotation_document(self):
		if self.annotation_document:
			# already created
			return

		from annotator.models import Document as AD
		ad = AD()
		ad.title = str(self)

		if self.document_content_type == "text/html":
			ad.body = base64.b64decode(self.document_content)
		elif self.document_content_type == "application/pdf":
			ad.body = Document.convert_pdf_to_html(base64.b64decode(self.document_content))
		else:
			raise ValueError("Don't know how to convert this file type: %s" % self.document_content_type)

		ad.save()
		
		self.annotation_document = ad
		self.save()

	@staticmethod
	def convert_pdf_to_text(pdf_blob):
		import sys, subprocess, tempfile, os

		if not os.path.exists("/usr/bin/pdftotext"):
			# fall back!
			return Document.convert_pdf_to_text_with_pdf2txt(pdf_blob)

		try:
			(fd1, fn1) = tempfile.mkstemp(suffix=".pdf")
			os.write(fd1, pdf_blob)
			os.close(fd1)
			
			(fd2, fn2) = tempfile.mkstemp(suffix=".txt")
			os.close(fd2)
			subprocess.check_call(["/usr/bin/pdftotext", "-layout", "-enc", "UTF-8", fn1, fn2])
			with open(fn2, "rb") as fo:
				return fo.read().decode("utf-8")
		finally:
			os.unlink(fn1)
			os.unlink(fn2)

	@staticmethod
	def convert_pdf_to_html(pdf_blob):
		return Document.convert_text_to_html(Document.convert_pdf_to_text(pdf_blob))
				
	@staticmethod
	def convert_pdf_to_text_with_pdf2txt(pdf_blob):
		import tempfile, os, subprocess

		# Convert the PDF to plain text. Conversion to HTML is usually either
		# ugly or produces complex HTML layouts that make selection behave
		# weirdly, and being able to select things is important for annotations.
		try:
			(fd1, fn1) = tempfile.mkstemp(suffix=".pdf")
			os.write(fd1, pdf_blob)
			os.close(fd1)
			text_blob = subprocess.check_output(["pdf2txt.py", "-c", "utf8", "-t", "text", "-Y", "loose", fn1])
			text_blob = text_blob.decode('utf8')
		finally:
			os.unlink(fn1)
		return text_blob

	@staticmethod
	def convert_text_to_html(text_blob):
		import lxml.etree

		root = lxml.etree.Element("div")
		for page in text_blob.split("\x0C"):
			page = page.strip()
			if page == "": continue

			page_node = lxml.etree.Element("div")
			page_node.set("class", "page")
			root.append(page_node)

			for line in page.split("\n"):
				n = lxml.etree.Element("div")
				n.set("style", "white-space: pre")
				page_node.append(n)
				if line.strip() == "":
					n.text = u'\u00a0' # nbsp prevents the <div> from collapsing to zero height
				else:
					print repr(line)
					n.text = line

		return lxml.etree.tostring(root, pretty_print=True, method="html", encoding=unicode)
		
