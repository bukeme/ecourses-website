from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView, View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from courses.models import Course, Module, Lecture, AdditionalFile
from courses.forms import ModuleForm
from courses.decorators import AjaxRequiredOnlyMixin
import json

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
		return redirect('lecture_list', module_pk=obj.pk)

	def test_func(self):
		return self.request.user == Course.objects.get(pk=self.kwargs['course_pk']).owner

module_create_view = ModuleCreateView.as_view()

class ModuleUpdateView(UserPassesTestMixin, LoginRequiredMixin, View):
	def post(self, request, *args, **kwargs):
		module = Module.objects.get(pk=kwargs['module_pk'])
		form = ModuleForm(request.POST, instance=module)
		if form.is_valid():
			form.save()
		return redirect(request.META['HTTP_REFERER'])

	def test_func(self):
		return self.request.user == Module.objects.get(pk=self.kwargs['module_pk']).course.owner

module_update_view = ModuleUpdateView.as_view()

class ModuleDeleteView(UserPassesTestMixin, LoginRequiredMixin, View):
	def post(self, request, *args, **kwargs):
		module = Module.objects.get(pk=kwargs['module_pk'])
		course = module.course
		module.delete()
		return redirect('module_list', pk=course.pk)

	def test_func(self):
		return self.request.user == Module.objects.get(pk=self.kwargs['module_pk']).course.owner

module_delete_view = ModuleDeleteView.as_view()

class ModuleOrderUpdateView(AjaxRequiredOnlyMixin, View):
	def post(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'not logged in'})
		if self.request.user != Course.objects.get(pk=kwargs['course_pk']).owner:
			return JsonResponse({'status': 'forbidden'})
		data = json.loads(request.body)
		for module_dict in data:
			module_obj = Module.objects.get(pk=int(module_dict['pk']))
			module_obj.order = module_dict['order']
			module_obj.save()
		print(data)
		return JsonResponse({'status': 'success'})

module_order_update_view = ModuleOrderUpdateView.as_view()

class LectureListView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
	template_name = 'courses/lecture_list.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		module = Module.objects.get(pk=kwargs['module_pk'])
		course = module.course
		course_module_list = course.module_set.all()
		form = ModuleForm()
		context.update(module=module, course=course, course_module_list=course_module_list, form=form)
		return context

	def test_func(self, *args, **kwargs):
		return self.request.user == Module.objects.get(pk=self.kwargs['module_pk']).course.owner

lecture_list_view = LectureListView.as_view()

class LectureCreateView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
	model = Lecture
	fields = ['topic', 'content',]

	def dispatch(self, request, *args, **kwargs):
		self.module = Module.objects.get(pk=kwargs['module_pk'])
		return super().dispatch(request, *args, **kwargs)

	def form_valid(self, form):
		form.instance.module = self.module
		files = self.request.FILES.getlist('additional_file')
		if files:
			lecture = form.save()
			for file in files:
				AdditionalFile.objects.create(lecture=lecture, file=file)
			return redirect('lecture_detail', pk=lecture.pk)
		else:
			return super().form_valid(form)

	def get_success_url(self):
		return reverse('lecture_detail', kwargs={'pk': self.object.pk})

	def test_func(self):
		return self.request.user == self.module.course.owner

lecture_create_view = LectureCreateView.as_view()

class LectureOrderUpdateView(AjaxRequiredOnlyMixin, View):
	def post(self, request, *args, **kwargs):
		if not request.user.is_authenticated:
			return JsonResponse({'status': 'not logged in'})
		if self.request.user != Course.objects.get(pk=kwargs['course_pk']).owner:
			return JsonResponse({'status': 'forbidden'})
		data = json.loads(request.body)
		for lecture_dict in data:
			lecture_obj = Lecture.objects.get(pk=int(lecture_dict['pk']))
			lecture_obj.order = lecture_dict['order']
			lecture_obj.save()
		print(data)
		return JsonResponse({'status': 'success'})

lecture_order_update_view = LectureOrderUpdateView.as_view()

class LectureDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
	model = Lecture

	def test_func(self):
		return self.request.user == self.get_object().module.course.owner

lecture_detail_view = LectureDetailView.as_view()

