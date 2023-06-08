from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from allauth.account.views import SignupView
from users.forms import UserSignupForm, UserForm, UserProfileForm

# Create your views here.


class UserSignupView(SignupView):
	form_class = UserSignupForm

user_signup_view = UserSignupView.as_view()

class UserProfileView(LoginRequiredMixin, TemplateView):
	template_name = 'users/user_profile.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['u_form'] = UserForm(instance=self.request.user)
		context['p_form'] = UserProfileForm(instance=self.request.user.userprofile)
		return context

	def post(self, request, *args, **kwargs):
		u_form = UserForm(request.POST, instance=self.request.user)
		p_form = UserProfileForm(request.POST, request.FILES, instance=self.request.user.userprofile)
		if u_form.is_valid() and p_form.is_valid():
			u_form.save()
			p_form.save()
			return redirect('user_profile')
		return self.render_to_response({'u_form': u_form, 'p_form': p_form})

user_profile_view = UserProfileView.as_view()
