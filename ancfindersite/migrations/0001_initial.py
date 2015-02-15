# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('anc', models.CharField(db_index=True, max_length=4, verbose_name=b'ANC', choices=[('1A', '1A'), ('1B', '1B'), ('1C', '1C'), ('1D', '1D'), ('2A', '2A'), ('2B', '2B'), ('2C', '2C'), ('2D', '2D'), ('2E', '2E'), ('2F', '2F'), ('3B', '3B'), ('3C', '3C'), ('3D', '3D'), ('3E', '3E'), ('3F', '3F'), ('3G', '3G'), ('4A', '4A'), ('4B', '4B'), ('4C', '4C'), ('4D', '4D'), ('5A', '5A'), ('5B', '5B'), ('5C', '5C'), ('5D', '5D'), ('5E', '5E'), ('6A', '6A'), ('6B', '6B'), ('6C', '6C'), ('6D', '6D'), ('6E', '6E'), ('7B', '7B'), ('7C', '7C'), ('7D', '7D'), ('7E', '7E'), ('7F', '7F'), ('8A', '8A'), ('8B', '8B'), ('8C', '8C'), ('8D', '8D'), ('8E', '8E')])),
                ('title', models.CharField(default=b'No Title', max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('doc_type', models.IntegerField(default=0, verbose_name=b'Document Type', choices=[(0, b'Unknown'), (1, b'Agenda'), (2, b'Minutes'), (3, b'Report'), (4, b'Resolution'), (5, b'Draft'), (6, b'Application'), (7, b'Grant'), (8, b'Official Correspondence'), (9, b'Financial Statement'), (10, b'Operating Document'), (11, b'Committee Agenda'), (12, b'Committee Minutes'), (13, b'Committee Report'), (14, b'Meeting Summary')])),
                ('pub_date', models.DateField(help_text=b'The date the document was published by the ANC, if known.', null=True, verbose_name=b'Date Published', blank=True)),
                ('meeting_date', models.DateField(help_text=b'The date of an associated meeting, if relevant.', null=True, verbose_name=b'Date of Meeting', blank=True)),
                ('document_content', models.TextField(help_text=b'The binary document content, stored Base64-encoded.', editable=False)),
                ('document_content_type', models.CharField(help_text=b'The MIME type of the document_content.', max_length=128, editable=False)),
                ('document_content_size', models.IntegerField(null=True, editable=False, blank=True)),
                ('source_url', models.CharField(help_text=b'The web address where this document was obtained from.', max_length=256, null=True, verbose_name=b'Source URL', blank=True)),
                ('annotation_document', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='annotator.Document', null=True)),
                ('owner', models.ForeignKey(related_name='uploaded_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
