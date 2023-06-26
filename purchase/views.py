from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View, TemplateView, ListView
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from purchase.cart import Cart
from purchase.models import Coupon, Payment, Notification
from courses.models import Course
import stripe
import math

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

class CartAddView(UserPassesTestMixin, View):
    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        cart.add(str(kwargs['course_pk']))
        return redirect(request.META.get('HTTP_REFERER'))
    def test_func(self):
        course = Course.objects.get(pk=self.kwargs['course_pk'])
        user =self.request.user
        return not user in course.students.all() and user != course.owner

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

class PurchaseCourse(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        course = Course.objects.get(pk=kwargs['course_pk'])
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': course.name,
                        },
                        'unit_amount': math.ceil(course.actual_price) * 100,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url = settings.BACKEND_HOST + reverse('course_purchase_success', kwargs={'course_pk': course.pk}),
            cancel_url = settings.BACKEND_HOST + reverse('purchase_cancel'),
        )
        return redirect(checkout_session.url, course_pk=course.pk)

purchase_course = PurchaseCourse.as_view()

class PurchaseSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/purchase_success.html'

    def dispatch(self, request, *args, **kwargs):
        cart = Cart(request)
        if kwargs.get('course_pk'):
            course = Course.objects.get(pk=kwargs['course_pk'])
            payment = Payment.objects.create(user=request.user, amount=course.price)
            payment.courses.add(course)
            course.students.add(request.user)
            course.save()
            cart.remove(kwargs['course_pk'])
            Notification.objects.create(actor=request.user, course=course, recipient=course.owner)
        else:
            price = math.ceil(cart.total_price()['actual_total_price'])
            payment = Payment.objects.create(user=request.user, amount=price)
            for course in cart:
                payment.courses.add(course)
                course.students.add(request.user)
                payment.save()
                course.save()
                Notification.objects.create(actor=request.user, course=course, recipient=course.owner)
            cart.clear()
        return super().dispatch(request, *args, **kwargs)

purchase_success_view = PurchaseSuccessView.as_view()

class PurchaseCancelView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/purchase_cancel.html'

purchase_cancel_view = PurchaseCancelView.as_view()

class PurchaseHistoryView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

purchase_history_view = PurchaseHistoryView.as_view()

class NotificationListView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase/notification_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        n_type = kwargs['n_type']
        if n_type == 'all':
            queryset = Notification.objects.filter(recipient=self.request.user)
        elif n_type == 'unread':
            queryset = Notification.objects.filter(recipient=self.request.user, read=False)
        context['notifications'] = queryset
        return context

notification_list_view = NotificationListView.as_view()

class NotificationReadView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        notification = Notification.objects.get(pk=kwargs['n_pk'])
        notification.read = True
        notification.save()
        return reverse('course_detail', kwargs={'pk': kwargs['course_pk']})

notification_read_view = NotificationReadView.as_view()
