from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from courses.models import Course

# Create your models here.

class CouponManager(models.Manager):
	def get_valid_coupon(self, coupon_code):
		queryset = super().get_queryset().filter(
			Q(start_date__lte=timezone.now()) &
			Q(end_date__gte=timezone.now())
		)
		try:
			queryset = queryset.filter(code=coupon_code).first()
			return queryset
		except:
			return None

class Coupon(models.Model):
	code = models.CharField(max_length=200, unique=True)
	discount = models.DecimalField(max_digits=4, decimal_places=2)
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()

	objects = CouponManager()

	def __str__(self):
		return self.code

class Payment(models.Model):
    courses = models.ManyToManyField(Course)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

