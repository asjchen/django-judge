# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('overall_rank', models.IntegerField(default=0)),
                ('overall_score', models.DecimalField(max_digits=6, decimal_places=4)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('score', models.IntegerField(default=0)),
                ('coder', models.ForeignKey(to='judge.Coder')),
            ],
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('statement', models.TextField()),
                ('slug', models.SlugField()),
                ('answer', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='problem',
            field=models.ForeignKey(to='judge.Problem'),
        ),
    ]
