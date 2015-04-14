# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ancfindersite', '0003_auto_20150215_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionerinfo',
            name='field_value',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='commissionerinfo',
            name='smd',
            field=models.CharField(max_length=2, null=True, verbose_name=b'SMD', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='commissionerinfo',
            name='superseded_by',
            field=models.OneToOneField(related_name='supersedes', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ancfindersite.CommissionerInfo', help_text=b'The CommissionerInfo that has newer info than this one.'),
            preserve_default=True,
        ),
    ]
