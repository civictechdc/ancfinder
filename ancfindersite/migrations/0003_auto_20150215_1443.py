# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ancfindersite', '0002_commissionerinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commissionerinfo',
            name='superseded_by',
            field=models.OneToOneField(related_name='supersedes', null=True, blank=True, to='ancfindersite.CommissionerInfo', help_text=b'The CommissionerInfo that has newer info than this one.'),
            preserve_default=True,
        ),
    ]
