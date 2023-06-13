from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from purchase.cart import Cart

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
		# cart_items = [item for item in cart]
		cart_total_price = cart.total_price()
		total_price = cart_total_price['total_price']
		actual_total_price = cart_total_price['actual_total_price']
		context.update(cart=cart, total_price=total_price, actual_total_price=actual_total_price, cart_len=len(cart))
		return context

cart_item_list_view = CartItemListView.as_view()

class CartItemRemoveView(View):
	def post(self, request, *args, **kwargs):
		cart = Cart(request)
		cart.remove(str(kwargs['course_pk']))
		return redirect(request.META.get('HTTP_REFERER'))

cart_item_remove_view = CartItemRemoveView.as_view()
