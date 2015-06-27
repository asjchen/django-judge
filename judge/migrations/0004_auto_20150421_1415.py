# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0003_auto_20150421_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coder',
            name='overall_score',
            field=models.DecimalField(max_digits=6, decimal_places=3),
        ),
    ]
