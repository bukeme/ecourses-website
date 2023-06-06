from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div


class UserSignupForm(SignupForm):
	first_name = forms.CharField(max_length=200)
	last_name = forms.CharField(max_length=200)
	
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.layout = Layout(
			Div(
				Div('first_name', css_class='col'),
				Div('last_name', css_class='col'),
				css_class='form-row'
			),
			Div('email'),
			Div('username'),
			Div(
				Div('password1', css_class='col'),
				Div('password2', css_class='col'),
				css_class='form-row'
			),
			Submit('submit', 'Sign Up', css_class='btn btn_primary w-100')
		)
