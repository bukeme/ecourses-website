from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

class Category(models.Model):
	category = models.CharField(max_length=200)
	thumbnail = models.ImageField(upload_to='category_thumbnail/%Y-%m-%d', default='profile_image/placeholder.jpg')

	def __str__(self):
		return self.category

class Published(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(publish=True)


class Course(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=500)
	headline = models.CharField(max_length=500)
	description = RichTextField(config_name='desc')
	thumbnail = models.ImageField(upload_to='courses_thumbnail/%Y-%m-%d')
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	discount = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
	actual_price = models.DecimalField(max_digits=6, decimal_places=2)
	students = models.ManyToManyField(User, blank=True, related_name='purchased_courses')
	publish = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	objects = models.Manager()
	published = Published()

	def __str__(self):
		return self.name

	def lecture_count(self):
		return sum([module.lecture_set.all().count() for module in self.module_set.all()])

	def save(self, *args, **kwargs):
		if self.discount:
			self.actual_price = (self.price) * (100 - self.discount) / 100
		else:
			self.actual_price = self.price
		return super(Course, self).save(*args, **kwargs)
		
class Module(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	name = models.CharField(max_length=500)
	order = models.IntegerField(blank=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.pk:
			self.order = Module.objects.filter(course=self.course).count() + 1
		self.course.updated = timezone.now()
		self.course.save()
		return super(Module, self).save(*args, **kwargs)

	class Meta:
		ordering = ['order',]

class Lecture(models.Model):
	module = models.ForeignKey(Module, on_delete=models.CASCADE)
	topic = models.CharField(max_length=500)
	content = RichTextUploadingField()
	order = models.IntegerField(blank=True)

	def __str__(self):
		return self.topic

	def save(self, *args, **kwargs):
		if not self.pk:
			self.order = Lecture.objects.filter(module=self.module).count() + 1
		self.module.course.updated = timezone.now()
		self.module.course.save()
		return super(Lecture, self).save(*args, **kwargs)

	def next(self):
		module = self.module
		try:
			next_lecture = module.lecture_set.filter(order=self.order+1).first()
		except:
			next_lecture = None
		if next_lecture:
			return next_lecture
		try:
			next_lecture = module.course.module_set.filter(order=module.order+1).first().lecture_set.all().first()
		except:
			next_lecture = None
		return next_lecture

	def prev(self):
		module = self.module
		try:
			prev_lecture = module.lecture_set.filter(order=self.order-1).first()
		except:
			prev_lecture = None
		if prev_lecture:
			return prev_lecture
		try:
			prev_lecture = module.course.module_set.filter(order=module.order-1).first().lecture_set.all().last()
		except:
			prev_lecture = None
		return prev_lecture

	class Meta:
		ordering = ['order',]

class AdditionalFile(models.Model):
	lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
	file = models.FileField(upload_to='additional_files/%Y-%m-%d')
	
