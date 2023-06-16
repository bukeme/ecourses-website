from django import template
from purchase.cart import Cart
from courses.models import Category

register = template.Library()

@register.simple_tag
def cart_count(request):
	cart = Cart(request)
	return len(cart)

@register.simple_tag
def category_list():
	return Category.objects.all()