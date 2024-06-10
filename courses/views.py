from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, CreateView, ListView, View, UpdateView
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from courses.models import Course, Module, Lecture, AdditionalFile, Category
from courses.forms import ModuleForm
from courses.decorators import AjaxRequiredOnlyMixin
from purchase.cart import Cart
import json

# Create your views here.

class HomePageView(TemplateView):
	template_name = 'courses/home.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		courses = Course.published.all()
		categories = Category.objects.all()
		context.update(courses=courses, categories=categories)
		return context

home_page_view = HomePageView.as_view()

class CourseCreateView(LoginRequiredMixin, CreateView):
	model = Course
	fields = ['name', 'headline', 'description', 'category', 'thumbnail', 'price', 'discount',]

	def form_valid(self, form):
		form.instance.owner = self.request.user
		return super().form_valid(form)

	def get_success_url(self):
		return reverse_lazy('module_list', kwargs={'pk': self.object.pk})

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
	fields = ['topic', 'video', 'content',]

	def dispatch(self, request, *args, **kwargs):
		self.module = Module.objects.get(pk=kwargs['module_pk'])
		return super().dispatch(request, *args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['module'] = self.module
		return context

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
		return JsonResponse({'status': 'success'})

lecture_order_update_view = LectureOrderUpdateView.as_view()

class LectureDetailView(UserPassesTestMixin, LoginRequiredMixin, DetailView):
	model = Lecture

	def test_func(self):
		return self.request.user == self.get_object().module.course.owner

lecture_detail_view = LectureDetailView.as_view()

class LectureUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
	model = Lecture
	fields = ['topic', 'video', 'content',]

	def form_valid(self, form):
		files = self.request.FILES.getlist('additional_file')
		if files:
			self.object.additionalfile_set.all().delete()
			for file in files:
				AdditionalFile.objects.create(lecture=self.object, file=file)
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('lecture_detail', kwargs={'pk': self.object.pk})

	def test_func(self):
		return self.request.user == self.get_object().module.course.owner

lecture_update_view = LectureUpdateView.as_view()

class LectureDeleteView(UserPassesTestMixin, LoginRequiredMixin, View):
	def post(self, request, *args, **kwargs):
		lecture = Lecture.objects.get(pk=kwargs['lecture_pk'])
		module = lecture.module
		lecture.delete()
		return redirect('lecture_list', module_pk=module.pk)

	def test_func(self):
		return self.request.user == Lecture.objects.get(pk=self.kwargs['lecture_pk']).module.course.owner

lecture_delete_view = LectureDeleteView.as_view()

class UserCourseListView(LoginRequiredMixin, ListView):
	template_name = 'courses/user_courses.html'
	def get_queryset(self):
		return Course.objects.filter(owner=self.request.user)

user_course_list_view = UserCourseListView.as_view()

class CourseDetailView(DetailView):
	model = Course

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['cart'] = Cart(self.request)
		return context

course_detail_view = CourseDetailView.as_view()

class CourseUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):
	model = Course
	fields = ['name', 'headline', 'description', 'category', 'thumbnail', 'price', 'discount',]

	def get_success_url(self):
		return reverse_lazy('module_list', kwargs={'pk': self.object.pk})

	def test_func(self):
		return self.request.user == self.get_object().owner

course_update_view = CourseUpdateView.as_view()

class CoursePublishView(UserPassesTestMixin, LoginRequiredMixin, View):
	def post(self, request, *args, **kwargs):
		course = Course.objects.get(pk=kwargs['course_pk'])
		modules = course.module_set.all()
		if modules.count() < 3:
			messages.error(request, 'Your Course Must Have At Least 3 Modules Before It Can Be Published')
			return redirect(request.META.get('HTTP_REFERER'))
		for module in modules:
			if module.lecture_set.all().count() < 3:
				messages.error(request, 'All Modules Must Have At Least 3 Lectures Before It Can Be Published')
				return redirect(request.META.get('HTTP_REFERER'))
		course.publish = True
		course.save()
		return redirect('course_detail', pk=course.pk)

	def test_func(self):
		return self.request.user == Course.objects.get(pk=self.kwargs['course_pk']).owner

course_publish_view = CoursePublishView.as_view()

class StudentCourseListView(LoginRequiredMixin, ListView):
	template_name = 'courses/mylearning.html'
	paginate_by = 6
	def get_queryset(self):
		query = self.request.GET.get('search_course', '')
		return Course.objects.filter(students__in=[self.request.user]).filter(name__icontains=query)

student_course_list_view = StudentCourseListView.as_view()

class StudentCourseDetailView(UserPassesTestMixin, LoginRequiredMixin, TemplateView):
	template_name = 'courses/student_course_detail.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		course = Course.objects.get(pk=kwargs['pk'])
		lecture_pk = kwargs.get('lecture_pk')
		if lecture_pk:
			lecture = Lecture.objects.get(pk=lecture_pk)
		else:
			lecture = course.module_set.all().first().lecture_set.all().first()
		context.update(lecture=lecture, course=course)
		return context

	def test_func(self):
		course = Course.objects.get(pk=self.kwargs['pk'])
		return self.request.user in course.students.all() or self.request.user == course.owner

student_course_detail_view = StudentCourseDetailView.as_view()

class CourseListView(ListView):
	paginate_by = 6
	category = None
	def dispatch(self, request, *args, **kwargs):
		if kwargs.get('category_pk'):
			self.category = Category.objects.get(pk=kwargs.get('category_pk'))
		return super().dispatch(request, *args, **kwargs)
	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['category'] = self.category
		return context
	def get_queryset(self):
		query = self.request.GET.get('search_course', '')
		queryset = Course.objects.filter(name__icontains=query)
		if self.category:
			queryset = Course.objects.filter(category_id=self.category.pk)
		return queryset

course_list_view = CourseListView.as_view()

