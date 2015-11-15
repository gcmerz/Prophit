from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
	balance = models.IntegerField()
	user = models.ForeignKey(User, related_name = "profile")
	customer_id = models.CharField(max_length = 255)
	api_key = models.CharField(max_length = 255)
	lat = models.IntegerField(help_text = "Latitude of user")
	lng = models.IntegerField(help_text = "Longitude of user")
	lat_dec = models.DecimalField(max_digits=19, decimal_places=10)
	lng_dec = models.DecimalField(max_digits=19, decimal_places=10)


class Merchant(models.Model):
	merchant_id = models.CharField(max_length = 255)
	name = models.CharField(max_length = 255)
	cats = models.CharField(max_length = 50)
	lat = models.IntegerField(help_text = "Latitude of merchant")
	lng = models.IntegerField(help_text = "Longitude of merchant")
	lat_dec = models.DecimalField(max_digits=19, decimal_places=10)
	lng_dec = models.DecimalField(max_digits=19, decimal_places=10)
	city = models.CharField(max_length = 255)
	state =	models.CharField(max_length = 255)


class Transaction(models.Model):
	t_id = models.CharField(max_length = 255)
	merchant = models.ForeignKey(Merchant, related_name = "transactions")
	payer = models.ForeignKey(Profile, related_name = "transactions")
	date = models.DateField(auto_now_add = True)
	amount = models.IntegerField()
	description = models.CharField(max_length = 255)
	available_balance = models.IntegerField(default = -1)


class Recommendation(models.Model):
	merchant = models.ForeignKey(Merchant, related_name = "recommendations")
	profile = models.ForeignKey(Profile, related_name = "recommendations")
	score = models.IntegerField(default=-1)
	obsolete = models.BooleanField(default=False)
