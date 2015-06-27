# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0002_auto_20150421_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coder',
            name='overall_rank',
            field=models.IntegerField(default=0),
        ),
    ]
