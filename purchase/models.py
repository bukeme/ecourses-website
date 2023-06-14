from django.db import models
from django.utils import timezone
from django.db.models import Q

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
	code = models.CharField(max_length=200)
	discount = models.DecimalField(max_digits=4, decimal_places=2)
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()

	objects = CouponManager()

	def __str__(self):
		return self.code

	# def is_valid(self):
	# 	return self.start_date <= timezone.now() and self.end_date >= timezone.now()
