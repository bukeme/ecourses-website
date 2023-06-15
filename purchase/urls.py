from django.urls import path
from . import views


urlpatterns = [
	path('cart/<int:course_pk>/add/', views.cart_add_view, name='cart_add'),
	path('cart/', views.cart_item_list_view, name='cart'),
	path('cart/<int:course_pk>/remove/', views.cart_item_remove_view, name='cart_remove'),
	path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
	path('coupon/remove/', views.remove_coupon, name='remove_coupon'),
    path('purchase/', views.purchase_view, name='purchase'),
    path('purchase-success/', views.purchase_success_view, name='purchase_success'),
    path('purchase-cancel/', views.purchase_cancel_view, name='purchase_cancel'),
]