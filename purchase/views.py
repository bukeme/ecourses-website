from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View, TemplateView
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from purchase.cart import Cart
from purchase.models import Coupon, Payment
import stripe
import math

stripe.api_key = settings.STRIPE_SECRET_KEY

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

class PurchaseView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        price = math.ceil(cart.total_price()['actual_total_price'])
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': cart.getname(),
                        },
                        'unit_amount': price * 100,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url = settings.BACKEND_HOST + reverse('purchase_success'),
            cancel_url = settings.BACKEND_HOST + reverse('purchase_cancel'),
        )
        return redirect(checkout_session.url)

purchase_view = PurchaseView.as_view()

class PurchaseSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/purchase_success.html'

    def dispatch(self, request, *args, **kwargs):
        cart = Cart(request)
        price = math.ceil(cart.total_price()['actual_total_price'])
        payment = Payment.objects.create(user=request.user, amount=price)
        for course in cart:
            payment.courses.add(course)
            course.students.add(request.user)
            payment.save()
            course.save()
        cart.clear()
        return super().dispatch(request, *args, **kwargs)

purchase_success_view = PurchaseSuccessView.as_view()

class PurchaseCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/purchase_cancel.html'

purchase_cancel_view = PurchaseCancelView.as_view()
