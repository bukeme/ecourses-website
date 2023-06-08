from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

class Category(models.Model):
	category = models.CharField(max_length=200)

	def __str__(self):
		return self.category


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

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if self.discount:
			self.actual_price = (self.price * self.discount) / 100
		else:
			self.actual_price = self.price
		return super(Course, self).save(*args, **kwargs)

class Rating(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	student = models.ForeignKey(User, on_delete=models.CASCADE)
	rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

class Module(models.Model):
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	name = models.CharField(max_length=500)
	order = models.IntegerField(blank=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.order = Module.objects.all().count() + 1
		self.course.updated = timezone.now()
		self.course.save()
		return super(Module, self).save(*args, **kwargs)
