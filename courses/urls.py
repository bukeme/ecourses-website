from django.urls import path
from . import views


urlpatterns = [
	path('', views.home_page_view, name='home'),
	path('course-create', views.course_create_view, name='course_create'),
	path('course/<int:pk>/module-list', views.module_list_view, name='module_list'),
	path('module/<int:course_pk>/create/', views.module_create_view, name='module_create'),
	path('module/<int:module_pk>/update/', views.module_update_view, name='module_update'),
	path('module/<int:module_pk>/delete/', views.module_delete_view, name='module_delete'),
	path('module/<int:course_pk>/order/update/', views.module_order_update_view, name='module_order_update'),
]