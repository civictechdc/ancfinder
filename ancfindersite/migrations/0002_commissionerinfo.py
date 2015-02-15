# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ancfindersite', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommissionerInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(help_text=b'The date and time that this value was entered.', auto_now_add=True, db_index=True)),
                ('anc', models.CharField(db_index=True, max_length=2, verbose_name=b'ANC', choices=[('1A', '1A'), ('1B', '1B'), ('1C', '1C'), ('1D', '1D'), ('2A', '2A'), ('2B', '2B'), ('2C', '2C'), ('2D', '2D'), ('2E', '2E'), ('2F', '2F'), ('3B', '3B'), ('3C', '3C'), ('3D', '3D'), ('3E', '3E'), ('3F', '3F'), ('3G', '3G'), ('4A', '4A'), ('4B', '4B'), ('4C', '4C'), ('4D', '4D'), ('5A', '5A'), ('5B', '5B'), ('5C', '5C'), ('5D', '5D'), ('5E', '5E'), ('6A', '6A'), ('6B', '6B'), ('6C', '6C'), ('6D', '6D'), ('6E', '6E'), ('7B', '7B'), ('7C', '7C'), ('7D', '7D'), ('7E', '7E'), ('7F', '7F'), ('8A', '8A'), ('8B', '8B'), ('8C', '8C'), ('8D', '8D'), ('8E', '8E')])),
                ('smd', models.CharField(max_length=2, verbose_name=b'SMD')),
                ('field_name', models.CharField(max_length=32)),
                ('field_value', models.CharField(max_length=256, blank=True)),
                ('author', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text=b'The user who provided this value.', null=True)),
                ('superseded_by', models.ForeignKey(related_name='supersedes', blank=True, to='ancfindersite.CommissionerInfo', help_text=b'The CommissionerInfo that has newer info than this one.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
