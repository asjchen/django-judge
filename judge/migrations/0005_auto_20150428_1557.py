# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0004_auto_20150421_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='arg_values',
            field=models.CharField(default=b'', max_length=200),
        ),
        migrations.AddField(
            model_name='problem',
            name='arg_vars',
            field=models.CharField(default=b'', max_length=200),
        ),
    ]
