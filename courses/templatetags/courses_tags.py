from django import template
from purchase.cart import Cart

register = template.Library()

@register.simple_tag
def cart_count(request):
	cart = Cart(request)
	return len(cart)