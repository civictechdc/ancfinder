# -*- coding: utf-8

from django.contrib import admin
from ancfindersite.models import *


@admin.register(CommissionerInfo)
class CommissionerInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'latest', 'created', 'author', 'anc', 'smd', 'field_name', 'field_value', 'linkage']
    raw_id_fields = ['author']
    readonly_fields = ['author', 'superseded_by', 'anc', 'smd', 'field_name']
    def latest(self, obj):
    	return obj.superseded_by is None
    latest.boolean = True
    def linkage(self, obj):
    	ret = []
    	if obj.superseded_by is not None: ret.append("next: %d" % obj.superseded_by.id)
    	try:
    		ret.append("prev: %d" % obj.supersedes.id)
    	except:
    		# obj.supersedes doesn't return None, instead it raises a DoesNotExist exception.
    		pass
    	return "; ".join(ret)


admin.site.register(Document)
