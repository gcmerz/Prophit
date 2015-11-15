# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capitalOne', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='available_balance',
            field=models.IntegerField(default=-1),
            preserve_default=False,
        ),
    ]
