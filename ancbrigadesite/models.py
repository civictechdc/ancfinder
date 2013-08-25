from django.db import models
import base64

class Document(models.Model):
	"""A ANC document."""

	anc = models.CharField(max_length=4, db_index=True, verbose_name="ANC") # e.g. "3B" or later perhaps "3B08"
	title = models.CharField(max_length=64, blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True, db_index=True)

	doc_type = models.IntegerField(choices=[
		(0, "Unknown"),
		(1, "Agenda"),
		(2, "Minutes"),
		(3, "Report"),
		(4, "Decision"),
		(5, "Draft"),
		(6, "Application"),
		(7, "Financial Statement"),
		], default=0, verbose_name="Document Type")
	pub_date = models.DateField(blank=True, null=True, verbose_name="Date Published", help_text="The date the document was published by the ANC, if known.")
	meeting_date = models.DateField(blank=True, null=True, verbose_name="Date of Meeting", help_text="The date of an associated meeting, if relevant.")
	
	document_content = models.TextField(editable=False, help_text="The binary document content, stored Base64-encoded.")
	document_content_type = models.CharField(editable=False, max_length=128, help_text="The MIME type of the document_content.")
	document_content_size = models.IntegerField(editable=False)
	
	annotation_document = models.ForeignKey('annotator.Document', editable=False, blank=True, null=True)

	source_id = models.CharField(max_length=256, unique=True, editable=False, help_text="Abitrary data to identify where the document was scraped from.")

	def __str__(self):
		return self.get_doc_type_display() + ("/" + self.title if self.title else "")

	def set_document_content(self, content):
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
		ad.body = Document.convert_pdf_to_html(base64.b64decode(self.document_content))
		ad.save()
		
		self.annotation_document = ad
		self.save()

	@staticmethod
	def convert_pdf_to_html(pdf_blob):
		# Use Josh's hacky CGI script running on his server as a PDF-to-HTML converter.
		# Extract just the <body> content.
		import urllib.request, lxml.etree, re
		html = urllib.request.urlopen("http://razor.occams.info/cgi-bin/ancbrigade-pdf-to-html.cgi", pdf_blob)
		dom = lxml.etree.parse(html, lxml.etree.HTMLParser())
		for n in dom.xpath('//*'):
			# clear various styles
			if n.get("style"):
				n.set("style", re.sub(r"(left|top|width|height|font-size|position):.*?(;|$)", "", n.get("style")))
		return lxml.etree.tostring(dom.getroot().xpath("body")[0], pretty_print=True, method="html")
		
