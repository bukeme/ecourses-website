from courses.models import Course
from purchase.models import Coupon
from django.conf import settings
import os


class Cart:
	def __init__(self, request):
		self.session = request.session
		try:
			self.cart = self.session['cart']
		except:
			request.session['cart'] = {}
			self.cart = {}
		self.coupon_code = request.session.get('coupon_code')

	def save(self):
		self.session.modified = True

	def add(self, course_pk):
		self.cart[course_pk] = ''
		self.save()

	def remove(self, course_pk):
		del self.cart[course_pk]
		self.save()

	def clear(self):
		self.session['cart'].clear()
		# self.cart.clear()
		if self.session.get('coupon_code'):
			del self.session['coupon_code']
		self.save()

	def getname(self):
		name = ''
		for index, course in enumerate(self, start=1):
			name += f'<{index}>{course.name}  '
		return name

	def total_price(self):
		total_price, actual_total_price = 0, 0
		for course_pk in self.cart.keys():
			course = Course.objects.get(pk=int(course_pk))
			total_price += course.price
			actual_total_price += course.actual_price
		coupon = Coupon.objects.get_valid_coupon(coupon_code=self.coupon_code)
		if coupon:
			actual_total_price = round((actual_total_price * (100 - coupon.discount) / 100), 2)
		return {'total_price': total_price, 'actual_total_price': actual_total_price}

	def __len__(self):
		return len(self.cart.values())

	def __iter__(self):
		courses = Course.objects.filter(pk__in=self.cart.keys())
		cart = self.cart.copy()
		for course in courses:
			cart[str(course.pk)] = course

		for item in cart.values():
			yield item

