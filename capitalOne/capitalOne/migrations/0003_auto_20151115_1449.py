# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capitalOne', '0002_transaction_available_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='available_balance',
            field=models.IntegerField(default=-1),
        ),
    ]
