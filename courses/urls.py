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
	path('lecture/<int:module_pk>/list/', views.lecture_list_view, name='lecture_list'),
	path('lecture/<int:module_pk>/create/', views.lecture_create_view, name='lecture_create'),
	path('lecture/<int:course_pk>/order/update/', views.lecture_order_update_view, name='lecture_order_update'),
	path('lecture/<int:pk>/detail/', views.lecture_detail_view, name='lecture_detail'),
	path('lecture/<int:pk>/update/', views.lecture_update_view, name='lecture_update'),
	path('lecture/<int:lecture_pk>/delete/', views.lecture_delete_view, name='lecture_delete'),
]