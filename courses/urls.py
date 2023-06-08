from django.urls import path
from . import views


urlpatterns = [
	path('', views.home_page_view, name='home'),
	path('course-create', views.course_create_view, name='course_create'),
	path('course/<int:pk>/module-list', views.module_list_view, name='module_list'),
	path('module/<int:course_pk>/create/', views.module_create_view, name='module_create'),
]