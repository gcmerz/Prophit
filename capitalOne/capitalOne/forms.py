from django import forms
import account.forms

class SignupForm(account.forms.SignupForm):
	""""for now, this form is disabled"""""
	api_key = forms.CharField(required = True)
	customer_id = forms.CharField(required = True)

	def __init__(self, *args, **kwargs):
	    super().__init__(*args, **kwargs)
	    self.fields['api_key'].label = "API Key"
	    self.fields['customer_id'].label = "Customer ID"
