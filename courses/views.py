from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from courses.models import Course, Module
from courses.forms import ModuleForm

# Create your views here.

class HomePageView(TemplateView):
	template_name = 'courses/home.html'

home_page_view = HomePageView.as_view()

class CourseCreateView(LoginRequiredMixin, CreateView):
	model = Course
	fields = ['name', 'headline', 'description', 'category', 'thumbnail', 'price', 'discount',]

	def form_valid(self, form):
		form.instance.owner = self.request.user
		return super().form_valid(form)

	def get_success_url(self):
		return reverse_lazy('course_module_list', kwargs={'pk': self.object.pk})

course_create_view = CourseCreateView.as_view()

class ModuleListView(UserPassesTestMixin, LoginRequiredMixin, SingleObjectMixin, ListView):
	def dispatch(self, request, *args, **kwargs):
		self.object = self.get_object(queryset=Course.objects.all())
		return super().dispatch(request, *args, **kwargs)

	def get_queryset(self):
		return self.object.module_set.all()

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['course'] = self.object
		context['form'] = ModuleForm()
		return context

	def test_func(self):
		return self.request.user == self.object.owner

module_list_view = ModuleListView.as_view()

class ModuleCreateView(UserPassesTestMixin, LoginRequiredMixin, View):
	def post(self, request, *args, **kwargs):
		course = Course.objects.get(pk=kwargs['course_pk'])
		form = ModuleForm(request.POST)
		if form.is_valid():
			form.instance.course = course
			obj = form.save()
		return redirect(request.META['HTTP_REFERER'])

	def test_func(self):
		return self.request.user == Course.objects.get(pk=self.kwargs['course_pk']).owner

module_create_view = ModuleCreateView.as_view()

