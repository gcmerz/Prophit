# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('merchant_id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('cats', models.CharField(max_length=50)),
                ('lat', models.IntegerField(help_text='Latitude of merchant')),
                ('lng', models.IntegerField(help_text='Longitude of merchant')),
                ('lat_dec', models.DecimalField(max_digits=19, decimal_places=10)),
                ('lng_dec', models.DecimalField(max_digits=19, decimal_places=10)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('balance', models.IntegerField()),
                ('customer_id', models.CharField(max_length=255)),
                ('api_key', models.CharField(max_length=255)),
                ('lat', models.IntegerField(help_text='Latitude of user')),
                ('lng', models.IntegerField(help_text='Longitude of user')),
                ('lat_dec', models.DecimalField(max_digits=19, decimal_places=10)),
                ('lng_dec', models.DecimalField(max_digits=19, decimal_places=10)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='profile')),
            ],
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField(default=-1)),
                ('obsolete', models.BooleanField(default=False)),
                ('merchant', models.ForeignKey(to='capitalOne.Merchant', related_name='recommendations')),
                ('profile', models.ForeignKey(to='capitalOne.Profile', related_name='recommendations')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('t_id', models.CharField(max_length=255)),
                ('date', models.DateField(auto_now_add=True)),
                ('amount', models.IntegerField()),
                ('description', models.CharField(max_length=255)),
                ('merchant', models.ForeignKey(to='capitalOne.Merchant', related_name='transactions')),
                ('payer', models.ForeignKey(to='capitalOne.Profile', related_name='transactions')),
            ],
        ),
    ]
