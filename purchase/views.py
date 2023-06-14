from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.views.generic.base import RedirectView
from django.contrib import messages
from django.db.models import Q
from purchase.cart import Cart
from purchase.models import Coupon

# Create your views here.


class CartAddView(View):
	def post(self, request, *args, **kwargs):
		cart = Cart(request)
		cart.add(str(kwargs['course_pk']))
		return redirect(request.META.get('HTTP_REFERER'))

cart_add_view = CartAddView.as_view()

class CartItemListView(TemplateView):
	template_name = 'purchase/cart.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		cart = Cart(self.request)
		cart_total_price = cart.total_price()
		total_price = cart_total_price['total_price']
		actual_total_price = cart_total_price['actual_total_price']
		coupon = Coupon.objects.get_valid_coupon(coupon_code=self.request.session.get('coupon_code'))
		context.update(cart=cart, total_price=total_price, actual_total_price=actual_total_price, cart_len=len(cart), coupon=coupon)
		return context

cart_item_list_view = CartItemListView.as_view()

class CartItemRemoveView(View):
	def post(self, request, *args, **kwargs):
		cart = Cart(request)
		cart.remove(str(kwargs['course_pk']))
		return redirect(request.META.get('HTTP_REFERER'))

cart_item_remove_view = CartItemRemoveView.as_view()

class ApplyCoupon(View):
	def post(self, request, *args, **kwargs):
		coupon_code = request.POST.get('coupon')
		coupon = Coupon.objects.get_valid_coupon(coupon_code=coupon_code)
		if coupon:
			request.session['coupon_code'] = coupon.code
		else:
			messages.error(request, 'Invalid Coupon Code')
		return redirect(request.META.get('HTTP_REFERER'))

apply_coupon = ApplyCoupon.as_view()

class RemoveCoupon(RedirectView):
	def get_redirect_url(self, *args, **kwargs):
		del self.request.session['coupon_code']
		self.request.session.modified = True
		return self.request.META.get('HTTP_REFERER')

remove_coupon = RemoveCoupon.as_view()
