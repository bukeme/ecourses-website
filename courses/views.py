from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class HomePageView(TemplateView):
	template_name = 'courses/home.html'

home_page_view = HomePageView.as_view()
