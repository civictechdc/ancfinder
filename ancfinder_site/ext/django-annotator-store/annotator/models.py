from django.db import models
from django.contrib.auth.models import User

import uuid, json

class Document(models.Model):
	"""A document being annotated"""
	owner = models.ForeignKey(User, db_index=True, blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True, db_index=True)
	title = models.CharField(max_length=64)
	body = models.TextField() # HTML

	def __str__(self):
		return self.title

class Annotation(models.Model):
	owner = models.ForeignKey(User, db_index=True, blank=True, null=True)
	document = models.ForeignKey(Document, db_index=True, related_name="annotations")
	guid = models.CharField(max_length=64, unique=True, editable=False)
	created = models.DateTimeField(auto_now_add=True, db_index=True)
	updated = models.DateTimeField(auto_now=True, db_index=True)
	data = models.TextField() # all other annotation data as JSON
	
	def set_guid(self):
		self.guid = str(uuid.uuid4())
	
	def can_edit(self, user):
		if self.owner and self.owner != user and (not user or not user.has_perm('annotator.change_annotation')):
			return False
		return True
	
	def as_json(self, user=None):
		d = {
			"id": self.guid,
			"document": self.document_id,
			"created": self.created.isoformat(),
			"updated": self.updated.isoformat(),
			"readonly": not self.can_edit(user),
		}
		
		
		d.update(json.loads(self.data))
		
		return d

	def update_from_json(self, new_data):
		d = json.loads(self.data)
		
		for k, v in new_data.items():
			# Skip special fields that we maintain and are not editable.
			if k in ('document', 'id', 'created', 'updated', 'readonly'):
				continue
				
			# Put other fields into the data object.
			d[k] = v
		
		self.data = json.dumps(d)
		
	@staticmethod
	def as_list(qs=None, user=None):
		if qs == None: qs = Annotation.objects.all()
		return [
			obj.as_json(user=user)
			for obj in qs.order_by('-updated')
		]

