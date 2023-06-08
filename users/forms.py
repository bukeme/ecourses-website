from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div
from users.models import UserProfile


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

# class UserProfileForm(forms.Form):
# 	first_name = forms.CharField(max_length=200)
# 	last_name = forms.CharField(max_length=200)
# 	email = forms.EmailField()
# 	username = forms.CharField(max_length=200)
# 	headline = forms.CharField(max_length=300)
# 	overview = forms.CharField(widget=forms.Textarea(attrs={'rows':2}))

class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name', 'email', 'username']

class UserProfileForm(forms.ModelForm):
	# headline = forms.CharField(max_length=300, required=False)
	# overview = forms.CharField(widget=forms.Textarea(attrs={'rows':2}), required=False)
	class Meta:
		model = UserProfile
		fields = ['headline', 'overview', 'image']


