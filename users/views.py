from django.shortcuts import render
from allauth.account.views import SignupView
from users.forms import UserSignupForm

# Create your views here.


class UserSignupView(SignupView):
	form_class = UserSignupForm

user_signup_view = UserSignupView.as_view()
